#!/usr/bin/env python3
"""GoogleフォームのFB、配布版、Classroomへの掲載確認をローカルで管理する。通信・投稿は行わない。"""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from urllib.parse import urlsplit

import package_classroom_materials as packaging
from materials_lock import distribution_lock

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / 'distributions/workflow.json'
OUTPUT = ROOT / 'distributions/classroom'
REQUIRED_COLUMNS = ['タイムスタンプ', '課題ID', '教材の版', '手順番号', '困ったこと・気づいたこと']


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load():
    return json.loads(STATE.read_text())


def save(state):
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=STATE.parent,
                                     prefix=STATE.name + '.', suffix='.tmp', delete=False) as file:
        temp = Path(file.name)
        try:
            file.write(json.dumps(state, ensure_ascii=False, indent=2) + '\n')
            file.close()
            temp.replace(STATE)
        finally:
            temp.unlink(missing_ok=True)


def classroom_url(value):
    url = urlsplit(value)
    if url.scheme != 'https' or url.hostname != 'classroom.google.com':
        raise ValueError('ClassroomのHTTPS URLを指定してください')
    return value


def course_key(value):
    classroom_url(value)
    match = re.search(r'/c/([^/]+)', urlsplit(value).path)
    if not match:
        raise ValueError('クラスを識別できるClassroomのURLが必要です')
    return match.group(1)


def drive_key(value, kind):
    url = urlsplit(value)
    pattern = r'/folders/([A-Za-z0-9_-]+)' if kind == 'folder' else r'/file/d/([A-Za-z0-9_-]+)'
    match = re.search(pattern, url.path)
    if url.scheme != 'https' or url.hostname != 'drive.google.com' or not match:
        raise ValueError('Google DriveのフォルダURL' if kind == 'folder' else 'Google DriveのファイルURLが必要です')
    return match.group(1)


def find_target(state, target_id):
    target = next((t for t in state['targets'] if t['id'] == target_id), None)
    if target is None:
        raise ValueError('配布先が未登録です。先にtargetコマンドを使ってください')
    return target


def configure_drive(state, args):
    target = find_target(state, args.target)
    if args.command == 'drive-target':
        folder_id = drive_key(args.folder_url, 'folder')
        if target.get('driveFolderId') and target['driveFolderId'] != folder_id:
            raise ValueError('Drive保存先は登録済みです。配布履歴への影響を確認して変更してください')
        target.update(driveFolderId=folder_id, driveFolderUrl=args.folder_url)
    else:
        file_id = drive_key(args.file_url, 'file')
        files = target.setdefault('driveFiles', {})
        if files.get(args.assignment) and files[args.assignment]['id'] != file_id:
            raise ValueError('別のDriveファイルが登録済みです。共有リンクと掲載履歴を確認してください')
        files[args.assignment] = {'id': file_id, 'url': args.file_url}
    save(state)
    print('Driveの参照先を保存しました。アップロード・掲載確認は別に行います。')


def upload_plan(state, args):
    target = find_target(state, args.target)
    if not target.get('driveFolderId'):
        raise ValueError('Driveの保存先が未登録です')
    releases = [r for r in state['releases'] if r['assignment'] == args.assignment]
    if not releases or current_problems(releases[-1]):
        raise ValueError('現在の教材に一致する準備版が必要です')
    release = releases[-1]
    file = target.get('driveFiles', {}).get(args.assignment)
    plan = {'operation': 'update-existing-file' if file else 'upload-new-file',
            'target': args.target, 'assignment': args.assignment, 'version': release['version'],
            'folderId': target['driveFolderId'], 'fileId': file['id'] if file else None,
            'localArchive': str(OUTPUT / release['archive']), 'sha256': release['sha256'],
            'mimeType': 'application/zip', 'fileName': release['archive'],
            'classroomUrl': target['courseUrl'], 'executed': False}
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    return plan


def source_snapshot(assignment):
    materials = ROOT / 'assignments' / packaging.ASSIGNMENTS[assignment] / 'materials'
    files, _ = packaging.collect(materials)
    if assignment == 'A02':
        teacher = materials.parent / 'teacher'
        files += [teacher / name for name in ('steps.json', 'render_materials.py', 'check_materials.py', 'assemble.py')]
    return {str(p.relative_to(ROOT)): digest(p) for p in files}


def current_problems(release):
    archive = OUTPUT / release['archive']
    issues = []
    if not archive.is_file() or digest(archive) != release['sha256']:
        issues.append('配布ZIPが欠落または変更')
    try:
        if source_snapshot(release['assignment']) != release['inputs']:
            issues.append('教材変更あり：新版を作成する')
    except (ValueError, OSError) as error:
        issues.append(f'教材参照の検査失敗: {error}')
    return issues


def delivered(state, release):
    required = {t['id'] for t in state['targets']}
    return bool(required) and required.issubset(release['deliveries'])


def import_feedback(state, args):
    source = urlsplit(args.source)
    if source.scheme != 'https' or not source.hostname:
        raise ValueError('回答元のGoogleフォームまたは回答シートのHTTPS URLが必要です')
    registered_source = state['feedbackSource'].get('responsesSheetUrl')
    if registered_source and registered_source != args.source:
        raise ValueError('登録済みの回答シートURLと一致しません。受付先の変更はsourceコマンドで行ってください')
    known = {f['sourceKey'] for f in state['feedback']}
    additions = []
    with args.csv.open(encoding='utf-8-sig', newline='') as file:
        rows = csv.DictReader(file)
        if not rows.fieldnames or not set(REQUIRED_COLUMNS).issubset(rows.fieldnames):
            raise ValueError('CSVに必要な列: ' + ' / '.join(REQUIRED_COLUMNS))
        for number, row in enumerate(rows, 2):
            record = {key: (row.get(key) or '').strip() for key in REQUIRED_COLUMNS}
            if not any(record.values()):
                continue
            if not all(record.values()) or record['課題ID'] not in packaging.ASSIGNMENTS:
                raise ValueError(f'CSV {number}行目の必須項目・課題IDを確認してください')
            key = hashlib.sha256((args.source + json.dumps(record, ensure_ascii=False, sort_keys=True)).encode()).hexdigest()
            if key in known:
                continue
            additions.append({
                'id': f"FB-{len(state['feedback']) + len(additions) + 1:04d}", 'sourceKey': key,
                'source': args.source, 'receivedAt': record['タイムスタンプ'],
                'assignment': record['課題ID'], 'version': record['教材の版'],
                'step': record['手順番号'], 'summary': record['困ったこと・気づいたこと'],
                'expected': (row.get('期待した表示や動作') or '').strip(),
                'decision': None,
            })
            known.add(key)
    state['feedback'].extend(additions)
    if source.hostname == 'docs.google.com' and '/spreadsheets/' in source.path:
        state['feedbackSource']['responsesSheetUrl'] = args.source
    state['feedbackSource']['lastImportedAt'] = now()
    save(state)
    print(f'FBを{len(additions)}件追加しました。同じ回答の再取込は追加しません。')


def configure_source(state, args):
    form, sheet = urlsplit(args.form_url), urlsplit(args.responses_sheet_url)
    if form.scheme != 'https' or not (form.hostname == 'forms.gle' or
            (form.hostname == 'docs.google.com' and form.path.startswith('/forms/'))):
        raise ValueError('GoogleフォームのHTTPS URLが必要です')
    if sheet.scheme != 'https' or sheet.hostname != 'docs.google.com' or not sheet.path.startswith('/spreadsheets/'):
        raise ValueError('回答先のGoogleスプレッドシートのHTTPS URLが必要です')
    source = state['feedbackSource']
    if (source.get('formUrl'), source.get('responsesSheetUrl')) != (args.form_url, args.responses_sheet_url):
        for key in ('formTitle', 'publicationStatus', 'responseSheetTab', 'verifiedAt',
                    'verificationMethod', 'storage', 'emailCollection', 'responseSummaryShared',
                    'responseCountAtVerification', 'lastImportedAt'):
            source.pop(key, None)
    state['feedbackSource'].update(formUrl=args.form_url, responsesSheetUrl=args.responses_sheet_url)
    save(state)
    print('受付先URLを登録しました。回答の取得はimport-feedbackで行います。')


def prepare(state, args):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*', args.version):
        raise ValueError('版名には英数字・ピリオド・ハイフン・アンダースコアを使います')
    if any(r['assignment'] == args.assignment and r['version'] == args.version for r in state['releases']):
        raise ValueError('登録済みの版です。statusを確認するか、新しい版名を指定してください')
    linked = set(args.feedback or [])
    previous = [r for r in state['releases'] if r['assignment'] == args.assignment]
    if previous and not delivered(state, previous[-1]):
        linked.update(previous[-1]['feedback'])
    records = {f['id']: f for f in state['feedback']}
    for fid in linked:
        if fid not in records or records[fid]['assignment'] != args.assignment or records[fid]['decision']:
            raise ValueError(f'この版へ対応付けできないFB: {fid}')
    if args.assignment == 'A02':
        teacher = ROOT / 'assignments/A02-profile-card/teacher'
        for script in ('render_materials.py', 'check_materials.py'):
            subprocess.run([sys.executable, '-B', str(teacher / script)], check=True)
    manifest = packaging.package(args.assignment, args.version, OUTPUT)
    release = {
        'assignment': args.assignment, 'version': args.version, 'preparedAt': now(),
        'archive': manifest['archive'], 'sha256': manifest['sha256'],
        'feedback': sorted(linked), 'changes': args.changes,
        'studentAction': args.student_action, 'verification': args.verification,
        'inputs': source_snapshot(args.assignment), 'deliveries': {},
    }
    notice = f'''{args.assignment} 教材更新：{args.version}

変更したこと
{args.changes}

学生が行うこと
{args.student_action}

添付する教材：{manifest['archive']}
教材ZIPを展開してindex.htmlを開いてください。
作業中のAndroidプロジェクトは上書きしないでください。
提出物はAPKファイル1つのみです。
'''
    (OUTPUT / (Path(manifest['archive']).stem + '.classroom-update.txt')).write_text(notice)
    state['releases'].append(release)
    save(state)
    print('版を登録しました。Classroomへの掲載・学生向け更新案内は未実施です。')


def record_delivery(state, args):
    target = find_target(state, args.target)
    releases = [r for r in state['releases'] if r['assignment'] == args.assignment]
    if not releases or releases[-1]['version'] != args.version:
        raise ValueError('最新の準備済み版だけ掲載完了を記録できます')
    release = releases[-1]
    if current_problems(release):
        raise ValueError('ZIPまたは教材が準備時から変わりました。新版を作成してください')
    if digest(args.downloaded_zip) != release['sha256']:
        raise ValueError('Classroomから再取得したZIPが、準備した版と一致しません')
    classroom_url(args.material_url)
    classroom_url(args.notice_url)
    if {course_key(args.material_url), course_key(args.notice_url)} != {course_key(target['courseUrl'])}:
        raise ValueError('掲載先・更新案内のクラスが、登録した配布先と一致しません')
    if args.target in release['deliveries']:
        raise ValueError('この版・配布先は記録済みです。再投稿せずstatusを確認してください')
    release['deliveries'][args.target] = {
        'recordedAt': now(), 'materialUrl': args.material_url, 'noticeUrl': args.notice_url,
        'downloadSha256': release['sha256'], 'studentAccessCheck': args.student_check,
    }
    save(state)
    print('掲載先・更新案内・再取得ZIPの一致・学生側の確認を記録しました。')


def status(state):
    lines = ['# 教材更新の状況', '', 'この表はローカルの記録です。Classroomを自動照会した結果ではありません。',
             'Googleフォームの回答はCSV取込時点までが対象です。新しい回答の自動監視は未接続です。', '']
    lines.append('回答の最終取込：' + state['feedbackSource'].get('lastImportedAt', '未取込'))
    source = state['feedbackSource']
    if source.get('formUrl'):
        lines.append(f"受付フォーム：[Googleフォーム]({source['formUrl']})")
    if source.get('responsesSheetUrl'):
        lines.append(f"回答保存先：[Googleスプレッドシート]({source['responsesSheetUrl']})")
    if source.get('publicationStatus') == 'unpublished':
        lines.append('フォーム公開状況：未公開として確認済み（回答の受付開始は公開後）。')
    for target in state['targets']:
        lines.append(f"配布先 {target['id']}：[Classroom]({target['courseUrl']})")
        if target.get('driveFolderUrl'):
            lines.append(f"Drive保存先：[教材フォルダ]({target['driveFolderUrl']})")
    lines.append('')
    pending = []
    if not state['targets']:
        pending.append('Classroomの配布先が未設定')
    if not state['feedbackSource'].get('responsesSheetUrl'):
        pending.append('Googleフォームの回答シートURLが未登録（CSV取込は利用可能）')
    registered = {r['archive'] for r in state['releases']}
    for file in OUTPUT.glob('*.manifest.json'):
        manifest = json.loads(file.read_text())
        if manifest['archive'] not in registered:
            pending.append(f"配布管理へ未登録のZIP: {manifest['archive']}")
    for file in OUTPUT.glob('*.zip'):
        if not file.with_suffix('.manifest.json').is_file():
            pending.append(f'manifestのないZIP: {file.name}')
    lines += ['| 課題 | 最新の準備済み版 | 配布状況 |', '| --- | --- | --- |']
    for assignment in packaging.ASSIGNMENTS:
        releases = [r for r in state['releases'] if r['assignment'] == assignment]
        if not releases:
            messages = ['配布版が未登録']
            version = '—'
        else:
            release = releases[-1]
            version = release['version']
            messages = current_problems(release)
            messages += [f"{t['id']}：掲載確認待ち" for t in state['targets'] if t['id'] not in release['deliveries']]
            if not state['targets']:
                messages.append('配布先未設定・掲載未確認')
        pending += [f'{assignment}: {m}' for m in messages]
        lines.append(f"| {assignment} | {version} | {' / '.join(messages) if messages else '全配布先の掲載確認を記録済み'} |")
    lines += ['', '## フィードバック', '']
    for feedback in state['feedback']:
        fid = feedback['id']
        candidates = [r for r in state['releases'] if fid in r['feedback']]
        if feedback['decision']:
            label = '対応しない判断を記録済み'
        elif any(delivered(state, r) for r in candidates):
            label = '反映版の掲載確認を記録済み'
        elif candidates:
            label = f"{candidates[-1]['version']}へ反映・再掲載待ち"
            pending.append(f'{fid}: {label}')
        else:
            label = '未対応'
            pending.append(f'{fid}: 未対応')
        summary = feedback['summary'].replace('\n', ' ')
        lines.append(f"- {fid} / {feedback['assignment']} / {label}：{summary}")
    if not state['feedback']:
        lines.append('学生からのFBはまだ取り込んでいません。')
    lines += ['', '## 残っている作業', ''] + (['- ' + x for x in pending] or ['残件なし（記録した配布先・確認範囲内）。'])
    report = '\n'.join(lines) + '\n'
    (ROOT / 'distributions/STATUS.md').write_text(report)
    print(report)
    return bool(pending)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    p = commands.add_parser('source')
    p.add_argument('--form-url', required=True)
    p.add_argument('--responses-sheet-url', required=True)
    p = commands.add_parser('import-feedback')
    p.add_argument('--csv', type=Path, required=True)
    p.add_argument('--source', required=True)
    p = commands.add_parser('prepare')
    p.add_argument('--assignment', choices=packaging.ASSIGNMENTS, required=True)
    p.add_argument('--version', required=True)
    p.add_argument('--feedback', action='append')
    for field in ('changes', 'student-action', 'verification'):
        p.add_argument('--' + field, required=True)
    p = commands.add_parser('target')
    p.add_argument('--id', required=True)
    p.add_argument('--url', required=True)
    p = commands.add_parser('drive-target')
    p.add_argument('--target', required=True)
    p.add_argument('--folder-url', required=True)
    p = commands.add_parser('bind-drive-file')
    p.add_argument('--target', required=True)
    p.add_argument('--assignment', choices=packaging.ASSIGNMENTS, required=True)
    p.add_argument('--file-url', required=True)
    p = commands.add_parser('upload-plan')
    p.add_argument('--target', required=True)
    p.add_argument('--assignment', choices=packaging.ASSIGNMENTS, required=True)
    p = commands.add_parser('decide-no-change')
    p.add_argument('--feedback', required=True)
    p.add_argument('--reason', required=True)
    p = commands.add_parser('record-delivery')
    p.add_argument('--assignment', choices=packaging.ASSIGNMENTS, required=True)
    for field in ('version', 'target', 'material-url', 'notice-url', 'student-check'):
        p.add_argument('--' + field, required=True)
    p.add_argument('--downloaded-zip', type=Path, required=True)
    p = commands.add_parser('status')
    p.add_argument('--check', action='store_true', help='未対応・未掲載・教材差分があれば終了コード1')
    args = parser.parse_args()
    for key, value in vars(args).items():
        if isinstance(value, str) and not value.strip():
            parser.error(f'{key}は空にできません')
    try:
        with distribution_lock(STATE.parent):
            return execute(load(), args)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(2, str(error) + '\n')


def execute(state, args):
    """呼び出し元が台帳読込前からロックを保持する。"""
    if args.command == 'import-feedback':
        import_feedback(state, args)
    elif args.command == 'source':
        configure_source(state, args)
    elif args.command in ('drive-target', 'bind-drive-file'):
        configure_drive(state, args)
    elif args.command == 'upload-plan':
        upload_plan(state, args)
        return 0
    elif args.command == 'prepare':
        prepare(state, args)
    elif args.command == 'target':
        course_key(args.url)
        if any(t['id'] == args.id for t in state['targets']):
            raise ValueError('同じ配布先IDは登録済みです')
        state['targets'].append({'id': args.id, 'courseUrl': args.url})
        save(state)
    elif args.command == 'decide-no-change':
        feedback = next((f for f in state['feedback'] if f['id'] == args.feedback), None)
        if feedback is None:
            raise ValueError('FBが見つかりません')
        if any(args.feedback in r['feedback'] for r in state['releases']):
            raise ValueError('すでに配布版に対応付けられたFBです')
        feedback['decision'] = {'reason': args.reason, 'at': now()}
        save(state)
    elif args.command == 'record-delivery':
        record_delivery(state, args)
    pending = status(state)
    if args.command == 'status' and args.check and pending:
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

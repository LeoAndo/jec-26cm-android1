#!/usr/bin/env python3
"""教材の入口から参照する学生用ファイルをZIPへ集め、別の場所で参照を再検査する。"""
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import tempfile
from urllib.parse import unquote, urlsplit
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
from materials_lock import distribution_lock

ROOT = Path(__file__).resolve().parents[1]
ASSIGNMENTS = {'A01': 'A01-first-app', 'A02': 'A02-profile-card'}
ALLOWED = {'.html', '.css', '.txt', '.png', '.svg', '.jpg', '.webp', '.zip'}


class Document(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.refs = []
        self.ids = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in {'base', 'script', 'iframe'}:
            raise ValueError(f'ローカル閲覧の検証対象外のタグ: {tag}')
        if 'id' in a:
            self.ids.append(a['id'])
        for key in ('href', 'src', 'poster'):
            if key in a:
                self.refs.append((a[key], tag == 'a' and key == 'href'))
        if 'srcset' in a:
            raise ValueError('srcsetの依存ファイル検査は未対応')


def collect(materials):
    """materialsの外・教員記録・外部依存が必須になる参照を受け付けない。"""
    materials = materials.resolve()
    pending = [materials / 'index.html']
    seen = set()
    references = 0
    while pending:
        file = pending.pop()
        if file in seen:
            continue
        relative = file.relative_to(materials)
        if file.suffix not in ALLOWED or not file.is_file():
            raise ValueError(f'学生用ファイルとして収録できない参照: {relative}')
        if {'teacher', 'solution', 'reference-template'} & set(relative.parts):
            raise ValueError(f'教員用資料への参照: {relative}')
        seen.add(file)
        refs = []
        if file.suffix == '.html':
            doc = Document(file.read_text(encoding='utf-8'))
            if len(doc.ids) != len(set(doc.ids)):
                raise ValueError(f'重複ID: {relative}')
            refs = doc.refs
        elif file.suffix == '.css':
            css = file.read_text(encoding='utf-8')
            if '@import' in css:
                raise ValueError(f'CSSのimportは配布前に展開する: {relative}')
            refs = [(x.strip(' \"\''), False) for x in re.findall(r'url\(([^)]+)\)', css)]
        for ref, supplemental in refs:
            url = urlsplit(ref)
            if url.scheme or url.netloc:
                if supplemental and url.scheme in ('https', 'http') and url.hostname not in ('localhost', '127.0.0.1'):
                    continue
                raise ValueError(f'ローカルで完結しない参照: {relative}: {ref}')
            if url.path.startswith('/') or url.query:
                raise ValueError(f'移動に対応しない参照: {relative}: {ref}')
            target = (file.parent / unquote(url.path)).resolve() if url.path else file
            if not target.is_relative_to(materials):
                raise ValueError(f'教材外への参照: {relative}: {ref}')
            if not target.is_file():
                raise ValueError(f'リンク先がない: {relative}: {ref}')
            if url.fragment:
                ids = Document(target.read_text(encoding='utf-8')).ids
                if unquote(url.fragment) not in ids:
                    raise ValueError(f'アンカーがない: {relative}: {ref}')
            pending.append(target)
            references += 1
    missing = {p.resolve() for p in materials.glob('*.html')} - seen
    if missing:
        raise ValueError('入口から参照されない教材ページ: ' + ', '.join(sorted(p.name for p in missing)))
    return sorted(seen), references


def package(assignment, version, output):
    materials = ROOT / 'assignments' / ASSIGNMENTS[assignment] / 'materials'
    files, references = collect(materials)
    name = f'{assignment}-materials-{version}'
    archive = output / f'{name}.zip'
    notice = f'''{assignment} 教材の開き方（{version}）

1. Classroomから教材ZIPをMacへダウンロードします。
2. FinderでZIPをダブルクリックして展開します。
3. 展開したフォルダーのindex.htmlをChromeまたはSafariで開きます。
4. 目次から授業のページを選びます。

HTMLとassetsを一緒に置き、教材フォルダーごと移動してください。
Classroomのプレビューの中ではなく、展開した教材を開きます。
提出物は完成したアプリのAPKファイル1つのみです。
新しい教材を展開するときも、自分のAndroidプロジェクトは残します。

現在は教員確認用の原稿です。
'''.encode('utf-8')
    contents = {str(f.relative_to(materials)): f.read_bytes() for f in files}
    contents['START_HERE.txt'] = notice
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='classroom-package-') as temp:
        candidate = Path(temp) / archive.name
        with ZipFile(candidate, 'w', compression=ZIP_DEFLATED) as zipped:
            for relative, data in sorted(contents.items()):
                info = ZipInfo(f'{name}/{relative}', date_time=(2026, 1, 1, 0, 0, 0))
                info.compress_type = ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                zipped.writestr(info, data)
        # 日本語・空白のある別の保存場所へ展開し、ソースツリーに頼らず照合する。
        relocated = Path(temp) / '学生の教材 コピー'
        with ZipFile(candidate) as zipped:
            zipped.extractall(relocated)
        extracted = relocated / name
        relocated_files, relocated_refs = collect(extracted)
        if relocated_refs != references or len(relocated_files) != len(files):
            raise ValueError('展開前後の参照が一致しない')
        for relative, data in contents.items():
            if (extracted / relative).read_bytes() != data:
                raise ValueError(f'展開後の内容が一致しない: {relative}')
        candidate_bytes = candidate.read_bytes()
        candidate_hash = hashlib.sha256(candidate_bytes).hexdigest()
        recorded_hashes = []
        existing_manifest = archive.with_suffix('.manifest.json')
        if existing_manifest.exists():
            recorded_hashes.append(json.loads(existing_manifest.read_text())['sha256'])
        ledger = ROOT / 'distributions/workflow.json'
        if ledger.exists():
            recorded_hashes += [r['sha256'] for r in json.loads(ledger.read_text())['releases']
                                if r['assignment'] == assignment and r['version'] == version]
        if (archive.exists() and archive.read_bytes() != candidate_bytes) or any(
                recorded != candidate_hash for recorded in recorded_hashes):
            raise ValueError(f'同じ版の内容は変更できません。新しい--versionを指定してください: {archive.name}')
        archive.write_bytes(candidate_bytes)
    manifest = {
        'assignment': assignment, 'version': version, 'status': 'teacher-review',
        'archive': archive.name, 'sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
        'entry': f'{name}/index.html', 'localReferences': references,
        'relocatedArchiveCheck': 'PASS',
        'files': {path: hashlib.sha256(data).hexdigest() for path, data in sorted(contents.items())},
    }
    archive.with_suffix('.manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(f'{archive.name}: {len(contents)}ファイル、{references}参照、展開後の確認PASS')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assignment', choices=ASSIGNMENTS, action='append')
    parser.add_argument('--version', required=True, help='例: 2026-09-14-r1')
    parser.add_argument('--output', type=Path, default=ROOT / 'distributions/classroom')
    args = parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*', args.version):
        parser.error('版は英数字・ピリオド・ハイフン・アンダースコアで指定してください')
    with distribution_lock(ROOT / 'distributions'):
        for assignment in args.assignment or ASSIGNMENTS:
            package(assignment, args.version, args.output)

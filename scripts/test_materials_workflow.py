#!/usr/bin/env python3
"""配布漏れ・版の取り違えを一時ディレクトリで検証する。外部サービスには接続しない。"""
from argparse import Namespace
from contextlib import redirect_stdout
import csv
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import materials_workflow as workflow


class WorkflowTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.output = self.root / 'distributions/classroom'
        self.output.mkdir(parents=True)
        self.state_file = self.root / 'distributions/workflow.json'
        self.state = {'schemaVersion': 1, 'feedbackSource': {'type': 'google_forms'},
                      'targets': [], 'feedback': [], 'releases': []}
        self.materials = self.root / 'assignments/A01-first-app/materials'
        self.materials.mkdir(parents=True)
        (self.materials / 'index.html').write_text('<html><a href="lesson.html#step1">授業</a></html>')
        (self.materials / 'lesson.html').write_text('<html><p id="step1">手順1</p></html>')
        for name, value in [('ROOT', self.root), ('STATE', self.state_file), ('OUTPUT', self.output)]:
            patcher = patch.object(workflow, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        patcher = patch.object(workflow.packaging, 'ROOT', self.root)
        patcher.start()
        self.addCleanup(patcher.stop)
        quiet = redirect_stdout(io.StringIO())
        quiet.__enter__()
        self.addCleanup(quiet.__exit__, None, None, None)
        workflow.save(self.state)

    def import_rows(self, rows):
        path = self.root / 'responses.csv'
        with path.open('w', encoding='utf-8-sig', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(workflow.REQUIRED_COLUMNS)
            writer.writerows(rows)
        workflow.import_feedback(self.state, Namespace(csv=path,
            source='https://docs.google.com/spreadsheets/d/test/edit'))

    def prepare(self, version='r1', feedback=None):
        workflow.prepare(self.state, Namespace(assignment='A01', version=version,
            feedback=feedback, changes='手順を補足', student_action='手順1を確認', verification='検証用'))
        return self.state['releases'][-1]

    def target(self, name='class-a'):
        self.state['targets'].append({'id': name, 'courseUrl': f'https://classroom.google.com/c/{name}'})

    def delivery_args(self, release, target='class-a'):
        downloaded = self.root / 'Classroomから再取得.zip'
        downloaded.write_bytes((self.output / release['archive']).read_bytes())
        return Namespace(assignment='A01', version=release['version'], target=target,
            material_url=f'https://classroom.google.com/c/{target}/m/material/details',
            notice_url=f'https://classroom.google.com/c/{target}/p/notice',
            student_check='テスト用の確認記録', downloaded_zip=downloaded)

    def test_csv_reimport_is_idempotent(self):
        rows = [['2026/09/14 12:00:00', 'A01', 'r0', '1', '説明が足りない']]
        self.import_rows(rows)
        self.import_rows(rows)
        self.assertEqual(['FB-0001'], [f['id'] for f in workflow.load()['feedback']])

    def test_invalid_csv_is_atomic(self):
        original = self.state_file.read_bytes()
        with self.assertRaisesRegex(ValueError, '3行目'):
            self.import_rows([['date', 'A01', 'r0', '1', '有効な回答'],
                              ['date', 'A99', 'r0', '1', '無効な回答']])
        self.assertEqual(original, self.state_file.read_bytes())
        self.assertEqual([], self.state['feedback'])

    def test_version_is_immutable_but_reproducible(self):
        release = self.prepare()
        archive = self.output / release['archive']
        original = archive.read_bytes()
        workflow.packaging.package('A01', 'r1', self.output)
        self.assertEqual(original, archive.read_bytes())
        (self.materials / 'lesson.html').write_text('<p id="step1">変更後</p>')
        with self.assertRaisesRegex(ValueError, '同じ版'):
            workflow.packaging.package('A01', 'r1', self.output)
        self.assertEqual(original, archive.read_bytes())

    def test_source_change_blocks_delivery(self):
        self.target()
        release = self.prepare()
        args = self.delivery_args(release)
        (self.materials / 'lesson.html').write_text('<p id="step1">教材変更</p>')
        self.assertTrue(workflow.current_problems(release))
        with self.assertRaisesRegex(ValueError, '準備時から変わりました'):
            workflow.record_delivery(self.state, args)
        self.assertEqual({}, release['deliveries'])

    def test_wrong_download_blocks_delivery(self):
        self.target()
        release = self.prepare()
        args = self.delivery_args(release)
        args.downloaded_zip.write_bytes(b'old ZIP')
        with self.assertRaisesRegex(ValueError, '一致しません'):
            workflow.record_delivery(self.state, args)
        self.assertEqual({}, release['deliveries'])

    def test_wrong_classroom_blocks_delivery(self):
        self.target()
        release = self.prepare()
        args = self.delivery_args(release)
        args.notice_url = 'https://classroom.google.com/c/wrong/p/notice'
        with self.assertRaisesRegex(ValueError, 'クラスが'):
            workflow.record_delivery(self.state, args)

    def test_all_classes_required_and_duplicate_record_rejected(self):
        self.target()
        self.target('class-b')
        release = self.prepare()
        args = self.delivery_args(release)
        workflow.record_delivery(self.state, args)
        self.assertFalse(workflow.delivered(self.state, release))
        with self.assertRaisesRegex(ValueError, '記録済み'):
            workflow.record_delivery(self.state, args)
        workflow.record_delivery(self.state, self.delivery_args(release, 'class-b'))
        self.assertTrue(workflow.delivered(self.state, release))
        saved = workflow.load()['releases'][-1]['deliveries']
        self.assertEqual(release['sha256'], saved['class-b']['downloadSha256'])
        self.assertTrue(saved['class-b']['studentAccessCheck'])

    def test_unpublished_feedback_is_carried_forward(self):
        self.import_rows([['date', 'A01', 'r0', '1', '説明不足']])
        old = self.prepare(feedback=['FB-0001'])
        newer = self.prepare('r2')
        self.assertEqual(['FB-0001'], newer['feedback'])
        self.target()
        with self.assertRaisesRegex(ValueError, '最新'):
            workflow.record_delivery(self.state, self.delivery_args(old))
        workflow.status(self.state)
        self.assertIn('r2へ反映・再掲載待ち', (self.root / 'distributions/STATUS.md').read_text())

    def test_unregistered_or_unmanifested_zip_is_reported(self):
        workflow.packaging.package('A01', 'r1', self.output)
        (self.output / 'forgotten.zip').write_bytes(b'zip')
        self.assertTrue(workflow.status(self.state))
        report = (self.root / 'distributions/STATUS.md').read_text()
        self.assertIn('配布管理へ未登録のZIP', report)
        self.assertIn('manifestのないZIP: forgotten.zip', report)

    def test_missing_reference_blocks_packaging(self):
        (self.materials / 'lesson.html').unlink()
        with self.assertRaisesRegex(ValueError, 'リンク先がない'):
            self.prepare()
        self.assertEqual([], workflow.load()['releases'])

    def test_source_registration_does_not_claim_sync(self):
        self.state['feedbackSource'].update(formUrl='https://forms.gle/previous',
            publicationStatus='unpublished', verifiedAt='old verification')
        workflow.configure_source(self.state, Namespace(form_url='https://forms.gle/test',
            responses_sheet_url='https://docs.google.com/spreadsheets/d/test/edit'))
        self.assertEqual('https://forms.gle/test', workflow.load()['feedbackSource']['formUrl'])
        self.assertNotIn('publicationStatus', workflow.load()['feedbackSource'])
        self.assertNotIn('verifiedAt', workflow.load()['feedbackSource'])
        workflow.status(self.state)
        self.assertIn('新しい回答の自動監視は未接続', (self.root / 'distributions/STATUS.md').read_text())

    def test_import_cannot_silently_replace_registered_sheet(self):
        self.state['feedbackSource'].update(
            responsesSheetUrl='https://docs.google.com/spreadsheets/d/registered/edit',
            publicationStatus='unpublished', verifiedAt='verified registration')
        workflow.save(self.state)
        original = self.state_file.read_bytes()
        with self.assertRaisesRegex(ValueError, '登録済みの回答シートURLと一致しません'):
            self.import_rows([['date', 'A01', 'r0', '1', '別シートの回答']])
        self.assertEqual(original, self.state_file.read_bytes())
        self.assertEqual([], self.state['feedback'])

    def test_completed_feedback_status_uses_delivery_evidence(self):
        self.import_rows([['date', 'A01', 'r0', '1', '説明不足']])
        self.target()
        release = self.prepare(feedback=['FB-0001'])
        workflow.record_delivery(self.state, self.delivery_args(release))
        workflow.status(self.state)
        self.assertIn('反映版の掲載確認を記録済み', (self.root / 'distributions/STATUS.md').read_text())

    def test_upload_plan_preserves_file_id_after_first_upload(self):
        self.target()
        release = self.prepare()
        workflow.configure_drive(self.state, Namespace(command='drive-target', target='class-a',
            folder_url='https://drive.google.com/drive/u/2/folders/test-folder'))
        args = Namespace(assignment='A01', target='class-a')
        plan = workflow.upload_plan(self.state, args)
        self.assertEqual('upload-new-file', plan['operation'])
        self.assertEqual(release['sha256'], plan['sha256'])
        workflow.configure_drive(self.state, Namespace(command='bind-drive-file', target='class-a',
            assignment='A01', file_url='https://drive.google.com/file/d/test-file/view'))
        plan = workflow.upload_plan(self.state, args)
        self.assertEqual('update-existing-file', plan['operation'])
        self.assertEqual('test-file', plan['fileId'])
        self.assertFalse(plan['executed'])
        self.assertEqual({}, release['deliveries'])

    def test_drive_binding_rejects_unrelated_host_and_replacement(self):
        self.target()
        with self.assertRaises(ValueError):
            workflow.configure_drive(self.state, Namespace(command='drive-target', target='class-a',
                folder_url='https://unrelated.example/folders/test-folder'))
        args = Namespace(command='bind-drive-file', target='class-a', assignment='A01',
            file_url='https://drive.google.com/file/d/first-file/view')
        workflow.configure_drive(self.state, args)
        args.file_url = 'https://drive.google.com/file/d/other-file/view'
        with self.assertRaisesRegex(ValueError, '別のDriveファイル'):
            workflow.configure_drive(self.state, args)


if __name__ == '__main__':
    unittest.main()

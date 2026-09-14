#!/usr/bin/env python3
"""開始プロジェクトのコピーへ、教材と共通の差分を順番に適用する。"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
STARTER = ROOT / 'starter/A02ProfileCard'
STEPS = json.loads((ROOT / 'teacher/steps.json').read_text())


def assemble(destination, stage):
    if destination.exists():
        raise SystemExit(f'既存フォルダーは上書きしません: {destination}')
    manifest = json.loads((ROOT / 'teacher/starter-manifest.json').read_text())
    for relative, expected in manifest.items():
        assert hashlib.sha256((STARTER / relative).read_bytes()).hexdigest() == expected, relative
    shutil.copytree(STARTER, destination)
    for step in STEPS:
        if step['id'] > stage:
            break
        for edit in step['edits']:
            file = destination / edit['file']
            text = file.read_text()
            assert text.count(edit['before']) == 1, (step['id'], edit['file'])
            file.write_text(text.replace(edit['before'], edit['after']))
        checkpoint = ROOT / ('teacher/solution' if step['id'] == 16 else f"materials/assets/checkpoints/step{step['id']:02}")
        for file in checkpoint.glob('*.txt'):
            matches = list((destination / 'app/src/main').rglob(file.name[:-4]))
            assert len(matches) == 1, file
            assert matches[0].read_bytes() == file.read_bytes(), (step['id'], file.name)
    print(f'第{stage}回終了相当: {destination}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path)
    parser.add_argument('--stage', type=int, choices=(4,5,6,7,8,9,10,11,12,13,14,15,16), default=16)
    args = parser.parse_args()
    assemble(args.destination, args.stage)

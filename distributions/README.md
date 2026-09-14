# Classroom向け教材ZIP

現時点のZIPは教員確認用。リンクの同梱と展開後の整合を確認済みで、Classroomから学生用アカウントで取得する確認と、初学者役の通し確認は残っている。[配布方法と学生向け案内](../docs/classroom-distribution.md)を参照する。

GoogleフォームのFBと再掲載は[更新手順](../docs/materials-maintenance.md)で管理する。[現在の状況](STATUS.md)は`python3 -B scripts/materials_workflow.py status`で更新する。配布先は[Android1のClassroom](https://classroom.google.com/c/ODY5NTI3MTEwNzgz)、管理IDは`android1`。

| 課題 | ZIP | 収録ファイル | 展開後の参照検査 |
| --- | --- | --- | --- |
| A01 はじめてのアプリ | [2026-09-14-r1](classroom/A01-materials-2026-09-14-r1.zip) | 7 | 83件成功 |
| A02 自己紹介カード | [2026-09-14-r2](classroom/A02-materials-2026-09-14-r2.zip) | 50 | 142件成功 |

両ZIPは、入口のindex.html・学生向けHTML・参照する画像やコード等を含む。教員用の完成解答・制作記録を含めない。学生の提出物はAPKファイル1つのみ。

## 修正後の新版作成

リポジトリのルートで実行する。通常は以下のコマンドで、教材検証・ZIP作成・対応FBと新版の登録・学生向け更新案内の作成をまとめて行う。

```sh
python3 -B scripts/materials_workflow.py prepare \
  --assignment A02 --version 2026-09-14-r3 \
  --changes '実際に修正した手順と内容' \
  --student-action '学生が新しい教材で確認すること' \
  --verification '実際の検証結果と残件'
```

FBの修正には`--feedback FB-0001`など、実際の取込IDを加える。Classroomへの掲載と確認は別の工程で、完了するまで一覧に残る。

## パッケージだけの再生成

教材を修正したら版名を更新する。同じ版の再生成は内容が完全に同じ場合だけ可能で、違う内容の上書きは拒否する。

```sh
python3 -B assignments/A02-profile-card/teacher/render_materials.py
python3 -B assignments/A02-profile-card/teacher/check_materials.py
python3 -B scripts/package_classroom_materials.py --assignment A02 --version 2026-09-14-r2
```

一方だけ作る場合は`--assignment A01`または`--assignment A02`を追加する。出力先を変える場合は`--output /任意のフォルダー`を指定する。ZIPと同名のmanifest.jsonに版・ZIPハッシュ・ファイルごとのハッシュ・参照数が残る。

パッケージだけの作成では配布管理へ登録されない。未登録の新版は`status`へ残るため、通常の更新には`materials_workflow.py prepare`を使う。

`materials/index.html`からたどれるファイルを収録する方式のため、教材へ新しい画像やコードを加えた場合も、その参照から自動収録される。教員用ファイルへのリンク、見つからないファイル、入口から孤立した学生用HTMLがあれば生成を失敗させる。ZIPの中でも元の相対パスを維持する。

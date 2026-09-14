# A02 教員用コードと検証

教材は教員確認用。[制作・検証記録](../materials/plan.md)に人間の確認が必要な項目をまとめている。このフォルダーの完成コードは学生用HTMLから参照しない。

## 段階別プロジェクトを作る

Python 3を使い、リポジトリのルートで実行する。出力先には存在しないフォルダーを指定する。

```sh
python3 -B assignments/A02-profile-card/teacher/assemble.py /tmp/A02-week2 --stage 8
python3 -B assignments/A02-profile-card/teacher/assemble.py /tmp/A02-solution --stage 16
```

`--stage 4`は開始状態。5〜16はその回の終了状態を作る。第8・12回は演習前の共通値へ戻した状態と同じ。元の開始プロジェクトは変更しない。各段階で比較用コードとの一致も検査する。

## 教材を修正・確認する

`steps.json`に学生の変更前後と教員用の第16回完成例がある。手順を変える場合は、対応するcheckpointsまたはsolutionも更新し、次の順でHTMLを再生成・確認する。説明文は`render_materials.py`で管理する。

```sh
python3 -B assignments/A02-profile-card/teacher/render_materials.py
python3 -B assignments/A02-profile-card/teacher/check_materials.py
```

静的確認ではHTMLの参照先・アンカー・変更前後、段階別コード、開始ZIPの39ファイルを照合する。開始プロジェクトを変更した場合は`starter-manifest.json`とZIPを同じ内容へ更新する。テーマは生成原本の設定を維持し、学生の編集手順へ追加しない。

## 端末テストを再現する

`assemble.py --stage 16`で作った一時プロジェクトを指定Android Studioで開き、SDKのパスを設定する。`ProfileCardTest.java`と`CaptureStatesTest.java`を、そのプロジェクトの`app/src/androidTest/java/jp/ac/jec/a02profilecard/`へコピーする。開始ZIPにはテストを追加しない。

一時プロジェクト内で`./gradlew assembleDebug assembleDebugAndroidTest`を実行する。Android SDKのplatform-toolsをPATHへ追加し、検証に使う端末を`adb devices`で確認して、以下の`SERIAL`を置き換える。

```sh
adb -s SERIAL install -r app/build/outputs/apk/debug/app-debug.apk
adb -s SERIAL install -r app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk
adb -s SERIAL shell am force-stop com.android.cli.interact.instrumentation
adb -s SERIAL shell am instrument -w jp.ac.jec.a02profilecard.test/androidx.test.runner.AndroidJUnitRunner
```

検査サービスの停止は、`android layout`が使うUiAutomationと画像取得テストの競合を避けるため。テスト終了まで`android layout`を同時に実行しない。画面キーボードが通常表示される端末を使い、IMEの初回案内を済ませる。

2026年9月14日はAndroid 16・API 36のエミュレーターで7件成功。[実行ログ](verification/instrumentation.txt)は機能5件、画像取得1件、生成テンプレートの確認1件を含む。日本語IMEの変換操作や初学者の学習到達を検証した結果ではない。

`verification/before-theme-policy-*`はテーマ方針を変更する前の履歴。学年2の配置と強制停止前後のJSONも変更前の結果であり、[制作記録](../materials/plan.md)に区別して記載している。

# A01：Panda 2テンプレートを起点にする教材

## 確認した生成物

2026年9月14日19:19に作成されたローカルのMyApplicationを読み取り、Panda 2のログにも同プロジェクトの同期・インポート完了が記録されていることを確認した。元のプロジェクトは変更していない。

- IDE：Panda 2 | 2025.3.2（AI-253.30387.90.2532.14935130）
- テンプレート：Empty Views Activity、Java
- AGP 9.1.1、Gradle 9.3.1、compileSdk 36.1、targetSdk 36、Java 11
- 初期依存関係：appcompat 1.7.1、material 1.13.0、activity 1.12.3、constraintlayout 2.2.1（変更しない）
- 確認した生成物のminSdkは30。教材初版の仮設定API 24をAPI 30へ改め、同じ生成条件を教材の統一値にする。minSdkによりアイコン用XMLの配置なども変わるため、数値だけ変えた別条件の生成物を同一テンプレートとして扱わない。

`assets/template/` は変更前の比較用コード。元の生成物から、パッケージ名を `jp.ac.jec.a01firstapp`、プロジェクト名とテーマ名を `A01FirstApp` に読み替え、末尾改行をそろえている。バイト単位の取得原本ではない。`themes-night.xml.txt` は `res/values-night/themes.xml` に対応する。

## 変更の範囲

| ファイル | 変更 |
| --- | --- |
| MainActivity.java | なし。AppCompatActivity、EdgeToEdge.enable、R.id.mainへの余白適用を維持する。 |
| activity_main.xml | ConstraintLayoutをLinearLayoutへ変更する。ルートのmain IDを維持し、システムバー用の余白処理はJavaの生成コードへ任せる。内側のLinearLayoutで24dpの余白と中央配置を扱う。 |
| strings.xml | app_nameを変更し、greeting_messageを追加する。 |
| values/themes.xml、values-night/themes.xml | Theme.Material3.DayNight.NoActionBarをTheme.Material3.Light.NoActionBarに変更し、強制ダーク化を無効にする。Base.ThemeとThemeの継承関係を維持する。 |
| AndroidManifest.xml、Gradle設定 | 学生のコード修正では変更しない。 |

[変更前から手順06への差分](assets/template-to-step06.patch)は教員の確認用。HTMLでは、対象ファイル・変更箇所・変更前後を示す。変更後の全文は見比べるための補助とする。手順09はgreeting_messageの言葉だけを日本語に変える。

## 検証範囲

Panda 2生成プロジェクトの一時コピーに、教材用の名前・minSdk 30と、手順06のコードを適用して検証する。依存関係は追加・更新しない。新規作成画面からの全操作の再現、エミュレーターでの動作、画像取得、初学者の通し確認は別途必要。結果は[制作・検証記録](plan.md)へ記録する。

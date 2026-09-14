# A02：開始コードの準備記録

> 指定テンプレートの実ファイルを基に、課題名などを読み替えた開始プロジェクトを作成した。学生がテーマを変更する手順は設けない。人間によるIDEの開き直し・初学者役の通し確認は未実施。

## 生成元と条件

2026年9月14日、Panda 2のidea.logにある19:19の読み込み記録と19:20:02のインポート完了記録から、`/Users/ando/Documents/Kotlin/MyApplication`を参照元として特定した。インストール済みIDEのproduct-info.jsonのビルド番号は`AI-253.30387.90.2532.14935130`。JavaのMainActivityとEmpty Views ActivityのXMLが実在する。

| 項目 | 参照元／A02 |
| --- | --- |
| IDE | Android Studio Panda 2 \| 2025.3.2、AI-253.30387.90.2532.14935130 |
| テンプレート・言語 | Empty Views Activity・Java |
| 名前 | 参照元My Application → A02ProfileCard |
| package / applicationId | jp.ac.jec.cm0199.myapplication → jp.ac.jec.a02profilecard |
| SDK | minSdk 30、targetSdk 36、compileSdk 36.1を維持 |
| AGP / Gradle | 9.1.1 / 9.3.1を維持 |
| Java設定 / Gradle実行JDK | ソース・ターゲット11 / JBR 21系（GradleのtoolchainVersion=21） |
| 初期依存 | appcompat 1.7.1、material 1.13.0、activity 1.12.3、constraintlayout 2.2.1を維持。新規ライブラリなし。 |
| テーマ | 通常・values-nightとも生成原本のDayNightを維持。課題名のみ読み替え。Light固定、forceDarkAllowed、テーマ色の上書きなし。 |

主要11ファイルの変更しない参考原本は[assets/reference-template](assets/reference-template/)に保存した。[原本のmanifest](assets/reference-template/manifest.json)は元のパスとSHA-256を記録する。主要5ファイルは、名前と改行をメモリー上で読み替えるとA01の比較コードと一致した（A01の今回のテーマ方針変更より前に照合）。

今回A02名でウィザードを再実行した原本とは扱わない。同じminSdk・SDK・言語の既存生成物を基にした、教員準備のプロジェクトである。元のMyApplicationは変更していない。同名のAndroidStudioProjects内のKotlin/Composeプロジェクトは参照していない。

## 生成物から開始状態へ行った変更

1. プロジェクト名、package、applicationId、themeの識別名、app_nameをA02用へ変更した。テーマの親や内容は変更していない。
2. 初期ConstraintLayoutをLinearLayout・ScrollView・内側のcontentへ変更し、開始画面を見出し1つにした。生成Javaが使うmain IDは維持した。
3. systemBarsとimeを合わせたInsetsにより、システム領域とキーボードの余白を付けた。ManifestにadjustResizeを追加した。
4. strings.xml、colors.xml、同梱のプロフィール素材を用意した。素材はStitchの出力から取得し、Androidへ同じPNGをコピーした。
5. タイトル以外のカード部品とイベント処理は学生の手順へ残した。テーマ切り替え・ダーク表示の評価は学習内容に含めない。

[教員の準備差分](../teacher/template-to-starter.patch)はテキストファイルの差分。[参照元ファイル一覧](../teacher/source-files.json)はWrapper・アイコン等も含むハッシュ。画像の取得方法は[Stitch記録](../design/stitch.md)にある。

## 開始リビジョンと配布物

- ソース：[starter/A02ProfileCard](../starter/A02ProfileCard/)。39ファイル。
- 学生向けZIP：[A02ProfileCard-starter.zip](assets/A02ProfileCard-starter.zip)。SDKのローカルパス、ビルド生成物、.idea、.gradleを含めない。
- [starter-manifest.json](../teacher/starter-manifest.json)で各ファイルを固定する。manifest自体のSHA-256は`ea973a06b35937a15bcbc747e0e8530f32c0fb7b02523818f8a828169240b72f`。
- `gradlew`の実行属性を含めてZIPへ格納。ZIPの各エントリーと開始ソースを照合済み。

## 必須手順と教員用完成例

[steps.json](../teacher/steps.json)の変更前後を順番に適用すると、開始→第5・6・7・9・10・11・13・14・15回→第16回へ進む。第8・12回は値を変更して予想を確かめた後、元へ戻す練習なので次回の開始コードは第7・11回と同じ。

学生用HTMLの変更前後と、assets/checkpointsの各時点の全文を照合する。第16回のリセット完成コードは[teacher/solution](../teacher/solution/)に分離し、学生ページに完成コードへのリンクを設けない。

教員は`python3 teacher/assemble.py /tmp/任意の新規フォルダー --stage 8`のように、指定段階の復帰用プロジェクトを作れる。相対パスはA02フォルダーから実行する。既存フォルダーは上書きしない。

ビルド・端末・HTML表示の結果と残件は[plan.md](plan.md)にまとめる。テンプレートの出所、コマごとのビルド、端末の動作、人間の授業レビューは別々の確認として扱う。

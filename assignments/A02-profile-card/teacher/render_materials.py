#!/usr/bin/env python3
"""steps.jsonの変更前後から、外部依存なしの学生用HTMLを生成する。"""
from pathlib import Path
import json
from html import escape as e

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'materials'
STEPS = {s['id']:s for s in json.loads((ROOT/'teacher/steps.json').read_text())}
PAGES = [('lesson-layout.html','第2週 画面を作る'),('lesson-events.html','第3週 ボタンで変える'),('lesson-input.html','第4週 名前を入力する'),('exercise.html','第16回 リセットを作る'),('checklist.html','完成確認・提出')]

def code(s):
    # 表示時だけ共通の字下げを取り除く。内容は検証時に照合する。
    import textwrap
    return '<pre tabindex="0"><code>'+e(textwrap.dedent(s).rstrip())+'</code></pre>'

def photo(name,alt):
    if not (OUT/'assets'/name).exists():return ''
    return f'<figure><img src="assets/{e(name)}" alt="{e(alt)}" width="360"><figcaption>{e(alt)}（検証用エミュレーターの実行画像）</figcaption></figure>'

def page(filename,title,lead,body):
    nav=''.join(f'<a href="{f}"'+(' aria-current="page"' if f==filename else '')+f'>{label}</a>' for f,label in PAGES)
    html=f'''<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>A02 | {e(title)}</title><link rel="stylesheet" href="assets/style.css"></head>
<body><a class="skip" href="#main">本文へ進む</a><header><p class="eyebrow">ANDROID 1 · A02 · 自己紹介カード</p><nav aria-label="教材の目次">{nav}</nav></header>
<main id="main"><p class="draft">教員確認用の原稿です。授業で使う前に、教員の確認を受けます。</p><h1>{e(title)}</h1><p class="lead">{lead}</p>{body}</main>
<footer><nav aria-label="ページの移動">{nav}</nav><p>A02 自己紹介カード · Java / XML · 1コマ90分。速さで評価しません。</p><a href="#main">ページの先頭へ</a></footer></body></html>'''
    (OUT/filename).write_text(html)

def step(n,next_link):
    s=STEPS[n]
    chunks=[]
    for i,x in enumerate(s['edits'],1):
        file=x['file']; basename=Path(file).name
        action='置き換えます' if x['after'] else '削除します'
        lines=x['before'].strip().splitlines()
        anchor=next((l.strip() for l in lines if 'android:id=' in l),None)
        anchor=anchor or next((l.strip() for l in lines if 'android:text=' in l),lines[0].strip())
        chunks.append(f'<section class="edit" id="edit-{n}-{i}"><h3>{n}-{i}　{e(basename)}を変更する</h3><p><strong>開くファイル：</strong><code>{e(file)}</code></p><ol><li>Android Studioのファイル一覧で、このファイルを開きます。</li><li>⌘Fで<code>{e(anchor)}</code>を探します。</li><li>その場所を含む「変更前」と同じ範囲だけを選び、{action}。</li></ol><p class="label">変更前（直前の手順が終わった状態）</p>'+code(x['before'])+('<p class="label">変更後（この範囲だけを貼り付ける）</p>'+code(x['after']) if x['after'] else '<p><strong>変更後：</strong>この3行と直後の空行を削除します。前後の処理をつなげます。</p>')+'<p>この範囲以外は残します。ファイル全体の置き換えではありません。</p></section>')
    checkpoint=f'assets/checkpoints/step{n:02}'
    files=sorted((OUT/checkpoint).glob('*.txt'))
    full_code=''.join(
        f'<details><summary>{e(f.name[:-4])}の全文</summary>'
        + code(f.read_text())
        + f'<p><a href="{checkpoint}/{f.name}" download>テキストを保存</a></p></details>'
        for f in files
    )
    return f'''<article id="step-{n}"><p class="eyebrow">第{n}回 · 90分</p><h2>{n}　{e(s['title'])}</h2><p>{e(s['goal'])}</p><aside class="note"><h3>この回の言葉</h3><p>{e(s['concept'])}</p></aside>{''.join(chunks)}
<section class="result"><h3>こうなればOK</h3><ol><li>Run → Run 'app' を選びます。</li><li>ビルドと起動が終わるまで待ちます。</li><li>{e(s['ok'])}</li></ol></section>
<details><summary>うまくいかないとき</summary><p>{e(s['trouble'])}</p><p>直せないときは、開いているファイルとBuildの最初のエラーを教員に見せます。</p></details>
<details><summary>第{n}回終了時の全文を比べる</summary><p>確認用です。上の部分変更を終えた状態です。ファイル名を押すと、このページ内に全文が開きます。</p>{full_code}</details><p class="next"><a href="{next_link}">次へ進む →</a></p></article>'''

intro='''<section id="start"><h2>はじめる前に</h2><p>使う環境はmacOS、Android Studio Panda 2 | 2025.3.2、教員が指定したスマートフォン型のエミュレーターです。A01で練習したRunと、ファイルの編集を使います。</p><p>今回は新しくプロジェクトを作りません。開始用ファイルを開きます。第3・4週も同じプロジェクトを続けます。</p><h3>まず動かしてみよう</h3><ol><li><a href="assets/A02ProfileCard-starter.zip" download>開始用プロジェクト（ZIP）</a>をダウンロードします。</li><li>FinderでZIPをダブルクリックします。</li><li>展開されたA02ProfileCardフォルダーを、授業用の作業場所へ移します。</li><li>Android Studioの最初の画面でOpenを選びます。別のプロジェクトが開いている場合はFile → Openを使います。</li><li>A02ProfileCardフォルダーを選びます。appだけを選ばないでください。</li><li>Gradleの同期が終わるまで待ちます。</li><li>上部の実行先で、教員指定のエミュレーターを選びます。</li><li>Run → Run 'app' を選びます。</li></ol><p class="result">「自己紹介カード」の見出しだけが出ればOKです。</p><details><summary>開けない・一覧が見えないとき</summary><p>settings.gradle.ktsとgradlewが入ったフォルダーを選びます。ファイル一覧が見えないときはView → Tool Windows → Projectで戻します。同期が失敗したら、Gradleの最初のエラーを教員に見せます。</p></details><h3>開くファイルと残す部分</h3><p>activity_main.xmlはapp → res → layout、strings.xmlとcolors.xmlはapp → res → valuesにあります。XMLはCodeで文字を編集します。Javaはappのjava内のjp.ac.jec.a02profilecard → MainActivityを開きます。同名のtestフォルダーは使いません。</p><p>mainとcontentの枠、ScrollView、画面端の余白処理は教員が準備済みです。入力欄と下のボタンの間は、標準のエラー案内が重ならないよう48dp空けます。ScrollViewは画面に入りきらない部分を上下へ動かす枠です。学生はその内側に部品を追加します。この課題で指定するファイルだけを編集します。</p><p>編集内容はAndroid Studioが自動保存します。コードのコピーは⌘C、貼り付けは⌘Vです。コード欄に行番号や差分記号はありません。</p></section>'''

practice='''<article id="step-8"><p class="eyebrow">第8回 · 90分</p><h2>8　見本と比べて直そう</h2><p>第7回の画面から始めます。値を1か所ずつ変え、実行して比べた後、元の値へ戻します。</p><table><caption>必須の予想・変更・確認</caption><thead><tr><th>開く場所・探す文字</th><th>変更前</th><th>変更後</th><th>予想する変化</th></tr></thead><tbody><tr><td>activity_main.xmlのnameTextView</td><td><code>android:textSize="24sp"</code></td><td><code>android:textSize="30sp"</code></td><td>名前が大きくなる</td></tr><tr><td>colors.xmlのcard_text</td><td><code>#1D1B20</code></td><td><code>#4E378A</code></td><td>文字が紫になる</td></tr><tr><td>activity_main.xmlのcontent</td><td><code>android:padding="24dp"</code></td><td><code>android:padding="32dp"</code></td><td>枠の内側の余白が増える</td></tr></tbody></table><ol><li>表の1行目の場所を開きます。</li><li>変化を予想して、値だけを変更します。</li><li>Runで結果を確かめます。</li><li>変更前の値へ戻し、再びRunします。</li><li>2・3行目も同じ順で確かめます。</li></ol><p>ほかの属性とタグは残します。元の色や余白が分からなくなったら、第7回の全文と比べます。</p><p class="result">画像と名前が横並び、あいさつとボタンがその下です。文字は24sp、色は#1D1B20、contentのpaddingは24dpへ戻っています。C01・C02を確認します。</p><p>今日の振り返り：paddingとmarginの位置を指で示してください。XML、strings.xml、colors.xml、drawableの役割を1つずつ答えてください。</p><p class="next"><a href="lesson-events.html">第3週へ進む →</a></p></article>'''

week2='<p class="toc"><a href="#start">準備</a> / <a href="#step-5">第5回</a> / <a href="#step-6">第6回</a> / <a href="#step-7">第7回</a> / <a href="#step-8">第8回</a></p>'+photo('week2.png','第2週の完成例。画像と名前、あいさつ、ボタンだけの画面。')+intro+step(5,'#step-6')+step(6,'#step-7')+step(7,'#step-8')+practice
page('lesson-layout.html','画面を作ろう','第5〜8回。画像・名前・あいさつを並べます。この週はボタンを押しても表示は変わりません。',week2)

grade='''<article id="step-12"><p class="eyebrow">第12回 · 90分</p><h2>12　表示を予想して確かめよう</h2><p>第11回の状態から、MainActivity.javaの学年だけを変えます。</p><ol><li>MainActivity.javaを開きます。</li><li><code>int grade = 1;</code>を探します。</li><li>次の1行だけを書き換えます。</li></ol><p class="label">変更前</p>'''+code('int grade = 1;')+'<p class="label">変更後</p>'+code('int grade = 2;')+'''<ol start="4"><li>ボタンを押すと何と表示するか予想します。</li><li>Runで起動します。</li><li>「あいさつする」を押します。</li></ol><p class="result">「こんにちは！2年生のサクラです。」ならOKです。</p><p>次に同じ行を<code>int grade = 1;</code>へ戻し、Runしてあいさつします。「こんにちは！1年生のサクラです。」へ戻してください。ほかの文やクリック処理は変えません。</p><h3>2種類のエラーを見分ける</h3><p>教員がセミコロンを消した例を見せます。Buildはアプリを作る段階の問題を示します。Logcatは実行中の記録を示します。動かないときはBuildの最初のエラー、起動後に終了するときはLogcatの赤い行を教員に見せます。学生のコードは正常な状態を残します。</p><p>振り返り：変数、id、クリック時の処理、setTextの場所を指してください。C03・C04を確認します。</p><p class="next"><a href="lesson-input.html">第4週へ進む →</a></p></article>'''
page('lesson-events.html','ボタンで表示を変えよう','第9〜12回。前週の必須完成状態から始め、ボタンを押したときの処理を作ります。','<p class="toc"><a href="#step-9">第9回</a> / <a href="#step-10">第10回</a> / <a href="#step-11">第11回</a> / <a href="#step-12">第12回</a></p><section><h2>始める時の確認</h2><p>第8回の色・文字サイズ・余白に戻っていることを確認します。画像・サクラ・初期のあいさつ・ボタンがあり、押してもまだ変わりません。追加練習のコードを前提にしません。</p><p><a href="lesson-layout.html#step-8">前週の完成確認へ戻る</a></p></section>'+photo('week3.png','第3週。ボタンを押すと「こんにちは！1年生のサクラです。」に変わる。')+step(9,'#step-10')+step(10,'#step-11')+step(11,'#step-12')+grade)

page('lesson-input.html','入力した名前を表示しよう','第13〜15回。文字を受け取り、空欄を確かめてから表示します。リセットは次の回で自分で追加します。','<p class="toc"><a href="#step-13">第13回</a> / <a href="#step-14">第14回</a> / <a href="#step-15">第15回</a></p><section><h2>始める時の確認</h2><p>第12回の学年を1へ戻したコードから始めます。あいさつボタンで「こんにちは！1年生のサクラです。」になります。入力欄はまだありません。</p><p><a href="lesson-events.html#step-12">前週の完成確認へ戻る</a></p></section>'+step(13,'#step-14')+step(14,'#step-15')+step(15,'exercise.html')+'<section><h2>この週の途中確認</h2><p><a href="checklist.html#checks">C05〜C10</a>を確かめます。リセットはまだないのでC11は次の回で確認します。</p><p>振り返り：空欄を確かめる前に行う2つの処理と、あいさつに使う名前の場所を指してください。</p></section>')

reset='''<article id="step-16"><h2>16　初めの表示に戻そう</h2><p>第15回の完成状態から始めます。この回は完成コードを見ずに、これまでの追加方法を使います。</p><h3>必須の仕様</h3><p>「名前を反映」の右に「リセット」を1つ追加します。idはresetButton、表示文字の名前はreset_buttonです。横幅は反映ボタンと同じにします。ボタンを押すと、次の4つを同時に戻します。</p><table><thead><tr><th>対象</th><th>戻す値</th></tr></thead><tbody><tr><td>カードの名前</td><td>サクラ</td></tr><tr><td>あいさつ</td><td>よろしくお願いします。</td></tr><tr><td>入力欄</td><td>空の文字列</td></tr><tr><td>エラー</td><td>なし</td></tr></tbody></table><p>画像はそのままです。確認のダイアログは不要です。</p><ol><li>strings.xmlへボタンの言葉を追加します。</li><li>activity_main.xmlの反映ボタンと同じ横向きの枠へ、新しいButtonを追加します。</li><li>MainActivity.javaで新しいボタンを見つけます。</li><li>クリック時に4つの値を戻す処理を書きます。</li><li>Runで起動します。</li><li>有効な名前を反映してからリセットします。</li><li>空欄エラーを出してからリセットします。</li><li>リセットを続けて2回押します。</li><li>その後「ミナ」を反映し、あいさつします。</li></ol><p class="result">毎回、表の初期表示へ戻り、再び名前を反映できればOKです。C11を確認します。</p><details><summary>ヒント1：どの手順を見直すか</summary><p>部品の追加は<a href="lesson-input.html#step-13">第13回</a>、クリック処理は<a href="lesson-events.html#step-11">第11回</a>、エラーを消す処理は<a href="lesson-input.html#step-14">第14回</a>を見ます。</p></details><details><summary>ヒント2：使える命令</summary><p>文字はsetText、エラーはsetErrorで変えられます。初期の言葉はstrings.xmlにあります。空の文字列は引用符の間に何も入れません。画像には処理を書きません。</p></details><details><summary>見た目をそろえる補助</summary><p>反映ボタンと同じ0dpとlayout_weight="1"を使います。左側の余白はlayout_marginStart="12dp"です。リセットはstyle="?attr/materialButtonOutlinedStyle"で枠線のボタンにできます。このstyleの綴りは見本どおり使って構いません。</p></details><details><summary>うまくいかないとき</summary><p>起動で終了するときはXMLのidとJavaのR.idを比べます。一部しか戻らないときは、表の4項目を1つずつ照合します。元からあるあいさつ処理と反映処理を消していないかも確認します。</p></details></article>
<section id="extra"><h2>追加の練習（任意）</h2><p>必須の確認が終わった人だけ取り組みます。次の課題へ進む前に、必須状態のコピーを残します。</p><ol><li>あいさつの文を1か所変え、結果を予想して実行します。</li><li>文字の色や余白を1か所変え、見やすさを比べます。</li><li>余裕があれば、別の文を表示するあいさつボタンを1つ追加します。</li></ol><p>保存や別画面の追加は、この課題では扱いません。</p></section><p class="next"><a href="checklist.html">完成確認と提出へ →</a></p>'''
page('exercise.html','リセットを自分で作ろう','第16回。仕様を読み、初期表示へ戻すボタンを作ります。',photo('initial.png','第16回の完成例。名前入力と、名前を反映・リセットのボタン。')+reset)

checks=[
('C01','第2週','実行して、画像・名前の横並びと、あいさつ・ボタンを確認する。'),
('C02','第2週','文字サイズ・色・余白を各1か所変え、予想と比べる。第8回の共通値へ戻す。'),
('C03','第3週','あいさつを2回押す。「こんにちは！1年生のサクラです。」が出る。'),
('C04','第3週','学年を2に変えて予想する。「2年生」と表示できたら1へ戻す。'),
('C05','第4週','リンを反映すると名前はリン、あいさつは初期文。あいさつを押すと「こんにちは！1年生のリンです。」。'),
('C06','第4週','入力だけミナに変えてあいさつする。リンのまま。反映すると名前はミナ、あいさつは初期文。次のあいさつはミナ。'),
('C07','第4週','空欄、半角スペース3個、全角スペース2個、半角・全角1個ずつで反映する。毎回「名前を入力してください」。直前のカードの名前とあいさつは残る。'),
('C08','第4週','前後に半角空白を付けた「 リン 」と、全角空白を付けた「　リン　」を反映する。名前はリン、エラーなし。入力欄の文字はそのまま。'),
('C09','第4週','「アナ マリア」と「アナ　マリア」を反映する。どちらも間に半角スペースがある「アナ マリア」。'),
('C10','第4週','「アレクサンドラマリアサクラアレクサンドラマリアサクラ」を反映してあいさつする。名前と文の全文を読める。キーボード表示中もスクロールして入力欄と各ボタンに届く。'),
('C11','第4週','名前反映後、空欄エラー後、それぞれリセットする。続けて2回押す。サクラ・初期文・空の入力・エラーなしに戻る。その後ミナを反映してあいさつできる。'),
('C12','第4週','名前変更後、アプリを強制停止して新しく起動する。サクラ・初期文・空の入力・エラーなしで始まる。')]
checkhtml=''.join(f'<label class="check"><input type="checkbox" id="{cid}"><span><strong>{cid}　{week}</strong><br>{e(desc)}</span></label>' for cid,week,desc in checks)
submit='''<section id="submit"><h2>提出しよう</h2><p>提出先・締切・ファイル名は、教員の授業案内で確認してから送信します。</p><h3>提出するもの</h3><p><strong>完成したアプリのAPKファイル1つのみ</strong>です。</p><h3>① APKを作る</h3>
<p>APK（エーピーケー）は、Androidにアプリを入れるためのファイルです。この授業では、初期設定のdebug（開発用）を使います。</p>
<ol class="steps">
<li>必須課題の完成状態でアプリを実行し、完成条件を確かめます。</li>
<li>Android Studioの上のメニューで <strong>Build</strong> を開きます。</li>
<li><strong>Generate App Bundles or APKs</strong> を選びます。</li>
<li><strong>Generate APKs</strong> を選びます。</li>
<li>APKの作成が成功した通知を待ちます。</li>
</ol>
<p>コードを直したときは、このAPK作成の操作をもう一度行ってから提出します。</p>
<h3>② APKを取り出す</h3>
<ol class="steps">
<li>Finderで、作業用の <code>A02ProfileCard</code> フォルダーを開きます。</li>
<li><code>app</code> → <code>build</code> → <code>outputs</code> → <code>apk</code> → <code>debug</code> の順に開きます。</li>
<li><code>app-debug.apk</code> を選びます。</li>
<li><kbd>⌘</kbd> + <kbd>C</kbd> でコピーします。</li>
<li>提出用の保存場所を開き、<kbd>⌘</kbd> + <kbd>V</kbd> で貼り付けます。</li>
<li>コピーしたAPKに、教員が案内したファイル名を付けます。末尾の <code>.apk</code> は残します。</li>
</ol>
<p>作業用プロジェクトは、自分のパソコンに残しておきます。</p>
<h3>③ APKを提出する</h3>
<ol class="steps">
<li>教員が案内した提出先へ、APKファイル1つを送ります。</li>
<li>提出先の画面で、送ったファイルの名前と末尾の <code>.apk</code> を確かめます。</li>
<li>送信が完了したことを確かめます。</li>
</ol>
<p class="result">APKファイル1つの送信が完了すれば、提出は完了です。</p><details><summary>APKが見つからない・作成に失敗したとき</summary><p>APKの作成が成功したかと、開いたプロジェクトの保存場所を教員と確かめます。Buildにエラーが出た場合は、最初のエラーを見せてください。送信に失敗した場合は、提出先の画面を教員に見せてください。</p></details><h3>④ 今日の振り返り（授業内）</h3><p>授業中に、名前反映・空欄・リセットの操作を教員に見せます。次の内容も授業内で振り返ります。振り返りの提出はありません。</p><ul><li>自分で変えた場所はどこですか。</li><li>空欄のときに動く処理はどこですか。</li><li>リセットで戻す4つの対象は何ですか。</li></ul><p>短い言葉や、コードを指して答えても構いません。</p></section>'''
page('checklist.html','できたか確かめよう','各週の終わりに操作して確認します。チェックはこのページを閉じると保持されないことがあります。','<section id="checks"><h2>完成条件 C01〜C12</h2>'+checkhtml+'</section>'+photo('greeting.png','リンを反映して、あいさつした状態。')+photo('error.png','空欄エラー。名前とあいさつは直前のリンのまま。')+'<section><h2>再起動を確かめるとき</h2><p>ホームへ戻るだけでは初期化されません。C12では教員と一緒に、端末のアプリ情報から「自己紹介カード」を強制停止します。その後ランチャーから起動します。アプリ情報の位置は端末によって異なります。分からないときは教員に画面を見せてください。</p></section>'+submit)
print('HTML:',len(PAGES),'files')

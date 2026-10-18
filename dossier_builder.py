from pathlib import Path
from html import escape
import json, re, base64, mimetypes, zipfile

ROOT = Path(__file__).resolve().parent
DIST = ROOT / 'dist'
C = json.loads((ROOT / 'content.json').read_text())
E = lambda value: escape(str(value), quote=True)

def paragraphs(items, cls=''):
    return ''.join('<p' + (' class="'+cls+'"' if cls else '') + '>' + E(p).replace('\n','<br>') + '</p>' for p in items)

def image(src, alt='', cls='', eager=False):
    return f'<img src="{E(src)}" alt="{E(alt)}" class="{cls}" loading="{"eager" if eager else "lazy"}" decoding="async">'

def window(n, cls=''):
    files = {1:'system-error-404',2:'access-denied',3:'file-not-found',4:'connection-lost',5:'data-corrupted',6:'unknown-error',7:'reconnecting'}
    return image(f'assets/window-{n:02d}-{files[n]}-glitch-modern.png','',cls)

NAV = [('about','公演について','ABOUT'),('story','ストーリー','STORY'),('system','遊び方','HOW TO PLAY'),('files','登場人物','CHARACTERS'),('information','公演概要','INFORMATION'),('access','アクセス','ACCESS'),('tickets','チケット','TICKETS'),('guide','注意事項','GUIDE')]

def header(sub=False):
    home = 'index.html' if sub else ''
    desktop = ''.join(f'<a href="{home}#{a}">{b}</a>' for a,b,_ in NAV[:4])
    menu = ''.join(f'<a href="{home}#{a}"><span>{b}</span><small>{c}</small></a>' for a,b,c in NAV)
    menu += '<a href="investigators.html"><span>捜査員紹介</span><small>PERSONNEL FILES</small></a>'
    return f'''<a class="skip" href="#main">本文へ移動</a>
    <header class="site-header"><a class="brand" href="{home}#main"><strong>{C['title']}</strong><small>JOHN DOE’S FINAL STATEMENT</small></a>
    <nav class="desktop-nav" aria-label="メインナビゲーション">{desktop}</nav>
    <a class="header-ticket" href="{home}#tickets">チケット情報 ↗</a>
    <details class="site-menu" id="site-menu"><summary id="menu-toggle" aria-controls="mobile-menu" aria-expanded="false"><span>MENU</span><i class="menu-lines" aria-hidden="true"></i></summary><nav class="menu-panel" id="mobile-menu" aria-label="サイトメニュー">{menu}<a href="{home}#contact"><span>お問い合わせ</span><small>CONTACT</small></a></nav></details></header>'''

def footer(sub=False):
    home = 'index.html' if sub else ''
    return f'''<footer class="site-footer"><div class="wrap"><div class="footer-top"><a href="{home}#main"><strong>{C['title']}</strong></a><nav class="footer-links" aria-label="フッター"><a href="{home}#guide">注意事項</a><a href="{home}#contact">お問い合わせ</a><a href="#main">ページ上部へ ↑</a></nav></div><div class="footer-bottom"><p>JOHN DOE’S FINAL STATEMENT<br>体験型ミステリー</p><p>開催情報・料金・参加条件は予定です。<br>正式なご案内は、公開後の情報をご確認ください。</p><button class="text-button" data-motion aria-pressed="true">MOTION <b>ON</b></button></div></div></footer>
    <div class="mobile-cta"><span>体験型ミステリー<br>{C['title']}</span><a href="{home}#tickets">チケット情報 ↗</a></div><div id="tap-point-marker" class="tap-point-marker" hidden aria-hidden="true"></div>'''

def head(title, description):
    return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#07090a"><meta name="description" content="{E(description)}"><title>{E(title)}</title><link rel="stylesheet" href="style.css"><script src="app.js" defer></script></head>'''

def section_head(n, title, tag):
    return f'<div class="section-head"><span><b>{n}</b>{title}</span><span>{tag}</span></div>'

def main_page():
    route = ''.join(f'<a href="#{a}"><span>{i+1:02}</span><b>{b}</b><small>{c}</small><i>↗</i></a>' for i,(a,b,c) in enumerate([NAV[1],NAV[2],NAV[3],NAV[6]]))
    subjects = [('yonekawa','01'),('kasuga','02'),('goto','03'),('matsuda','04'),('marin','05')]
    cards = ''.join(f'<button class="subject-button" data-person="{n}" aria-label="人物記録{n}を開く"><span class="subject-art">{image("assets/subject-"+name+".png","身元不明の人物の記録写真")}</span><span class="subject-caption"><span>SUBJECT FILE_{n}</span><span>OPEN ↗</span></span></button>' for name,n in subjects)
    steps = ''.join(f'<article class="step"><div class="step-no"><b>{i+1:02}</b><span>{s["english"]}</span></div><h3>{s["title"]}</h3><p>{s["body"]}</p></article>' for i,s in enumerate(C['steps']))
    ticket_cards = ''.join(f'<article class="ticket-card"><span class="eyebrow red">{tag}</span><h3>{label}</h3><p class="price">¥{price} <small>税込・予定</small></p><p>{body}</p><button class="button" data-ticket-status>{status}<span>↗</span></button></article>' for tag,label,price,body,status in [
        ('01 / ADVANCE','前売チケット','5,980','事前に参加日時を指定してご購入いただくチケットです。','発売日・購入先は後日発表'),
        ('02 / ON THE DAY','当日チケット','6,480','販売方法と残席の案内は、販売開始時にお知らせします。','販売のご案内は後日発表'),
        ('03 / REVENGE','リベンジチケット','4,000','もう一度、事件に向き合いたい方へ。対象者・利用条件は後日発表します。','ご利用条件は後日発表')])
    guides = [
        ('チケットの変更・払い戻し','購入後の日時変更・キャンセル・返金は、原則お受けしない予定です。公演中止時の対応、譲渡・分配の可否を含む正式な購入条件は、販売開始時にご案内します。'),
        ('集合・受付・遅刻','東京メトロ丸ノ内線「方南町駅 3a番出口」へ余裕を持ってお越しください。受付時にチケットを確認します。集合時刻、遅刻時の参加可否・返金の扱いは、販売時の案内をご確認ください。'),
        ('演出・参加条件・体調について','演出内容や体調面に不安のある方は、ご予約前にご相談ください。年齢制限、乳幼児の同伴、妊娠中・持病のある方の参加条件は後日ご案内します。泥酔状態での参加はお控えください。'),
        ('キャスト・設備への接触','スタッフの案内に従い、キャストへの接触や暴力、設備を無理に動かす行為はおやめください。現場の物を動かす際は、担当刑事に確認してください。'),
        ('お手洗い・途中退出・緊急時','お手洗いは受付前にお済ませください。途中退出のルールは販売時にご案内します。体調不良など緊急の場合は、その場でスタッフへお知らせください。'),
        ('ネタバレ・リピート参加','事件の真相や仕掛けなど、体験の核心に触れる投稿はお控えください。再参加の際も、初参加の方に答えや手がかりの場所を伝えないようご協力ください。')]
    guide_html = ''.join(f'<details><summary><span>{i+1:02}</span>{title}</summary><p>{body}</p></details>' for i,(title,body) in enumerate(guides))
    return head(C['title']+'｜体験型ミステリー',C['about'][0])+f'''<body>{header()}<main id="main">
    <section class="hero" aria-label="キービジュアル"><div class="hero-topline"><span><i class="status-dot"></i>JOHN DOE / CASE ARCHIVE</span><span>IDENTITY : UNRESOLVED</span><span>FINAL STATEMENT_</span></div><div class="hero-visual">{image('assets/kv.jpg',C['title']+' キービジュアル。人物写真とエラーウィンドウが重なる赤とシアンの画面。','hero-kv',True)}</div><div class="hero-caption"><div><h1>最後に、男を逮捕するか、しないか。<br>その判断を下すのは、あなたたちです。</h1><p>あなた自身が刑事となり、殺人事件の捜査に参加する体験型ミステリー。</p></div><div class="hero-actions"><a class="button primary" href="#tickets">チケット情報<span>↗</span></a><a class="button" href="#about">公演について<span>↓</span></a></div></div><div class="hero-tools"><span class="mono muted">SPECIAL INVESTIGATION UNIT 0</span><div><button class="text-button" data-motion aria-pressed="true">MOTION <b>ON</b></button><button class="text-button" id="sound" aria-pressed="false" aria-label="効果音をオンにする">SOUND <b>OFF</b></button></div><a href="#about">SCROLL ↓</a></div></section>
    <nav class="wrap" aria-label="コンテンツ"><div class="route-nav">{route}</div></nav>
    <section class="section" id="about"><div class="wrap">{section_head('01','ABOUT','INVESTIGATION START')}<div class="split"><div class="about-title"><span class="lead-mark">IMMERSIVE MYSTERY</span><h2>ジョン・ドゥの<br>最終陳述とは</h2><div class="case-signal"><span class="signal-label mono">IDENTITY NOT FOUND</span>{window(1)}<p>供述と証拠。<br>その先にある真相へ。</p></div></div><div class="body-copy">{paragraphs(C['about'][:2])}<div class="decision">{E(C['about'][2]).replace(chr(10),'<br>')}</div></div></div></div></section>
    <section class="section story-section" id="story"><div class="wrap">{section_head('02','STORY','STATEMENT / 供述記録')}<div class="split"><div><h2 class="story-quote">「僕がやりました」</h2><div class="story-aside">{window(7,'ghost-window')}<span class="case-stamp">MOTIVE : UNKNOWN</span></div></div><div class="body-copy story-copy">{paragraphs(C['story'])}</div></div></div></section>
    <section class="section" id="system"><div class="wrap">{section_head('03','HOW TO PLAY','SPECIAL INVESTIGATION UNIT 0')}<h2>あなたの言葉で、捜査する。</h2><div class="system-intro"><div><p class="eyebrow">IMMERSIVE EXPERIENCE</p><h3>本公演における<br>イマーシブ（没入体験）とは</h3></div><div class="body-copy">{paragraphs(C['immersive'])}</div></div><h3 class="eyebrow cyan" style="margin-bottom:20px">INVESTIGATION FLOW / 遊び方</h3><div class="steps">{steps}</div><aside class="info-card-note"><div class="info-card-visual" aria-hidden="true"><span>INVESTIGATION MEMO</span><b>情報カード</b><i></i><i></i></div><div><h3>情報カード</h3><p>{E(C['informationCards']).replace(chr(10),'<br>')}</p></div></aside></div></section>
    <section class="section" id="files"><div class="wrap">{section_head('04','CHARACTERS','PERSONNEL / SUBJECT FILES')}<h2>登場人物</h2><div class="cast-heading"><div><h3>謎の男</h3><p>殺人を自供する身元不明の男。<br>その素性も動機も明らかになっていない。</p></div><span class="eyebrow red">IDENTITY UNKNOWN</span></div><div class="subject-grid">{cards}</div><p class="file-hint">人物記録を選ぶと、写真を拡大してご覧いただけます。</p><a class="investigator-link" href="investigators.html"><div class="file-folder" aria-hidden="true">PERSONNEL FILES<b>捜査第一課</b></div><div><h3>捜査一課の刑事</h3><p>現場指揮を執る刑事。<br>特殊捜査0課のあなたたちとともに、事件の捜査を進める。</p><p class="cyan" style="margin-top:14px">捜査資料を開く ／ 捜査員紹介・出演日程</p></div><span class="link-arrow" aria-hidden="true">↗</span></a><div class="character-minor"><article><span class="eyebrow muted">MOBILE INVESTIGATION UNIT</span><h3>麻生 <small>（あそう）</small></h3><p>機動捜査隊員。<br>あなたたちを現場へ案内し、捜査に関する情報を伝える。</p></article><article><span class="eyebrow muted">VICTIM</span><h3>鬼島 司 <small>（きじま つかさ）</small></h3><p>事件の被害者。50歳。<br>指定暴力団・坂口組系「鬼島組」の幹部。</p></article></div><aside class="experience-note"><h3>物語体験について</h3><div>{paragraphs(C['experience'])}</div></aside><div class="error-pair" aria-hidden="true">{window(3)}{window(4)}</div></div></section>
    <section class="section" id="information"><div class="wrap narrow">{section_head('05','INFORMATION','PERFORMANCE DETAILS')}<h2>公演概要</h2><p class="section-sub">体験型ミステリー「{C['title']}」</p><dl class="info-table"><div class="info-row"><dt>公演日程</dt><dd>開催日は後日発表<small>15日間・全90公演（1日6公演）を予定</small></dd></div><div class="info-row"><dt>公演時間・定員</dt><dd>80分・各回6名<small>公演時間・定員・公演数は予定です</small></dd></div><div class="info-row"><dt>会場</dt><dd>後日発表</dd></div><div class="info-row"><dt>集合場所</dt><dd>東京メトロ丸ノ内線<br>方南町駅 3a番出口</dd></div><div class="info-row"><dt>出演日程</dt><dd><a class="cyan" href="investigators.html#schedule">臨場予定／出演日程を見る ↗</a></dd></div></dl><p class="note">開催日・開演時刻・会場・料金などの正式な情報は、公開後のご案内をご確認ください。</p></div></section>
    <section class="section" id="tickets"><div class="wrap">{section_head('06','TICKETS','ADMISSION / 販売開始前')}<h2>捜査への参加はこちら。</h2><p class="section-sub">チケットの発売日・購入先は後日ご案内します。</p><div class="ticket-grid">{ticket_cards}</div><p class="note">料金・定員・公演数は試算に基づく予定です。発券・決済手数料の有無、参加対象年齢、受付時間、1〜5名での参加や貸切の可否については、正式な販売案内をご確認ください。</p><a class="button" href="#guide">ご予約前に注意事項を確認する<span>↓</span></a></div></section>
    <section class="section" id="access"><div class="wrap">{section_head('07','ACCESS','MEETING POINT')}<div class="access-panel"><div><h2>集合場所</h2><p class="eyebrow muted">TOKYO METRO / MARUNOUCHI LINE</p><p class="station">方南町駅<br><small>3a番出口</small></p><p class="muted" style="font-size:13px">東京メトロ丸ノ内線<br>会場・集合時刻・受付の目印は、販売開始時にご案内します。</p><a class="button" href="https://maps.app.goo.gl/snG4QUyvxEAzQvsg9" target="_blank" rel="noopener noreferrer">Google マップで確認<span>↗</span></a></div><div class="access-path"><ol><li><span>01</span>方南町駅 3a番出口へ</li><li><span>02</span>受付でチケットをご提示ください</li><li><span>03</span>スタッフがご案内します</li></ol><p class="note">集合時刻は正式な販売案内をご確認ください。余裕を持ってお越しください。</p></div></div></div></section>
    <section class="section" id="guide"><div class="wrap narrow">{section_head('08','PARTICIPATION GUIDE','PLEASE READ BEFORE ENTERING')}<h2>ご参加にあたって</h2><p class="section-sub">各項目を開いてご確認ください。</p><p class="note">受付・キャンセル・参加条件などの正式なルールは、チケット販売開始時に確定します。以下は現時点でのご案内です。</p><div class="guide-list">{guide_html}</div><div class="contact-box" id="contact"><span class="eyebrow cyan">CONTACT</span><h3>お問い合わせ</h3><p>お問い合わせ窓口は、公演情報の公開に合わせてご案内します。</p></div><div class="error-pair" aria-hidden="true">{window(2)}{window(5)}{window(6)}</div></div></section>
    </main>{footer()}
    <dialog id="file-dialog" aria-labelledby="dialog-title"><div class="dialog-bar"><span id="dialog-file">SUBJECT FILE</span><button class="close-dialog" aria-label="人物記録を閉じる">×</button></div><div class="dialog-content"><div id="dialog-photo" class="subject-art"></div><div><span class="eyebrow red">IDENTITY UNKNOWN</span><h2 id="dialog-title">謎の男</h2><p>殺人を自供する身元不明の男。<br>その素性も動機も明らかになっていない。</p><p class="mono muted">STATEMENT : 「僕がやりました」</p><button class="button close-dialog">人物記録を閉じる<span>↵</span></button></div></div></dialog>
    <dialog id="ticket-dialog" aria-labelledby="ticket-title"><div class="dialog-bar"><span>TICKETS / SALES STATUS</span><button class="close-dialog" aria-label="販売状況を閉じる">×</button></div><div class="dialog-status"><span class="eyebrow red">NOT ON SALE YET</span><h2 id="ticket-title">チケット販売開始前です。</h2><p>発売日・購入先・正式な参加条件は、後日ご案内します。</p><p class="muted">前売 5,980円 ／ 当日 6,480円<br>リベンジ 4,000円（いずれも税込・予定）</p><button class="button close-dialog">閉じる<span>↵</span></button></div></dialog></body></html>'''

def officers_page():
    files = ''
    for i,o in enumerate(C['officers']):
        files += f'''<article class="officer-file" id="{o['id']}"><div class="officer-photo">{image(o['photo'],o['name']+'の制服写真')}<span class="id-label">INVESTIGATOR / {i+1:02} — PERSONNEL RECORD</span></div><div class="officer-content"><div class="file-row mono"><span>PERSONNEL FILE_{i+1:02}</span><span>捜査第一課</span></div><h2>{o['name']}</h2><p class="officer-english">{o['english']}</p><dl class="officer-facts"><dt>所属</dt><dd>{o['department']}</dd><dt>階級・年齢</dt><dd>{o['rank']} ／ {o['age']}歳</dd><dt>担当キャスト</dt><dd>{o['cast']}</dd></dl><div class="officer-description">{paragraphs(o['body'])}</div><a class="button schedule-link" href="#schedule" data-officer="{o['name']}" data-cast="{o['cast']}">{o['name']}の臨場日・出演日程を見る<span>↓</span></a></div></article>'''
    menu = ''.join(f'<a href="#{o["id"]}">{o["name"]}</a>' for o in C['officers'])
    schedule_img = C.get('scheduleImage')
    if schedule_img:
        schedule_body = image(schedule_img,C.get('scheduleAlt','捜査員の出演日程表'))
    else:
        schedule_body = '<p>出演日程は後日公開します。<br>公開後、こちらから各キャストの臨場日をご確認いただけます。</p>'
    return head('捜査員紹介｜'+C['title'],'あなたとともに事件を追う、捜査一課の刑事たち。捜査員の人物資料と臨場予定・出演日程。')+f'''<body class="file-page">{header(True)}<main id="main"><section class="dossier-top"><div class="wrap"><nav class="breadcrumb" aria-label="パンくず"><a href="index.html#main">TOP</a><span>/</span><a href="index.html#files">登場人物</a><span>/</span><span>捜査員紹介</span></nav><span class="eyebrow cyan">PERSONNEL FILES / 捜査第一課</span><h1>捜査員紹介</h1><p class="lede">あなたとともに事件を追う、捜査一課の刑事たち。</p><div class="dossier-meta mono"><span>警視庁刑事部捜査第一課</span><span>JOINT INVESTIGATION / 特殊捜査0課</span><span>5 PERSONNEL FILES</span></div><nav class="dossier-menu" aria-label="捜査員一覧">{menu}<a href="#schedule">臨場予定・出演日程 ↓</a></nav></div></section><div class="wrap officer-list">{files}</div><section class="schedule" id="schedule"><div class="wrap">{section_head('06','CAST SCHEDULE','臨場予定／出演日程')}<div class="schedule-box"><span class="eyebrow cyan">ASSIGNMENT SCHEDULE</span><h3>臨場予定／出演日程</h3><p id="schedule-selected" class="schedule-selected" aria-live="polite" hidden></p>{schedule_body}</div><a class="back-link" href="index.html#files">← 登場人物に戻る</a></div></section></main>{footer(True)}</body></html>'''

def data_url(asset):
    p = DIST / asset
    if not p.is_file():
        raise FileNotFoundError(p)
    return 'data:'+(mimetypes.guess_type(str(p))[0] or 'application/octet-stream')+';base64,'+base64.b64encode(p.read_bytes()).decode()

def standalone(html, sub=False):
    css=(DIST/'style.css').read_text()
    js=(DIST/'app.js').read_text()
    html=html.replace('<link rel="stylesheet" href="style.css">','<style>'+css+'</style>').replace('<script src="app.js" defer></script>','')
    cache={}
    def embed(m):
        path=m.group(1)
        if path not in cache:cache[path]=data_url(path)
        return 'src="'+cache[path]+'"'
    html=re.sub(r'src="(assets/[^"]+)"',embed,html)
    html=html.replace('href="index.html','href="john-doe-preview-v15.html').replace('href="investigators.html','href="john-doe-investigators-v15.html')
    return html.replace('</body>','<script>'+js+'</script></body>')

if __name__=='__main__':
    main=main_page();officers=officers_page()
    (DIST/'index.html').write_text(main)
    (DIST/'investigators.html').write_text(officers)
    (ROOT.parent/'john-doe-preview-v15.html').write_text(standalone(main))
    (ROOT.parent/'john-doe-investigators-v15.html').write_text(standalone(officers,True))
    print('Built local source and two standalone HTML previews.')

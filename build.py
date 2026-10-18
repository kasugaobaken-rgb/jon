from pathlib import Path
from html import escape
import re, json, base64, hashlib, mimetypes, importlib.util

ROOT=Path(__file__).resolve().parent
DIST=ROOT/'dist'
C=json.loads((ROOT/'content.json').read_text())
def esc(x):return escape(str(x),quote=True)
def paras(items):return ''.join('<p>'+esc(p).replace('\n','<br>')+'</p>' for p in items)
def section_replace(html,id,body):
    result,n=re.subn(r'<section id="'+id+r'"[^>]*>.*?</section>',lambda m:body,html,flags=re.S)
    assert n==1,(id,n)
    return result

def externalize(s):
    def save(m):
        mime,payload=m.group(1),m.group(2)
        raw=base64.b64decode(payload)
        ext={'image/png':'png','image/jpeg':'jpg','image/webp':'webp'}.get(mime,'img')
        path='assets/legacy-'+hashlib.sha256(raw).hexdigest()[:12]+'.'+ext
        if not (DIST/path).exists():(DIST/path).write_bytes(raw)
        return path
    return re.sub(r'data:(image/[^;]+);base64,([A-Za-z0-9+/=]+)',save,s)

def embed(s):
    cache={}
    def insert(m):
        p=m.group(0)
        if p not in cache:
            f=DIST/p
            cache[p]='data:'+(mimetypes.guess_type(str(f))[0] or 'application/octet-stream')+';base64,'+base64.b64encode(f.read_bytes()).decode()
        return cache[p]
    s=re.sub(r'assets/[A-Za-z0-9_.-]+\.(?:png|jpg|jpeg|webp)',insert,s)
    s=s.replace('href="index.html','href="john-doe-preview-v23.html').replace('href="investigators.html','href="john-doe-investigators-v23.html')
    return s

def build():
    original=(ROOT/'base-v14.html').read_text()
    s=externalize(original).replace('ジョン・ドウ','ジョン・ドゥ')
    # Keep all original CSS and scripts. Add a small, separately maintained update sheet.
    s=s.replace('</style>','</style><link rel="stylesheet" href="updates.css">',1)
    s=s.replace('真実は、どこにも存在しないのか。ミステリーイベント『ジョン・ドゥの最終陳述』のコンセプトサイト。',C['about'][0])
    s=s.replace('aria-label="六人の人物の捜査写真"','aria-label="身元不明の人物の捜査写真"')
    # The old sixth fictitious person becomes the unresolved-file window already present in the KV.
    unknown='<div class="profile profile-6" aria-hidden="true"><span class="window-bar"><i></i><i></i><i></i><span>SUBJECT FILE</span><b>− ×</b></span><span class="unknown-photo">JOHN DO<small>IDENTITY UNRESOLVED</small></span></div>'
    s,n=re.subn(r'<button class="profile profile-6"[^>]*>.*?</button>',lambda m:unknown,s,flags=re.S);assert n==1
    s=s.replace('<i class="file-photo p6"></i>','')
    s=s.replace('<p class="hero-prologue">一つの事件。消された真実。<br>あなたは、どの記録を信じる？</p>','<p class="hero-prologue">「僕がやりました」<br>その自白は、真実なのか。</p>')
    s=s.replace('真実は、どこにも存在しないのか。</p>','男を逮捕するか、しないか。</p>')
    # Portrait assets already include their own window frames.
    subject_assets=['subject-yonekawa.png','subject-kasuga.png','subject-goto.png','subject-marin.png','subject-matsuda.png']
    def image_only_profile(match):
        tag=match.group().split('>',1)[0]+'>'
        i=int(re.search(r'profile-([1-5])',tag).group(1))-1
        return tag+f'<img class="profile-image" src="assets/{subject_assets[i]}" alt="人物ファイル{i+1:02}の捜査写真" decoding="async"></button>'
    s,n=re.subn(r'<button class="profile profile-[1-5]"[^>]*>.*?</button>',image_only_profile,s,flags=re.S);assert n==5
    # Use the supplied transparent logo unchanged, with an SVG viewport for its canvas margins.
    logo='<svg class="title-art supplied-title" viewBox="400 320 972 440" role="img" aria-label="ジョン・ドゥの最終陳述"><image href="assets/title-logo-supplied.png" width="1754" height="1240"/></svg>'
    s,n=re.subn(r'<svg class="title-art".*?</svg>',lambda m:logo,s,flags=re.S);assert n==1

    s=s.replace('ひとつの事件。消された記録。<br>その先に、まだ真実が眠っている。','「僕がやりました」<br>その自白の先にあるものを確かめる。')
    s=s.replace('それぞれの証言が、真実を歪める。<br>人物ファイルにアクセスする。','身元不明の男と、事件を追う刑事たち。<br>人物ファイルにアクセスする。')
    s=s.replace('失われたデータを追跡し、<br>断片的な証言から真実を読み解く。','現場検証、取り調べ、情報共有。<br>証拠をつなぎ、最後の判断へ。')

    story=f'''<section id="story" class="section story-section"><div class="section-label reveal"><span class="mono red">01 / STORY</span><span class="mono muted">case_00404 / overview.txt</span></div><div class="overview-content reveal" id="about"><div><p class="eyebrow">IMMERSIVE MYSTERY</p><h2>ジョン・ドゥの<br>最終陳述とは</h2></div><div>{paras(C['about'])}</div></div><div class="story-layout"><div class="story-heading reveal"><p class="eyebrow">すべては、一通の陳述から。</p><h2 class="updated-quote">「僕がやりました」</h2><div class="case-stamp mono">CLASSIFIED<br><small>CASE NO. 00404</small></div></div><div class="story-copy reveal">{paras(C['story'])}</div></div><div class="terminal reveal"><div class="terminal-top mono"><span>● &nbsp; RECOVERY TERMINAL</span><span>read_only</span></div><div class="terminal-content mono"><span class="muted">&gt; accessing /archive/john_doe/statement.log</span><br><span class="red">WARNING:</span> <span id="terminal-text">Identity verification failed.</span><span class="terminal-cursor">▌</span></div></div></section>'''
    s=section_replace(s,'story',story)

    officer_links=''.join(f'<a class="officer-file" href="investigators.html#{esc(o["id"])}" aria-label="{esc(o["name"])}の捜査員紹介を見る"><span class="file-num">{i+1:02}</span><img class="officer-thumbnail" src="{esc(o["photo"])}" alt="{esc(o["name"])}の制服写真"><span class="file-name">{esc(o["name"])}<span>{esc(o["english"])}</span><small>担当キャスト：{esc(o["cast"])}</small></span><span class="file-state">{esc(o["rank"])} ／ {o["age"]}歳</span><span class="file-plus" aria-hidden="true">↗</span></a>' for i,o in enumerate(C['officers']))
    files=f'''<section id="files" class="section files-section"><div class="section-label reveal"><span class="mono red">02 / PERSON FILES</span><span class="mono muted">personnel records_</span></div><div class="section-heading reveal"><h2>登場人物</h2><p>捜査員を選んで、紹介資料へ。</p></div><article class="mystery-man-copy reveal"><h3>謎の男</h3><p>殺人を自供する身元不明の男。<br>その素性も動機も明らかになっていない。</p></article><div class="officer-list-intro reveal"><p class="eyebrow">PERSONNEL FILES / 捜査第一課</p><h3>捜査一課の刑事</h3><p>現場指揮を執る刑事。<br>特殊捜査0課のあなたたちとともに、事件の捜査を進める。</p></div><nav class="file-list officer-list reveal" aria-label="捜査員を選ぶ">{officer_links}</nav><a class="officer-schedule-link reveal" href="investigators.html#schedule">臨場予定／出演日程を見る <span aria-hidden="true">↗</span></a><div class="minor-characters reveal"><article><h3>麻生 <small>（あそう）</small></h3><p>機動捜査隊員。<br>あなたたちを現場へ案内し、捜査に関する情報を伝える。</p></article><article><h3>鬼島 司 <small>（きじま つかさ）</small></h3><p>事件の被害者。50歳。<br>指定暴力団・坂口組系「鬼島組」の幹部。</p></article></div></section>'''
    s=section_replace(s,'files',files)

    steps=''.join(f'<article><span>{i+1:02} / {o["english"]}</span><h3>{o["title"]}</h3><p>{o["body"]}</p></article>' for i,o in enumerate(C['steps']))
    system=f'''<section id="system" class="section system-section"><div class="section-label reveal"><span class="mono red">03 / SYSTEM</span><span class="mono muted">investigate with your own words_</span></div><div class="section-heading reveal"><h2>体験システム</h2><p>現場検証から、最後の逮捕判断まで。</p></div><div class="immersive-copy reveal"><h3>本公演におけるイマーシブ（没入体験）とは</h3>{paras(C['immersive'])}</div><h3 class="eyebrow reveal">遊び方 / INVESTIGATION FLOW</h3><div class="system-steps reveal">{steps}</div><div class="information-card-copy reveal"><h3>情報カード</h3>{paras([C['informationCards']])}</div><div class="experience-copy reveal"><h3>物語体験について</h3>{paras(C['experience'])}</div></section>'''
    s=section_replace(s,'system',system)
    # Publish the supplied participation rules, retaining the established accordion UI.
    groups=json.loads((ROOT/'notices.json').read_text())
    def notice_text(text):
        return re.sub(r'\*\*(.*?)\*\*',r'<strong>\1</strong>',esc(text)).replace('\n','<br>')
    panels=''.join('<details'+(' open' if i<2 else '')+'><summary><span class="guide-index">'+f'{i+1:02}'+'</span><span>'+esc(g['title'])+'</span><span class="guide-toggle" aria-hidden="true"></span></summary><div class="guide-body">'+''.join('<p>'+notice_text(item)+'</p>' for item in g['items'])+'</div></details>' for i,g in enumerate(groups))
    contact=re.search(r'<div id="contact".*?</div>',s,re.S).group()
    guide='<section id="guide" class="section guide-section" aria-labelledby="guide-title"><div class="section-label reveal"><span class="mono red">06 / PARTICIPATION GUIDE</span><span class="mono muted">please read before entering_</span></div><div class="section-heading reveal"><div><p class="eyebrow">ご予約・ご参加の前に、必ずお読みください。</p><h2 id="guide-title">注意事項</h2></div><span class="guide-caption">各項目を開いてご確認ください。</span></div><div class="guide-list reveal">'+panels+'</div>'+contact+'</section>'
    s=section_replace(s,'guide',guide)
    s=s.replace('集合時刻・受付の目印は、販売開始時にご案内します。','チケットに記載された公演時間の５分前にお集まりください。')
    s=s.replace('購入者が負担する発券・決済手数料の有無、参加対象年齢、受付時間は販売開始時にご案内します。','購入者が負担する発券・決済手数料の有無、参加対象年齢は販売開始時にご案内します。集合時間や参加条件は、下記の注意事項をご確認ください。')
    s=s.replace('購入先や正式な参加条件も、販売開始に合わせてご案内します。','購入先は販売開始に合わせてご案内します。参加条件は、注意事項をご確認ください。')
    # Confirmed performance times and prices supplied on 2026-10-18.
    s=s.replace('開催日・開演時刻は後日発表','開催日・会場は後日発表')
    s=s.replace('1日6公演 / 開催日は後日発表','1日6公演 / 開催日は後日発表')
    s=s.replace('<dt>チケット</dt><dd>前売 5,980円（税込・予定）<span>当日 6,480円 / リベンジ 4,000円（税込・予定）</span></dd>', '<dt>チケット</dt><dd>前売券 5,980円（税込・手数料別）<span>当日券 6,500円（税込）<br>当日リベンジ 4,000円</span></dd>')
    s=s.replace('<dt>公演時間・定員</dt><dd>80分・各回6名<span>料金・公演数は試算に基づく予定です</span></dd>', '<dt>所要時間・定員</dt><dd>約80分・各回6名</dd>')
    compact='<div><dt>公演時間</dt><dd class="performance-times-compact">①11:00 ／ ②12:40 ／ ③14:20<br>④16:00 ／ ⑤17:40 ／ ⑥19:20</dd></div>'
    s=s.replace('<div><dt>会場</dt>',compact+'<div><dt>会場</dt>',1)
    s=s.replace('<small>所要時間</small><strong>80<em>分</em></strong>','<small>所要時間</small><strong><span class="ticket-approx">約</span>80<em>分</em></strong>')
    s=s.replace('開催日・開演時刻・会場は後日発表します。','開催日・会場は後日発表します。')
    times=['11:00','12:40','14:20','16:00','17:40','19:20']
    schedule='<div class="performance-schedule reveal" aria-label="公演時間"><h3>公演時間</h3><ol>'+''.join(f'<li><span>第{i+1}回</span><strong>{time}</strong></li>' for i,time in enumerate(times))+'</ol></div>'
    s=s.replace('<div id="access" class="meeting-point',schedule+'<div id="access" class="meeting-point',1)
    s=s.replace('5,980<small>税込・予定</small>','5,980<small>税込・手数料別</small>')
    s=s.replace('6,480<small>税込・予定</small>','6,500<small>税込</small>')
    s=s.replace('4,000<small>税込・予定</small>','4,000')
    s=s.replace('<span>03 / REVENGE</span><span>再挑戦</span>','<span>03 / SAME-DAY REVENGE</span><span>当日リベンジ</span>')
    s=s.replace('<h3>リベンジチケット</h3>','<h3>当日リベンジ</h3>')
    s=s.replace('もう一度、事件に向き合いたい方へ。対象者・利用条件・販売方法は後日発表します。','もう一度、事件に向き合いたい方へ。当日リベンジの対象者・利用条件・販売方法は後日発表します。')
    s=s.replace('料金・定員・公演数は試算に基づく予定です。購入者が負担する発券・決済手数料の有無、参加対象年齢は販売開始時にご案内します。','前売券は税込・手数料別、当日券は税込です。参加対象年齢は販売開始時にご案内します。')
    s=s.replace('リベンジ券の適用条件','当日リベンジの適用条件')
    s=s.replace('開催日・会場は未定。料金・公演数は試算に基づく予定です。','開催日・会場は後日発表。公演日数・公演数は予定です。')
    s=s.replace('前売 5,980円 ／ 当日 6,480円<br>リベンジ 4,000円（いずれも税込・予定）','前売券：5,980円（税込・手数料別）<br>当日券：6,500円（税込）<br>当日リベンジ：4,000円')
    s=s.replace('開催日・開演時刻・会場・販売開始日は後日発表します。','開催日・会場・販売開始日は後日発表します。')
    # Update only the person-data array; keep the original dialog, menu, sound, noise and shake handlers.
    subjects=[['謎の男','「僕がやりました」'] for _ in range(6)]
    s,n=re.subn(r'const subjects = \[.*?\n\];',lambda m:'const subjects = '+json.dumps(subjects,ensure_ascii=False)+';',s,flags=re.S);assert n==1
    s=s.replace('6 statements recovered. Truth: unresolved.','Statement recovered. Truth: unresolved.')
    s=s.replace('この記録はデザイン用の仮設定です。<br>正式な人物・公演情報は公開をお待ちください。','殺人を自供する身元不明の男。<br>その素性も動機も明らかになっていない。')
    s=s.replace('RECOVERED STATEMENT','PERSON FILE / 供述記録').replace('<h2 id="dialog-title">最初の証言</h2>','<h2 id="dialog-title">謎の男</h2>')
    s=s.replace('<div class="front-controls">','<div class="front-controls"><button class="kv-open" data-kv>キービジュアルを見る</button>',1)
    kv_dialog='<dialog id="kv-dialog" aria-labelledby="kv-title"><div class="dialog-bar mono"><span id="kv-title">KEY VISUAL / ジョン・ドゥの最終陳述</span><button class="close-dialog" aria-label="キービジュアルを閉じる">×</button></div><img class="kv-modal-image" src="assets/kv.jpg" alt="ジョン・ドゥの最終陳述 キービジュアル"><button class="dialog-bottom close-dialog">閉じる <span>↵</span></button></dialog>'
    s=s.replace('<dialog id="file-dialog"',kv_dialog+'<dialog id="file-dialog"',1)
    s=s.replace('</body>','<script>document.querySelector("[data-kv]").addEventListener("click",()=>openDialog(document.getElementById("kv-dialog")));</script></body>')
    from character_modals import add_character_modals
    s=add_character_modals(s,C)
    from clean_hero import remove_marked_copy
    s=remove_marked_copy(s)
    (DIST/'updates.css').write_text((ROOT/'updates.css').read_text())
    (DIST/'index.html').write_text(s)
    # Reuse the requested new personnel page; it had no counterpart in the old site.
    spec=importlib.util.spec_from_file_location('dossier',ROOT/'dossier_builder.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.C=C
    staff=module.officers_page().replace('href="style.css"','href="dossier.css"').replace('src="app.js"','src="dossier.js"')
    staff=staff.replace('開催情報・料金・参加条件は予定です。','公演時間・料金は公演サイトをご確認ください。参加条件は注意事項をご確認ください。')
    (DIST/'investigators.html').write_text(staff)
    main_single=s.replace('<link rel="stylesheet" href="updates.css">','<style>'+(ROOT/'updates.css').read_text()+'</style>')
    (ROOT.parent/'john-doe-preview-v23.html').write_text(embed(main_single))
    staff_single=staff.replace('<link rel="stylesheet" href="dossier.css">','<style>'+(DIST/'dossier.css').read_text()+'</style>').replace('<script src="dossier.js" defer></script>','')
    staff_single=staff_single.replace('</body>','<script>'+(DIST/'dossier.js').read_text()+'</script></body>')
    (ROOT.parent/'john-doe-investigators-v23.html').write_text(embed(staff_single))
    print('Built v23 from the v14 original layout and event handlers.')

if __name__=='__main__':build()

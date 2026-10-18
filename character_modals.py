"""Focused v22 changes: officer dialogs and the supplied sixth portrait."""
from html import escape
import re


def add_character_modals(page, content):
    def esc(value):
        return escape(str(value), quote=True)

    sixth = '<button class="profile profile-6" data-person="5" aria-label="人物ファイル06を開く"><img class="profile-image" src="assets/subject-sixth.jpg" alt="人物ファイル06の捜査写真" decoding="async"></button>'
    page, count = re.subn(r'<div class="profile profile-6"[^>]*>.*?</div>', lambda _: sixth, page, flags=re.S)
    assert count == 1

    dialogs = []
    for index, officer in enumerate(content['officers'], 1):
        oid = esc(officer['id'])
        pattern = r'<a class="officer-file" href="investigators.html#' + oid + r'"([^>]*)>(.*?)</a>'
        page, count = re.subn(pattern, lambda m: f'<button type="button" class="officer-file" data-officer-dialog="{oid}" aria-haspopup="dialog" aria-controls="officer-dialog-{oid}"{m[1]}>{m[2].replace("↗", "+")}</button>', page, flags=re.S)
        assert count == 1, oid
        body = ''.join(f'<p>{esc(paragraph)}</p>' for paragraph in officer['body'])
        dialogs.append(f'''<dialog id="officer-dialog-{oid}" class="officer-dialog" aria-labelledby="officer-title-{oid}">
<div class="dialog-bar mono"><span>OFFICER_{index:02} / PERSONNEL FILE</span><button type="button" class="close-dialog" aria-label="捜査員紹介を閉じる">×</button></div>
<div class="dialog-content"><img class="officer-dialog-photo" src="{esc(officer['photo'])}" alt="{esc(officer['name'])}の制服写真">
<div class="officer-dialog-copy"><p class="eyebrow red">PERSONNEL FILE / 捜査員紹介</p><h2 id="officer-title-{oid}">{esc(officer['name'])}</h2><p class="officer-dialog-english mono">{esc(officer['english'])}</p>
<dl class="dialog-details officer-dialog-details"><div><dt>所属</dt><dd>{esc(officer['department'])}</dd></div><div><dt>階級・年齢</dt><dd>{esc(officer['rank'])} ／ {officer['age']}歳</dd></div><div><dt>担当キャスト</dt><dd>{esc(officer['cast'])}</dd></div></dl>
<div class="officer-dialog-description">{body}</div>
<details class="officer-inline-schedule"><summary>臨場日・出演日程を見る</summary><p>出演日程表は後日公開します。</p></details>
</div></div><button type="button" class="dialog-bottom close-dialog">ファイルを閉じる <span>↵</span></button></dialog>''')

    page = page.replace('捜査員を選んで、紹介資料へ。', '捜査員を選んで、人物ファイルを開く。')
    page, count = re.subn(r'<a class="officer-schedule-link reveal" href="investigators.html#schedule">.*?</a>', '<button type="button" class="officer-schedule-link reveal" data-officer-schedule aria-haspopup="dialog" aria-controls="officer-schedule-dialog">臨場予定／出演日程を見る <span aria-hidden="true">+</span></button>', page, flags=re.S)
    assert count == 1
    dialogs.append('''<dialog id="officer-schedule-dialog" aria-labelledby="officer-schedule-title"><div class="dialog-bar mono"><span>PERSONNEL FILE / SCHEDULE</span><button type="button" class="close-dialog" aria-label="出演日程を閉じる">×</button></div><div class="officer-schedule-content"><p class="eyebrow red">SCHEDULE / 臨場予定</p><h2 id="officer-schedule-title">臨場予定／出演日程</h2><p>出演日程表は後日公開します。</p></div><button type="button" class="dialog-bottom close-dialog">ファイルを閉じる <span>↵</span></button></dialog>''')
    # Insert before the original scripts bind close, backdrop and signal effects.
    page = page.replace('<dialog id="file-dialog"', ''.join(dialogs) + '<dialog id="file-dialog"', 1)
    script = '''<script>
document.querySelectorAll('[data-officer-dialog]').forEach(button => {
  button.addEventListener('click', () => openDialog(document.getElementById('officer-dialog-' + button.dataset.officerDialog)));
});
document.querySelector('[data-officer-schedule]').addEventListener('click', () => openDialog(document.getElementById('officer-schedule-dialog')));
</script>'''
    return page.replace('</body>', script + '</body>')

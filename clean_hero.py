"""Remove only the top-of-page copy marked in the supplied screenshots."""


def remove_marked_copy(page):
    marked = [
        '<p class="hero-prologue">「僕がやりました」<br>その自白は、真実なのか。</p>',
        '<p class="hero-question">男を逮捕するか、しないか。</p>',
        '<div class="hero-date"><strong>COMING SOON</strong><span>開催日程は近日公開</span></div>',
        '<p class="vertical-copy"><em>削除された記録の先に、</em><br>まだ終わっていない真実がある。</p>',
        '<p>これは、<br>誰の記録だ？</p>',
        '<span class="mono">SEARCHING...<br>NO RESULTS.<br>THE TRUTH IS NOWHERE.</span>',
    ]
    for fragment in marked:
        assert page.count(fragment) == 1, fragment
        page = page.replace(fragment, '', 1)
    return page

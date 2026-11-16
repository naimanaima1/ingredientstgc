"""TEST pages (noindex, unlinked, nothing is sent anywhere):
  /programs/jara-landing-test/   a proposed itsjara.com landing page
  /programs/goodcoil-home-test/  a proposed thegoodcoil.com homepage + quiz results page
They live here so the JARA and Hostinger sites stay untouched until you approve a design.
"""
import build as B

e = B.e
JARA = 'https://itsjara.com'
GC = 'https://thegoodcoil.com'
GUIDE = 'https://thegoodcoil.com/wash-and-go-guide'

def u(url, medium, campaign='jara_beta', content=''):
    return e(B.utm(url, medium, campaign, content))

CSS = '''
.et{color:#432731;font-family:Manrope,sans-serif}
.et *{box-sizing:border-box}
.et-test{margin:0;padding:10px 16px;background:#DCF473;font-weight:600;font-size:14px;text-align:center}
.et section{padding:84px 5%}
.et-in{max-width:1080px;margin:0 auto}
.et h1,.et h2{font-family:"Instrument Serif",serif;font-style:italic;font-weight:400;letter-spacing:-.01em;line-height:1.04;margin:0 0 16px}
.et h1{font-size:clamp(42px,7.5vw,76px)}
.et h2{font-size:clamp(32px,5vw,52px)}
.et h3{font-size:20px;margin:0 0 8px;letter-spacing:-.02em}
.et p{font-size:18px;line-height:1.65;margin:0 0 14px}
.et .eyebrow{font-size:12px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;display:block;margin-bottom:12px}
.et-btn{display:inline-flex;align-items:center;justify-content:center;min-height:54px;padding:0 30px;border-radius:999px;background:#2548D7;color:#F8F7F2;font-weight:800;font-size:17px;text-decoration:none;border:0;cursor:pointer;font-family:inherit}
.et-btn:hover{background:#432731}
.et-btn:focus-visible,.et a:focus-visible,.et button:focus-visible,.et input:focus-visible{outline:3px solid #DCF473;outline-offset:3px;box-shadow:0 0 0 6px #432731}
.et-ghost{background:transparent;color:#432731;border:2px solid #432731}
.et-ghost:hover{background:#432731;color:#F8F7F2}
.et-micro{font-size:15px!important;opacity:.85;max-width:34em;margin-top:14px}
.et-link{font-weight:700;text-underline-offset:3px}
.et-paper{background:#F8F7F2}.et-mist{background:#DCE6F0}.et-ink{background:#432731;color:#F8F7F2}.et-cobalt{background:#2548D7;color:#F8F7F2}
.et-ink .eyebrow,.et-cobalt .eyebrow{color:#DCF473}
.et-ink .et-btn,.et-cobalt .et-btn{background:#DCF473;color:#432731}
.et-ink .et-btn:hover,.et-cobalt .et-btn:hover{background:#F8F7F2}
.et-hero{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,.9fr);gap:56px;align-items:center}
.et-hero img{width:100%;border-radius:28px;display:block}
.et-two{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:32px}
.et-three{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}
.et-card{background:#fff;border:2px solid #432731;border-radius:22px;padding:26px}
.et-card p{font-size:16px;margin:0}
.et-phone{aspect-ratio:9/16;max-height:420px;border:3px solid #432731;border-radius:34px;background:#F8F7F2;display:flex;align-items:flex-end;padding:18px;font-size:14px;font-weight:700;position:relative;overflow:hidden;width:100%;max-width:240px;margin:0 auto 12px}
.et-phone:before{content:"";position:absolute;left:50%;top:10px;width:60px;height:6px;border-radius:9px;background:#432731;transform:translateX(-50%)}
.et-phone i{position:absolute;border-radius:50%}
.et-phone i:nth-child(1){width:120px;height:120px;background:#2548D7;left:-30px;top:40px}
.et-phone i:nth-child(2){width:80px;height:80px;background:#DCF473;right:-14px;top:150px}
.et-phone span{position:relative;background:#F8F7F2;padding:4px 8px;border-radius:8px}
.et-shots{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:18px}
.et-shots p{font-size:15px;text-align:center}
.et-price{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:0;border:2px solid #432731;border-radius:24px;overflow:hidden;background:#fff}
.et-price>div{padding:30px 26px;border-right:2px solid #432731}.et-price>div:last-child{border-right:0}
.et-price .on{background:#DCF473}
.et-price b{display:block;font-family:"Instrument Serif",serif;font-style:italic;font-size:58px;line-height:1;font-weight:400;margin:6px 0 10px}
.et-price small{font-size:12px;font-weight:800;letter-spacing:.1em;text-transform:uppercase}
.et-price p{font-size:16px}
.et-price .later{opacity:.75}
.et-steps{list-style:none;margin:0;padding:0;display:grid;gap:14px;counter-reset:s}
.et-steps li{counter-increment:s;display:grid;grid-template-columns:64px 1fr;gap:16px;align-items:start;padding:20px;background:#fff;border:2px solid #432731;border-radius:20px}
.et-steps li:before{content:counter(s);font-family:"Instrument Serif",serif;font-style:italic;font-size:48px;line-height:1}
.et-steps b{display:block;font-size:18px}.et-steps span{font-size:16px;line-height:1.55}
.et details{border-bottom:2px solid #432731;padding:18px 0}.et summary{font-weight:800;font-size:18px;cursor:pointer}.et details p{margin:10px 0 0;font-size:17px}
.et-form{display:flex;gap:10px;flex-wrap:wrap;margin-top:14px}
.et-form input[type=email]{flex:1 1 240px;min-height:54px;border:2px solid #432731;border-radius:999px;padding:0 20px;font:600 16px Manrope,sans-serif;color:#432731;background:#fff}
dialog.et-modal{border:2px solid #432731;border-radius:24px;padding:32px;max-width:460px;width:calc(100% - 32px);background:#F8F7F2;color:#432731}
dialog.et-modal::backdrop{background:rgba(67,39,49,.55)}
.et-x{position:absolute;right:14px;top:10px;background:none;border:0;font-size:28px;cursor:pointer;color:#432731;min-width:44px;min-height:44px}
.et-note{margin-top:8px;font-weight:700}
.et-quiz{border:2px dashed #432731;border-radius:22px;padding:22px;margin-top:20px;background:rgba(255,255,255,.6)}
@media(max-width:820px){.et section{padding:56px 6%}.et-hero,.et-two,.et-three,.et-shots,.et-price{grid-template-columns:1fr}.et-price>div{border-right:0;border-bottom:2px solid #432731}.et-price>div:last-child{border-bottom:0}.et-shots{gap:28px}}
'''

def wrap(body, js=''):
    return f'<div class="et"><p class="et-test" role="note">Test page. Not linked from the site, hidden from search engines, and nothing is sent or collected.</p>{body}</div><style>{CSS}</style>' + (f'<script>{js}</script>' if js else '')

def phone(label):
    return f'<div><div class="et-phone" role="img" aria-label="Screenshot placeholder: {e(label)}"><i></i><i></i><span>{e(label)}</span></div><p>{e(label)}</p></div>'

FAQ = [
 ("How much does it cost?", "$19 during the beta, instead of $39. There is no subscription."),
 ("Can I try it before I pay?", "Yes. Set up your hair profile and log your last wash day first. You only pay when you want to keep your diary."),
 ("What do I get if I buy during the beta?", "The full web app today, and the iOS app free when it launches."),
 ("Who is it for?", "Anyone who wants to stop guessing: people growing out their hair, protecting length, testing products, or learning what their routine actually does."),
 ("Is it a lot of work?", "No. A wash day entry takes a minute or two, and a monthly photo takes about the same."),
 ("What are the insights?", "They are built from your own logs, not guesses and not AI. They show which products and routines show up on your best hair days, and how your length changes over time."),
 ("Does it work on my phone?", "Yes. It runs in any browser, and you can add it to your phone's home screen."),
 ("Are my entries private?", "Your diary is yours. You can mark entries private, and you choose what to share, like your hair profile card."),
]

def jara_page():
    cta = u(JARA + '/try', 'landing_test', 'jara_beta', 'hero')
    free = u(JARA + '/free-hair-tracker', 'landing_test', 'jara_freebie', 'free_section')
    feats = [
     ('Wash day journal', 'Every wash day saved with the products you used and a photo, searchable any time.'),
     ('Best combos', 'See which products and routines go with your best hair days.'),
     ('Length and trim tracker', 'Track length checks and trims so you know what you actually retained.'),
     ('Goal projection', 'See where your length goal lands, based on your own last 90 days of checks.'),
     ('Progress photos', 'Monthly photos side by side, so you can see what memory misses.'),
     ('Product stash', 'What you own, what you rated, and what you would buy again.'),
    ]
    fcards = ''.join(f'<div class="et-card"><h3>{e(a)}</h3><p>{e(b)}</p></div>' for a, b in feats)
    faq = ''.join(f'<details><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in FAQ)
    body = f'''
<section class="et-paper"><div class="et-in et-hero"><div>
<span class="eyebrow">JARA hair journal</span>
<h1>Your hair's complete record: wash days, products, and growth in one place.</h1>
<p>Stop guessing about your hair growth. Start tracking your journey.</p>
<a class="et-btn" href="{cta}">Try JARA</a>
<p class="et-micro">$19 right now instead of $39. Beta buyers get the iOS app free.</p>
<p class="et-micro"><a class="et-link" href="{cta}">Try it free first</a>: set up your hair profile and log your last wash day.</p>
</div><img src="../../assets/img/jara-promo.jpg" alt="The JARA app showing a hair journal entry." width="1000" height="1000"></div></section>

<section class="et-ink" id="problem"><div class="et-in et-two"><div><span class="eyebrow">The problem</span>
<h2>Most of us are growing our hair on memory.</h2></div><div>
<p>You switch a gel, try a new mask, trim a little, and a few months later you cannot say what helped.</p>
<p>An occasional photo in your camera roll is not a record. Without one place for wash days, products, and monthly photos, every change is a guess.</p></div></div></section>

<section class="et-paper" id="solution"><div class="et-in"><span class="eyebrow">The solution</span>
<h2>One diary that remembers for you.</h2>
<p style="max-width:34em">JARA fits the routine you already have. After a wash day, add what you used and a photo. Once a month, add a progress photo. JARA lines it all up so you can see what is working.</p></div></section>

<section class="et-mist" id="walkthrough"><div class="et-in"><span class="eyebrow">See the app</span><h2>A quick look inside.</h2>
<div class="et-shots">{phone('Wash day entry with photo')}{phone('Insights: length grown and retained')}{phone('Length goal chart with trim marker')}{phone('My Week: last wash day and next care')}</div>
<p class="et-micro">Sample data. Real screenshots go in these frames (see the notes sent with this page).</p></div></section>

<section class="et-paper" id="features"><div class="et-in"><span class="eyebrow">What you can track</span><h2>Built for how coily hair really works.</h2>
<div class="et-three">{fcards}</div></div></section>

<section class="et-cobalt" id="journey"><div class="et-in"><span class="eyebrow">An example journey (sample data)</span><h2>What three months can show.</h2>
<ol class="et-steps" style="color:#432731">
<li><div><b>Week 1: start your record</b><span>Set up your hair profile and log a wash day with the products you used.</span></div></li>
<li><div><b>Day 30: your first side-by-side</b><span>Add a monthly photo and compare it with day one.</span></div></li>
<li><div><b>Day 90: see what held up</b><span>Your length checks give you a goal projection, and your best combos show which routines you keep reaching for.</span></div></li></ol></div></section>

<section class="et-paper" id="beta"><div class="et-in"><span class="eyebrow">The beta offer</span><h2>Join during the beta and pay the lowest price.</h2>
<p style="max-width:36em">Beta buyers get the iOS app when it launches, at no extra cost.</p>
<div class="et-price" role="list">
<div class="on" role="listitem"><small>Available now</small><b>$19</b><h3>Founder's Web Beta</h3><p>Free iOS app upgrade included.</p></div>
<div class="later" role="listitem"><small>Upcoming</small><b>$29</b><h3>Public Web Release</h3><p>After beta closes.</p></div>
<div class="later" role="listitem"><small>Future</small><b>$39</b><h3>Apple iOS App Store</h3><p>Official iOS launch price.</p></div></div>
<p style="margin-top:28px"><a class="et-btn" href="{u(JARA + '/try', 'landing_test', 'jara_beta', 'pricing')}">Try JARA</a></p></div></section>

<section class="et-mist" id="faq"><div class="et-in" style="max-width:760px"><span class="eyebrow">Questions</span><h2>Good to know.</h2>{faq}</div></section>

<section class="et-paper" id="free"><div class="et-in et-two"><div><span class="eyebrow">Not ready for the app?</span><h2>Start with our free printable tracker.</h2>
<p>Print it, fill it in after wash day, and see how it feels. Pop in your email and we'll send it, plus one short note on getting started.</p></div>
<div><form class="et-form" id="free-form" method="post" action=""><input type="hidden" name="source" value="jara_freebie"><label for="fe" style="position:absolute;left:-9999px">Email</label><input id="fe" type="email" name="email" required placeholder="you@email.com" autocomplete="email"><button class="et-btn" type="submit">Send me the tracker</button></form>
<p class="et-note" id="free-msg" role="status"></p><p class="et-micro">Or <a class="et-link" href="{free}">open the printable now</a>.</p></div></div></section>

<section class="et-ink"><div class="et-in" style="text-align:center"><h2>Stop guessing. Start tracking.</h2><p style="max-width:30em;margin:0 auto 24px">Your wash days, products, and growth, in one place.</p>
<a class="et-btn" href="{u(JARA + '/try', 'landing_test', 'jara_beta', 'final')}">Try JARA</a></div></section>

<dialog class="et-modal" id="exit" aria-labelledby="exit-h"><button class="et-x" type="button" aria-label="Close" id="exit-x">&times;</button>
<h2 id="exit-h" style="font-size:38px">Before you go: a free tracker.</h2><p>A printable hair tracker you can start tonight. No app needed.</p>
<form class="et-form" id="exit-form" method="post" action=""><input type="hidden" name="source" value="jara_freebie"><label for="xe" style="position:absolute;left:-9999px">Email</label><input id="xe" type="email" name="email" required placeholder="you@email.com"><button class="et-btn" type="submit">Send it</button></form>
<p class="et-note" id="exit-msg" role="status"></p></dialog>'''
    js = '''
(function(){
 var d=document.getElementById('exit');var shown=false;try{shown=sessionStorage.getItem('et-exit')==='1'}catch(x){}
 function open(){if(shown||!d.showModal)return;shown=true;try{sessionStorage.setItem('et-exit','1')}catch(x){}d.showModal()}
 document.addEventListener('mouseout',function(ev){if(ev.clientY<=0&&!ev.relatedTarget&&window.scrollY>600)open()});
 document.getElementById('exit-x').addEventListener('click',function(){d.close()});
 ['free','exit'].forEach(function(k){var f=document.getElementById(k+'-form');f.addEventListener('submit',function(ev){if(!f.getAttribute('action')){ev.preventDefault();document.getElementById(k+'-msg').textContent='Test mode: nothing was sent. (source=jara_freebie)'}})});
})();'''
    html = B.shell('../../', 'JARA landing test · The Good Coil', 'Test page.', wrap(body, js), 'programs/jara-landing-test/', 'plans')
    B.write('programs/jara-landing-test/index.html', html.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<meta name="robots" content="noindex">', 1))

def home_page():
    q = 'https://thegoodcoil.com/routine-builder'
    body = f'''
<section class="et-paper"><div class="et-in et-hero"><div>
<span class="eyebrow">The Good Coil</span>
<h1>Know your hair. Then keep what works.</h1>
<p>Answer a few questions and get a routine built for your hair, then the plan, products, and tracking to go with it.</p>
<a class="et-btn" href="{q}">Take Your Hair Quiz</a>
<p class="et-micro">Free. About 2 minutes.</p></div>
<img src="../../assets/img/ends.jpg" alt="A woman with long dark curls holds the ends of a curl between her fingers." width="799" height="1344"></div></section>

<section class="et-mist"><div class="et-in et-two"><div><span class="eyebrow">Our approach</span><h2>Good knowledge. Happy hair.</h2></div>
<div><p>We explain what is going on with your hair and why, in plain words. No scores, no verdicts, no one-size-fits-all.</p><p>Quiz, plan, products, record: each step leads to the next.</p></div></div></section>

<section class="et-paper" id="quiz"><div class="et-in"><span class="eyebrow">1 &middot; Discover your hair</span><h2>Start with a quiz.</h2>
<div class="et-three">
<div class="et-card"><h3>Routine Quiz</h3><p>Two minutes. Your hair profile and a routine to try first.</p><p style="margin-top:14px"><a class="et-btn" href="https://thegoodcoil.com/routine-builder">Start the quiz</a></p></div>
<div class="et-card"><h3>Quiz slot 2</h3><p>Name and one-line promise to confirm.</p></div>
<div class="et-card"><h3>Quiz slot 3</h3><p>Name and one-line promise to confirm.</p></div></div></div></section>

<section class="et-ink"><div class="et-in et-two"><div><span class="eyebrow">2 &middot; Your hair routine</span><h2>Your plan lives in the Library.</h2></div>
<div><p>Every quiz result points to a hair plan, with the products and ingredients behind it explained.</p>
<a class="et-btn" href="{u('https://library.thegoodcoil.com', 'home_test', 'library', 'section')}">Open the Library</a></div></div></section>

<section class="et-paper"><div class="et-in et-two"><div><span class="eyebrow">3 &middot; Track your progress</span><h2>Keep the record in JARA.</h2></div>
<div><p>Wash days, products, and monthly photos in one place, so you can see what your routine is really doing.</p>
<a class="et-btn" href="{u(JARA, 'home_test', 'jara_beta', 'section')}">Try JARA</a></div></div></section>

<section class="et-mist"><div class="et-in"><span class="eyebrow">4 &middot; Hair-care resources</span><h2>Guides to go deeper.</h2>
<div class="et-three">
<div class="et-card"><h3>The Wash and Go Guide &middot; $10</h3><p>Wash and gos that last, step by step.</p><p style="margin-top:14px"><a class="et-btn" href="{e(GUIDE)}">Get the guide</a></p></div>
<div class="et-card"><h3>More guides</h3><p>Your other ebooks go here, in the same card.</p></div>
<div class="et-card"><h3>Studio</h3><p>Artwork and wallpapers live in their own Studio page, apart from the hair tools.</p></div></div></div></section>

<section class="et-paper"><div class="et-in"><span class="eyebrow">What people say</span><h2>Real words go here.</h2><p>Only real reviews from real customers, with permission. This slot stays empty until we have them.</p></div></section>

<section class="et-cobalt"><div class="et-in" style="text-align:center"><h2>Stop guessing. Start tracking.</h2><p style="max-width:30em;margin:0 auto 24px">Take the quiz, follow your plan, and keep the proof in JARA.</p><a class="et-btn" href="{u(JARA, 'home_test', 'jara_beta', 'final')}">Try JARA</a></div></section>

<section class="et-paper" id="results"><div class="et-in"><span class="eyebrow">Quiz results page (mock-up)</span><h2>Your hair profile.</h2>
<div class="et-card"><h3>Example: medium-porosity, tight coils</h3><p>You hold moisture best with layered leave-ins, and heavy products can weigh your coils down.</p></div>
<div class="et-quiz"><h3>Unlock your full routine</h3><p>Pop in your email and we'll send your routine and a link to your matching hair plan.</p>
<form class="et-form" method="post" action="" onsubmit="event.preventDefault();this.nextElementSibling.textContent='Test mode: nothing was sent.'"><input type="hidden" name="source" value="quiz_result"><label for="qe" style="position:absolute;left:-9999px">Email</label><input id="qe" type="email" required placeholder="you@email.com"><button class="et-btn" type="submit">Send my routine</button></form><p class="et-note" role="status"></p></div>
<p style="margin:28px 0 12px;font-weight:800">Your next step</p>
<div class="et-two">
<div class="et-card"><h3>Quick win &middot; $10</h3><p>Master Your Styling: The Wash and Go Guide.</p><p style="margin-top:14px"><a class="et-btn" href="{e(GUIDE)}">Get the guide</a></p></div>
<div class="et-card"><h3>Track your results in JARA</h3><p>Log wash days and monthly photos, so you can see what your routine is doing.</p><p style="margin-top:14px"><a class="et-btn" href="{u(JARA + '/try', 'quiz_results', 'jara_beta', 'results')}">Try JARA</a></p></div></div></div></section>'''
    html = B.shell('../../', 'Good Coil homepage test · The Good Coil', 'Test page.', wrap(body), 'programs/goodcoil-home-test/', 'plans')
    B.write('programs/goodcoil-home-test/index.html', html.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<meta name="robots" content="noindex">', 1))

def build():
    jara_page()
    home_page()

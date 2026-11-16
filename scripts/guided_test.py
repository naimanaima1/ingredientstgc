"""TEST: guided colour-block steps + a partial email gate at /programs/guided-test/ (noindex, unlinked).
Content comes from content/guide-winter.json. No email is sent anywhere: set GATE_ACTION to a
provider's form URL (Buttondown, ConvertKit, Mailchimp...) to collect real addresses.
"""
import json, os
import build as B

e = B.e
GATE_ACTION = ''          # empty = test mode, nothing is sent
FREE_STEPS = 2            # how many steps stay open before the gate
TONES = ['cobalt', 'citrus', 'mist', 'ink']

CSS = '''
.gt{background:#F8F7F2;color:#432731}
.gt-test{margin:0;padding:10px 16px;background:#DCF473;color:#432731;font:600 14px/1.4 Manrope,sans-serif;text-align:center}
.gt-hero{padding:56px 20px 40px;max-width:760px;margin:0 auto}
.gt-hero h1{font:italic 400 clamp(38px,8vw,64px)/1.05 "Instrument Serif",serif;margin:8px 0 14px}
.gt-hero p{font-size:18px;line-height:1.6;max-width:34em}
.gt-steps{list-style:none;margin:0;padding:0}
.gt-step{min-height:78vh;display:flex;align-items:center;padding:56px 20px;transition:background .4s,color .4s;background:#F8F7F2;color:#432731}
.gt-in{max-width:640px;margin:0 auto;width:100%}
.gt-n{font:italic 400 clamp(64px,16vw,120px)/1 "Instrument Serif",serif;opacity:.5}
.gt-step h2{font:700 clamp(26px,5vw,36px)/1.15 Manrope,sans-serif;margin:6px 0 14px}
.gt-step p{font-size:18px;line-height:1.65;margin:0 0 12px}
.gt-step .gt-note{font-size:16px;opacity:.85}
.gt-step.is-on[data-tone=cobalt]{background:#2548D7;color:#F8F7F2}
.gt-step.is-on[data-tone=citrus]{background:#DCF473;color:#432731}
.gt-step.is-on[data-tone=mist]{background:#DCE6F0;color:#432731}
.gt-step.is-on[data-tone=ink]{background:#432731;color:#F8F7F2}
.gt-step a{color:inherit;text-underline-offset:3px}
.gt-step a:focus-visible,.gt-gate button:focus-visible,.gt-dash button:focus-visible{outline:3px solid #DCF473;outline-offset:3px;box-shadow:0 0 0 6px #432731}
.gt-lock{position:relative}
.gt-locked .gt-step{filter:blur(7px);pointer-events:none;user-select:none;max-height:44vh;overflow:hidden;min-height:0}
.gt-gate{position:relative;z-index:2;max-width:560px;margin:-34vh auto 0;padding:28px 24px;background:#F8F7F2;border:2px solid #432731;border-radius:20px;box-shadow:0 18px 40px rgba(67,39,49,.18)}
.gt-gate h2{font:italic 400 32px/1.1 "Instrument Serif",serif;margin:0 0 8px}
.gt-gate p{font-size:17px;line-height:1.55;margin:0 0 14px}
.gt-gate form{display:flex;gap:8px;flex-wrap:wrap}
.gt-gate input[type=email]{flex:1 1 220px;min-height:48px;padding:0 14px;border:2px solid #432731;border-radius:12px;background:#fff;font:600 16px Manrope,sans-serif;color:#432731}
.gt-gate button{min-height:48px;padding:0 20px;border:0;border-radius:12px;background:#2548D7;color:#F8F7F2;font:700 16px Manrope,sans-serif;cursor:pointer}
.gt-fine{font-size:14px!important;opacity:.8;margin:10px 0 0!important}
.gt-msg{font-weight:700;margin-top:10px}
.gt-unlocked .gt-gate{display:none}
.gt-unlocked .gt-locked .gt-step{filter:none;pointer-events:auto;user-select:auto;max-height:none;min-height:78vh}
.gt-dash{max-width:640px;margin:48px auto;padding:20px;border:1px dashed #432731;border-radius:16px;font-size:16px;line-height:1.6}
.gt-dash b{font-weight:700}
.gt-dash table{border-collapse:collapse;margin-top:8px}.gt-dash td,.gt-dash th{padding:4px 12px 4px 0;text-align:left}
@media(prefers-reduced-motion:reduce){.gt-step{transition:none}}
'''

JS = '''
(function(){
  var KEY='tgc-gate-test';var root=document.querySelector('.gt');
  function store(){try{return JSON.parse(localStorage.getItem(KEY)||'{}')}catch(x){return {}}}
  function save(o){try{localStorage.setItem(KEY,JSON.stringify(o))}catch(x){}}
  function show(){var s=store();var d=document.getElementById('gt-count');if(d)d.textContent=s.unlocked?'1 unlock on this device ('+(s.email||'')+', '+(s.at||'')+')':'0 unlocks on this device yet';}
  function open(){root.classList.add('gt-unlocked');var l=document.querySelector('.gt-locked');if(l){l.removeAttribute('inert');l.removeAttribute('aria-hidden')}}
  var st=store();if(st.unlocked)open();show();
  var form=document.getElementById('gt-form');
  if(form)form.addEventListener('submit',function(ev){
    var action=form.getAttribute('action');var email=form.email.value.trim();
    if(!action){ev.preventDefault();}
    save({unlocked:true,email:email,at:new Date().toISOString().slice(0,16).replace('T',' ')});
    open();show();
    var m=document.getElementById('gt-msg');if(m)m.textContent=action?'Thanks! Unlocked.':'Unlocked. (Test mode: nothing was sent.)';
  });
  var reset=document.getElementById('gt-reset');
  if(reset)reset.addEventListener('click',function(){try{localStorage.removeItem(KEY)}catch(x){}location.reload()});
  var steps=[].slice.call(document.querySelectorAll('.gt-step'));
  if('IntersectionObserver' in window){
    var io=new IntersectionObserver(function(es){es.forEach(function(en){en.target.classList.toggle('is-on',en.isIntersecting)})},{rootMargin:'-40% 0px -40% 0px'});
    steps.forEach(function(s){io.observe(s)});
  }else{steps.forEach(function(s){s.classList.add('is-on')})}
})();
'''

def step(i, s):
    t, text, ex = s[0], s[1], (s[2] if len(s) > 2 else {})
    note = f'<p class="gt-note">{e(ex["note"])}</p>' if ex.get('note') else ''
    link = f'<p><a href="../../{ex["link"][1]}">{e(ex["link"][0])}</a></p>' if ex.get('link') else ''
    tone = TONES[i % len(TONES)]
    return f'<li class="gt-step" data-tone="{tone}"><div class="gt-in"><div class="gt-n" aria-hidden="true">{i + 1}</div><h2>{e(t)}</h2><p>{e(text)}</p>{note}{link}</div></li>'

def build():
    path = os.path.join(B.ROOT, 'content', 'guide-winter.json')
    if not os.path.exists(path):
        return
    d = json.load(open(path, encoding='utf-8'))
    steps = d['routine']['washes'][0]['steps']
    free = ''.join(step(i, s) for i, s in enumerate(steps[:FREE_STEPS]))
    rest = ''.join(step(i + FREE_STEPS, s) for i, s in enumerate(steps[FREE_STEPS:]))
    gate = f'''<div class="gt-gate" id="gate"><h2>Want the last {len(steps) - FREE_STEPS} locks?</h2>
<p>Pop in your email and they unlock right here. We'll send the Winter arc lock-in checklist too, and that's it.</p>
<form id="gt-form" method="post" action="{e(GATE_ACTION)}"><label class="sr-only" for="gt-email" style="position:absolute;left:-9999px">Email</label><input id="gt-email" name="email" type="email" required autocomplete="email" placeholder="you@email.com"><button type="submit">Unlock the rest</button></form>
<p class="gt-msg" id="gt-msg" role="status"></p>
<p class="gt-fine">No spam, unsubscribe any time.</p></div>'''
    body = f'''<div class="gt"><p class="gt-test" role="note">Test page. Not linked from the site and hidden from search engines. No emails are collected.</p>
<header class="gt-hero"><span class="eyebrow">Test: guided steps + email gate</span><h1>{e(d['name'])}</h1><p>{e(d['intro'])}</p></header>
<ol class="gt-steps">{free}</ol>
<div class="gt-lock"><ol class="gt-steps gt-locked" inert aria-hidden="true">{rest}</ol>{gate}</div>
<section class="gt-dash"><b>Dashboard (test)</b><p id="gt-count"></p><p>This only shows unlocks on this device. To see everyone's emails you need an email provider (see the notes sent with this page). <button type="button" id="gt-reset" style="min-height:40px;padding:0 14px;border:2px solid #432731;border-radius:10px;background:transparent;color:#432731;font:700 14px Manrope,sans-serif;cursor:pointer">Reset my unlock</button></p></section></div>
<style>{CSS}</style><script>{JS}</script>'''
    html = B.shell('../../', 'Guided steps and email gate test · The Good Coil', 'Test page.', body, 'programs/guided-test/', 'plans')
    B.write('programs/guided-test/index.html', html.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<meta name="robots" content="noindex">', 1))

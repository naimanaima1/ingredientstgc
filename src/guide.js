/* Small behaviours for hair-plan pages. Everything works without this file: the
   readiness cards just sit there and the prep stays closed. */
(function () {
  'use strict';

  /* Are you ready? Yep / Not yet on each card, then one clear next step. */
  document.querySelectorAll('.rd').forEach(function (rd) {
    var total = +rd.getAttribute('data-total') || 5;
    var cards = rd.querySelectorAll('.rd-card');
    var out = rd.querySelector('.rd-out');
    var msg = out.querySelector('.rd-msg');
    var go = out.querySelector('.rd-go');
    var prep = document.getElementById('prep');
    var answers = {};

    function update() {
      var n = Object.keys(answers).length;
      var yes = Object.keys(answers).filter(function (k) { return answers[k] === 1; }).length;
      out.hidden = false;
      out.className = 'rd-out';
      go.hidden = false;
      if (n < total) {
        out.className += ' is-wait';
        msg.textContent = out.getAttribute('data-wait').replace('{n}', n).replace('{total}', total);
        go.hidden = true;
        return;
      }
      if (yes === total) {
        out.className += ' is-all';
        msg.textContent = out.getAttribute('data-all');
      } else if (yes === total - 1) {
        out.className += ' is-four';
        msg.textContent = out.getAttribute('data-four');
      } else {
        out.className += ' is-few';
        msg.textContent = out.getAttribute('data-few');
        if (prep) prep.open = true;
        go.hidden = true;
      }
      if (yes === total - 1 && prep) {
        go.hidden = false;
      }
    }

    cards.forEach(function (card, i) {
      card.querySelectorAll('button').forEach(function (b) {
        b.addEventListener('click', function () {
          answers[i] = +b.getAttribute('data-v');
          card.querySelectorAll('button').forEach(function (x) {
            x.setAttribute('aria-pressed', x === b ? 'true' : 'false');
          });
          card.classList.toggle('is-yes', answers[i] === 1);
          card.classList.toggle('is-no', answers[i] === 0);
          update();
          /* on a phone, nudge to the next card so the answers feel like a flow */
          var next = cards[i + 1];
          if (next && window.matchMedia('(max-width: 800px)').matches) {
            setTimeout(function () {
              next.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
            }, 160);
          }
        });
      });
    });
  });

  /* Routine steps light up as you read down them. */
  var steps = document.querySelectorAll('.gd-steps > li');
  if (steps.length && 'IntersectionObserver' in window) {
    document.documentElement.classList.add('has-spy');
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        en.target.classList.toggle('is-on', en.isIntersecting);
      });
    }, { rootMargin: '-38% 0px -42% 0px', threshold: 0 });
    steps.forEach(function (s) { io.observe(s); });
  }

  /* Week-by-week timeline: dots follow the swipe, tapping a dot jumps to that week. */
  document.querySelectorAll('.tl-sec').forEach(function (sec) {
    var list = sec.querySelector('.tl-list');
    var items = sec.querySelectorAll('.tl-item');
    var dots = sec.querySelectorAll('.tl-path button');
    if (!list || !dots.length) return;
    dots.forEach(function (b) {
      b.addEventListener('click', function () {
        var it = items[+b.getAttribute('data-i')];
        if (!it) return;
        if (window.matchMedia('(max-width: 900px)').matches) {
          list.scrollTo({ left: it.offsetLeft - list.offsetLeft, behavior: 'smooth' });
        } else {
          it.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      });
    });
    if ('IntersectionObserver' in window) {
      var io2 = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (!en.isIntersecting) return;
          var i = Array.prototype.indexOf.call(items, en.target);
          dots.forEach(function (b, k) {
            if (k === i) b.setAttribute('aria-current', 'true'); else b.removeAttribute('aria-current');
          });
        });
      }, { root: null, threshold: 0.6 });
      items.forEach(function (it) { io2.observe(it); });
    }
  });

  /* Guided plans: each colour block lights up as it reaches the middle of the screen. */
  var gz = document.querySelectorAll('.gz-step');
  if (gz.length && 'IntersectionObserver' in window) {
    document.documentElement.classList.add('gz-js');
    var gio = new IntersectionObserver(function (es) {
      es.forEach(function (en) { en.target.classList.toggle('is-on', en.isIntersecting); });
    }, { rootMargin: '-35% 0px -35% 0px' });
    gz.forEach(function (x) { gio.observe(x); });
  }
  /* Chapter openers: slow parallax where CSS scroll timelines aren't supported (Safari, Firefox). */
  var opens = document.querySelectorAll('.gz-open-img img');
  if (opens.length && !(window.CSS && CSS.supports && CSS.supports('animation-timeline: view()')) &&
      !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    var ticking = false;
    var move = function () {
      ticking = false;
      var vh = window.innerHeight;
      opens.forEach(function (img) {
        var box = img.parentNode.getBoundingClientRect();
        if (box.bottom < 0 || box.top > vh) return;
        var t = (vh - box.top) / (vh + box.height); /* 0 entering, 1 leaving */
        img.style.transform = 'translateY(' + (-18 + 18 * Math.min(1, Math.max(0, t))) + '%)';
      });
    };
    window.addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(move); } }, { passive: true });
    move();
  }
  /* Count which lessons people open (Google Analytics + PostHog via tgcTrack). */
  document.querySelectorAll('details[data-track]').forEach(function (d) {
    d.addEventListener('toggle', function () {
      if (d.open && window.tgcTrack) tgcTrack('plan_fold_open', { plan: location.pathname, habit: +d.getAttribute('data-habit'), fold: d.getAttribute('data-track') });
    });
  });
  /* Free guide form: posts to JARA's sign-up endpoint, which adds the address to the JARA list and emails the PDF. */
  document.querySelectorAll('form.lead-form').forEach(function (f) {
    var msg = f.querySelector('.lead-msg'), ok = f.querySelector('.lead-ok'), btn = f.querySelector('button');
    f.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var email = f.email.value.trim();
      if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) { msg.hidden = false; msg.textContent = 'Enter a valid email.'; f.email.focus(); return; }
      btn.disabled = true; msg.hidden = false; msg.textContent = 'Sending…';
      fetch(f.getAttribute('data-endpoint'), {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email, printable: f.getAttribute('data-printable'), website: f.website.value })
      }).then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
        .then(function (res) {
          if (!res.ok) throw new Error((res.j && res.j.error) || 'Something went wrong.');
          msg.hidden = true; ok.hidden = false; f.querySelector('.lead-row').hidden = true; f.querySelector('label').hidden = true;
          if (window.tgcTrack) tgcTrack('generate_lead', { source: 'library-' + f.getAttribute('data-slug') });
        })
        .catch(function (err) {
          btn.disabled = false;
          var known = err && err.message && /valid email|Try again/.test(err.message);
          if (known) { msg.textContent = err.message; return; }
          /* couldn't reach JARA from here: send them to the same form on itsjara.com */
          msg.innerHTML = '';
          var a = document.createElement('a'); a.href = f.getAttribute('data-fallback'); a.textContent = 'Get it on itsjara.com \u2192';
          msg.appendChild(document.createTextNode("Couldn't send it from here. ")); msg.appendChild(a);
        });
    });
  });
})();

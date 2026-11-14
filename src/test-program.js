// Test program page: week planner, protein track, ticks saved on this device.
(function () {
  const sec = document.getElementById('weeks'); if (!sec) return;
  document.documentElement.classList.add('tp-js');
  const KEY = 'tgc-plan-' + location.pathname;
  let state = {}; try { state = JSON.parse(localStorage.getItem(KEY) || '{}'); } catch (e) {}
  const save = () => { try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {} };
  const rail = [...sec.querySelectorAll('.tp-rail a')], panels = [...sec.querySelectorAll('.tp-week')];
  function show(n, focus) {
    rail.forEach(a => a.dataset.w == n ? a.setAttribute('aria-current', 'true') : a.removeAttribute('aria-current'));
    panels.forEach(p => p.classList.toggle('on', p.id === 'w' + n));
    state.week = n; save();
    if (focus) rail.find(a => a.dataset.w == n).focus();
  }
  rail.forEach(a => a.addEventListener('click', ev => { ev.preventDefault(); show(+a.dataset.w); }));
  sec.querySelector('.tp-rail').addEventListener('keydown', ev => {
    const d = ev.key === 'ArrowRight' ? 1 : ev.key === 'ArrowLeft' ? -1 : 0; if (!d) return;
    ev.preventDefault(); show(Math.min(panels.length, Math.max(1, (state.week || 1) + d)), true);
  });
  function done() {
    panels.forEach((p, i) => { const b = [...p.querySelectorAll('input')]; rail[i].classList.toggle('done', b.length > 0 && b.every(x => x.checked)); });
  }
  sec.querySelectorAll('.tp-checks input').forEach(b => {
    b.checked = !!(state.ticks || {})[b.dataset.k];
    b.addEventListener('change', () => { (state.ticks = state.ticks || {})[b.dataset.k] = b.checked; save(); done(); });
  });
  sec.querySelectorAll('input[name=track]').forEach(rd => {
    if (rd.value === (state.track || 'none')) rd.checked = true;
    rd.addEventListener('change', () => { sec.dataset.track = state.track = rd.value; save(); });
  });
  sec.dataset.track = state.track || 'none';
  const h = (location.hash.match(/^#w(\d)$/) || [])[1];
  show(+h || state.week || 1); done();
})();

/* Product pages: graphics enter with the scroll, as on the home page journey.
   Scroll position sets the progress, so a graphic builds as it comes into view and reverses on the way back.
   Frames (.shot, .snip, .map, .phones) rise, grow and sharpen. Phones and raw-description rows arrive one after another. */
(() => {
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const cl = x => Math.max(0, Math.min(1, x));
  const sm = (a, b, x) => { const t = cl((x - a) / (b - a)); return t * t * (3 - 2 * t); };
  const out = t => 1 - Math.pow(1 - t, 3);
  const items = [];
  const add = (el, kind, extra) => { el.classList.add('sx'); items.push(Object.assign({ el, kind, p: -1 }, extra)); };
  document.querySelectorAll('main .shot, main .snip, main .map').forEach(el => add(el, 'frame'));
  document.querySelectorAll('main .phones').forEach(box => {
    const ph = [...box.querySelectorAll('.phone')];
    ph.forEach((el, i) => add(el, 'phone', { box, ord: ph.length > 1 ? i / (ph.length - 1) : 0 }));
  });
  document.querySelectorAll('main .rawrow').forEach((el, i) => add(el, 'row', { dir: i % 2 ? 1 : -1 }));
  if (!items.length) return;
  document.documentElement.classList.add('sx-on');

  // progress of an element: 0 when its top edge meets the bottom of the window, 1 after it has moved up by `span` window heights
  const prog = (r, vh, span) => cl((vh - r.top) / (vh * span));
  let queued = false;
  const run = () => {
    queued = false;
    const vh = innerHeight, small = innerWidth < 760, k = small ? 0.5 : 1, writes = [];
    for (const it of items) {
      let p;
      if (it.kind === 'phone') p = cl((prog(it.box.getBoundingClientRect(), vh, 0.7) - it.ord * 0.45) / 0.55);
      else p = prog(it.el.getBoundingClientRect(), vh, it.kind === 'row' ? 0.3 : 0.5);
      p = Math.round(p * 500) / 500;
      if (p !== it.p) { it.p = p; writes.push(it); }
    }
    for (const it of writes) {
      const p = it.p, e = out(p), s = it.el.style;
      if (p >= 1) { s.opacity = ''; s.transform = ''; s.filter = ''; it.el.classList.add('sx-done'); continue; }
      it.el.classList.remove('sx-done');
      s.opacity = sm(0, 0.4, p).toFixed(3);
      if (it.kind === 'frame') { s.transform = `translate3d(0,${(90 * k * (1 - e)).toFixed(1)}px,0) scale(${(0.88 + 0.12 * e).toFixed(3)})`; s.filter = e < 0.97 ? `blur(${(8 * (1 - e)).toFixed(1)}px)` : ''; }
      else if (it.kind === 'phone') s.transform = `translate3d(0,${(110 * k * (1 - e)).toFixed(1)}px,0) scale(${(0.8 + 0.2 * e).toFixed(3)})`;
      else s.transform = `translate3d(${(it.dir * 70 * k * (1 - e)).toFixed(1)}px,0,0) scale(${(0.94 + 0.06 * e).toFixed(3)})`;
    }
  };
  const ask = () => { if (!queued) { queued = true; requestAnimationFrame(run); } };
  addEventListener('scroll', ask, { passive: true });
  addEventListener('resize', ask);
  addEventListener('load', ask);
  run();
})();

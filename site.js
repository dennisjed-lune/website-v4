(() => {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const hasIO = 'IntersectionObserver' in window;
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* storage is optional */ } }
  };

  // ---- Mobile menu ----
  const menuBtn = document.querySelector('.menu-btn');
  const nav = document.querySelector('.site-nav');
  if (menuBtn && nav) {
    const setOpen = open => {
      nav.classList.toggle('is-open', open);
      menuBtn.setAttribute('aria-expanded', String(open));
      if (open) { const first = nav.querySelector('a'); if (first) first.focus(); }
    };
    menuBtn.addEventListener('click', () => setOpen(!nav.classList.contains('is-open')));
    nav.addEventListener('click', e => { if (e.target.closest('a')) setOpen(false); });
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape' && nav.classList.contains('is-open')) { setOpen(false); menuBtn.focus(); }
    });
  }

  // ---- Sample transactions ----
  // Raw lines use the short, cut and coded forms that card networks and acquirers send.
  const TX = [
    { raw: 'POS PUR 448812 LVL SHS DXB MALL 00AE', merchant: 'Level Shoes', logo: 'levelshoes.png', category: 'Shopping', sub: 'Clothing', amount: 'AED 1,032.00', offer: '10% cashback' },
    { raw: 'UBR* PENDING 4029357733 NLD', merchant: 'Uber', logo: 'uber.png', category: 'Transportation', sub: 'Ride hailing', amount: 'GBP 18.40' },
    { raw: 'ALSHAYA SBX 0921 NEWYORK 100NY', merchant: 'Starbucks', logo: 'starbucks.png', category: 'Dining', sub: 'Cafés', amount: 'USD 6.75' },
    { raw: 'NF* 8665797172 LOS GATOS 00012', merchant: 'Netflix', logo: 'netflix.png', category: 'Entertainment', sub: 'Streaming', rec: true, amount: 'USD 15.49' },
    { raw: 'MAF HYPMKT MOE-0042 DXB ARE', merchant: 'Carrefour', logo: 'carrefour.png', category: 'Groceries', sub: 'Supermarkets', amount: 'AED 412.30' },
    { raw: 'EXP*72619940183 ECOM WA 840', merchant: 'Expedia', logo: 'expedia.png', category: 'Travel', sub: 'Travel booking', amount: 'USD 642.18', offer: '8% cashback' },
    { raw: 'AMZ*MKTPL SA 2K4LP0 RUH 682', merchant: 'Amazon', logo: 'amazon.png', category: 'Shopping', sub: 'Online marketplaces', amount: 'SAR 249.00' },
    { raw: 'FZ 1418829 T2 DXB AE 784', merchant: 'flydubai', logo: 'flydubai.png', category: 'Travel', sub: 'Airlines', amount: 'AED 1,890.00' },
    { raw: 'RBK 3307 MIRDIF CC TID88120', merchant: 'Reebok', logo: 'reebok.png', category: 'Shopping', sub: 'Sportswear', amount: 'AED 329.00', offer: '15% cashback' },
    { raw: 'SPTF AB P2A91F STO 752', merchant: 'Spotify', logo: 'spotify.png', category: 'Entertainment', sub: 'Music', rec: true, amount: 'EUR 10.99' },
    { raw: 'ALSHAYA BBW 0118 DFC MID4471', merchant: 'Bath & Body Works', logo: 'bbw.png', category: 'Shopping', sub: 'Beauty', amount: 'AED 215.00', offer: '15% cashback' },
    { raw: 'ARLO*ESIM 6531 SGP 702', merchant: 'Airalo', logo: 'airalo.png', category: 'Travel', sub: 'Mobile services', amount: 'USD 9.00' },
    { raw: 'FTLKR #2291 PARIS 08 FR 250', merchant: 'Foot Locker', logo: 'footlocker.png', category: 'Shopping', sub: 'Sportswear', amount: 'EUR 129.99' }
  ];
  const OFFERS = TX.filter(t => t.offer);

  // ---- Text effects ----
  const typeText = (el, text, ms) => {
    clearInterval(el._t);
    let n = 0;
    el.textContent = '';
    el._t = setInterval(() => { n += 2; el.textContent = text.slice(0, n); if (n >= text.length) clearInterval(el._t); }, ms / (text.length / 2));
  };
  const GLYPHS = 'ABCDEFGHKLMNPRSTUVXZ0123456789*#';
  const scramble = (el, text) => {
    clearInterval(el._t);
    let f = 0;
    el._t = setInterval(() => {
      f += 1;
      el.textContent = [...text].map((c, i) => (i < f / 2 || c === ' ') ? c : GLYPHS[Math.floor(Math.random() * GLYPHS.length)]).join('');
      if (f / 2 >= text.length) clearInterval(el._t);
    }, 32);
  };

  // ---- Demo hooks: change the content of a demo at each loop ----
  const HOOKS = {};
  let feedCount = 1482113;
  const trailChip = t => { const s = document.createElement('span'); const im = new Image(); im.src = 'img/logos/' + t.logo; im.alt = ''; s.append(im, t.merchant); return s; };

  // One transaction: raw description, merchant, logo, category, amount, offer.
  HOOKS.tx = (el, loop, step) => {
    const list = el.dataset.only === 'offer' ? OFFERS : TX;
    const t = list[loop % list.length];
    const all = k => el.querySelectorAll(`[data-f="${k}"]`);
    if (step === 0) {
      const trail = el.querySelector('.trail');
      if (trail) {
        if (!trail.children.length) [9, 7, 6, 4, 3, 2].forEach(i => trail.append(trailChip(TX[i])));
        if (loop > 0) { trail.prepend(trailChip(list[(loop - 1) % list.length])); if (trail.children.length > 9) trail.lastChild.remove(); }
      }
      all('raw').forEach(r => (r.hasAttribute('data-type') && !reduce) ? typeText(r, t.raw, 800) : (r.textContent = t.raw));
      all('logo').forEach(i => { i.src = 'img/logos/' + t.logo; });
      all('merchant').forEach(m => { clearInterval(m._t); m.textContent = t.merchant; });
      all('cat').forEach(c => { c.textContent = `${t.category} › ${t.sub}`; });
      all('rec').forEach(c => { c.textContent = t.rec ? 'Yes' : 'No'; });
      all('amt').forEach(c => { c.textContent = t.amount; });
      all('offer').forEach(c => { c.textContent = t.offer || ''; });
      el.classList.toggle('no-offer', !t.offer);
      const cnt = el.querySelector('[data-feedcount]');
      if (cnt) { feedCount += 37 + Math.floor(Math.random() * 60); cnt.textContent = feedCount.toLocaleString('en-US'); }
    }
    if (step === 2 && !reduce) scramble(all('merchant')[0], t.merchant);
  };

  // Analytics dashboard: the totals for two scopes.
  const SCOPES = [
    { period: 'Last 6 months', country: 'All countries', k: [[412880, 0, '', ''], [18.6, 1, '', 'M'], [3.94, 2, 'AED ', 'B'], [9543, 0, 'AED ', '']],
      rows: [['Shopping', 'AED 698M', 100], ['Groceries', 'AED 695M', 99], ['Dining', 'AED 511M', 73], ['Travel', 'AED 447M', 64], ['Household', 'AED 399M', 57], ['Transportation', 'AED 252M', 36]],
      note: 'Shopping and Groceries each take AED 0.7B of card spend in six months.' },
    { period: 'Last 30 days', country: 'United Arab Emirates', k: [[268140, 0, '', ''], [2.4, 1, '', 'M'], [512, 0, 'AED ', 'M'], [1909, 0, 'AED ', '']],
      rows: [['Groceries', 'AED 96M', 100], ['Shopping', 'AED 88M', 92], ['Dining', 'AED 71M', 74], ['Travel', 'AED 52M', 54], ['Household', 'AED 49M', 51], ['Transportation', 'AED 37M', 39]],
      note: 'In the United Arab Emirates, Groceries leads card spend in the last 30 days.' }
  ];
  HOOKS.dash = (el, loop, step) => {
    if (step !== 0) return;
    const s = SCOPES[loop % SCOPES.length];
    ['period', 'country'].forEach(k => {
      const c = el.querySelector(`[data-f="${k}"]`);
      if (c.textContent === s[k]) return;
      c.textContent = s[k];
      c.classList.remove('flash'); void c.offsetWidth; c.classList.add('flash');
    });
    el.querySelectorAll('[data-count]').forEach((c, i) => { const [v, dec, pre, suf] = s.k[i]; Object.assign(c.dataset, { count: v, dec, pre, suf }); });
    el.querySelectorAll('.ui__tr:not(.ui__tr--head)').forEach((r, i) => {
      const [name, value, w] = s.rows[i];
      r.querySelector('.ui__td').textContent = name;
      r.querySelector('i').style.setProperty('--w', w + '%');
      r.querySelector('em').textContent = value;
    });
    el.querySelector('[data-f="note"]').textContent = s.note;
  };

  // ---- Demo engine: adds s1, s2, ... to a .dv element, one class for each duration in data-steps ----
  const fmt = (v, dec) => v.toLocaleString('en-US', { minimumFractionDigits: dec, maximumFractionDigits: dec });
  const setCount = (el, v) => { el.textContent = (el.dataset.pre || '') + fmt(v, +el.dataset.dec || 0) + (el.dataset.suf || ''); };
  const countUp = el => {
    const to = +el.dataset.count, from = +(el.dataset.from || 0), t0 = performance.now();
    const frame = now => {
      const p = Math.min(1, (now - t0) / 1100);
      setCount(el, from + (to - from) * (1 - Math.pow(1 - p, 3)));
      if (p < 1) el._raf = requestAnimationFrame(frame);
    };
    cancelAnimationFrame(el._raf);
    el._raf = requestAnimationFrame(frame);
  };
  const dvs = [...document.querySelectorAll('.dv')].map(el => {
    const steps = el.dataset.steps.split(',').map(Number);
    const hook = HOOKS[el.dataset.hook];
    const counts = [...el.querySelectorAll('[data-count]')];
    const d = { el, i: 0, loop: 0, timer: null, on: false };
    const go = () => {
      if (d.i === 0) {
        steps.forEach((_, k) => el.classList.remove('s' + k));
        if (hook) hook(el, d.loop, 0);
        counts.forEach(c => { cancelAnimationFrame(c._raf); setCount(c, +(c.dataset.from || 0)); });
      } else {
        el.classList.add('s' + d.i);
        if (hook) hook(el, d.loop, d.i);
        counts.forEach(c => { if (+c.dataset.at === d.i) countUp(c); });
      }
      d.timer = setTimeout(() => { d.i = (d.i + 1) % steps.length; if (d.i === 0) d.loop += 1; go(); }, steps[d.i]);
    };
    d.start = () => { if (d.on) return; d.on = true; d.i = 0; go(); };
    d.stop = () => { d.on = false; clearTimeout(d.timer); };
    d.final = () => { if (hook) hook(el, 0, 0); steps.forEach((_, k) => { if (k) el.classList.add('s' + k); }); counts.forEach(c => setCount(c, +c.dataset.count)); };
    d.still = el.hasAttribute('data-static');
    return d;
  });
  const seen = new Set();
  let paused = false;
  const sync = () => { if (!reduce && hasIO) dvs.forEach(d => { if (!d.still) ((!paused && seen.has(d.el) && d.el.offsetParent !== null) ? d.start() : d.stop()); }); };
  dvs.forEach(d => { if (d.still) d.final(); });
  if (reduce || !hasIO) dvs.forEach(d => { if (!d.still) d.final(); });
  else {
    const io = new IntersectionObserver(es => { es.forEach(en => en.isIntersecting ? seen.add(en.target) : seen.delete(en.target)); sync(); }, { threshold: 0.2 });
    dvs.forEach(d => { if (!d.still) io.observe(d.el); });
  }

  // ---- Pause control: one button next to each looping animation stops all of them ----
  if (!reduce && hasIO) {
    // One control for the page. It stops and starts all looping animations.
    const b = document.createElement('button');
    b.type = 'button'; b.className = 'motion-btn';
    const label = () => { const t = paused ? 'Play all animations' : 'Pause all animations'; b.setAttribute('aria-label', t); b.title = t; b.setAttribute('aria-pressed', String(paused)); };
    b.addEventListener('click', () => { paused = !paused; document.documentElement.classList.toggle('paused', paused); label(); sync(); });
    if (dvs.some(d => !d.still)) { label(); (document.querySelector('main') || document.body).prepend(b); }
    // ?still starts with all animations paused, for captures and screenshots.
    if (/[?&]still\b/.test(location.search)) b.click();
  }

  // ---- Reveal on scroll ----
  const RV = '.sec .head, .sec .card, .points > div, .party > div, .stats > div, .chapter__copy, .feature__copy, .phones .phone, .quote, .case, .cta, .rawrow, .map, .map__base, .band, .flow, .badges, .shot';
  if (hasIO && !reduce) {
    const io = new IntersectionObserver(es => es.forEach(en => { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } }), { rootMargin: '0px 0px -6% 0px', threshold: 0.06 });
    document.querySelectorAll(RV).forEach(el => {
      const sibs = [...el.parentElement.children].filter(c => c.matches(RV));
      el.style.setProperty('--d', Math.min(sibs.indexOf(el), 5) * 90 + 'ms');
      el.classList.add('rv');
      io.observe(el);
    });
  }

  // ---- Parallax: small vertical shifts, only on wide screens ----
  const pxEls = [...document.querySelectorAll('[data-parallax], [data-parallax-top]')];
  if (pxEls.length && !reduce) {
    let queued = false;
    const run = () => {
      queued = false;
      const vh = innerHeight, wide = innerWidth >= 760;
      if (!wide) { pxEls.forEach(el => { el.style.translate = ''; }); return; }
      // Read every position first, then write, so the browser lays out the page once per frame.
      const moves = [];
      pxEls.forEach(el => {
        if (el.closest('[hidden]')) return;
        if (el.dataset.parallaxTop) { if (scrollY < vh * 1.5) moves.push([el, scrollY * +el.dataset.parallaxTop]); return; }
        const r = el.parentElement.getBoundingClientRect();
        if (r.bottom < -200 || r.top > vh + 200) return;
        moves.push([el, Math.max(-140, Math.min(140, -(r.top + r.height / 2 - vh / 2) * +el.dataset.parallax))]);
      });
      moves.forEach(([el, y]) => { el.style.translate = `0 ${y.toFixed(1)}px`; });
    };
    const ask = () => { if (!queued) { queued = true; requestAnimationFrame(run); } };
    addEventListener('scroll', ask, { passive: true });
    addEventListener('resize', ask);
    run();
  }

  // ---- Hero B: the card follows the pointer ----
  document.querySelectorAll('.scene').forEach(scene => {
    if (reduce) return;
    const sec = scene.closest('section'), tilt = scene.querySelector('.scene__tilt');
    sec.addEventListener('pointermove', e => {
      const r = sec.getBoundingClientRect();
      tilt.style.setProperty('--ry', (((e.clientX - r.left) / r.width - 0.5) * 14).toFixed(2) + 'deg');
      tilt.style.setProperty('--rx', (-((e.clientY - r.top) / r.height - 0.5) * 10).toFixed(2) + 'deg');
    });
    sec.addEventListener('pointerleave', () => { tilt.style.removeProperty('--rx'); tilt.style.removeProperty('--ry'); });
  });

  // ---- Step rail: shows the current chapter ----
  const railLinks = [...document.querySelectorAll('.rail a')];
  if (railLinks.length && hasIO) {
    const io = new IntersectionObserver(es => es.forEach(en => {
      if (!en.isIntersecting) return;
      railLinks.forEach(a => { const on = a.hash === '#' + en.target.id; a.classList.toggle('is-on', on); on ? a.setAttribute('aria-current', 'location') : a.removeAttribute('aria-current'); if (on) { const row = a.parentElement; row.scrollLeft = a.offsetLeft - (row.clientWidth - a.offsetWidth) / 2; } });
    }), { rootMargin: '-45% 0px -50% 0px' });
    document.querySelectorAll('.chapter').forEach(c => io.observe(c));
  }

  // ---- Hero selector for review. build.py sets data-review on <html>; set REVIEW = False there before launch. Also ?hero=a|b|c ----
  const heroes = [...document.querySelectorAll('[data-hero]')];
  if (heroes.length) {
    const review = document.documentElement.hasAttribute('data-review');
    const params = new URLSearchParams(location.search);
    const pick = params.get('hero') || (review && store.get('lune2-hero')) || 'b';
    const show = v => heroes.forEach(h => { h.hidden = h.dataset.hero !== v; });
    show(pick);
    if (review) {
      const bar = document.createElement('div');
      bar.className = 'draftbar';
      bar.setAttribute('role', 'group');
      bar.setAttribute('aria-label', 'Hero option, for review');
      const names = { a: 'Decode', b: '3D card', c: 'Journey' };
      const lab = document.createElement('span'); lab.textContent = 'Hero';
      const box = document.createElement('div');
      Object.keys(names).forEach(v => {
        const b = document.createElement('button');
        b.type = 'button'; b.dataset.val = v; b.textContent = v.toUpperCase(); b.title = names[v];
        b.setAttribute('aria-label', 'Hero ' + names[v]); b.setAttribute('aria-pressed', String(v === pick));
        box.append(b);
      });
      bar.append(lab, box);
      bar.addEventListener('click', e => {
        const b = e.target.closest('button');
        if (!b) return;
        store.set('lune2-hero', b.dataset.val);
        show(b.dataset.val);
        box.querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', String(x === b)));
        requestAnimationFrame(sync);
      });
      document.body.append(bar);
    }
    requestAnimationFrame(sync);
  }

  // ---- Contact form: checks the fields, then opens an email draft ----
  const form = document.getElementById('contact-form');
  if (form) {
    const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
    const bad = (name, isBad) => { form.querySelector(`[data-field="${name}"]`).classList.toggle('is-bad', isBad); return isBad; };
    form.addEventListener('submit', e => {
      e.preventDefault();
      const v = n => form.elements[n].value.trim();
      const products = [...form.querySelectorAll('input[name=product]:checked')].map(c => c.value);
      const errors = [
        bad('first', !v('first')), bad('last', !v('last')), bad('email', !EMAIL.test(v('email'))),
        bad('company', !v('company')), bad('product', products.length === 0)
      ];
      if (errors.some(Boolean)) { form.querySelector('.is-bad input, .is-bad select').focus(); return; }
      const body = [
        `Name: ${v('first')} ${v('last')}`, `Work email: ${v('email')}`, `Company: ${v('company')}`,
        `Job title: ${v('title')}`, `Country: ${v('country')}`, `Products: ${products.join(', ')}`, '', v('notes')
      ].join('\n');
      window.location.href = 'mailto:hello@lunedata.io?subject=' + encodeURIComponent('Demo request: ' + v('company')) + '&body=' + encodeURIComponent(body);
      document.getElementById('form-done').hidden = false;
    });
  }
})();

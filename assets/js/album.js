// Nathan Bui — album pages. One file; each album's theme (body.alb--<theme>) gets its own decoration and motion.
(() => {
  const html = document.documentElement, body = document.body;
  const theme = ([...body.classList].find((c) => c.startsWith('alb--')) || 'alb--').slice(5);
  const decor = document.querySelector('.decor');
  const track = document.querySelector('.agal__track');
  const figs = [...document.querySelectorAll('.ap')];
  const narrow = () => matchMedia('(max-width: 760px)').matches;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const G = window.gsap && window.ScrollTrigger && !reduce;
  const el = (tag, cls, htmlStr) => { const n = document.createElement(tag); if (cls) n.className = cls; if (htmlStr) n.innerHTML = htmlStr; return n; };
  const rnd = (a, b) => a + Math.random() * (b - a);
  const svgNS = 'http://www.w3.org/2000/svg';
  let lenis = null;

  document.querySelectorAll('[data-year]').forEach((n) => { n.textContent = new Date().getFullYear(); });
  if (!G) html.classList.add('no-motion');

  if (G) {
    gsap.registerPlugin(ScrollTrigger);
    if (window.Lenis) {
      lenis = new Lenis({ lerp: .1 });
      lenis.on('scroll', ScrollTrigger.update);
      gsap.ticker.add((t) => lenis.raf(t * 1000));
      gsap.ticker.lagSmoothing(0);
      document.querySelectorAll('a[href^="#"]').forEach((a) => a.addEventListener('click', (e) => { const t = document.querySelector(a.getAttribute('href')); if (t) { e.preventDefault(); lenis.scrollTo(t); } }));
    }
  }

  // arriving from a card on the home page: the iris opens on that photo, then it lifts away
  const into = document.querySelector('.into');
  const ARR = into && G ? 1.25 : 0;
  if (into) {
    if (!G) into.remove();
    else {
      const im = into.querySelector('img');
      gsap.timeline({ onComplete: () => into.remove() })
        .to(into.querySelector('.into__iris'), { '--r': '150vmax', duration: .9, ease: 'power3.out' }, .05)
        .fromTo(im, { scale: 1.08 }, { scale: 1, duration: 1.2, ease: 'power2.out' }, 0)
        .to(into, { clipPath: 'inset(0% 0% 100% 0%)', duration: .9, ease: 'expo.inOut' }, .85)
        .to(im, { yPercent: -14, duration: .9, ease: 'expo.inOut' }, .85);
    }
  }
  // reveal helper: runs fn once when the figure scrolls in (or straight away without motion)
  const onIn = (f, fn, start = 'top 80%') => { if (!G) return; ScrollTrigger.create({ trigger: f, start, once: true, onEnter: () => fn(f) }); };
  const img = (f) => f.querySelector('img');
  const link = (f) => f.querySelector('.ap__a');

  // ================= themes =================
  const T = {};

  // 01 harbour: horizontal shoreline, the sky and sea change colour as the evening goes on
  T.horizon = () => {
    const sky = el('div', 'sky', '<i class="sun"></i><i class="sea"></i>');
    body.prepend(sky);
    // [progress, sky top, sky horizon, sea top, sea deep, text]
    const stops = [
      [0, '#9db9cc', '#eadcc3', '#5d7f93', '#2f4a5a', '#1d0e0b'],
      [.4, '#c9a98a', '#f3cf92', '#6f6c6a', '#36393f', '#1d0e0b'],
      [.72, '#9a4f4c', '#ee9a5e', '#4c2e36', '#24161d', '#fbf1e3'],
      [1, '#2a1520', '#8a4236', '#1d1017', '#0d0709', '#fbf1e3'],
    ];
    const paint = (p) => {
      let i = 0; while (i < stops.length - 2 && p > stops[i + 1][0]) i++;
      const a = stops[i], b = stops[i + 1], t = Math.min(1, Math.max(0, (p - a[0]) / (b[0] - a[0])));
      const c = (k) => (G ? gsap.utils.interpolate(a[k], b[k], t) : a[k]);
      const s = body.style;
      s.setProperty('--sky1', c(1)); s.setProperty('--sky2', c(2)); s.setProperty('--sea1', c(3)); s.setProperty('--sea2', c(4)); s.setProperty('--fg', c(5));
      s.setProperty('--sun-y', `${16 + p * 58}vh`); s.setProperty('--glint', String(1 - p * .7));
    };
    paint(0);
    if (!G) return;
    const mm = gsap.matchMedia();
    mm.add('(min-width: 761px)', () => {
      const dist = () => track.scrollWidth - innerWidth;
      gsap.to(track, { x: () => -dist(), ease: 'none', scrollTrigger: { trigger: '.agal', pin: true, start: 'top top', end: () => '+=' + dist(), scrub: .6, invalidateOnRefresh: true, onUpdate: (s) => paint(s.progress) } });
    });
    mm.add('(max-width: 760px)', () => { ScrollTrigger.create({ trigger: '.agal', start: 'top 50%', end: 'bottom bottom', onUpdate: (s) => paint(s.progress) }); });
  };

  // 02 city: a skyline with windows lighting up, three columns drifting at different speeds, long-exposure reveals
  T.skyline = () => {
    const W = 1440, H = 420, svg = document.createElementNS(svgNS, 'svg');
    svg.setAttribute('viewBox', `0 0 ${W} ${H}`); svg.setAttribute('preserveAspectRatio', 'xMidYMax slice'); svg.classList.add('city');
    let out = '', x = 0;
    while (x < W) {
      const w = rnd(40, 110), h = rnd(90, 360), back = Math.random() < .4;
      out += `<rect class="${back ? 'b2' : 'b'}" x="${x}" y="${H - h}" width="${w}" height="${h}"/>`;
      if (!back) for (let wy = H - h + 14; wy < H - 10; wy += 16) for (let wx = x + 8; wx < x + w - 10; wx += 13)
        if (Math.random() < .22) out += `<rect class="w" x="${wx}" y="${wy}" width="5" height="7" style="animation-delay:${rnd(0, 5).toFixed(2)}s;animation-duration:${rnd(4, 9).toFixed(1)}s"/>`;
      x += w + rnd(-10, 6);
    }
    svg.innerHTML = out; decor.append(svg);
    for (let i = 0; i < 6; i++) { const t = el('i', `trail trail--${i % 2 ? 'w' : 'r'}`); t.style.cssText = `bottom:${rnd(2, 9)}vh;animation-duration:${rnd(2.6, 5).toFixed(1)}s;animation-delay:${rnd(0, 4).toFixed(1)}s;opacity:${rnd(.4, .9).toFixed(2)}`; decor.append(t); }
    if (!narrow()) {
      const cols = el('div', 'cols'); const cs = [0, 1, 2].map(() => cols.appendChild(el('div', 'col')));
      figs.forEach((f, i) => cs[i % 3].append(f)); track.append(cols); track.style.display = 'block';
      if (G) cs.forEach((c, i) => gsap.fromTo(c, { yPercent: [6, -4, 12][i] }, { yPercent: [-6, 4, -12][i], ease: 'none', scrollTrigger: { trigger: '.agal', start: 'top bottom', end: 'bottom top', scrub: true } }));
    }
    figs.forEach((f) => {
      if (G) gsap.set(img(f), { opacity: 0, scaleY: 1.4, filter: 'blur(14px) brightness(2.4)', transformOrigin: '50% 100%' });
      onIn(f, () => gsap.to(img(f), { opacity: 1, scaleY: 1, filter: 'blur(0px) brightness(1)', duration: 1.5, ease: 'expo.out' }));
    });
  };

  // 03 Ninh Bình: ink hills and mist; each photo spreads out of an ink blot and the colour comes in after
  T.ink = () => {
    decor.innerHTML = `
      <svg class="karst" viewBox="0 0 1200 500" preserveAspectRatio="xMidYMax slice">
        <defs><linearGradient id="fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1b1a17"/><stop offset="1" stop-color="#1b1a17" stop-opacity="0"/></linearGradient></defs>
        <path d="M0 330 C60 200 90 120 130 230 C160 90 210 60 250 210 C290 150 320 150 350 250 C400 70 470 40 510 220 C560 140 600 150 640 260 C700 80 770 60 810 230 C850 170 890 170 930 250 C980 110 1050 90 1090 230 C1130 180 1170 170 1200 220 L1200 500 L0 500Z" fill="url(#fade)" opacity=".1"/>
        <path d="M0 400 C50 300 90 250 140 340 C190 210 250 190 300 330 C350 280 390 270 430 350 C480 220 550 200 600 340 C660 260 700 260 740 360 C800 230 860 220 910 350 C960 290 1010 290 1050 370 C1100 270 1160 260 1200 330 L1200 500 L0 500Z" fill="url(#fade)" opacity=".2"/>
        <path d="M0 470 C80 410 140 400 220 450 C300 390 380 390 460 455 C560 400 640 400 720 460 C820 410 900 405 980 455 C1060 420 1130 415 1200 440 L1200 500 L0 500Z" fill="#1b1a17" opacity=".35"/>
      </svg>
      <i class="mist" style="left:-10vw;bottom:24vh"></i><i class="mist" style="left:40vw;bottom:12vh;animation-duration:34s"></i><i class="mist" style="left:10vw;bottom:2vh;animation-duration:30s;animation-direction:alternate-reverse"></i>
      <span class="seal">NB</span><span class="vtext">Ninh Bình · Việt Nam · 2026</span>`;
    const nums = ['một', 'hai', 'ba', 'bốn', 'năm', 'sáu', 'bảy', 'tám', 'chín', 'mười'];
    const blob = (seed) => {
      let d = '';
      for (let k = 0; k <= 72; k++) {
        const a = (k / 72) * Math.PI * 2;
        const r = 34 + 6 * Math.sin(a * 3 + seed) + 3.5 * Math.sin(a * 7 + seed * 2.3) + 2 * Math.sin(a * 13 + seed * 5.1);
        d += `${k ? 'L' : 'M'}${(50 + r * Math.cos(a)).toFixed(1)} ${(50 + r * Math.sin(a)).toFixed(1)}`;
      }
      const drops = [0, 1, 2, 3].map((j) => { const a = seed * 1.7 + j * 1.6, r = 41 + j * 2; return `<circle cx="${(50 + r * Math.cos(a)).toFixed(1)}" cy="${(50 + r * Math.sin(a)).toFixed(1)}" r="${(1.4 + j * .5).toFixed(1)}"/>`; }).join('');
      return `url("data:image/svg+xml,${encodeURIComponent(`<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><path d='${d}Z'/>${drops}</svg>`)}")`;
    };
    figs.forEach((f, i) => {
      f.append(el('span', 'ink-num', nums[i] || ''));
      const a = link(f); a.style.setProperty('--blob', blob(i * 2.1 + 1));
      if (!G) return;
      gsap.set(a, { '--m': '0%' }); gsap.set(img(f), { filter: 'grayscale(1) contrast(1.35) brightness(.9)' });
      onIn(f, () => {
        gsap.to(a, { '--m': '280%', duration: 2.4, ease: 'power2.inOut' });
        gsap.to(img(f), { filter: 'grayscale(0) contrast(1) brightness(1)', duration: 2.2, delay: 1, ease: 'power1.inOut' });
      }, 'top 78%');
    });
    if (G) gsap.to('.karst', { yPercent: 18, ease: 'none', scrollTrigger: { trigger: '.ahero', start: 'top top', end: 'bottom top', scrub: true } });
  };

  // 04 Hội An: lanterns sway, a warm light follows you, prints stack on top of each other
  T.lantern = () => {
    const cols = ['#c8342b', '#e8742c', '#e2b33c', '#c8342b', '#d9542f', '#e8742c', '#c8342b', '#e2b33c', '#d9542f'];
    cols.forEach((c, i) => {
      const s = rnd(46, 92), lan = el('span', 'lan', '<b></b><i></i>');
      lan.style.cssText = `left:${4 + i * 11 + rnd(-2, 2)}%;--s:${s}px;--h:${rnd(30, 170)}px;--c:${c};--d:${rnd(2.6, 4.6).toFixed(1)}s;animation-delay:-${rnd(0, 3).toFixed(1)}s`;
      decor.append(lan);
    });
    const warm = el('div', 'warm'); body.append(warm);
    addEventListener('pointermove', (e) => { warm.style.setProperty('--px', e.clientX + 'px'); warm.style.setProperty('--py', e.clientY + 'px'); }, { passive: true });
    if (!G) return;
    figs.forEach((f, i) => {
      const a = link(f);
      gsap.set(a, { clipPath: 'circle(0% at 50% 0%)' });
      onIn(f, () => gsap.to(a, { clipPath: 'circle(150% at 50% 0%)', duration: 1.8, ease: 'power2.inOut' }), 'top 70%');
      if (i < figs.length - 1) gsap.to(f, { scale: .9, filter: 'brightness(.4)', ease: 'none', scrollTrigger: { trigger: figs[i + 1], start: 'top bottom', end: 'top 11%', scrub: true } });
    });
  };

  // 05 Shanghai: huge outlined characters and window-blind reveals
  T.blinds = () => {
    decor.innerHTML = '<span class="big-cn" lang="zh">上海</span>';
    figs.forEach((f) => {
      const sl = el('span', 'slats', '<i></i>'.repeat(8)); link(f).append(sl);
      if (!G) { sl.remove(); return; }
      gsap.set(img(f), { scale: 1.18 });
      onIn(f, () => {
        gsap.to(sl.children, { scaleY: 0, duration: .9, ease: 'power3.inOut', stagger: .07 });
        gsap.to(img(f), { scale: 1, duration: 1.8, ease: 'power3.out' });
      });
    });
    if (G) gsap.to('.big-cn', { xPercent: -22, ease: 'none', scrollTrigger: { trigger: '.ahero', start: 'top top', end: 'bottom top', scrub: true } });
  };

  // 06 USyd portraits: the contact sheet with grease-pencil picks, jacaranda petals, rack-focus reveals
  T.contact = () => {
    const picks = new Set([0, 6, 7, 11, 14]);
    const sheet = el('div', 'sheet');
    figs.forEach((f, i) => {
      const s = el('span'); s.dataset.f = `${i + 12}A`; s.style.backgroundImage = `url("${img(f).getAttribute('src')}")`;
      if (picks.has(i)) s.innerHTML = '<svg viewBox="0 0 100 100" preserveAspectRatio="none"><path pathLength="1" d="M10 54 C6 18 86 6 92 44 C97 84 20 98 8 60 C4 44 16 26 40 20"/></svg>';
      sheet.append(s);
    });
    sheet.append(el('span'));
    decor.append(sheet);
    const pet = el('div', 'petals');
    for (let i = 0; i < 16; i++) { const p = el('i'); p.style.cssText = `left:${rnd(0, 100)}%;--s:${rnd(7, 13)}px;--c:${['#9b7fc4', '#b79bd8', '#8467ad'][i % 3]};--d:${rnd(9, 17).toFixed(1)}s;--dl:-${rnd(0, 16).toFixed(1)}s`; pet.append(p); }
    body.append(pet);
    if (!G) return;
    gsap.fromTo('.sheet path', { strokeDasharray: 1, strokeDashoffset: 1 }, { strokeDashoffset: 0, duration: .7, ease: 'power2.inOut', stagger: .35, delay: 1 });
    gsap.from('.sheet', { rotation: 9, y: 60, opacity: 0, duration: 1.4, ease: 'power3.out', delay: .15 });
    figs.forEach((f) => {
      gsap.set(img(f), { filter: 'blur(18px)', scale: 1.07 });
      onIn(f, () => gsap.to(img(f), { filter: 'blur(0px)', scale: 1, duration: 1.4, ease: 'power2.out' }));
    });
  };

  // 07 USyd graduation: arches rise up, caps get thrown on arrival
  T.arches = () => {
    let p = '';
    for (let i = 0; i < 9; i++) { const x = i * 160; p += `M${x + 10} 420 V230 C${x + 10} 130 ${x + 80} 90 ${x + 80} 90 C${x + 80} 90 ${x + 150} 130 ${x + 150} 230 V420 `; }
    decor.innerHTML = `<svg class="arcade" viewBox="0 0 1440 420" preserveAspectRatio="xMidYMax slice"><path d="${p}"/><path d="M0 60 H1440 M0 74 H1440"/></svg>`;
    const capSVG = '<svg viewBox="0 0 120 90"><path d="M60 8 L116 30 L60 52 L4 30Z" fill="#1c2540"/><path d="M28 40 V62 C28 74 92 74 92 62 V40 L60 52Z" fill="#111830"/><path d="M60 30 L100 40 V64" stroke="#c9a43f" stroke-width="2.5" fill="none"/><circle cx="100" cy="68" r="4" fill="#c9a43f"/></svg>';
    [22, 50, 76].forEach((x) => { const c = el('span', 'cap', capSVG); c.style.setProperty('--x', x + '%'); decor.append(c); });
    if (!G) { document.querySelectorAll('.cap').forEach((c, i) => { c.style.bottom = (30 + i * 8) + 'vh'; }); return; }
    gsap.utils.toArray('.cap').forEach((c, i) => {
      const peak = rnd(48, 70);
      gsap.timeline({ delay: .5 + i * .14 })
        .to(c, { y: () => -innerHeight * peak / 100, rotation: rnd(-540, 540), duration: 1.3, ease: 'power2.out' })
        .to(c, { y: () => -innerHeight * (peak - 14) / 100, rotation: '+=40', duration: 1.6, ease: 'sine.inOut' })
        .to(c, { y: '+=14', rotation: '+=6', duration: 2.4, ease: 'sine.inOut', yoyo: true, repeat: -1 });
    });
    figs.forEach((f) => {
      const a = link(f);
      gsap.set(a, { clipPath: 'inset(100% -30px -30px -30px)' }); gsap.set(img(f), { scale: 1.3 });
      onIn(f, () => { gsap.to(a, { clipPath: 'inset(-30px -30px -30px -30px)', duration: 1.4, ease: 'power3.inOut' }); gsap.to(img(f), { scale: 1, duration: 2, ease: 'power3.out' }); });
    });
  };

  // 08 Macquarie graduation: prints placed into an old album with photo corners
  T.album = () => {
    const flower = (c) => `<svg viewBox="0 0 60 60"><g fill="${c}">${[0, 72, 144, 216, 288].map((r) => `<ellipse cx="30" cy="15" rx="8" ry="14" transform="rotate(${r} 30 30)"/>`).join('')}</g><circle cx="30" cy="30" r="5" fill="#c9a43f"/></svg>`;
    decor.innerHTML = '<i class="ribbon"></i>';
    [[8, 18, 70, '#c98a8a'], [62, 12, 44, '#e3d3b2'], [84, 58, 60, '#b98aa8'], [40, 70, 36, '#e3d3b2']].forEach(([x, y, s, c]) => {
      const f = el('span', 'flower', flower(c)); f.style.cssText = `left:${x}%;top:${y}%;--s:${s}px;transform:rotate(${rnd(0, 90)}deg)`; decor.append(f);
    });
    figs.forEach((f, i) => {
      const r = [-2.5, 1.8, -1.2, 2.6, -2, 1.3][i % 6];
      f.style.setProperty('--r', r + 'deg');
      const a = link(f); for (let k = 0; k < 4; k++) a.append(el('i', 'corner'));
      if (!G) return;
      gsap.set(f, { rotation: r + (i % 2 ? 12 : -12), y: -80, scale: 1.08, opacity: 0 });
      onIn(f, () => gsap.to(f, { rotation: r, y: 0, scale: 1, opacity: 1, duration: 1.1, ease: 'back.out(1.4)' }), 'top 85%');
    });
  };

  // 09 Sydney Go: a route draws itself from checkpoint to checkpoint, each photo gets stamped
  T.route = () => {
    decor.innerHTML = `<svg class="compass" viewBox="0 0 100 100" fill="none" stroke="currentColor"><circle cx="50" cy="50" r="46" stroke-width="1"/><circle cx="50" cy="50" r="38" stroke-width=".6" stroke-dasharray="2 3"/><path d="M50 6 L57 50 L50 94 L43 50Z" fill="currentColor" opacity=".85" stroke="none"/><path d="M6 50 L50 44 L94 50 L50 56Z" fill="currentColor" opacity=".35" stroke="none"/><text x="50" y="22" text-anchor="middle" font-size="9" fill="currentColor" stroke="none" font-family="monospace">N</text></svg>`;
    const svg = document.createElementNS(svgNS, 'svg'); svg.classList.add('route');
    svg.innerHTML = '<path class="r-base"/><path class="r-live"/>';
    track.prepend(svg);
    figs.forEach((f, i) => {
      f.append(el('span', 'pin', `<b>${i + 1}</b>`));
      const st = el('span', 'stamp', `Checkpoint ${String(i + 1).padStart(2, '0')} ✓`); link(f).append(st);
      if (!G) return;
      gsap.set(st, { opacity: 0, scale: 2.6, rotation: -24 });
      onIn(f, () => { f.querySelector('.pin').classList.add('is-hit'); gsap.to(st, { opacity: 1, scale: 1, rotation: -8, duration: .5, ease: 'back.out(2.2)', delay: .35 }); }, 'top 60%');
    });
    const live = svg.querySelector('.r-live'), base = svg.querySelector('.r-base');
    let len = 1, prog = 0;
    const draw = () => {
      const tr = track.getBoundingClientRect();
      svg.setAttribute('viewBox', `0 0 ${tr.width} ${tr.height}`);
      let d = `M${tr.width / 2} -60`, px = tr.width / 2, py = -60;
      figs.forEach((f, i) => {
        const r = link(f).getBoundingClientRect();
        const x = (i % 2 ? r.left - tr.left : r.right - tr.left) + (i % 2 ? -1 : 1) * Math.min(60, tr.width * .05);
        const x2 = narrow() ? tr.width / 2 : x, y = r.top - tr.top + r.height / 2;
        const my = (py + y) / 2;
        d += ` C${px} ${my} ${x2} ${my} ${x2} ${y}`; px = x2; py = y;
      });
      base.setAttribute('d', d); live.setAttribute('d', d);
      len = live.getTotalLength(); live.style.strokeDasharray = len; live.style.strokeDashoffset = len * (1 - prog);
    };
    draw(); addEventListener('load', draw);
    if (!G) { live.style.strokeDashoffset = 0; return; }
    ScrollTrigger.addEventListener('refresh', draw);
    ScrollTrigger.create({ trigger: track, start: 'top 65%', end: 'bottom 55%', onUpdate: (s) => { prog = s.progress; live.style.strokeDashoffset = len * (1 - prog); } });
  };

  // 10 Hackathon: a terminal types the folder, photos render in from big pixels
  T.terminal = () => {
    const files = figs.map((f) => (link(f).getAttribute('href') || '').split('/').pop());
    const lines = ['$ cd ~/photos/hackathon-2026', '$ ls', files.join('   '), `$ open *.jpg   # ${files.length} files`];
    const pre = el('pre', 'term'); decor.append(pre);
    figs.forEach((f) => {
      const im = img(f), name = (link(f).getAttribute('href') || '').split('/').pop();
      f.prepend(el('span', 'win', `<i></i><i></i><i></i><code>${name} — ${im.getAttribute('width')}×${im.getAttribute('height')}</code>`));
    });
    if (!G) { pre.textContent = lines.join('\n'); return; }
    let li = 0, ci = 0, txt = '';
    const type = () => {
      if (li >= lines.length) { pre.innerHTML = txt + '<span class="cur"></span>'; return; }
      txt += ci < lines[li].length ? lines[li][ci++] : (ci = 0, li++, '\n');
      pre.innerHTML = txt.replace(/</g, '&lt;') + '<span class="cur"></span>';
      setTimeout(type, ci === 0 ? 260 : 18);
    };
    setTimeout(type, 500);
    const pixelate = async (f) => {
      const im = img(f), a = link(f), cap = f.querySelector('figcaption b');
      try { await im.decode(); } catch (e) { gsap.set(im, { opacity: 1 }); return; }
      const cv = el('canvas'), ctx = cv.getContext('2d'), off = el('canvas'), octx = off.getContext('2d');
      const W = cv.width = Math.round(a.clientWidth), H = cv.height = Math.round(a.clientHeight);
      a.append(cv);
      const full = cap.textContent; cap.textContent = '';
      for (const s of [6, 12, 24, 48, 96, 192]) {
        off.width = s; off.height = Math.max(1, Math.round(s * H / W));
        octx.drawImage(im, 0, 0, off.width, off.height);
        ctx.imageSmoothingEnabled = false; ctx.drawImage(off, 0, 0, W, H);
        cap.textContent = full.slice(0, Math.round(full.length * s / 192));
        await new Promise((r) => setTimeout(r, 120));
      }
      gsap.set(im, { opacity: 1 }); cap.textContent = full;
      gsap.to(cv, { opacity: 0, duration: .25, onComplete: () => cv.remove() });
    };
    figs.forEach((f) => { gsap.set(img(f), { opacity: 0 }); onIn(f, pixelate, 'top 75%'); });
  };

  // 11 Đại hội: velvet curtains open, then each photo lights up in its gold frame
  T.curtain = () => {
    const stage = el('div', 'stage', '<div class="cur cur--l"><i></i></div><div class="cur cur--r"><i></i></div><div class="valance"></div>');
    document.querySelector('.ahero').append(stage);
    if (!G) return;
    gsap.fromTo('.cur--l i', { xPercent: 0 }, { xPercent: -70, duration: 2, ease: 'power3.inOut', delay: .3 + ARR });
    gsap.fromTo('.cur--r i', { xPercent: 0 }, { xPercent: 70, duration: 2, ease: 'power3.inOut', delay: .3 + ARR });
    gsap.to('.cur--l', { xPercent: -40, ease: 'none', scrollTrigger: { trigger: '.ahero', start: 'top top', end: 'bottom top', scrub: true } });
    gsap.to('.cur--r', { xPercent: 40, ease: 'none', scrollTrigger: { trigger: '.ahero', start: 'top top', end: 'bottom top', scrub: true } });
    gsap.from('[data-in]', { opacity: 0, y: 30, duration: 1, stagger: .1, delay: 1.1 + ARR, ease: 'power3.out', overwrite: true });
    figs.forEach((f) => {
      gsap.set(link(f), { opacity: 0, scale: .94 }); gsap.set(img(f), { filter: 'brightness(0)' });
      onIn(f, () => {
        gsap.to(link(f), { opacity: 1, scale: 1, duration: 1, ease: 'power3.out' });
        gsap.to(img(f), { keyframes: [{ filter: 'brightness(0.35)', duration: .4 }, { filter: 'brightness(0.15)', duration: .15 }, { filter: 'brightness(1.12)', duration: .6 }, { filter: 'brightness(1)', duration: .5 }], delay: .3 });
      });
    });
  };

  // 12 Cultural Day: rice paper discs and herbs; each photo unrolls like a sheet of rice paper
  T.ricepaper = () => {
    [[62, 10, '38vmin'], [80, 46, '24vmin'], [52, 60, '16vmin']].forEach(([x, y, s]) => { const d = el('i', 'disc'); d.style.cssText = `left:${x}%;top:${y}%;--s:${s}`; decor.append(d); });
    const leaf = '<svg viewBox="0 0 40 60"><path d="M20 2 C36 16 38 40 20 58 C2 40 4 16 20 2Z" fill="currentColor"/><path d="M20 6 V56" stroke="rgba(255,255,255,.45)" stroke-width="1.2"/></svg>';
    [[58, 18, 40, '#6f8f3a'], [74, 30, 30, '#8aa84c'], [88, 14, 26, '#5a7a2c'], [66, 64, 34, '#8aa84c'], [90, 70, 28, '#6f8f3a'], [48, 40, 22, '#b3262d']].forEach(([x, y, s, c], i) => {
      const l = el('span', 'leaf', leaf); l.style.cssText = `left:${x}%;top:${y}%;--s:${s}px;--c:${c};--r:${rnd(-60, 60).toFixed(0)}deg;--dl:-${i}s`; decor.append(l);
    });
    if (!G) return;
    figs.forEach((f) => {
      gsap.set(link(f), { rotationX: -96, transformOrigin: '50% 0%', opacity: 0 });
      onIn(f, () => gsap.to(link(f), { rotationX: 0, opacity: 1, duration: 1.5, ease: 'power3.out' }), 'top 75%');
      gsap.from(f.querySelector('.ap__n'), { yPercent: 60, opacity: 0, duration: 1, ease: 'power3.out', scrollTrigger: { trigger: f, start: 'top 75%', once: true } });
    });
  };

  // 13 Serenade: dark stage; the cursor (or a slow sweep on touch screens) is the spotlight
  T.spotlight = () => {
    [[30, 18, 0], [70, -18, -4]].forEach(([x, r, dl]) => { const b = el('i', 'beam'); b.style.cssText = `--x:${x}%;--r:${r}deg;--dl:${dl}s`; decor.append(b); });
    for (let i = 0; i < 40; i++) { const d = el('i', 'dust'); d.style.cssText = `left:${rnd(10, 90)}%;top:${rnd(10, 90)}%;--d:${rnd(4, 9).toFixed(1)}s;--dx:${rnd(-30, 30).toFixed(0)}px;animation-delay:-${rnd(0, 8).toFixed(1)}s`; decor.append(d); }
    if (!G) return;
    const fine = matchMedia('(pointer: fine)').matches;
    figs.forEach((f) => {
      const a = link(f);
      gsap.fromTo(a, { '--r': '6%' }, { '--r': '62%', ease: 'none', scrollTrigger: { trigger: f, start: 'top 90%', end: 'center 40%', scrub: true } });
      const sweep = gsap.fromTo(a, { '--x': '22%', '--y': '40%' }, { '--x': '78%', '--y': '58%', duration: 3.4, ease: 'sine.inOut', yoyo: true, repeat: -1 });
      if (!fine) return;
      a.addEventListener('pointerenter', () => sweep.pause());
      a.addEventListener('pointerleave', () => sweep.resume());
      a.addEventListener('pointermove', (e) => {
        const r = a.getBoundingClientRect();
        gsap.to(a, { '--x': ((e.clientX - r.left) / r.width * 100) + '%', '--y': ((e.clientY - r.top) / r.height * 100) + '%', duration: .35, ease: 'power2.out', overwrite: 'auto' });
      });
    });
  };

  // ================= run =================
  if (T[theme]) T[theme]();
  if (G && theme !== 'curtain') gsap.from('[data-in]', { opacity: 0, y: 36, duration: 1.1, stagger: .09, ease: 'power3.out', delay: .1 + ARR });
  if (G) addEventListener('load', () => ScrollTrigger.refresh());


  // the way into an album: the picture you clicked grows to fill the screen, the title comes up, then the iris closes
  const leaveTo = (href, img, title, kicker, acc, titleIsHTML) => {
    const r = img.getBoundingClientRect();
    const small = img.currentSrc || img.src;
    const full = small.replace(/-sm\.jpg(\?.*)?$/, '.jpg');
    const ov = document.createElement('div'); ov.className = 'leave'; ov.style.setProperty('--acc', acc || '#111');
    const im = new Image(); im.alt = ''; im.src = small; ov.appendChild(im);
    const big = new Image(); big.onload = () => { im.src = full; }; big.src = full;
    const t = document.createElement('div'); t.className = 'leave__t';
    const k = document.createElement('small'); k.textContent = kicker;
    const b = document.createElement('b'); if (titleIsHTML) b.innerHTML = title; else b.textContent = title;
    t.append(k, b);
    const iris = document.createElement('i'); iris.className = 'leave__iris';
    ov.append(t, iris);
    Object.assign(ov.style, { left: r.left + 'px', top: r.top + 'px', width: r.width + 'px', height: r.height + 'px' });
    document.body.appendChild(ov);
    try { sessionStorage.setItem('nb-into', JSON.stringify({ src: new URL(full, location.href).href, acc })); } catch (e) {}
    gsap.timeline({ onComplete: () => { location.href = href; } })
      .to(ov, { left: 0, top: 0, width: innerWidth, height: innerHeight, duration: .8, ease: 'expo.inOut' })
      .fromTo(im, { scale: 1.18 }, { scale: 1, duration: 1.2, ease: 'power2.out' }, 0)
      .fromTo(t, { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: .5, ease: 'power3.out' }, .55)
      .to(iris, { '--r': '0vmax', duration: .55, ease: 'power3.in' }, 1.2);
  };
  addEventListener('pageshow', (e) => { if (e.persisted) document.querySelectorAll('.leave').forEach((n) => n.remove()); });
  const plainClick = (e) => !(e.defaultPrevented || e.button || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey);
  const nextCard = document.querySelector('.anext__card');
  if (G && nextCard) nextCard.addEventListener('click', (e) => {
    if (!plainClick(e)) return;
    e.preventDefault();
    leaveTo(nextCard.href, nextCard.querySelector('img'), nextCard.querySelector('.anext__txt b').textContent, 'Next album', getComputedStyle(nextCard).getPropertyValue('--nacc').trim(), false);
  });

  // ================= lightbox =================
  const lb = document.querySelector('.lb');
  if (lb && typeof lb.showModal === 'function') {
    const links = [...document.querySelectorAll('.ap__a')];
    const im = lb.querySelector('img'), cap = lb.querySelector('figcaption b'), exif = lb.querySelector('figcaption span');
    let i = 0;
    const show = (n) => {
      i = (n + links.length) % links.length; const a = links[i];
      im.src = a.href; im.alt = a.dataset.cap; cap.textContent = a.dataset.cap; exif.textContent = a.dataset.exif;
      if (G) gsap.fromTo(im, { clipPath: 'inset(0% 0% 100% 0%)' }, { clipPath: 'inset(0% 0% 0% 0%)', duration: .55, ease: 'power3.inOut' });
    };
    links.forEach((a, k) => a.addEventListener('click', (e) => { e.preventDefault(); show(k); lb.showModal(); lenis && lenis.stop(); }));
    lb.querySelector('.lb__prev').addEventListener('click', () => show(i - 1));
    lb.querySelector('.lb__next').addEventListener('click', () => show(i + 1));
    lb.querySelector('.lb__x').addEventListener('click', () => lb.close());
    lb.addEventListener('click', (e) => { if (e.target === lb) lb.close(); });
    lb.addEventListener('close', () => { lenis && lenis.start(); });
    lb.addEventListener('keydown', (e) => { if (e.key === 'ArrowLeft') show(i - 1); if (e.key === 'ArrowRight') show(i + 1); });
  }
})();

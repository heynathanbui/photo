// Nathan Bui — Photography: page behaviour (scroll, viewfinder HUD, AF cursor, reveals, filters, lightbox).
// The WebGL layer lives in scene.js; the two talk through window.NB.
(() => {
  const root = document.documentElement;
  const NB = window.NB || (window.NB = {});
  const hasGsap = !!(window.gsap && window.ScrollTrigger);
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const fine = matchMedia('(pointer: fine)').matches;
  const webgl = (() => { try { const c = document.createElement('canvas'); return !!(c.getContext('webgl2') || c.getContext('webgl')); } catch (e) { return false; } })();
  if (!webgl || reduce || !hasGsap || /[?&]nogl/.test(location.search)) root.classList.add('no-gl');
  if (!hasGsap) { root.classList.remove('js'); wireBasics(); return; }

  gsap.registerPlugin(ScrollTrigger);
  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));

  // ---------- smooth scroll ----------
  let lenis = null;
  if (window.Lenis && !reduce) {
    lenis = new Lenis({ lerp: .1, wheelMultiplier: 1 });
    lenis.on('scroll', ScrollTrigger.update);
    gsap.ticker.add((t) => lenis.raf(t * 1000));
    gsap.ticker.lagSmoothing(0);
  }
  const scrollToEl = (el, immediate) => lenis ? lenis.scrollTo(el, { immediate, offset: 0 }) : el.scrollIntoView({ behavior: immediate ? 'auto' : 'smooth' });

  // ---------- focal-plane shutter ----------
  const shutter = document.querySelector('.shutter');
  const [curtA, curtB] = shutter.querySelectorAll('i');
  NB.shutter = (mid) => gsap.timeline()
    .set(shutter, { autoAlpha: 1 })
    .fromTo(curtA, { yPercent: -100 }, { yPercent: 0, duration: .26, ease: 'power3.in' }, 0)
    .fromTo(curtB, { yPercent: 100 }, { yPercent: 0, duration: .26, ease: 'power3.in' }, 0)
    .add(() => mid && mid())
    .to(curtA, { yPercent: 100, duration: .42, ease: 'power3.out' }, '+=.06')
    .to(curtB, { yPercent: -100, duration: .42, ease: 'power3.out' }, '<.05')
    .set(shutter, { autoAlpha: 0 });

  // ---------- pinned hero (lens) and roll (film) ----------
  const gl = !root.classList.contains('no-gl');
  if (gl) {
    ScrollTrigger.create({ trigger: '.hero', pin: '.hero__pin', start: 'top top', end: '+=160%', onUpdate: (s) => { NB.heroP = s.progress; } });
    const copy = gsap.timeline({ scrollTrigger: { trigger: '.hero', start: 'top top', end: '+=160%', scrub: true } });
    copy.to('.hero__copy', { autoAlpha: 0, y: -60, ease: 'none', duration: .3 }, 0)
      .to('.hero__scroll', { autoAlpha: 0, duration: .1 }, 0)
      .to('.hero__aperture', { autoAlpha: 0, duration: .12 }, .7);
    ScrollTrigger.create({ trigger: '.roll', pin: '.roll__pin', start: 'top top', end: '+=520%', onUpdate: (s) => { NB.rollP = s.progress; } });
    gsap.from('.roll__ui > *', { autoAlpha: 0, y: 30, stagger: .1, scrollTrigger: { trigger: '.roll', start: 'top 40%', toggleActions: 'play none none reverse' } });
    gsap.to('.roll__ui', { autoAlpha: 0, scrollTrigger: { trigger: '.roll', start: 'top -60%', end: 'top -110%', scrub: true } });
    // the skip button pops in as the roll arrives, and Esc does the same thing
    gsap.from('.roll__skip', { autoAlpha: 0, scale: .6, y: -20, duration: .7, ease: 'back.out(2)', scrollTrigger: { trigger: '.roll', start: 'top 30%', toggleActions: 'play none none reverse' } });
    addEventListener('keydown', (e) => {
      if (e.key !== 'Escape' || document.querySelector('.lb[open]')) return;
      const r = document.querySelector('.roll').getBoundingClientRect();
      if (r.top < innerHeight * .5 && r.bottom > innerHeight * .5) document.querySelector('.roll__skip').click();
    });
  }

  // ---------- intro: shutter opens once the lens has its first photos ----------
  let opened = false;
  NB.ready = () => {
    if (opened) return; opened = true; NB.opened = true;
    const tl = gsap.timeline();
    tl.to(curtA, { yPercent: -100, duration: .9, ease: 'expo.inOut' }, .1)
      .to(curtB, { yPercent: 100, duration: .9, ease: 'expo.inOut' }, .1)
      .set(shutter, { autoAlpha: 0 })
      .add(() => { shutter.classList.remove('is-loading'); NB.playIntro && NB.playIntro(); }, .2)
      .from('[data-intro]', { autoAlpha: 0, y: 40, duration: 1.1, ease: 'power3.out', stagger: .09 }, .75);
  };
  shutter.classList.add('is-loading');
  gsap.set([curtA, curtB], { yPercent: 0 }); gsap.set(shutter, { autoAlpha: 1 });
  if (!gl) setTimeout(NB.ready, 300);
  setTimeout(NB.ready, 4000);

  // ---------- aperture breaks between galleries: the iris opens as you scroll through ----------
  if (reduce) root.classList.add('no-motion');
  else gsap.utils.toArray('.iris-break').forEach((el) => {
    const iris = el.querySelector('.iris'), label = el.querySelector('.iris-break__label');
    gsap.timeline({ scrollTrigger: { trigger: el, start: 'top top', end: 'bottom bottom', scrub: .6 } })
      .fromTo(iris, { '--r': '0vmax', '--spin': '-70deg' }, { '--r': '100vmax', '--spin': '0deg', ease: 'power2.in', duration: 1 }, 0)
      .fromTo(label, { scale: .82 }, { scale: 1.06, ease: 'none', duration: 1 }, 0)
      .to(label, { autoAlpha: 0, y: -40, duration: .25 }, .78);
  });

  // ---------- section motifs ----------
  if (!reduce) {
    const sky = { trigger: '.motif--scenery', start: 'top bottom', end: 'bottom 60%', scrub: true };
    gsap.fromTo('.m-sun', { y: 110 }, { y: -70, ease: 'none', scrollTrigger: sky });
    gsap.fromTo('.m-far', { y: 40 }, { y: -10, ease: 'none', scrollTrigger: sky });
    gsap.fromTo('.m-mid', { y: 24 }, { y: 0, ease: 'none', scrollTrigger: sky });
  }

  // ---------- each gallery reveals its photos differently ----------
  // scenery: exposes up from the horizon like a sunrise · people: racks into focus · events: pops with a flash
  const FX = {
    expose: {
      from: { clipPath: 'inset(100% 0% 0% 0%)', filter: 'brightness(.2) sepia(.9) saturate(1.5)', scale: 1.14 },
      play: (img) => gsap.timeline()
        .to(img, { clipPath: 'inset(0% 0% 0% 0%)', duration: .9, ease: 'power3.inOut' })
        .to(img, { filter: 'brightness(1) sepia(0) saturate(1)', scale: 1, duration: 1.6, ease: 'power2.out', clearProps: 'filter,transform' }, '-=.5'),
    },
    focus: {
      from: { filter: 'blur(18px)', scale: 1.08, opacity: 0 },
      play: (img) => gsap.to(img, { filter: 'blur(0px)', scale: 1, opacity: 1, duration: 1.3, ease: 'power3.out', clearProps: 'filter,transform' }),
    },
    flash: {
      from: { opacity: 0 },
      play: (img, fig) => gsap.timeline()
        .set(img, { opacity: 1, filter: 'brightness(1.9) contrast(.8)' })
        .fromTo(fig.querySelector('.flash'), { opacity: .95 }, { opacity: 0, duration: .75, ease: 'expo.out' }, 0)
        .to(img, { filter: 'brightness(1) contrast(1)', duration: 1.1, ease: 'power2.out', clearProps: 'filter' }, 0),
    },
  };
  const fxOf = (fig) => FX[fig.closest('.set').dataset.fx] || FX.focus;
  document.querySelectorAll('.set--events .ph').forEach((fig) => { const f = document.createElement('i'); f.className = 'flash'; fig.appendChild(f); });
  if (!reduce) {
    // album cards: the cover reveals with its section's effect, the card behind it fans in after
    document.querySelectorAll('.acard').forEach((card) => {
      gsap.set(card.querySelector('.acard__cover'), fxOf(card).from);
      gsap.set(card.querySelectorAll('.acard__stack img:not(.acard__cover)'), { autoAlpha: 0 });
      gsap.set(card.querySelector('.acard__meta'), { autoAlpha: 0, x: -16 });
    });
    ScrollTrigger.batch('.acard', {
      start: 'top 88%', once: true,
      onEnter: (batch) => batch.forEach((card, i) => gsap.delayedCall(i * .14, () => {
        fxOf(card).play(card.querySelector('.acard__cover'), card);
        gsap.to(card.querySelectorAll('.acard__stack img:not(.acard__cover)'), { autoAlpha: 1, duration: .6, stagger: .12, delay: .5, clearProps: 'opacity,visibility' });
        gsap.to(card.querySelector('.acard__meta'), { autoAlpha: 1, x: 0, duration: .8, delay: .35, ease: 'power3.out', clearProps: 'all' });
      })),
    });
    document.querySelectorAll('.ph').forEach((fig) => gsap.set(fig.querySelector('img'), fxOf(fig).from));
    ScrollTrigger.batch('.ph', {
      start: 'top 92%', once: true,
      onEnter: (batch) => batch.forEach((fig, i) => gsap.delayedCall(i * .09, () => fxOf(fig).play(fig.querySelector('img'), fig))),
    });
  }
  // recent-events ticker: duplicate the items so the loop is seamless
  const track = document.querySelector('.recent__track');
  if (track) [...track.children].forEach((n) => { const c = n.cloneNode(true); c.setAttribute('aria-hidden', 'true'); track.appendChild(c); });
  gsap.utils.toArray('.set__head, .tips, .set__cta, .offer__grid .card, .steps li, .about__grid > *, .reach__card').forEach((el) => {
    gsap.from(el, { autoAlpha: 0, y: 40, duration: 1, ease: 'power3.out', scrollTrigger: { trigger: el, start: 'top 88%' } });
  });

  // ---------- filters ----------
  document.querySelectorAll('.chips').forEach((group) => {
    const grid = group.nextElementSibling;
    group.addEventListener('click', (e) => {
      const b = e.target.closest('.chip'); if (!b) return;
      group.querySelectorAll('.chip').forEach((c) => { c.classList.toggle('is-on', c === b); c.setAttribute('aria-pressed', c === b); });
      const v = b.dataset.filter;
      const figs = [...grid.children];
      gsap.to(grid, { autoAlpha: 0, duration: .2, onComplete: () => {
        figs.forEach((f) => { f.hidden = !(v === 'all' || f.dataset.tag === v); });
        figs.filter((f) => !f.hidden).forEach((f) => { gsap.set(f.querySelector('img'), { clearProps: 'all' }); });
        gsap.to(grid, { autoAlpha: 1, duration: .35 });
        ScrollTrigger.refresh();
      } });
    });
  });

  // ---------- viewfinder HUD ----------
  const hud = { ss: q('[data-hud="ss"]'), f: q('[data-hud="f"]'), iso: q('[data-hud="iso"]'), mm: q('[data-hud="mm"]'), n: q('[data-hud="n"]'), level: q('.hud__level i') };
  function q(s) { return document.querySelector(s); }
  const visible = new Set();
  const io = new IntersectionObserver((es) => es.forEach((e) => e.isIntersecting ? visible.add(e.target) : visible.delete(e.target)), { rootMargin: '-30% 0px -30% 0px' });
  document.querySelectorAll('.ph, .acard').forEach((f) => io.observe(f));
  let last = '';
  const setHud = (o) => {
    const key = o.f + o.ss + o.iso + o.mm + o.n; if (key === last) return; last = key;
    hud.ss.textContent = o.ss; hud.f.textContent = o.f; hud.iso.textContent = o.iso; hud.mm.textContent = o.mm; hud.n.textContent = o.n;
  };
  const onPaper = () => document.querySelector('.paper').getBoundingClientRect().top < innerHeight * .5;
  gsap.ticker.add(() => {
    root.classList.toggle('on-paper', onPaper());
    if (NB.hudOverride && !onPaper()) setHud(NB.hudOverride);
    else {
      let best = null, bd = Infinity;
      visible.forEach((f) => { const r = f.getBoundingClientRect(), d = Math.abs(r.top + r.height / 2 - innerHeight / 2); if (d < bd && !f.hidden) { bd = d; best = f; } });
      if (best) {
        const [fs, ss, iso, mm] = (best.matches('a') ? best : best.querySelector('a')).dataset.exif.split(' · ');
        setHud({ f: fs.replace('f/', 'F'), ss, iso, mm, n: best.dataset.n });
      }
    }
    const v = lenis ? lenis.velocity : 0;
    hud.level.style.transform = `rotate(${clamp(v * .35, -14, 14)}deg)`;
  });

  // ---------- AF reticle cursor ----------
  const af = document.querySelector('.af');
  if (fine && !reduce) {
    root.classList.add('has-af');
    const label = af.querySelector('.af__label');
    const st = { x: innerWidth / 2, y: innerHeight / 2, w: 44, h: 44, tx: 0, ty: 0, tw: 44, th: 44 };
    let target = null, mx = st.x, my = st.y;
    addEventListener('pointermove', (e) => { mx = e.clientX; my = e.clientY; }, { passive: true });
    document.addEventListener('pointerover', (e) => {
      const a = e.target.closest('.ph a, .strip__frame, .acard__stack');
      if (a !== target) {
        target = a; af.classList.toggle('is-locked', !!a);
        const ex = a && (a.dataset.exif || (a.closest('.acard') || {}).dataset?.exif); label.textContent = ex || '';
      }
      af.classList.toggle('is-link', !a && !!e.target.closest('a, button, .chip, input, select, textarea'));
    });
    gsap.ticker.add(() => {
      if (target && target.isConnected) {
        const r = target.getBoundingClientRect();
        st.tx = r.left - 6; st.ty = r.top - 6; st.tw = r.width + 12; st.th = r.height + 12;
      } else {
        const s = root.classList.contains('roll-hover') ? 70 : 44;
        st.tx = mx - s / 2; st.ty = my - s / 2; st.tw = s; st.th = s;
      }
      const k = target ? .22 : .35;
      st.x += (st.tx - st.x) * k; st.y += (st.ty - st.y) * k; st.w += (st.tw - st.w) * k; st.h += (st.th - st.h) * k;
      af.style.transform = `translate3d(${st.x}px, ${st.y}px, 0)`; af.style.width = st.w + 'px'; af.style.height = st.h + 'px';
    });
  }

  // ---------- nav jumps through the shutter ----------
  document.querySelectorAll('a[href^="#"]').forEach((a) => a.addEventListener('click', (e) => {
    const el = document.querySelector(a.getAttribute('href')); if (!el) return;
    e.preventDefault();
    if (reduce) { scrollToEl(el, true); return; }
    NB.shutter(() => { scrollToEl(el, true); ScrollTrigger.update(); });
  }));

  wireBasics();

  function wireBasics() {
    // lightbox
    const lb = document.querySelector('.lb');
    if (lb && typeof lb.showModal === 'function') {
      const links = [...document.querySelectorAll('.ph a')];
      const img = lb.querySelector('img'), cap = lb.querySelector('figcaption b'), exif = lb.querySelector('figcaption span');
      let list = links, i = 0;
      const show = (n) => {
        const items = list.filter((a) => !a.closest('[hidden]'));
        if (!items.length) return;
        i = (n + items.length) % items.length;
        const a = items[i];
        img.src = a.href; img.alt = a.dataset.cap; cap.textContent = a.dataset.cap; exif.textContent = a.dataset.exif;
        if (window.gsap) gsap.fromTo(img, { clipPath: 'inset(0% 0% 100% 0%)' }, { clipPath: 'inset(0% 0% 0% 0%)', duration: .55, ease: 'power3.inOut' });
      };
      const open = () => { lb.showModal(); lenis && lenis.stop(); };
      links.forEach((a) => a.addEventListener('click', (e) => { e.preventDefault(); list = links; lb.classList.remove('is-single'); show(list.filter((x) => !x.closest('[hidden]')).indexOf(a)); open(); }));
      NB.openSingle = (href, c, x) => {
        const a = document.createElement('a'); a.href = href; a.dataset.cap = c; a.dataset.exif = x;
        list = [a]; lb.classList.add('is-single'); show(0); open();
      };
      lb.querySelector('.lb__prev').addEventListener('click', () => show(i - 1));
      lb.querySelector('.lb__next').addEventListener('click', () => show(i + 1));
      lb.querySelector('.lb__x').addEventListener('click', () => lb.close());
      lb.addEventListener('click', (e) => { if (e.target === lb) lb.close(); });
      lb.addEventListener('close', () => { lenis && lenis.start(); });
      lb.addEventListener('keydown', (e) => { if (e.key === 'ArrowLeft') show(i - 1); if (e.key === 'ArrowRight') show(i + 1); });
    }
    // enquiry form: opens the visitor's email app with the details filled in
    const form = document.getElementById('enquiry');
    if (form) form.addEventListener('submit', (e) => {
      e.preventDefault();
      const d = Object.fromEntries(new FormData(form));
      const subject = `Photo enquiry: ${d.type}${d.date ? ' on ' + d.date : ''}`;
      const body = [`Hi Nathan,`, ``, `Shoot: ${d.type}`, `Date: ${d.date || 'flexible'}`, `Where: ${d.where || 'not sure yet'}`, ``, d.msg || '', ``, `${d.name}`, `${d.email}`, d.phone ? `${d.phone}` : ''].join('\n');
      window.location.href = `mailto:buithanhnhatstudent3@gmail.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    });
    document.querySelectorAll('[data-year]').forEach((el) => { el.textContent = new Date().getFullYear(); });
  }
})();

// the transition into an album
(() => {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const G = window.gsap && window.ScrollTrigger && !reduce;
  if (!G) return;

  // the way into an album: the picture you clicked grows to fill the screen, the title comes up, then the iris closes
  const leaveTo = (href, img, title, kicker, acc, titleIsHTML, tpl) => {
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
    // the place's stamp (uni or landmark) draws itself in the middle while the title comes up
    let stamp = null;
    if (tpl && tpl.content && tpl.content.firstElementChild) { stamp = document.createElement('div'); stamp.className = 'leave__stamp'; stamp.appendChild(tpl.content.cloneNode(true)); }
    ov.append(t); if (stamp) ov.append(stamp); ov.append(iris);
    Object.assign(ov.style, { left: r.left + 'px', top: r.top + 'px', width: r.width + 'px', height: r.height + 'px' });
    document.body.appendChild(ov);
    try { sessionStorage.setItem('nb-into', JSON.stringify({ src: new URL(full, location.href).href, acc })); } catch (e) {}
    const tl = gsap.timeline({ onComplete: () => { location.href = href; } })
      .to(ov, { left: 0, top: 0, width: innerWidth, height: innerHeight, duration: .8, ease: 'expo.inOut' })
      .fromTo(im, { scale: 1.18 }, { scale: 1, duration: 1.2, ease: 'power2.out' }, 0)
      .fromTo(t, { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: .5, ease: 'power3.out' }, .55);
    let close = 1.2;
    if (stamp) {
      const lines = [...stamp.querySelectorAll('.pstamp__m path, .pstamp__m circle, .pstamp__o')];
      lines.forEach((el) => { const L = el.getTotalLength ? Math.ceil(el.getTotalLength()) : 300; el.style.strokeDasharray = L; el.style.strokeDashoffset = L; });
      gsap.set(stamp, { xPercent: -50, yPercent: -50 });
      tl.fromTo(stamp, { opacity: 0, scale: .72 }, { opacity: 1, scale: 1, duration: .6, ease: 'back.out(1.6)' }, .5)
        .to(lines, { strokeDashoffset: 0, duration: .9, stagger: .025, ease: 'power2.inOut' }, .55)
        .fromTo(stamp.querySelector('.pstamp__spin'), { rotation: -120, svgOrigin: '60 60' }, { rotation: 0, svgOrigin: '60 60', duration: 1.6, ease: 'power3.out' }, .5)
        .fromTo(stamp.querySelectorAll('.pstamp__t, .pstamp__i'), { opacity: 0 }, { opacity: 1, duration: .5 }, .75);
      close = 1.9;
    }
    tl.to(iris, { '--r': '0vmax', duration: .55, ease: 'power3.in' }, close);
  };
  addEventListener('pageshow', (e) => { if (e.persisted) document.querySelectorAll('.leave').forEach((n) => n.remove()); });
  const plainClick = (e) => !(e.defaultPrevented || e.button || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey);

  document.addEventListener('click', (e) => {
    const a = e.target.closest('a.acard');
    if (!a || !plainClick(e)) return;
    e.preventDefault();
    const acc = getComputedStyle(a).getPropertyValue('--acc').trim();
    leaveTo(a.href, a.querySelector('.acard__cover'), a.querySelector('.acard__meta b').innerHTML, a.querySelector('.acard__meta small').textContent, acc, true, a.querySelector('template.stamp-tpl'));
  });
})();

// home floaters: nearer drawings (bigger --d) slide faster as the Portrait section scrolls past
(() => {
  if (!window.gsap || !window.ScrollTrigger || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  document.querySelectorAll('.set .floaters .fl').forEach((f) => {
    const d = parseFloat(getComputedStyle(f).getPropertyValue('--d')) || .5;
    gsap.fromTo(f, { y: d * 160 }, { y: -d * 220, ease: 'none', scrollTrigger: { trigger: f.closest('.set'), start: 'top bottom', end: 'bottom top', scrub: .6 } });
  });
})();

// mstrip hint: on phones the roll nudges once when it comes into view so people know it swipes
(() => {
  const tr = document.querySelector('.mstrip__track');
  if (!tr || matchMedia('(prefers-reduced-motion: reduce)').matches || !('IntersectionObserver' in window)) return;
  const io = new IntersectionObserver((es) => es.forEach((e) => {
    if (!e.isIntersecting) return; io.disconnect();
    setTimeout(() => { tr.scrollTo({ left: tr.clientWidth * .6, behavior: 'smooth' }); setTimeout(() => tr.scrollTo({ left: 0, behavior: 'smooth' }), 900); }, 400);
  }), { threshold: .6 });
  io.observe(tr);
})();

// nav: mark the section in view, so phones show where you are
(() => {
  const links = [...document.querySelectorAll('.nav__link:not(.nav__cta)')];
  const secs = links.map((a) => document.querySelector(a.getAttribute('href'))).filter(Boolean);
  if (!secs.length || !('IntersectionObserver' in window)) return;
  const io = new IntersectionObserver((es) => es.forEach((e) => {
    if (!e.isIntersecting) return;
    links.forEach((a) => a.toggleAttribute('aria-current', a.getAttribute('href') === '#' + e.target.id));
    links.forEach((a) => a.getAttribute('aria-current') !== null && a.setAttribute('aria-current', 'true'));
  }), { rootMargin: '-45% 0px -50% 0px' });
  secs.forEach((s) => io.observe(s));
})();

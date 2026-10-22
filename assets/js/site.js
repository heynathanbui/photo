// Nathan Bui — Photography. Without JS every photo link still opens the full image.
document.documentElement.classList.add('js');

// Reveal photos as they scroll in
(() => {
  const items = document.querySelectorAll('.ph');
  if (!('IntersectionObserver' in window)) { items.forEach((el) => el.classList.add('in')); return; }
  const io = new IntersectionObserver((entries) => entries.forEach((e) => {
    if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
  }), { rootMargin: '0px 0px -8% 0px' });
  items.forEach((el) => io.observe(el));
})();

// Lightbox, stepping through every photo on the page
(() => {
  const lb = document.querySelector('.lb');
  if (!lb || typeof lb.showModal !== 'function') return;
  const links = [...document.querySelectorAll('.ph a')];
  const img = lb.querySelector('img'), cap = lb.querySelector('figcaption b'), exif = lb.querySelector('figcaption span');
  let i = 0;
  const show = (n) => {
    i = (n + links.length) % links.length;
    const a = links[i];
    img.src = a.href; img.alt = a.dataset.cap;
    cap.textContent = a.dataset.cap; exif.textContent = a.dataset.exif;
  };
  links.forEach((a, n) => a.addEventListener('click', (e) => { e.preventDefault(); show(n); lb.showModal(); }));
  lb.querySelector('.lb__prev').addEventListener('click', () => show(i - 1));
  lb.querySelector('.lb__next').addEventListener('click', () => show(i + 1));
  lb.querySelector('.lb__x').addEventListener('click', () => lb.close());
  lb.addEventListener('click', (e) => { if (e.target === lb) lb.close(); });
  lb.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowLeft') show(i - 1);
    if (e.key === 'ArrowRight') show(i + 1);
  });
})();

// Enquiry form: no server, so it opens the visitor's email app with the details filled in
(() => {
  const form = document.getElementById('enquiry');
  if (!form) return;
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const d = Object.fromEntries(new FormData(form));
    const subject = `Photo enquiry: ${d.type}${d.date ? ' on ' + d.date : ''}`;
    const body = [
      `Hi Nathan,`, ``,
      `Shoot: ${d.type}`, `Date: ${d.date || 'flexible'}`, ``,
      d.msg || '', ``,
      `${d.name}`, `${d.email}`,
    ].join('\n');
    window.location.href = `mailto:buithanhnhatstudent3@gmail.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
  });
})();

document.querySelectorAll('[data-year]').forEach((el) => { el.textContent = new Date().getFullYear(); });

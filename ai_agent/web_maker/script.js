'use strict';

/* ── Nav scroll shadow ──────────────────────────────────────── */
const nav = document.getElementById('nav');
window.addEventListener('scroll', () => {
  nav.classList.toggle('scrolled', window.scrollY > 20);
}, { passive: true });

/* ── Mobile menu ────────────────────────────────────────────── */
const burger = document.querySelector('.nav__burger');
const navLinks = document.querySelector('.nav__links');
burger?.addEventListener('click', () => {
  const open = navLinks.classList.toggle('open');
  burger.setAttribute('aria-expanded', String(open));
  burger.querySelectorAll('span')[0].style.transform = open ? 'rotate(45deg) translate(4px, 4px)' : '';
  burger.querySelectorAll('span')[1].style.transform = open ? 'rotate(-45deg) translate(4px, -4px)' : '';
});
navLinks?.querySelectorAll('a').forEach(a =>
  a.addEventListener('click', () => {
    navLinks.classList.remove('open');
    burger.setAttribute('aria-expanded', 'false');
    burger.querySelectorAll('span').forEach(s => s.style.transform = '');
  })
);

/* ── Active nav link ────────────────────────────────────────── */
const sections = document.querySelectorAll('section[id]');
const navAnchors = document.querySelectorAll('.nav__links a');
const navObserver = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      navAnchors.forEach(a => a.classList.remove('active'));
      document.querySelector(`.nav__links a[href="#${e.target.id}"]`)?.classList.add('active');
    }
  });
}, { rootMargin: '-40% 0px -55% 0px' });
sections.forEach(s => navObserver.observe(s));

/* ── Reveal on scroll ───���───────────────────────────────────── */
const reveals = document.querySelectorAll('.reveal');
const revealObserver = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (!e.isIntersecting) return;
    const delay = parseInt(e.target.dataset.delay || 0);
    setTimeout(() => e.target.classList.add('in'), delay);
    revealObserver.unobserve(e.target);
  });
}, { threshold: 0.1 });
reveals.forEach(el => revealObserver.observe(el));

/* ── Stat counters ──────────────────────────────────────────── */
function runCounter(el) {
  const target = parseFloat(el.dataset.count);
  const dec = parseInt(el.dataset.dec ?? 0);
  const prefix = el.dataset.prefix ?? '';
  const duration = 1800;
  const start = performance.now();
  const easeOut = t => 1 - Math.pow(1 - t, 4);

  function tick(now) {
    const p = Math.min((now - start) / duration, 1);
    const val = target * easeOut(p);
    el.textContent = prefix + (dec > 0 ? val.toFixed(dec) : Math.round(val).toLocaleString());
    if (p < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

const statObserver = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (!e.isIntersecting) return;
    runCounter(e.target);
    statObserver.unobserve(e.target);
  });
}, { threshold: 0.5 });
document.querySelectorAll('.stat__num').forEach(el => statObserver.observe(el));

/* ── Revenue bars (animate width on scroll) ─────────────────── */
const barObserver = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (!e.isIntersecting) return;
    e.target.querySelectorAll('.bar-fill').forEach(bar => {
      const target = bar.style.getPropertyValue('--w');
      bar.style.width = '0';
      requestAnimationFrame(() => {
        bar.style.transition = 'width 1.2s cubic-bezier(0.16,1,0.3,1)';
        bar.style.width = target;
      });
    });
    barObserver.unobserve(e.target);
  });
}, { threshold: 0.3 });
document.querySelectorAll('.fin__bars').forEach(el => barObserver.observe(el));

/* ── Smooth scroll offset for fixed nav ─────────────────────── */
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    const target = document.querySelector(a.getAttribute('href'));
    if (!target) return;
    e.preventDefault();
    const offset = nav.offsetHeight + 16;
    window.scrollTo({ top: target.offsetTop - offset, behavior: 'smooth' });
  });
});

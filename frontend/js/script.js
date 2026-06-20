// ============================================
//   KEL VAL CLAUDE — DIGITAL HQ
//   script.js v2 — FULLY WIRED TO BACKEND
// ============================================

const API = ''; // Same origin — Flask serves both

// ============================================
//   1. PARTICLE SYSTEM
// ============================================
const canvas = document.getElementById('particleCanvas');
const ctx    = canvas.getContext('2d');
let particles = [], W, H;

function resizeCanvas() { W = canvas.width = window.innerWidth; H = canvas.height = window.innerHeight; }
resizeCanvas();
window.addEventListener('resize', resizeCanvas);

class Particle {
  constructor() { this.reset(); }
  reset() {
    this.x = Math.random() * W; this.y = Math.random() * H;
    this.size = Math.random() * 1.5 + 0.3;
    this.speedX = (Math.random() - 0.5) * 0.3; this.speedY = (Math.random() - 0.5) * 0.3;
    this.alpha = Math.random() * 0.12 + 0.03; this.gold = Math.random() > 0.85;
  }
  update() { this.x += this.speedX; this.y += this.speedY; if (this.x<0||this.x>W||this.y<0||this.y>H) this.reset(); }
  draw() {
    ctx.beginPath(); ctx.arc(this.x, this.y, this.size, 0, Math.PI*2);
    ctx.fillStyle = this.gold ? `rgba(212,175,55,${this.alpha*1.5})` : `rgba(255,255,255,${this.alpha})`;
    ctx.fill();
  }
}

for (let i = 0; i < 120; i++) particles.push(new Particle());

function drawConnections() {
  for (let i = 0; i < particles.length; i++) {
    for (let j = i+1; j < particles.length; j++) {
      const dx = particles[i].x - particles[j].x, dy = particles[i].y - particles[j].y;
      const dist = Math.sqrt(dx*dx + dy*dy);
      if (dist < 100) {
        ctx.beginPath(); ctx.moveTo(particles[i].x, particles[i].y); ctx.lineTo(particles[j].x, particles[j].y);
        ctx.strokeStyle = `rgba(212,175,55,${0.04*(1-dist/100)})`; ctx.lineWidth = 0.5; ctx.stroke();
      }
    }
  }
}

function animateParticles() { ctx.clearRect(0,0,W,H); particles.forEach(p=>{p.update();p.draw();}); drawConnections(); requestAnimationFrame(animateParticles); }
animateParticles();

// ============================================
//   2. NAVBAR
// ============================================
const navbar = document.getElementById('navbar');
const hamburger = document.getElementById('hamburger');
const mobileMenu = document.getElementById('mobileMenu');

window.addEventListener('scroll', () => {
  navbar.style.borderBottomColor = window.scrollY > 30 ? 'rgba(212,175,55,0.15)' : 'rgba(255,255,255,0.06)';
});

hamburger.addEventListener('click', () => mobileMenu.classList.toggle('open'));
mobileMenu.querySelectorAll('a').forEach(a => a.addEventListener('click', () => mobileMenu.classList.remove('open')));

// ============================================
//   3. ANIMATED COUNTER
// ============================================
function animateCounter(el, target, duration=1800) {
  if (!el) return;
  let start = null;
  function step(ts) {
    if (!start) start = ts;
    const progress = Math.min((ts - start) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    el.textContent = Math.floor(eased * target);
    if (progress < 1) requestAnimationFrame(step); else el.textContent = target;
  }
  requestAnimationFrame(step);
}

const counterObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting && !entry.target.dataset.animated) {
      entry.target.dataset.animated = 'true';
      animateCounter(entry.target, parseInt(entry.target.dataset.target || entry.target.textContent));
    }
  });
}, { threshold: 0.4 });

// ============================================
//   4. SKILL BARS
// ============================================
const skillObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting && !entry.target.dataset.animated) {
      entry.target.dataset.animated = 'true';
      entry.target.querySelectorAll('.skill-fill').forEach(fill => {
        setTimeout(() => { fill.style.width = fill.dataset.width + '%'; }, 200);
      });
    }
  });
}, { threshold: 0.3 });

const techSection = document.querySelector('.techstack');
if (techSection) skillObserver.observe(techSection);

// ============================================
//   5. SCROLL REVEAL
// ============================================
const revealTargets = document.querySelectorAll(
  '.service-card,.ach-card,.future-card,.partner-card,.review-card,.contact-box,.process-step,.status-item,.faq-item,.profile-card,.about-card'
);
revealTargets.forEach((el, i) => {
  el.classList.add('reveal');
  el.style.transitionDelay = `${(i % 4) * 80}ms`;
});
const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => { if (entry.isIntersecting) entry.target.classList.add('visible'); });
}, { threshold: 0.1 });
revealTargets.forEach(el => revealObserver.observe(el));

// ============================================
//   6. FAQ
// ============================================
function toggleFaq(btn) {
  const answer = btn.nextElementSibling;
  const isOpen = answer.classList.contains('open');
  document.querySelectorAll('.faq-a').forEach(a => a.classList.remove('open'));
  document.querySelectorAll('.faq-q').forEach(q => q.classList.remove('open'));
  if (!isOpen) { answer.classList.add('open'); btn.classList.add('open'); }
}

// ============================================
//   7. SMOOTH SCROLL
// ============================================
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    const target = document.querySelector(a.getAttribute('href'));
    if (target) { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth' }); }
  });
});

// ============================================
//   8. TRACK CONTACT CLICKS
// ============================================
function trackClick(type) {
  fetch(`${API}/api/analytics/click`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ type, source: 'contact_hub' })
  }).catch(() => {});
}

// Track portfolio views
function trackView(project) {
  fetch(`${API}/api/analytics/view`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ project })
  }).catch(() => {});
  // Also count page visit
  fetch(`${API}/api/analytics/click`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ type: 'portfolio_view', source: project })
  }).catch(() => {});
}

// ============================================
//   9. LOAD PROFILE FROM API
// ============================================
async function loadProfile() {
  try {
    const data = await fetch(`${API}/api/profile`).then(r => r.json());

    // Hero card stats — animate them
    const statProjects = document.getElementById('stat-projects');
    const statPartners = document.getElementById('stat-partners');
    const statDeals    = document.getElementById('stat-deals');

    if (statProjects) { statProjects.dataset.target = data.projects_built; counterObserver.observe(statProjects); }
    if (statPartners) { statPartners.dataset.target = data.partnerships;   counterObserver.observe(statPartners); }
    if (statDeals)    { statDeals.dataset.target    = data.deals_closed;    counterObserver.observe(statDeals); }

    // Achievement counters
    const achMap = {
      'ach-projects': data.projects_built,
      'ach-deals':    data.deals_closed,
      'ach-hours':    data.hours_saved,
      'ach-systems':  data.systems_built,
      'ach-bots':     data.bots_created,
      'ach-tasks':    data.tasks_automated,
    };
    Object.entries(achMap).forEach(([id, val]) => {
      const el = document.getElementById(id);
      if (el) { el.dataset.target = val; counterObserver.observe(el); }
    });

    // Focus tags
    const focusTags = document.getElementById('focusTags');
    if (focusTags && data.current_focus) {
      focusTags.innerHTML = data.current_focus.split(',').map(f =>
        `<span>${f.trim()}</span>`
      ).join('');
    }

  } catch(e) {
    console.warn('[KEL HQ] Profile API unavailable — using static values');
    // Fallback: animate static values already in HTML
    ['ach-projects','ach-deals','ach-hours','ach-systems','ach-bots','ach-tasks'].forEach(id => {
      const el = document.getElementById(id);
      if (el) { el.dataset.target = el.textContent || 0; counterObserver.observe(el); }
    });
  }
}

// ============================================
//   10. LOAD AVAILABILITY FROM API
// ============================================
async function loadAvailability() {
  try {
    const data = await fetch(`${API}/api/status`).then(r => r.json());
    const isAvail = data.status === 'available';

    // Navbar status
    const navDot  = document.getElementById('navStatusDot');
    const navText = document.getElementById('navStatusText');
    if (navDot)  { navDot.style.background  = isAvail ? 'var(--green)' : 'var(--yellow)'; }
    if (navText) { navText.textContent = isAvail ? 'Available' : 'Booked'; navText.style.color = isAvail ? 'var(--green)' : 'var(--yellow)'; }

    // Profile card status
    const pDot   = document.getElementById('pstatusDot');
    const pText  = document.getElementById('pstatusText');
    const pLabel = document.getElementById('pstatusLabel');
    const pBar   = document.getElementById('profileStatusBar');

    if (pDot)   { pDot.style.background = isAvail ? 'var(--green)' : 'var(--yellow)'; }
    if (pText)  { pText.textContent = isAvail ? 'Available' : 'Booked'; pText.style.color = isAvail ? 'var(--green)' : 'var(--yellow)'; }
    if (pLabel) { pLabel.textContent = isAvail ? 'Open for new projects' : `Next: ${data.next_opening || 'TBD'}`; }
    if (pBar)   { pBar.style.borderColor = isAvail ? 'rgba(46,204,113,0.15)' : 'rgba(241,196,15,0.15)'; pBar.style.background = isAvail ? 'rgba(46,204,113,0.06)' : 'rgba(241,196,15,0.05)'; }

    // Availability section
    const availDot  = document.getElementById('availDot');
    const availMode = document.getElementById('availMode');
    const availText = document.getElementById('availStatusText');
    const availNext = document.getElementById('availNextText');
    const availCard = document.getElementById('availCard');
    const availUpd  = document.getElementById('availUpdated');

    if (availDot)  { availDot.className = 'avail-dot'; availDot.classList.add(isAvail ? 'available-dot' : 'booked-dot'); }
    if (availMode) { availMode.textContent = isAvail ? 'AVAILABLE MODE' : 'BOOKED MODE'; availMode.style.color = isAvail ? 'var(--green)' : 'var(--yellow)'; }
    if (availText) { availText.textContent = isAvail ? 'Available For New Projects' : 'Currently Booked'; }
    if (availNext) { availNext.textContent = !isAvail && data.next_opening ? `Next Opening: ${data.next_opening}` : ''; }
    if (availCard) { availCard.style.borderColor = isAvail ? 'rgba(46,204,113,0.2)' : 'rgba(241,196,15,0.2)'; }
    if (availUpd && data.last_updated) { availUpd.textContent = `Last Updated · ${data.last_updated.slice(0,10)}`; }

  } catch(e) {
    console.warn('[KEL HQ] Status API unavailable');
  }
}

// ============================================
//   11. LOAD PROJECTS FROM API
// ============================================
const CATEGORY_COLORS = {
  'Website':    { bg: '#FFF8F0', strip: '#8B5E3C', mcs: 'rgba(139,94,60,0.2)', dark: false },
  'E-Commerce': { bg: 'linear-gradient(135deg,#0D0D0D,#0f1729)', strip: '#3B82F6', mcs: 'rgba(59,130,246,0.2)', dark: true },
  'SaaS':       { bg: 'linear-gradient(135deg,#0D0D0D,#0a0f1e)', strip: '#8B5CF6', mcs: 'rgba(139,92,246,0.2)', dark: true },
  'Bot':        { bg: 'linear-gradient(135deg,#0D0D0D,#0a1a0a)', strip: '#2ECC71', mcs: 'rgba(46,204,113,0.2)', dark: true },
  'default':    { bg: 'linear-gradient(135deg,#111,#1a1a1a)', strip: '#D4AF37', mcs: 'rgba(212,175,55,0.2)', dark: true },
};

async function loadProjects() {
  const grid = document.getElementById('portfolioGrid');
  if (!grid) return;

  try {
    const projects = await fetch(`${API}/api/projects`).then(r => r.json());

    if (!projects.length) { grid.innerHTML = '<p style="color:var(--muted)">No projects yet.</p>'; return; }

    const firstFeatured = projects.find(p => p.complexity === 'High') || projects[0];

    grid.innerHTML = projects.map((p, i) => {
      const style = CATEGORY_COLORS[p.category] || CATEGORY_COLORS['default'];
      const isFeatured = p.id === firstFeatured.id;
      const tags = (p.tags || '').split(',').map(t => `<span>${t.trim()}</span>`).join('');
      const mockStyle = style.dark
        ? `background:${style.bg}`
        : `background:${style.bg}`;

      return `
        <div class="port-card ${isFeatured ? 'featured-port' : ''}">
          ${isFeatured ? '<div class="port-badge">⭐ Featured</div>' : ''}
          <div class="port-preview">
            <div class="port-preview-mockup" style="${mockStyle}">
              <div class="mock-bar ${style.dark ? 'dark-bar' : ''}"><span></span><span></span><span></span></div>
              <div class="mock-hero-strip" style="color:${style.strip}">${p.title}</div>
              <div class="mock-content-strips ${style.dark ? 'dark-strips' : ''}">
                <div class="mcs" style="background:${style.mcs}"></div>
                <div class="mcs short" style="background:${style.mcs}"></div>
                <div class="mcs" style="background:${style.mcs}"></div>
              </div>
            </div>
          </div>
          <div class="port-info">
            <div class="port-meta">
              <span class="port-cat">${p.category || 'Project'}</span>
              <span class="port-complexity ${p.complexity === 'High' ? 'high' : ''}">${p.complexity || 'Medium'}</span>
            </div>
            <h3>${p.title}</h3>
            <p>${p.description || ''}</p>
            <div class="port-tags">${tags}</div>
            <div class="port-footer">
              <span class="port-time">⏱ ${p.duration || 'Custom'}</span>
              ${p.link ? `<a href="${p.link}" class="btn btn-gold port-btn" target="_blank" onclick="trackView('${p.title}')">View Project</a>` : '<span class="port-time" style="color:var(--gold)">In Dev</span>'}
            </div>
          </div>
        </div>`;
    }).join('');

  } catch(e) {
    console.warn('[KEL HQ] Projects API unavailable');
    grid.innerHTML = `
      <div class="port-card"><div class="port-preview"><div class="port-preview-mockup bakery-mock"><div class="mock-bar"><span></span><span></span><span></span></div><div class="mock-hero-strip">🍰 Crust Bakery</div><div class="mock-content-strips"><div class="mcs warm"></div><div class="mcs warm short"></div><div class="mcs warm"></div></div></div></div><div class="port-info"><div class="port-meta"><span class="port-cat">Website</span><span class="port-complexity">Medium</span></div><h3>🍰 Crust Bakery</h3><p>Modern bakery showcase.</p><div class="port-tags"><span>HTML</span><span>CSS</span><span>JS</span></div><div class="port-footer"><span class="port-time">⏱ 1 Day</span><a href="../crust-bakery/index.html" class="btn btn-gold port-btn" target="_blank">View Project</a></div></div></div>
      <div class="port-card featured-port"><div class="port-badge">⭐ Featured</div><div class="port-preview"><div class="port-preview-mockup volt-mock"><div class="mock-bar dark-bar"><span></span><span></span><span></span></div><div class="mock-hero-strip dark-strip">⚡ Volt Electronics</div><div class="mock-content-strips dark-strips"><div class="mcs dark-mcs"></div><div class="mcs dark-mcs short"></div><div class="mcs dark-mcs"></div></div></div></div><div class="port-info"><div class="port-meta"><span class="port-cat">E-Commerce</span><span class="port-complexity high">High</span></div><h3>⚡ Volt Electronics</h3><p>Full electronics marketplace.</p><div class="port-tags"><span>HTML</span><span>CSS</span><span>JS</span></div><div class="port-footer"><span class="port-time">⏱ 2 Days</span><a href="../volt-electronics/index.html" class="btn btn-gold port-btn" target="_blank">View Project</a></div></div></div>
      <div class="port-card"><div class="port-preview"><div class="port-preview-mockup timely-mock"><div class="mock-bar dark-bar"><span></span><span></span><span></span></div><div class="mock-hero-strip timely-strip">🧠 TIMELY AI</div><div class="mock-content-strips dark-strips"><div class="mcs blue-mcs"></div><div class="mcs blue-mcs short"></div><div class="mcs blue-mcs"></div></div></div></div><div class="port-info"><div class="port-meta"><span class="port-cat">SaaS</span><span class="port-complexity high">High</span></div><h3>🧠 TIMELY AI</h3><p>AI productivity SaaS platform.</p><div class="port-tags"><span>HTML</span><span>CSS</span><span>JS</span></div><div class="port-footer"><span class="port-time">⏱ 1 Day</span><a href="../timely-ai/index.html" class="btn btn-gold port-btn" target="_blank">View Project</a></div></div></div>`;
  }
}

// ============================================
//   12. LOAD PARTNERS FROM API
// ============================================
async function loadPartners() {
  const grid = document.getElementById('partnersGrid');
  if (!grid) return;

  try {
    const partners = await fetch(`${API}/api/partners`).then(r => r.json());

    grid.innerHTML = partners.map((p, i) => `
      <div class="partner-card ${i === 0 ? 'gold-partner' : ''}">
        <div class="partner-type">${p.type}</div>
        <div class="partner-logo">${p.name}</div>
        <p>${p.description || ''}</p>
        <a href="${p.url || '#'}" class="btn ${i === 0 ? 'btn-gold' : 'btn-outline'}" target="_blank">Visit →</a>
      </div>`).join('') + `
      <div class="partner-card open-partner">
        <div class="partner-type">Open Slot</div>
        <div class="partner-logo open-logo">+ Open Partnership</div>
        <p>Available for collaboration with developers, studios, and digital agencies aligned with our ecosystem vision.</p>
        <a href="#contact" class="btn btn-outline">Get In Touch →</a>
      </div>`;

  } catch(e) {
    console.warn('[KEL HQ] Partners API unavailable');
    grid.innerHTML = `
      <div class="partner-card gold-partner"><div class="partner-type">Ecosystem Partner</div><div class="partner-logo">SILENCE <span>&lt;/&gt;</span> SYS</div><p>Core technology ecosystem powering digital systems and automation infrastructure.</p><a href="#" class="btn btn-gold">Visit →</a></div>
      <div class="partner-card"><div class="partner-type">Strategic Partner</div><div class="partner-logo">SILENCE <span>//</span> FED</div><p>Strategic federation for collaborative development and ecosystem expansion.</p><a href="#" class="btn btn-outline">Visit →</a></div>
      <div class="partner-card open-partner"><div class="partner-type">Open Slot</div><div class="partner-logo open-logo">+ Open Partnership</div><p>Available for collaboration.</p><a href="#contact" class="btn btn-outline">Get In Touch →</a></div>`;
  }
}

// ============================================
//   13. LOAD REVIEWS FROM API
// ============================================
async function loadReviews() {
  const grid = document.getElementById('reviewsGrid');
  if (!grid) return;

  try {
    const reviews = await fetch(`${API}/api/reviews`).then(r => r.json());

    grid.innerHTML = reviews.map(r => `
      <div class="review-card ${r.featured ? 'featured-review' : ''}">
        <div class="review-stars">${'★'.repeat(r.rating)}${'☆'.repeat(5 - r.rating)}</div>
        <p>"${r.content}"</p>
        <div class="review-author">
          <div class="rv-av">${r.name.charAt(0)}</div>
          <div><strong>${r.name}</strong><small>${r.role || ''}</small></div>
        </div>
      </div>`).join('');

    // Update average rating
    if (reviews.length) {
      const avg = (reviews.reduce((s, r) => s + r.rating, 0) / reviews.length).toFixed(1);
      const avgEl = document.getElementById('avgRating');
      const cntEl = document.getElementById('reviewCount');
      if (avgEl) avgEl.textContent = avg;
      if (cntEl) cntEl.textContent = `Based on ${reviews.length} review${reviews.length !== 1 ? 's' : ''}`;
    }

  } catch(e) {
    console.warn('[KEL HQ] Reviews API unavailable — using static');
    grid.innerHTML = `
      <div class="review-card featured-review"><div class="review-stars">★★★★★</div><p>"Professional work from start to finish. Kel understood exactly what I needed and delivered a system that exceeded my expectations."</p><div class="review-author"><div class="rv-av">A</div><div><strong>Amara O.</strong><small>Business Owner</small></div></div></div>
      <div class="review-card"><div class="review-stars">★★★★★</div><p>"Fast delivery and clean architecture. My Telegram bot was done in 2 days and worked perfectly."</p><div class="review-author"><div class="rv-av">T</div><div><strong>Taiwo A.</strong><small>Startup Founder</small></div></div></div>
      <div class="review-card"><div class="review-stars">★★★★★</div><p>"The automation system saves my team hours every week. Excellent communication throughout."</p><div class="review-author"><div class="rv-av">D</div><div><strong>David K.</strong><small>Operations Lead</small></div></div></div>
      <div class="review-card"><div class="review-stars">★★★★★</div><p>"Clean code, fast turnaround, and a developer who thinks about your business goals."</p><div class="review-author"><div class="rv-av">C</div><div><strong>Chidi E.</strong><small>Agency Director</small></div></div></div>`;
  }
}

// ============================================
//   14. LOAD ANNOUNCEMENT BANNER
// ============================================
async function loadAnnouncement() {
  try {
    const data = await fetch(`${API}/api/announcements`).then(r => r.json());
    if (data.length) {
      const banner = document.getElementById('announceBanner');
      const text   = document.getElementById('announceText');
      if (banner && text) {
        text.textContent = data[0].message;
        banner.style.display = 'flex';
        banner.dataset.type  = data[0].type;
      }
    }
  } catch(e) {}
}

// ============================================
//   15. BOOK APPOINTMENT FORM
// ============================================
async function submitBooking(e) {
  e.preventDefault();
  const note = document.getElementById('bfNote');
  const btn  = e.target.querySelector('button[type=submit]');

  btn.textContent = 'Sending...';
  btn.disabled    = true;

  try {
    const res = await fetch(`${API}/api/appointments/book`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name:    document.getElementById('bf-name').value,
        contact: document.getElementById('bf-contact').value,
        service: document.getElementById('bf-service').value,
        message: document.getElementById('bf-message').value,
      })
    });
    const data = await res.json();

    if (data.ok) {
      note.textContent = '✅ Request sent! I\'ll reach out shortly.';
      note.style.color = 'var(--green)';
      e.target.reset();
    } else {
      note.textContent = data.error || 'Something went wrong. Try again.';
      note.style.color = 'var(--red)';
    }
  } catch(err) {
    note.textContent = 'Could not connect. Please message me directly.';
    note.style.color = 'var(--yellow)';
  }

  btn.textContent = 'Send Request 🚀';
  btn.disabled    = false;
}

// ============================================
//   16. TRACK PAGE VISIT
// ============================================
function trackPageVisit() {
  fetch(`${API}/api/analytics/click`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ type: 'page_visit', source: document.referrer || 'direct' })
  }).catch(() => {});
}

// ============================================
//   INIT — Load everything on page load
// ============================================
document.addEventListener('DOMContentLoaded', () => {
  trackPageVisit();
  loadProfile();
  loadAvailability();
  loadProjects();
  loadPartners();
  loadReviews();
  loadAnnouncement();
});

// Verified badge hover
const vb = document.querySelector('.verified-badge');
if (vb) { vb.style.transition = 'transform 0.3s ease, box-shadow 0.3s ease'; vb.addEventListener('mouseover', () => { vb.style.transform = 'rotate(15deg) scale(1.15)'; }); vb.addEventListener('mouseout', () => { vb.style.transform = ''; }); }

// Ecosystem node click
document.querySelectorAll('.eco-node:not(.root-node)').forEach(node => {
  node.addEventListener('click', () => {
    node.style.background = 'var(--gold-soft)'; node.style.borderColor = 'var(--gold)'; node.style.color = 'var(--gold)';
    setTimeout(() => { node.style.background = ''; node.style.borderColor = ''; node.style.color = ''; }, 1000);
  });
});

console.log('%c KEL VAL CLAUDE · DIGITAL HQ v2 ', 'background:#D4AF37;color:#0A0A0A;font-weight:700;font-size:14px;padding:4px 8px;');
console.log('%c Fully wired. Backend connected.', 'color:#D4AF37;font-size:11px;');



// ============================================
//   v7 UPDATES
// ============================================

// ---- DYNAMIC CONTACT GRID ----
// All 8 possible contact types with metadata
const CONTACT_TYPES = [
  { key: 'contact_wa',      label: 'WA',      name: 'WhatsApp',  icon: '💬', action: 'Message →',  gold: false },
  { key: 'contact_tg',      label: 'TG',      name: 'Telegram',  icon: '✈️',  action: 'Chat →',     gold: false },
  { key: 'contact_channel', label: 'CH',      name: 'Channel',   icon: '📢', action: 'Follow →',   gold: false },
  { key: 'contact_github',  label: 'GH',      name: 'GitHub',    icon: '⌨️',  action: 'View →',     gold: false },
  { key: 'contact_facebook',label: 'FB',      name: 'Facebook',  icon: '📘', action: 'Connect →',  gold: false },
  { key: 'contact_discord', label: 'DC',      name: 'Discord',   icon: '🎮', action: 'Join →',     gold: false },
  { key: 'contact_x',       label: 'X',       name: 'X / Twitter',icon: '✕', action: 'Follow →',  gold: false },
  { key: 'contact_email',   label: 'MAIL',    name: 'Email',     icon: '📧', action: 'Email →',    gold: true  },
];

function loadContactGrid() {
  const grid = document.getElementById('contactGrid');
  if (!grid) return;

  // Load from API settings
  fetch(`${API}/api/settings`, { credentials: 'include' })
    .then(r => r.ok ? r.json() : {})
    .then(settings => {
      const visibleLinks = CONTACT_TYPES.filter(c => {
        const val = settings[c.key] || '';
        // Only show if link is set and not a placeholder
        return val && val !== '' &&
               !val.includes('XXXXXXXXXX') &&
               !val.includes('kelvalclaude') === false || // allow real links
               val.startsWith('http') || val.startsWith('mailto');
      });

      // Actually: show if value is non-empty and not a dummy placeholder
      const filtered = CONTACT_TYPES.filter(c => {
        const val = (settings[c.key] || '').trim();
        return val !== '' && !val.includes('XXXXXXXXXX');
      });

      if (!filtered.length) {
        grid.innerHTML = '<p style="color:var(--muted);font-size:0.85rem">Contact links not set yet. Add them in Command Center → Site Settings.</p>';
        return;
      }

      grid.innerHTML = filtered.map(c => {
        const url = settings[c.key];
        return `<a href="${url}" class="contact-box ${c.gold ? 'gold-box' : ''}" target="_blank"
                   data-type="${c.label}" onclick="trackClick('${c.label}')">
          <span class="cb-icon">${c.icon}</span>
          <span class="cb-label">${c.label}</span>
          <span class="cb-name">${c.name}</span>
          <span class="cb-action">${c.action}</span>
        </a>`;
      }).join('');
    })
    .catch(() => {
      // Fallback: show static links
      grid.innerHTML = CONTACT_TYPES.slice(0, 6).map(c =>
        `<a href="#" class="contact-box ${c.gold ? 'gold-box' : ''}">
          <span class="cb-icon">${c.icon}</span>
          <span class="cb-label">${c.label}</span>
          <span class="cb-name">${c.name}</span>
          <span class="cb-action">${c.action}</span>
        </a>`
      ).join('');
    });
}

// ---- LOAD PROFILE SETTINGS ----
function loadProfileSettings() {
  fetch(`${API}/api/settings`, { credentials: 'include' })
    .then(r => r.ok ? r.json() : {})
    .then(s => {
      // Name
      const nameEl = document.getElementById('profileName');
      if (nameEl && s.profile_name) nameEl.textContent = s.profile_name;

      // Handle
      const handleEl = document.getElementById('profileHandle');
      if (handleEl && s.profile_handle) handleEl.textContent = s.profile_handle;

      // Titles
      const titlesEl = document.getElementById('profileTitlesMini');
      if (titlesEl) {
        const t1 = s.profile_title1 || 'Developer';
        const t2 = s.profile_title2 || 'System Architect';
        const t3 = s.profile_title3 || 'Digital Builder';
        titlesEl.innerHTML = `<span>${t1}</span><span class="dot">·</span><span>${t2}</span><span class="dot">·</span><span>${t3}</span>`;
      }

      // Photo URL
      const photoEl = document.getElementById('profilePhoto');
      if (photoEl && s.profile_photo_url) {
        photoEl.src = s.profile_photo_url;
      }

      // Hero titles row
      const heroTitles = document.querySelector('.hero-titles');
      if (heroTitles) {
        heroTitles.innerHTML = `
          <span class="title-tag">${s.profile_title1 || 'Developer'}</span>
          <span class="title-div">·</span>
          <span class="title-tag">${s.profile_title2 || 'System Architect'}</span>
          <span class="title-div">·</span>
          <span class="title-tag">${s.profile_title3 || 'Digital Builder'}</span>
          <span class="title-div">·</span>
          <span class="title-tag">Founder of VALCORE &lt;/&gt;</span>`;
      }
    })
    .catch(() => {});
}

// ---- VISITOR STAR RATING ----
let selectedRating = 0;

function initStarRating() {
  const stars = document.querySelectorAll('.star-btn');
  stars.forEach(star => {
    star.addEventListener('mouseover', () => {
      const val = parseInt(star.dataset.val);
      stars.forEach(s => {
        s.classList.toggle('active', parseInt(s.dataset.val) <= val);
      });
    });

    star.addEventListener('mouseout', () => {
      stars.forEach(s => {
        s.classList.toggle('active', parseInt(s.dataset.val) <= selectedRating);
      });
    });

    star.addEventListener('click', () => {
      selectedRating = parseInt(star.dataset.val);
      document.getElementById('ratingVal').value = selectedRating;
      stars.forEach(s => {
        s.classList.toggle('active', parseInt(s.dataset.val) <= selectedRating);
      });
    });
  });
}

function submitRating() {
  const note    = document.getElementById('ratingNote');
  const name    = document.getElementById('ratingName').value.trim();
  const comment = document.getElementById('ratingComment').value.trim();
  const rating  = parseInt(document.getElementById('ratingVal').value || '0');

  if (!name) { note.textContent = 'Please enter your name.'; note.style.color = 'var(--red)'; return; }
  if (!rating) { note.textContent = 'Please select a star rating.'; note.style.color = 'var(--red)'; return; }

  note.textContent = 'Submitting...';
  note.style.color = 'var(--muted)';

  fetch(`${API}/api/ratings/submit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, comment, rating })
  })
    .then(r => r.json())
    .then(data => {
      if (data.ok) {
        note.textContent = '✅ Thank you! Your rating was submitted.';
        note.style.color = 'var(--green)';
        document.getElementById('ratingName').value = '';
        document.getElementById('ratingComment').value = '';
        document.getElementById('ratingVal').value = '0';
        selectedRating = 0;
        document.querySelectorAll('.star-btn').forEach(s => s.classList.remove('active'));
      } else {
        note.textContent = 'Something went wrong. Try again.';
        note.style.color = 'var(--red)';
      }
    })
    .catch(() => {
      note.textContent = 'Could not connect. Please try again.';
      note.style.color = 'var(--yellow)';
    });
}

// ---- INIT ALL v7 ON PAGE LOAD ----
document.addEventListener('DOMContentLoaded', () => {
  loadContactGrid();
  loadProfileSettings();
  initStarRating();
});

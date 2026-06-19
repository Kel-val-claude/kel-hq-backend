# ============================================
#   KEL HQ — COMMAND CENTER (Complete Clean v6)
#   app/routes/command.py
# ============================================

from flask import Blueprint, jsonify, request, session, render_template_string
from app.core.database import get_db
from app.core.auth import owner_required, log_activity

command_bp = Blueprint('command', __name__, url_prefix='/command-center')

DASHBOARD_PAGE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>K. Command Center</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{
  --bg:#0A0A0A;--surface:#111;--card:#141414;
  --border:rgba(255,255,255,0.06);--gold:#D4AF37;
  --gold-soft:rgba(212,175,55,0.08);--text:#F0F0F0;
  --muted:#666;--green:#2ECC71;--red:#E74C3C;--yellow:#F1C40F
}
body{background:var(--bg);color:var(--text);font-family:Inter,sans-serif;font-size:14px}

/* LAYOUT */
.layout{display:grid;grid-template-columns:220px 1fr;min-height:100vh}

/* SIDEBAR */
.sidebar{
  background:var(--surface);border-right:1px solid var(--border);
  padding:1.25rem 0.75rem;position:fixed;top:0;left:0;
  height:100vh;width:220px;overflow-y:auto;
  display:flex;flex-direction:column;gap:2px;
  z-index:50;transition:left 0.28s ease
}
.sidebar-logo{font-size:1.1rem;font-weight:700;color:var(--gold);
  margin-bottom:1.25rem;padding:0 0.5rem}
.sidebar-logo span{color:var(--text)}
.nav-item{
  display:block;width:100%;padding:0.6rem 0.75rem;
  border-radius:8px;cursor:pointer;font-size:0.82rem;
  font-weight:500;color:var(--muted);
  background:none;border:none;text-align:left;
  transition:all 0.18s
}
.nav-item:hover,.nav-item.active{background:var(--gold-soft);color:var(--gold)}
.nav-divider{height:1px;background:var(--border);margin:0.5rem 0}
.logout-link{
  display:block;margin-top:auto;padding:0.6rem 0.75rem;
  background:rgba(231,76,60,0.08);border:1px solid rgba(231,76,60,0.15);
  border-radius:8px;color:#E74C3C;font-size:0.78rem;font-weight:600;
  text-decoration:none;text-align:center
}

/* MAIN */
.main{margin-left:220px;padding:1.5rem;min-height:100vh}
.page-header{margin-bottom:1.5rem}
.page-header h1{font-size:1.4rem;font-weight:700;margin-bottom:0.2rem}
.page-header p{font-size:0.78rem;color:var(--muted)}

/* STATS */
.stat-row{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-bottom:1.5rem}
.stat-box{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:1.25rem}
.stat-box strong{display:block;font-size:1.8rem;font-weight:700;color:var(--gold);margin-bottom:0.2rem}
.stat-box span{font-size:0.72rem;color:var(--muted)}

/* PANELS */
.panel-row{display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:1rem}
.panel{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:1.25rem;margin-bottom:1rem}
.panel-title{font-size:0.85rem;font-weight:700;margin-bottom:0.85rem;color:var(--text);
  display:flex;align-items:center;justify-content:space-between}

/* TABLE */
.tbl-wrap{overflow-x:auto}
table{width:100%;border-collapse:collapse;font-size:0.78rem;min-width:400px}
th{text-align:left;padding:0.5rem 0.6rem;color:var(--muted);font-weight:600;
  border-bottom:1px solid var(--border);text-transform:uppercase;font-size:0.62rem;letter-spacing:0.06em}
td{padding:0.6rem 0.6rem;border-bottom:1px solid var(--border);color:var(--text)}
tr:last-child td{border-bottom:none}
tr:hover td{background:rgba(255,255,255,0.02)}

/* BADGES */
.badge{font-size:0.6rem;font-weight:700;padding:0.15rem 0.5rem;border-radius:4px;text-transform:uppercase;display:inline-block}
.bg{background:rgba(46,204,113,0.1);color:var(--green)}
.by{background:rgba(241,196,15,0.08);color:var(--yellow)}
.br{background:rgba(231,76,60,0.08);color:var(--red)}
.bo{background:var(--gold-soft);color:var(--gold);border:1px solid rgba(212,175,55,0.2)}

/* FORMS */
.form-group{margin-bottom:0.85rem}
.form-group label{display:block;font-size:0.7rem;color:var(--muted);margin-bottom:0.3rem;font-weight:600;text-transform:uppercase;letter-spacing:0.05em}
.form-group input,.form-group select,.form-group textarea{
  width:100%;background:var(--bg);border:1px solid var(--border);
  border-radius:7px;padding:0.6rem 0.8rem;color:var(--text);
  font-family:Inter,sans-serif;font-size:0.82rem;outline:none
}
.form-group input:focus,.form-group select:focus,.form-group textarea:focus{border-color:rgba(212,175,55,0.4)}
.form-row{display:grid;grid-template-columns:1fr 1fr;gap:0.85rem}
.hidden-form{display:none;padding:1rem 0;border-bottom:1px solid var(--border);margin-bottom:1rem}

/* BUTTONS */
.btn{display:inline-block;padding:0.55rem 1.1rem;border-radius:7px;font-size:0.78rem;
  font-weight:600;cursor:pointer;border:none;font-family:Inter,sans-serif;transition:all 0.18s}
.btn-gold{background:var(--gold);color:#0A0A0A}
.btn-gold:hover{background:#c9a227}
.btn-danger{background:rgba(231,76,60,0.1);color:var(--red);border:1px solid rgba(231,76,60,0.2)}
.btn-danger:hover{background:rgba(231,76,60,0.2)}
.btn-sm{padding:0.28rem 0.65rem;font-size:0.68rem}

/* FEED */
.feed-item{display:flex;gap:0.65rem;padding:0.6rem 0;border-bottom:1px solid var(--border);align-items:flex-start;font-size:0.78rem}
.feed-dot{width:7px;height:7px;border-radius:50%;background:var(--gold);flex-shrink:0;margin-top:4px}

/* SECTIONS */
.section{display:none}
.section.active{display:block}

/* TOAST */
.toast{position:fixed;bottom:20px;right:20px;background:var(--gold);color:#0A0A0A;
  padding:0.6rem 1.1rem;border-radius:8px;font-size:0.82rem;font-weight:700;
  opacity:0;transform:translateY(10px);transition:all 0.25s;pointer-events:none;z-index:9999}
.toast.show{opacity:1;transform:translateY(0)}

/* MOBILE TOP BAR */
.topbar{
  display:none;position:fixed;top:0;left:0;right:0;height:50px;
  background:var(--surface);border-bottom:1px solid var(--border);
  align-items:center;justify-content:space-between;
  padding:0 1rem;z-index:200
}
.topbar-menu{background:none;border:none;color:var(--gold);font-size:1.5rem;cursor:pointer;padding:0.3rem}
.topbar-title{font-size:0.9rem;font-weight:700}
.topbar-logout{color:var(--muted);text-decoration:none;font-size:0.8rem}
.overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.6);z-index:49}
.overlay.open{display:block}

/* MOBILE RESPONSIVE */
@media(max-width:900px){
  .topbar{display:flex}
  .layout{grid-template-columns:1fr}
  .sidebar{left:-240px}
  .sidebar.open{left:0}
  .main{margin-left:0;padding:1rem;margin-top:54px}
  .stat-row{grid-template-columns:1fr 1fr}
  .panel-row{grid-template-columns:1fr}
  .form-row{grid-template-columns:1fr}
  table{font-size:0.72rem}
  th,td{padding:0.4rem 0.45rem}
}
@media(max-width:480px){
  .stat-row{grid-template-columns:1fr 1fr}
}
</style>
</head>
<body>

<!-- MOBILE TOP BAR -->
<div class="topbar" id="topbar">
  <button class="topbar-menu" id="menuBtn">&#9776;</button>
  <span class="topbar-title">K. Command Center</span>
  <a class="topbar-logout" href="/logout">Logout</a>
</div>

<!-- OVERLAY -->
<div class="overlay" id="overlay"></div>

<div class="layout">

  <!-- SIDEBAR -->
  <aside class="sidebar" id="sidebar">
    <div class="sidebar-logo">K<span>.</span> HQ</div>

    <button class="nav-item active" data-section="dashboard">&#127968; Dashboard</button>
    <button class="nav-item" data-section="availability">&#128994; Availability</button>
    <button class="nav-item" data-section="appointments">&#128197; Appointments</button>
    <button class="nav-item" data-section="projects">&#128193; Projects</button>
    <button class="nav-item" data-section="reviews">&#11088; Reviews</button>
    <button class="nav-item" data-section="partners">&#129309; Partners</button>
    <button class="nav-item" data-section="analytics">&#128202; Analytics</button>
    <div class="nav-divider"></div>
    <button class="nav-item" data-section="profile">&#9881; Profile Stats</button>
    <button class="nav-item" data-section="announce">&#128226; Announcements</button>
    <button class="nav-item" data-section="deals">&#128176; Deal Tracker</button>
    <button class="nav-item" data-section="visitors">&#128065; Visitors</button>
    <button class="nav-item" data-section="profile-edit">&#128247; Profile Editor</button>
    <button class="nav-item" data-section="settings">&#128279; Site Settings</button>
    <button class="nav-item" data-section="ratings">&#11088; Visitor Ratings</button>
    <div class="nav-divider"></div>
    <button class="nav-item" data-section="activity">&#128225; Activity Log</button>
    <div class="nav-divider"></div>
    <a class="logout-link" href="/logout">&#9211; Logout</a>
  </aside>

  <!-- MAIN -->
  <main class="main">

    <!-- DASHBOARD -->
    <div id="sec-dashboard" class="section active">
      <div class="page-header">
        <h1>Command Center</h1>
        <p>Welcome back, {{ owner_name }} &middot; Your HQ at a glance</p>
      </div>
      <div class="stat-row">
        <div class="stat-box"><strong>{{ stats.pending_appts }}</strong><span>Pending Appointments</span></div>
        <div class="stat-box"><strong>{{ stats.live_projects }}</strong><span>Live Projects</span></div>
        <div class="stat-box"><strong>{{ stats.total_reviews }}</strong><span>Reviews</span></div>
        <div class="stat-box"><strong>{{ stats.total_clicks }}</strong><span>Total Clicks</span></div>
      </div>
      <div class="panel-row">
        <div class="panel">
          <div class="panel-title">Recent Appointments</div>
          {% if appts %}
            {% for a in appts %}
            <div class="feed-item">
              <div class="feed-dot"></div>
              <div style="flex:1">
                <strong>{{ a.name }}</strong> &mdash; {{ a.service or 'General' }}<br>
                <span style="color:var(--muted);font-size:0.65rem">{{ (a.created_at or '')[:16] }}</span>
              </div>
              <span class="badge {{ 'by' if a.status == 'pending' else 'bg' }}">{{ a.status }}</span>
            </div>
            {% endfor %}
          {% else %}
            <p style="color:var(--muted);font-size:0.78rem">No appointments yet.</p>
          {% endif %}
        </div>
        <div class="panel">
          <div class="panel-title">Live Activity Feed</div>
          {% if activity %}
            {% for a in activity %}
            <div class="feed-item">
              <div class="feed-dot"></div>
              <div>
                <strong>{{ a.action }}</strong>{% if a.detail %} &middot; {{ a.detail }}{% endif %}<br>
                <span style="color:var(--muted);font-size:0.65rem">{{ (a.created_at or '')[:16] }}</span>
              </div>
            </div>
            {% endfor %}
          {% else %}
            <p style="color:var(--muted);font-size:0.78rem">No activity yet.</p>
          {% endif %}
        </div>
      </div>
    </div>

    <!-- AVAILABILITY -->
    <div id="sec-availability" class="section">
      <div class="page-header"><h1>Availability</h1><p>Control what visitors see on your HQ</p></div>
      <div class="panel" style="max-width:480px">
        <div class="panel-title">Current Status</div>
        <div style="display:flex;gap:0.75rem;margin-bottom:1rem">
          <button class="btn btn-gold" onclick="setAvailStatus('available')">&#128994; Set Available</button>
          <button class="btn" style="background:rgba(241,196,15,0.1);color:var(--yellow);border:1px solid rgba(241,196,15,0.2)" onclick="setAvailStatus('booked')">&#128992; Set Booked</button>
        </div>
        <div class="form-group" id="nextOpenGroup" style="display:none">
          <label>Next Opening Date</label>
          <input type="text" id="nextOpening" placeholder="e.g. July 3rd, 2026"/>
        </div>
        <button class="btn btn-gold" onclick="saveAvail()">Save Status</button>
        <p id="availNote" style="font-size:0.75rem;color:var(--green);margin-top:0.5rem"></p>
      </div>
    </div>

    <!-- APPOINTMENTS -->
    <div id="sec-appointments" class="section">
      <div class="page-header"><h1>Appointments</h1><p>Manage booking requests from clients</p></div>
      <div class="panel">
        <div class="panel-title">All Appointments</div>
        <div class="tbl-wrap"><table>
          <thead><tr><th>Name</th><th>Contact</th><th>Service</th><th>Status</th><th>Date</th><th>Action</th></tr></thead>
          <tbody id="apptBody"><tr><td colspan="6" style="color:var(--muted)">Loading...</td></tr></tbody>
        </table></div>
      </div>
    </div>

    <!-- PROJECTS -->
    <div id="sec-projects" class="section">
      <div class="page-header"><h1>Projects</h1><p>Manage your portfolio</p></div>
      <div class="panel">
        <div class="panel-title">
          Projects
          <button class="btn btn-gold btn-sm" onclick="toggleForm('addProjectForm')">+ Add Project</button>
        </div>
        <div class="hidden-form" id="addProjectForm">
          <div class="form-row">
            <div class="form-group"><label>Title</label><input type="text" id="pTitle" placeholder="Project name"/></div>
            <div class="form-group"><label>Category</label><input type="text" id="pCat" placeholder="Website / SaaS / Bot"/></div>
          </div>
          <div class="form-group"><label>Description</label><textarea id="pDesc" rows="2" placeholder="Short description"></textarea></div>
          <div class="form-row">
            <div class="form-group"><label>Tags (comma-separated)</label><input type="text" id="pTags" placeholder="HTML,CSS,JS"/></div>
            <div class="form-group"><label>Project Link</label><input type="text" id="pLink" placeholder="../project/index.html"/></div>
          </div>
          <div class="form-row">
            <div class="form-group"><label>Complexity</label>
              <select id="pComplex"><option>Low</option><option selected>Medium</option><option>High</option></select>
            </div>
            <div class="form-group"><label>Duration</label><input type="text" id="pDuration" placeholder="3-7 Days"/></div>
          </div>
          <button class="btn btn-gold" onclick="addProject()">Save Project</button>
        </div>
        <div class="tbl-wrap"><table>
          <thead><tr><th>Title</th><th>Category</th><th>Complexity</th><th>Status</th><th>Action</th></tr></thead>
          <tbody id="projectBody"><tr><td colspan="5" style="color:var(--muted)">Loading...</td></tr></tbody>
        </table></div>
      </div>
    </div>

    <!-- REVIEWS -->
    <div id="sec-reviews" class="section">
      <div class="page-header"><h1>Reviews</h1><p>Manage client testimonials</p></div>
      <div class="panel">
        <div class="panel-title">
          Reviews
          <button class="btn btn-gold btn-sm" onclick="toggleForm('addReviewForm')">+ Add Review</button>
        </div>
        <div class="hidden-form" id="addReviewForm">
          <div class="form-row">
            <div class="form-group"><label>Client Name</label><input type="text" id="rName" placeholder="Name"/></div>
            <div class="form-group"><label>Role / Company</label><input type="text" id="rRole" placeholder="Business Owner"/></div>
          </div>
          <div class="form-group"><label>Review Text</label><textarea id="rContent" rows="3" placeholder="What they said..."></textarea></div>
          <div class="form-row">
            <div class="form-group"><label>Rating</label>
              <select id="rRating"><option value="5">5 Stars</option><option value="4">4 Stars</option><option value="3">3 Stars</option></select>
            </div>
            <div class="form-group"><label>Featured?</label>
              <select id="rFeatured"><option value="0">No</option><option value="1">Yes</option></select>
            </div>
          </div>
          <button class="btn btn-gold" onclick="addReview()">Save Review</button>
        </div>
        <div class="tbl-wrap"><table>
          <thead><tr><th>Name</th><th>Role</th><th>Rating</th><th>Featured</th><th>Action</th></tr></thead>
          <tbody id="reviewBody"><tr><td colspan="5" style="color:var(--muted)">Loading...</td></tr></tbody>
        </table></div>
      </div>
    </div>

    <!-- PARTNERS -->
    <div id="sec-partners" class="section">
      <div class="page-header"><h1>Partners</h1></div>
      <div class="panel">
        <div class="panel-title">
          Partners
          <button class="btn btn-gold btn-sm" onclick="toggleForm('addPartnerForm')">+ Add Partner</button>
        </div>
        <div class="hidden-form" id="addPartnerForm">
          <div class="form-row">
            <div class="form-group"><label>Name</label><input type="text" id="partName" placeholder="SILENCE SYS"/></div>
            <div class="form-group"><label>Type</label><input type="text" id="partType" placeholder="Ecosystem Partner"/></div>
          </div>
          <div class="form-group"><label>Description</label><textarea id="partDesc" rows="2"></textarea></div>
          <div class="form-group"><label>Website URL</label><input type="text" id="partUrl" placeholder="https://..."/></div>
          <button class="btn btn-gold" onclick="addPartner()">Save Partner</button>
        </div>
        <div class="tbl-wrap"><table>
          <thead><tr><th>Name</th><th>Type</th><th>URL</th><th>Status</th><th>Action</th></tr></thead>
          <tbody id="partnerBody"><tr><td colspan="5" style="color:var(--muted)">Loading...</td></tr></tbody>
        </table></div>
      </div>
    </div>

    <!-- ANALYTICS -->
    <div id="sec-analytics" class="section">
      <div class="page-header"><h1>Analytics</h1></div>
      <div class="stat-row">
        <div class="stat-box"><strong id="a-clicks">-</strong><span>Total Clicks</span></div>
        <div class="stat-box"><strong id="a-views">-</strong><span>Portfolio Views</span></div>
        <div class="stat-box"><strong id="a-wa">-</strong><span>WhatsApp Clicks</span></div>
        <div class="stat-box"><strong id="a-tg">-</strong><span>Telegram Clicks</span></div>
      </div>
      <div class="panel">
        <div class="panel-title">Recent Events</div>
        <div class="tbl-wrap"><table>
          <thead><tr><th>Type</th><th>Value</th><th>Source</th><th>Time</th></tr></thead>
          <tbody id="analyticsBody"><tr><td colspan="4" style="color:var(--muted)">Loading...</td></tr></tbody>
        </table></div>
      </div>
    </div>

    <!-- PROFILE STATS -->
    <div id="sec-profile" class="section">
      <div class="page-header"><h1>Profile Stats</h1><p>Numbers shown on your hero card</p></div>
      <div class="panel" style="max-width:500px">
        <div class="form-row">
          <div class="form-group"><label>Projects Built</label><input type="number" id="st-projects"/></div>
          <div class="form-group"><label>Deals Closed</label><input type="number" id="st-deals"/></div>
        </div>
        <div class="form-row">
          <div class="form-group"><label>Partnerships</label><input type="number" id="st-partners"/></div>
          <div class="form-group"><label>Hours Saved</label><input type="number" id="st-hours"/></div>
        </div>
        <div class="form-row">
          <div class="form-group"><label>Systems Built</label><input type="number" id="st-systems"/></div>
          <div class="form-group"><label>Bots Created</label><input type="number" id="st-bots"/></div>
        </div>
        <div class="form-group"><label>Tasks Automated</label><input type="number" id="st-tasks"/></div>
        <div class="form-group"><label>Current Focus (comma-separated)</label><input type="text" id="st-focus"/></div>
        <button class="btn btn-gold" onclick="saveProfile()">Update Stats</button>
        <p id="profileNote" style="font-size:0.75rem;color:var(--green);margin-top:0.5rem"></p>
      </div>
    </div>

    <!-- ANNOUNCEMENTS -->
    <div id="sec-announce" class="section">
      <div class="page-header"><h1>Announcements</h1><p>Push banners to your homepage</p></div>
      <div class="panel" style="max-width:500px">
        <div class="form-group"><label>Message</label><input type="text" id="annMsg" placeholder="Available For New Projects"/></div>
        <div class="form-group"><label>Type</label>
          <select id="annType"><option value="info">Info</option><option value="success">Success</option><option value="warning">Warning</option></select>
        </div>
        <button class="btn btn-gold" onclick="addAnnouncement()">Push Announcement</button>
      </div>
      <div class="panel">
        <div class="panel-title">Active Announcements</div>
        <div id="announceList"><p style="color:var(--muted);font-size:0.78rem">Loading...</p></div>
      </div>
    </div>

    <!-- DEAL TRACKER -->
    <div id="sec-deals" class="section">
      <div class="page-header"><h1>Deal Tracker</h1></div>
      <div class="stat-row" style="grid-template-columns:repeat(3,1fr)">
        <div class="stat-box"><strong id="d-active">-</strong><span>Active Deals</span></div>
        <div class="stat-box"><strong id="d-completed">-</strong><span>Completed</span></div>
        <div class="stat-box"><strong id="d-pending">-</strong><span>Pending</span></div>
      </div>
      <div class="panel">
        <div class="panel-title">
          Deals
          <button class="btn btn-gold btn-sm" onclick="toggleForm('addDealForm')">+ Add Deal</button>
        </div>
        <div class="hidden-form" id="addDealForm">
          <div class="form-row">
            <div class="form-group"><label>Deal Title</label><input type="text" id="dTitle" placeholder="e.g. Bakery Website"/></div>
            <div class="form-group"><label>Client</label><input type="text" id="dClient" placeholder="Client name"/></div>
          </div>
          <div class="form-row">
            <div class="form-group"><label>Value</label><input type="text" id="dValue" placeholder="e.g. &#8358;50,000"/></div>
            <div class="form-group"><label>Status</label>
              <select id="dStatus"><option value="active">Active</option><option value="completed">Completed</option><option value="pending">Pending</option></select>
            </div>
          </div>
          <button class="btn btn-gold" onclick="addDeal()">Save Deal</button>
        </div>
        <div class="tbl-wrap"><table>
          <thead><tr><th>Title</th><th>Client</th><th>Value</th><th>Status</th><th>Date</th><th>Action</th></tr></thead>
          <tbody id="dealBody"><tr><td colspan="6" style="color:var(--muted)">Loading...</td></tr></tbody>
        </table></div>
      </div>
    </div>

    <!-- VISITORS -->
    <div id="sec-visitors" class="section">
      <div class="page-header"><h1>Visitors</h1></div>
      <div class="stat-row" style="grid-template-columns:1fr 1fr">
        <div class="stat-box"><strong id="v-total">-</strong><span>Total Visits</span></div>
        <div class="stat-box"><strong id="v-today">-</strong><span>Today</span></div>
      </div>
      <div class="panel">
        <div class="panel-title">Daily Breakdown</div>
        <div class="tbl-wrap"><table>
          <thead><tr><th>Date</th><th>Visits</th></tr></thead>
          <tbody id="visitorBody"><tr><td colspan="2" style="color:var(--muted)">Loading...</td></tr></tbody>
        </table></div>
      </div>
    </div>

    <!-- SITE SETTINGS -->
    <div id="sec-settings" class="section">
      <div class="page-header"><h1>Site Settings</h1><p>Edit contact links &mdash; homepage updates automatically</p></div>
      <div class="panel">
        <div class="panel-title">Contact Links</div>
        <div class="form-row">
          <div class="form-group"><label>WhatsApp URL</label><input type="text" id="s-wa" placeholder="https://wa.me/234..."/></div>
          <div class="form-group"><label>Telegram URL</label><input type="text" id="s-tg" placeholder="https://t.me/..."/></div>
        </div>
        <div class="form-row">
          <div class="form-group"><label>Channel URL</label><input type="text" id="s-ch" placeholder="https://t.me/..."/></div>
          <div class="form-group"><label>GitHub URL</label><input type="text" id="s-gh" placeholder="https://github.com/..."/></div>
        </div>
        <div class="form-row">
          <div class="form-group"><label>Facebook URL</label><input type="text" id="s-fb" placeholder="https://facebook.com/..."/></div>
          <div class="form-group"><label>Email</label><input type="text" id="s-mail" placeholder="mailto:..."/></div>
        </div>
      </div>
      <div class="panel">
        <div class="panel-title">Site Text</div>
        <div class="form-group"><label>Hero Description</label><textarea id="s-herodesc" rows="3"></textarea></div>
        <div class="form-row">
          <div class="form-group"><label>Location</label><input type="text" id="s-location"/></div>
          <div class="form-group"><label>Experience</label><input type="text" id="s-experience"/></div>
        </div>
        <div class="form-row">
          <div class="form-group"><label>Languages</label><input type="text" id="s-languages"/></div>
          <div class="form-group"><label>Focus</label><input type="text" id="s-focus-site"/></div>
        </div>
        <div class="form-group"><label>Resume PDF URL</label><input type="text" id="s-resume" placeholder="assets/resume.pdf"/></div>
      </div>
      <button class="btn btn-gold" onclick="saveSettings()">&#128190; Save All Settings</button>
      <p id="settingsNote" style="font-size:0.75rem;color:var(--green);margin-top:0.5rem"></p>
    </div>

    <!-- PROFILE EDITOR -->
    <div id="sec-profile-edit" class="section">
      <div class="page-header"><h1>Profile Editor</h1><p>Edit your public profile — updates homepage instantly</p></div>
      <div class="panel" style="max-width:500px">
        <div class="panel-title">Identity</div>
        <div class="form-group">
          <label>Display Name</label>
          <input type="text" id="pe-name" placeholder="Kel Val Claude"/>
        </div>
        <div class="form-group">
          <label>Handle / Username</label>
          <input type="text" id="pe-handle" placeholder="@kel_val_claude"/>
        </div>
        <div class="form-group">
          <label>Title 1</label>
          <input type="text" id="pe-title1" placeholder="Developer"/>
        </div>
        <div class="form-group">
          <label>Title 2</label>
          <input type="text" id="pe-title2" placeholder="System Architect"/>
        </div>
        <div class="form-group">
          <label>Title 3</label>
          <input type="text" id="pe-title3" placeholder="Digital Builder"/>
        </div>
      </div>
      <div class="panel" style="max-width:500px;margin-top:1rem">
        <div class="panel-title">Profile Photo</div>
        <div class="form-group">
          <label>Photo URL or path</label>
          <input type="text" id="pe-photo" placeholder="assets/logo.png"/>
          <small style="color:var(--muted);font-size:0.7rem;display:block;margin-top:0.3rem">
            Drop your image in the assets/ folder then enter filename here e.g. assets/myphoto.jpg
          </small>
        </div>
        <div id="pe-preview-wrap" style="margin-top:0.75rem">
          <img id="pe-preview" src="assets/logo.png" 
               style="width:72px;height:72px;border-radius:50%;object-fit:cover;border:2px solid var(--gold)"
               onerror="this.style.display='none'" />
        </div>
      </div>
      <div class="panel" style="max-width:500px;margin-top:1rem">
        <div class="panel-title">Contact Links</div>
        <div class="form-group"><label>WhatsApp URL</label><input type="text" id="pe-wa" placeholder="https://wa.me/234..."/></div>
        <div class="form-group"><label>Telegram URL</label><input type="text" id="pe-tg" placeholder="https://t.me/..."/></div>
        <div class="form-group"><label>Channel URL</label><input type="text" id="pe-ch" placeholder="https://t.me/..."/></div>
        <div class="form-group"><label>GitHub URL</label><input type="text" id="pe-gh" placeholder="https://github.com/..."/></div>
        <div class="form-group"><label>Facebook URL</label><input type="text" id="pe-fb" placeholder="https://facebook.com/..."/></div>
        <div class="form-group"><label>Discord Invite URL</label><input type="text" id="pe-dc" placeholder="https://discord.gg/..."/></div>
        <div class="form-group"><label>X / Twitter URL</label><input type="text" id="pe-x" placeholder="https://x.com/..."/></div>
        <div class="form-group"><label>Email</label><input type="text" id="pe-mail" placeholder="mailto:you@gmail.com"/></div>
      </div>
      <button class="btn btn-gold" onclick="saveProfileEdit()" style="margin-top:0.5rem">&#128190; Save Profile</button>
      <p id="peNote" style="font-size:0.75rem;color:var(--green);margin-top:0.5rem"></p>
    </div>

    <!-- VISITOR RATINGS -->
    <div id="sec-ratings" class="section">
      <div class="page-header"><h1>Visitor Ratings</h1><p>Approve ratings to show them as reviews</p></div>
      <div class="panel">
        <div class="panel-title">Submitted Ratings</div>
        <div class="tbl-wrap"><table>
          <thead><tr><th>Name</th><th>Rating</th><th>Comment</th><th>Status</th><th>Date</th><th>Action</th></tr></thead>
          <tbody id="ratingsBody"><tr><td colspan="6" style="color:var(--muted)">Loading...</td></tr></tbody>
        </table></div>
      </div>
    </div>

    <!-- ACTIVITY LOG -->
    <div id="sec-activity" class="section">
      <div class="page-header"><h1>Activity Log</h1></div>
      <div class="panel"><div id="activityList"><p style="color:var(--muted);font-size:0.78rem">Loading...</p></div></div>
    </div>

  </main>
</div>

<div class="toast" id="toast"></div>

<script>
// ============================================================
//   NAVIGATION — clean, simple, no dependencies
// ============================================================
const sections = document.querySelectorAll('.section');
const navBtns  = document.querySelectorAll('.nav-item[data-section]');

navBtns.forEach(function(btn) {
  btn.addEventListener('click', function() {
    var name = btn.getAttribute('data-section');

    // Show section
    sections.forEach(function(s) { s.classList.remove('active'); });
    var sec = document.getElementById('sec-' + name);
    if (sec) sec.classList.add('active');

    // Update active nav
    navBtns.forEach(function(b) { b.classList.remove('active'); });
    btn.classList.add('active');

    // Close mobile sidebar
    closeSidebar();

    // Load data for section
    loadSection(name);
  });
});

// ============================================================
//   MOBILE SIDEBAR
// ============================================================
var sidebar  = document.getElementById('sidebar');
var overlay  = document.getElementById('overlay');
var menuBtn  = document.getElementById('menuBtn');

menuBtn.addEventListener('click', function() {
  sidebar.classList.add('open');
  overlay.classList.add('open');
});

overlay.addEventListener('click', function() {
  closeSidebar();
});

function closeSidebar() {
  sidebar.classList.remove('open');
  overlay.classList.remove('open');
}

// ============================================================
//   XHR HELPERS (work on localhost without internet)
// ============================================================
function xhr(method, url, data, callback) {
  var req = new XMLHttpRequest();
  req.open(method, url, true);
  req.withCredentials = true;
  if (method === 'POST') req.setRequestHeader('Content-Type', 'application/json');
  req.onreadystatechange = function() {
    if (req.readyState === 4) {
      if (req.status === 401) { window.location.href = '/login'; return; }
      try {
        callback(JSON.parse(req.responseText));
      } catch(e) {
        callback([]);
      }
    }
  };
  req.send(data ? JSON.stringify(data) : null);
}

function get(url, cb) { xhr('GET', url, null, cb); }
function post(url, data, cb) { xhr('POST', url, data, cb || function(){}); }

// ============================================================
//   TOAST
// ============================================================
function toast(msg) {
  var t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(function() { t.classList.remove('show'); }, 2500);
}

function toggleForm(id) {
  var el = document.getElementById(id);
  el.style.display = el.style.display === 'block' ? 'none' : 'block';
}

// ============================================================
//   LOAD SECTION DATA
// ============================================================
function loadSection(name) {
  if (name === 'appointments') loadAppointments();
  if (name === 'projects')     loadProjects();
  if (name === 'reviews')      loadReviews();
  if (name === 'partners')     loadPartners();
  if (name === 'analytics')    loadAnalytics();
  if (name === 'profile')      loadProfile();
  if (name === 'announce')     loadAnnouncements();
  if (name === 'deals')        loadDeals();
  if (name === 'visitors')     loadVisitors();
  if (name === 'settings')     loadSettings();
  if (name === 'profile-edit') loadProfileEdit();
  if (name === 'ratings')      loadRatings();
  if (name === 'activity')     loadActivity();
  if (name === 'availability') loadAvailability();
}

// ============================================================
//   AVAILABILITY
// ============================================================
var currentAvailStatus = 'available';

function loadAvailability() {
  get('/api/status', function(d) {
    currentAvailStatus = d.status || 'available';
    if (d.status === 'booked') {
      document.getElementById('nextOpenGroup').style.display = 'block';
      document.getElementById('nextOpening').value = d.next_opening || '';
    }
  });
}

function setAvailStatus(status) {
  currentAvailStatus = status;
  document.getElementById('nextOpenGroup').style.display = status === 'booked' ? 'block' : 'none';
}

function saveAvail() {
  var next = document.getElementById('nextOpening').value;
  post('/command-center/update/availability', { status: currentAvailStatus, next_opening: next }, function() {
    document.getElementById('availNote').textContent = '✓ Status updated!';
    toast('✓ Availability updated!');
  });
}

// ============================================================
//   APPOINTMENTS
// ============================================================
function loadAppointments() {
  get('/command-center/data/appointments', function(data) {
    var tbody = document.getElementById('apptBody');
    if (!data.length) { tbody.innerHTML = '<tr><td colspan="6" style="color:var(--muted);padding:0.8rem">No appointments yet.</td></tr>'; return; }
    tbody.innerHTML = data.map(function(a) {
      return '<tr>' +
        '<td><strong>' + (a.name||'') + '</strong></td>' +
        '<td>' + (a.contact||'') + '</td>' +
        '<td>' + (a.service||'-') + '</td>' +
        '<td><span class="badge ' + (a.status==='pending'?'by':a.status==='approved'?'bg':'br') + '">' + (a.status||'') + '</span></td>' +
        '<td style="color:var(--muted)">' + ((a.created_at||'').slice(0,10)) + '</td>' +
        '<td>' +
          '<button class="btn btn-gold btn-sm" onclick="approveAppt(' + a.id + ')">&#10003;</button> ' +
          '<button class="btn btn-danger btn-sm" onclick="cancelAppt(' + a.id + ')">&#10005;</button>' +
        '</td></tr>';
    }).join('');
  });
}

function approveAppt(id) {
  post('/command-center/update/appointment', {id:id, status:'approved'}, function() {
    toast('✓ Appointment approved'); loadAppointments();
  });
}

function cancelAppt(id) {
  post('/command-center/update/appointment', {id:id, status:'cancelled'}, function() {
    toast('Appointment cancelled'); loadAppointments();
  });
}

// ============================================================
//   PROJECTS
// ============================================================
function loadProjects() {
  get('/command-center/data/projects', function(data) {
    var tbody = document.getElementById('projectBody');
    if (!data.length) { tbody.innerHTML = '<tr><td colspan="5" style="color:var(--muted);padding:0.8rem">No projects yet.</td></tr>'; return; }
    tbody.innerHTML = data.map(function(p) {
      return '<tr>' +
        '<td><strong>' + (p.title||'') + '</strong></td>' +
        '<td>' + (p.category||'-') + '</td>' +
        '<td>' + (p.complexity||'-') + '</td>' +
        '<td><span class="badge ' + (p.status==='live'?'bg':'by') + '">' + (p.status||'') + '</span></td>' +
        '<td><button class="btn btn-danger btn-sm" onclick="deleteProject(' + p.id + ')">Delete</button></td>' +
        '</tr>';
    }).join('');
  });
}

function addProject() {
  post('/command-center/add/project', {
    title:       document.getElementById('pTitle').value,
    description: document.getElementById('pDesc').value,
    category:    document.getElementById('pCat').value,
    tags:        document.getElementById('pTags').value,
    link:        document.getElementById('pLink').value,
    complexity:  document.getElementById('pComplex').value,
    duration:    document.getElementById('pDuration').value,
  }, function() {
    toast('✓ Project added!'); toggleForm('addProjectForm'); loadProjects();
  });
}

function deleteProject(id) {
  if (!confirm('Delete this project?')) return;
  post('/command-center/delete/project', {id:id}, function() {
    toast('Project deleted'); loadProjects();
  });
}

// ============================================================
//   REVIEWS
// ============================================================
function loadReviews() {
  get('/command-center/data/reviews', function(data) {
    var tbody = document.getElementById('reviewBody');
    if (!data.length) { tbody.innerHTML = '<tr><td colspan="5" style="color:var(--muted);padding:0.8rem">No reviews yet.</td></tr>'; return; }
    tbody.innerHTML = data.map(function(r) {
      return '<tr>' +
        '<td><strong>' + (r.name||'') + '</strong></td>' +
        '<td>' + (r.role||'-') + '</td>' +
        '<td>' + ('&#11088;'.repeat(r.rating||5)) + '</td>' +
        '<td>' + (r.featured ? '<span class="badge bo">Featured</span>' : '-') + '</td>' +
        '<td><button class="btn btn-danger btn-sm" onclick="deleteReview(' + r.id + ')">Delete</button></td>' +
        '</tr>';
    }).join('');
  });
}

function addReview() {
  post('/command-center/add/review', {
    name:     document.getElementById('rName').value,
    role:     document.getElementById('rRole').value,
    content:  document.getElementById('rContent').value,
    rating:   parseInt(document.getElementById('rRating').value),
    featured: parseInt(document.getElementById('rFeatured').value),
  }, function() {
    toast('✓ Review added!'); toggleForm('addReviewForm'); loadReviews();
  });
}

function deleteReview(id) {
  post('/command-center/delete/review', {id:id}, function() {
    toast('Review deleted'); loadReviews();
  });
}

// ============================================================
//   PARTNERS
// ============================================================
function loadPartners() {
  get('/command-center/data/partners', function(data) {
    var tbody = document.getElementById('partnerBody');
    if (!data.length) { tbody.innerHTML = '<tr><td colspan="5" style="color:var(--muted)">No partners.</td></tr>'; return; }
    tbody.innerHTML = data.map(function(p) {
      return '<tr>' +
        '<td><strong>' + (p.name||'') + '</strong></td>' +
        '<td>' + (p.type||'') + '</td>' +
        '<td><a href="' + (p.url||'#') + '" style="color:var(--gold)" target="_blank">' + (p.url||'-') + '</a></td>' +
        '<td><span class="badge ' + (p.active?'bg':'br') + '">' + (p.active?'Active':'Inactive') + '</span></td>' +
        '<td><button class="btn btn-danger btn-sm" onclick="deletePartner(' + p.id + ')">Delete</button></td>' +
        '</tr>';
    }).join('');
  });
}

function addPartner() {
  post('/command-center/add/partner', {
    name:        document.getElementById('partName').value,
    type:        document.getElementById('partType').value,
    description: document.getElementById('partDesc').value,
    url:         document.getElementById('partUrl').value,
  }, function() {
    toast('✓ Partner added!'); toggleForm('addPartnerForm'); loadPartners();
  });
}

function deletePartner(id) {
  post('/command-center/delete/partner', {id:id}, function() {
    toast('Partner deleted'); loadPartners();
  });
}

// ============================================================
//   ANALYTICS
// ============================================================
function loadAnalytics() {
  get('/command-center/data/analytics', function(data) {
    document.getElementById('a-clicks').textContent = data.filter(function(d){return d.event_type==='click';}).length;
    document.getElementById('a-views').textContent  = data.filter(function(d){return d.event_type==='view';}).length;
    document.getElementById('a-wa').textContent     = data.filter(function(d){return d.value==='WA';}).length;
    document.getElementById('a-tg').textContent     = data.filter(function(d){return d.value==='TG';}).length;
    var tbody = document.getElementById('analyticsBody');
    tbody.innerHTML = data.slice(0,20).map(function(d) {
      return '<tr><td><span class="badge bo">' + d.event_type + '</span></td><td>' + (d.value||'-') + '</td><td>' + (d.source||'-') + '</td><td style="color:var(--muted)">' + ((d.created_at||'').slice(0,16)) + '</td></tr>';
    }).join('') || '<tr><td colspan="4" style="color:var(--muted)">No events yet.</td></tr>';
  });
}

// ============================================================
//   PROFILE STATS
// ============================================================
function loadProfile() {
  get('/api/profile', function(d) {
    document.getElementById('st-projects').value = d.projects_built || 0;
    document.getElementById('st-deals').value    = d.deals_closed   || 0;
    document.getElementById('st-partners').value = d.partnerships   || 0;
    document.getElementById('st-hours').value    = d.hours_saved    || 0;
    document.getElementById('st-systems').value  = d.systems_built  || 0;
    document.getElementById('st-bots').value     = d.bots_created   || 0;
    document.getElementById('st-tasks').value    = d.tasks_automated|| 0;
    document.getElementById('st-focus').value    = d.current_focus  || '';
  });
}

function saveProfile() {
  post('/command-center/update/profile', {
    projects_built:  parseInt(document.getElementById('st-projects').value)||0,
    deals_closed:    parseInt(document.getElementById('st-deals').value)||0,
    partnerships:    parseInt(document.getElementById('st-partners').value)||0,
    hours_saved:     parseInt(document.getElementById('st-hours').value)||0,
    systems_built:   parseInt(document.getElementById('st-systems').value)||0,
    bots_created:    parseInt(document.getElementById('st-bots').value)||0,
    tasks_automated: parseInt(document.getElementById('st-tasks').value)||0,
    current_focus:   document.getElementById('st-focus').value,
  }, function() {
    document.getElementById('profileNote').textContent = '✓ Stats updated!';
    toast('✓ Profile stats updated!');
  });
}

// ============================================================
//   ANNOUNCEMENTS
// ============================================================
function loadAnnouncements() {
  get('/command-center/data/announcements', function(data) {
    var el = document.getElementById('announceList');
    el.innerHTML = data.length ? data.map(function(a) {
      return '<div class="feed-item"><div class="feed-dot"></div><strong>' + a.message + '</strong> <span class="badge bo">' + a.type + '</span>' +
        '<button class="btn btn-danger btn-sm" onclick="deleteAnnouncement(' + a.id + ')" style="margin-left:auto">Remove</button></div>';
    }).join('') : '<p style="color:var(--muted);font-size:0.78rem">No active announcements.</p>';
  });
}

function addAnnouncement() {
  post('/command-center/add/announcement', {
    message: document.getElementById('annMsg').value,
    type:    document.getElementById('annType').value,
  }, function() {
    toast('✓ Announcement pushed!'); loadAnnouncements();
  });
}

function deleteAnnouncement(id) {
  post('/command-center/delete/announcement', {id:id}, function() {
    loadAnnouncements();
  });
}

// ============================================================
//   DEALS
// ============================================================
function loadDeals() {
  get('/command-center/data/deals', function(data) {
    document.getElementById('d-active').textContent    = data.filter(function(d){return d.status==='active';}).length;
    document.getElementById('d-completed').textContent = data.filter(function(d){return d.status==='completed';}).length;
    document.getElementById('d-pending').textContent   = data.filter(function(d){return d.status==='pending';}).length;
    var tbody = document.getElementById('dealBody');
    tbody.innerHTML = data.length ? data.map(function(d) {
      return '<tr>' +
        '<td><strong>' + (d.title||'') + '</strong></td>' +
        '<td>' + (d.client||'-') + '</td>' +
        '<td>' + (d.value||'-') + '</td>' +
        '<td><span class="badge ' + (d.status==='completed'?'bg':d.status==='active'?'bo':'by') + '">' + (d.status||'') + '</span></td>' +
        '<td style="color:var(--muted)">' + ((d.created_at||'').slice(0,10)) + '</td>' +
        '<td><button class="btn btn-danger btn-sm" onclick="deleteDeal(' + d.id + ')">Delete</button></td>' +
        '</tr>';
    }).join('') : '<tr><td colspan="6" style="color:var(--muted);padding:0.8rem">No deals yet.</td></tr>';
  });
}

function addDeal() {
  post('/command-center/add/deal', {
    title:  document.getElementById('dTitle').value,
    client: document.getElementById('dClient').value,
    value:  document.getElementById('dValue').value,
    status: document.getElementById('dStatus').value,
  }, function() {
    toast('✓ Deal added!'); toggleForm('addDealForm'); loadDeals();
  });
}

function deleteDeal(id) {
  if (!confirm('Delete this deal?')) return;
  post('/command-center/delete/deal', {id:id}, function() {
    toast('Deal deleted'); loadDeals();
  });
}

// ============================================================
//   VISITORS
// ============================================================
function loadVisitors() {
  get('/command-center/data/visitors', function(data) {
    document.getElementById('v-total').textContent = data.total || 0;
    document.getElementById('v-today').textContent = data.today || 0;
    var tbody = document.getElementById('visitorBody');
    var daily = data.daily || [];
    tbody.innerHTML = daily.length ? daily.map(function(v) {
      return '<tr><td>' + v.date + '</td><td><strong style="color:var(--gold)">' + v.count + '</strong></td></tr>';
    }).join('') : '<tr><td colspan="2" style="color:var(--muted)">No visits recorded yet.</td></tr>';
  });
}

// ============================================================
//   SETTINGS
// ============================================================
var settingsMap = {
  's-wa':       'contact_wa',
  's-tg':       'contact_tg',
  's-ch':       'contact_channel',
  's-gh':       'contact_github',
  's-fb':       'contact_facebook',
  's-mail':     'contact_email',
  's-herodesc': 'hero_desc',
  's-location': 'about_location',
  's-experience':'about_experience',
  's-languages':'about_languages',
  's-focus-site':'about_focus',
  's-resume':   'resume_url',
};

function loadSettings() {
  get('/command-center/data/settings', function(d) {
    Object.keys(settingsMap).forEach(function(elId) {
      var key = settingsMap[elId];
      var el = document.getElementById(elId);
      if (el && d[key] !== undefined) el.value = d[key];
    });
  });
}

function saveSettings() {
  var payload = {};
  Object.keys(settingsMap).forEach(function(elId) {
    var el = document.getElementById(elId);
    if (el) payload[settingsMap[elId]] = el.value;
  });
  post('/command-center/update/settings', payload, function() {
    document.getElementById('settingsNote').textContent = '✓ Settings saved! Homepage updated.';
    toast('✓ Settings saved!');
  });
}

// ============================================================
//   ACTIVITY LOG
// ============================================================
function loadActivity() {
  get('/command-center/data/activity', function(data) {
    var el = document.getElementById('activityList');
    el.innerHTML = data.length ? data.map(function(a) {
      return '<div class="feed-item"><span style="color:var(--muted);font-size:0.65rem;white-space:nowrap">' + ((a.created_at||'').slice(11,16)) + '</span>' +
        '<div class="feed-dot"></div>' +
        '<div><strong>' + (a.action||'') + '</strong>' + (a.detail?' &middot; <span style="color:var(--muted)">'+a.detail+'</span>':'') + '<br>' +
        '<span style="color:var(--muted);font-size:0.65rem">' + ((a.created_at||'').slice(0,10)) + '</span></div>' +
        '</div>';
    }).join('') : '<p style="color:var(--muted);font-size:0.78rem">No activity yet.</p>';
  });
}

// ============================================================
//   PROFILE EDITOR
// ============================================================
var peMap = {
  'pe-name':  'profile_name',
  'pe-handle':'profile_handle',
  'pe-title1':'profile_title1',
  'pe-title2':'profile_title2',
  'pe-title3':'profile_title3',
  'pe-photo': 'profile_photo_url',
  'pe-wa':    'contact_wa',
  'pe-tg':    'contact_tg',
  'pe-ch':    'contact_channel',
  'pe-gh':    'contact_github',
  'pe-fb':    'contact_facebook',
  'pe-dc':    'contact_discord',
  'pe-x':     'contact_x',
  'pe-mail':  'contact_email',
};

function loadProfileEdit() {
  get('/command-center/data/settings', function(d) {
    Object.keys(peMap).forEach(function(elId) {
      var el = document.getElementById(elId);
      var key = peMap[elId];
      if (el && d[key] !== undefined) el.value = d[key];
    });
    // Show photo preview
    var photo = d['profile_photo_url'];
    var prev = document.getElementById('pe-preview');
    if (prev && photo) prev.src = photo;
  });
}

function saveProfileEdit() {
  var payload = {};
  Object.keys(peMap).forEach(function(elId) {
    var el = document.getElementById(elId);
    if (el) payload[peMap[elId]] = el.value;
  });

  // Update preview
  var photo = document.getElementById('pe-photo');
  var prev  = document.getElementById('pe-preview');
  if (photo && prev) prev.src = photo.value;

  post('/command-center/update/settings', payload, function() {
    document.getElementById('peNote').textContent = '✓ Profile saved! Homepage updated.';
    toast('✓ Profile updated!');
  });
}

// ============================================================
//   VISITOR RATINGS
// ============================================================
function buildApproveBtn(r) {
  return '<button class="btn btn-gold btn-sm" data-id="' + r.id + '" onclick="approveRatingById(this)">Approve</button>';
}

function approveRatingById(btn) {
  var id = parseInt(btn.getAttribute('data-id'));
  var row = null;
  for (var i = 0; i < ratingsCache.length; i++) {
    if (ratingsCache[i].id === id) { row = ratingsCache[i]; break; }
  }
  if (row) approveRating(row.id, row.name, row.rating, row.comment);
}

var ratingsCache = [];

function loadRatings() {
  get('/command-center/data/ratings', function(data) {
    ratingsCache = Array.isArray(data) ? data : [];
    var tbody = document.getElementById('ratingsBody');
    if (!Array.isArray(data) || !data.length) {
      tbody.innerHTML = '<tr><td colspan="6" style="color:var(--muted);padding:0.8rem">No ratings submitted yet.</td></tr>';
      return;
    }
    tbody.innerHTML = data.map(function(r) {
      return '<tr>' +
        '<td><strong>' + (r.name||'') + '</strong></td>' +
        '<td>' + '&#11088;'.repeat(r.rating||5) + '</td>' +
        '<td style="color:var(--muted)">' + (r.comment||'-') + '</td>' +
        '<td><span class="badge ' + (r.approved?'bg':'by') + '">' + (r.approved?'Approved':'Pending') + '</span></td>' +
        '<td style="color:var(--muted)">' + ((r.created_at||'').slice(0,10)) + '</td>' +
        '<td>' +
          (!r.approved ? buildApproveBtn(r) : '') +
          '<button class="btn btn-danger btn-sm" onclick="deleteRating(' + r.id + ')">Delete</button>' +
        '</td></tr>';
    }).join('');
  });
}

function approveRating(id, name, rating, comment) {
  // Approve = add to reviews table and mark approved
  post('/command-center/approve/rating', {id:id, name:name, rating:rating, comment:comment}, function() {
    toast('✓ Rating approved and added to reviews!');
    loadRatings();
  });
}

function deleteRating(id) {
  post('/command-center/delete/rating', {id:id}, function() {
    toast('Rating deleted'); loadRatings();
  });
}

</script>
</body>
</html>
'''


@command_bp.route('/')
@owner_required
def dashboard():
    db = get_db()
    try:
        appts    = db.execute("SELECT * FROM appointments ORDER BY id DESC").fetchall()
        projects = db.execute("SELECT * FROM projects ORDER BY id").fetchall()
        reviews  = db.execute("SELECT * FROM reviews ORDER BY id").fetchall()
        analytics= db.execute("SELECT COUNT(*) as c FROM analytics").fetchone()
        activity = db.execute("SELECT * FROM activity_log ORDER BY id DESC LIMIT 6").fetchall()

        stats = {
            'pending_appts': sum(1 for a in appts if a['status'] == 'pending'),
            'live_projects': sum(1 for p in projects if p['status'] == 'live'),
            'total_reviews': len(reviews),
            'total_clicks':  analytics['c'] if analytics else 0,
        }
    except Exception as e:
        stats = {'pending_appts':0,'live_projects':0,'total_reviews':0,'total_clicks':0}
        appts = activity = []
    finally:
        db.close()

    return render_template_string(
        DASHBOARD_PAGE,
        owner_name = session.get('owner_name', 'Kel'),
        stats      = stats,
        appts      = [dict(a) for a in appts[:5]],
        activity   = [dict(a) for a in activity],
    )


# ============================================================
#   DATA ENDPOINTS
# ============================================================

@command_bp.route('/data/appointments')
@owner_required
def data_appointments():
    db   = get_db()
    rows = db.execute('SELECT * FROM appointments ORDER BY id DESC').fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])


@command_bp.route('/data/projects')
@owner_required
def data_projects():
    db   = get_db()
    rows = db.execute('SELECT * FROM projects ORDER BY id').fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])


@command_bp.route('/data/reviews')
@owner_required
def data_reviews():
    db   = get_db()
    rows = db.execute('SELECT * FROM reviews ORDER BY featured DESC, id').fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])


@command_bp.route('/data/partners')
@owner_required
def data_partners():
    db   = get_db()
    rows = db.execute('SELECT * FROM partners ORDER BY id').fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])


@command_bp.route('/data/analytics')
@owner_required
def data_analytics():
    db   = get_db()
    rows = db.execute('SELECT * FROM analytics ORDER BY id DESC LIMIT 100').fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])


@command_bp.route('/data/activity')
@owner_required
def data_activity():
    db   = get_db()
    rows = db.execute('SELECT * FROM activity_log ORDER BY id DESC LIMIT 50').fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])


@command_bp.route('/data/announcements')
@owner_required
def data_announcements():
    db   = get_db()
    rows = db.execute("SELECT * FROM announcements WHERE active=1 ORDER BY id DESC").fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])


@command_bp.route('/data/deals')
@owner_required
def data_deals():
    db   = get_db()
    rows = db.execute('SELECT * FROM deals ORDER BY id DESC').fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])


@command_bp.route('/data/visitors')
@owner_required
def data_visitors():
    db    = get_db()
    rows  = db.execute('SELECT * FROM visitors ORDER BY date DESC LIMIT 30').fetchall()
    total = db.execute('SELECT SUM(count) as t FROM visitors').fetchone()['t'] or 0
    today = db.execute("SELECT count FROM visitors WHERE date=date('now')").fetchone()
    db.close()
    return jsonify({
        'total': total,
        'today': today['count'] if today else 0,
        'daily': [dict(r) for r in rows]
    })


@command_bp.route('/data/settings')
@owner_required
def data_settings():
    db   = get_db()
    rows = db.execute('SELECT key, value FROM settings').fetchall()
    db.close()
    return jsonify({r['key']: r['value'] for r in rows})


# ============================================================
#   UPDATE / ADD / DELETE ENDPOINTS
# ============================================================

@command_bp.route('/update/availability', methods=['POST'])
@owner_required
def update_availability():
    data = request.get_json() or {}
    db   = get_db()
    db.execute(
        "UPDATE availability SET status=?, next_opening=?, last_updated=CURRENT_TIMESTAMP WHERE id=1",
        (data.get('status','available'), data.get('next_opening',''))
    )
    log_activity(db, 'Availability Updated', data.get('status',''))
    db.commit()
    db.close()
    return jsonify({'ok': True})


@command_bp.route('/update/appointment', methods=['POST'])
@owner_required
def update_appointment():
    data = request.get_json() or {}
    db   = get_db()
    db.execute('UPDATE appointments SET status=? WHERE id=?', (data['status'], data['id']))
    log_activity(db, 'Appointment Updated', f"ID {data['id']} → {data['status']}")
    db.commit()
    db.close()
    return jsonify({'ok': True})


@command_bp.route('/update/profile', methods=['POST'])
@owner_required
def update_profile():
    data = request.get_json() or {}
    db   = get_db()
    db.execute('''UPDATE profile SET
        projects_built=?,partnerships=?,deals_closed=?,
        hours_saved=?,systems_built=?,bots_created=?,
        tasks_automated=?,current_focus=? WHERE id=1''',
        (data.get('projects_built',12), data.get('partnerships',2),
         data.get('deals_closed',20),   data.get('hours_saved',400),
         data.get('systems_built',8),   data.get('bots_created',6),
         data.get('tasks_automated',1000), data.get('current_focus',''))
    )
    log_activity(db, 'Profile Stats Updated')
    db.commit()
    db.close()
    return jsonify({'ok': True})


@command_bp.route('/update/settings', methods=['POST'])
@owner_required
def update_settings():
    data = request.get_json() or {}
    db   = get_db()
    for key, value in data.items():
        db.execute(
            'INSERT INTO settings (key,value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value',
            (key, value)
        )
    log_activity(db, 'Settings Updated', ', '.join(data.keys()))
    db.commit()
    db.close()
    return jsonify({'ok': True})


@command_bp.route('/add/project', methods=['POST'])
@owner_required
def add_project():
    data = request.get_json() or {}
    db   = get_db()
    db.execute(
        'INSERT INTO projects (title,description,category,tags,link,complexity,duration) VALUES (?,?,?,?,?,?,?)',
        (data.get('title'), data.get('description'), data.get('category'),
         data.get('tags'), data.get('link'), data.get('complexity','Medium'), data.get('duration'))
    )
    log_activity(db, 'Project Added', data.get('title',''))
    db.commit()
    db.close()
    return jsonify({'ok': True})


@command_bp.route('/delete/project', methods=['POST'])
@owner_required
def delete_project():
    data = request.get_json() or {}
    db   = get_db()
    db.execute('DELETE FROM projects WHERE id=?', (data['id'],))
    log_activity(db, 'Project Deleted', f"ID {data['id']}")
    db.commit()
    db.close()
    return jsonify({'ok': True})


@command_bp.route('/add/review', methods=['POST'])
@owner_required
def add_review():
    data = request.get_json() or {}
    db   = get_db()
    db.execute(
        'INSERT INTO reviews (name,role,content,rating,featured) VALUES (?,?,?,?,?)',
        (data.get('name'), data.get('role'), data.get('content'),
         data.get('rating',5), data.get('featured',0))
    )
    log_activity(db, 'Review Added', data.get('name',''))
    db.commit()
    db.close()
    return jsonify({'ok': True})


@command_bp.route('/delete/review', methods=['POST'])
@owner_required
def delete_review():
    data = request.get_json() or {}
    db   = get_db()
    db.execute('DELETE FROM reviews WHERE id=?', (data['id'],))
    db.commit()
    db.close()
    return jsonify({'ok': True})


@command_bp.route('/add/partner', methods=['POST'])
@owner_required
def add_partner():
    data = request.get_json() or {}
    db   = get_db()
    db.execute(
        'INSERT INTO partners (name,type,description,url,active) VALUES (?,?,?,?,1)',
        (data.get('name'), data.get('type','Partner'), data.get('description'), data.get('url'))
    )
    log_activity(db, 'Partner Added', data.get('name',''))
    db.commit()
    db.close()
    return jsonify({'ok': True})


@command_bp.route('/delete/partner', methods=['POST'])
@owner_required
def delete_partner():
    data = request.get_json() or {}
    db   = get_db()
    db.execute('DELETE FROM partners WHERE id=?', (data['id'],))
    log_activity(db, 'Partner Deleted')
    db.commit()
    db.close()
    return jsonify({'ok': True})


@command_bp.route('/add/announcement', methods=['POST'])
@owner_required
def add_announcement():
    data = request.get_json() or {}
    db   = get_db()
    db.execute(
        'INSERT INTO announcements (message,type) VALUES (?,?)',
        (data.get('message'), data.get('type','info'))
    )
    log_activity(db, 'Announcement Pushed', data.get('message',''))
    db.commit()
    db.close()
    return jsonify({'ok': True})


@command_bp.route('/delete/announcement', methods=['POST'])
@owner_required
def delete_announcement():
    data = request.get_json() or {}
    db   = get_db()
    db.execute('UPDATE announcements SET active=0 WHERE id=?', (data['id'],))
    db.commit()
    db.close()
    return jsonify({'ok': True})


@command_bp.route('/add/deal', methods=['POST'])
@owner_required
def add_deal():
    data = request.get_json() or {}
    db   = get_db()
    db.execute(
        'INSERT INTO deals (title,client,value,status) VALUES (?,?,?,?)',
        (data.get('title'), data.get('client'), data.get('value'), data.get('status','active'))
    )
    log_activity(db, 'Deal Added', data.get('title',''))
    db.commit()
    db.close()
    return jsonify({'ok': True})


@command_bp.route('/delete/deal', methods=['POST'])
@owner_required
def delete_deal():
    data = request.get_json() or {}
    db   = get_db()
    db.execute('DELETE FROM deals WHERE id=?', (data['id'],))
    log_activity(db, 'Deal Deleted')
    db.commit()
    db.close()
    return jsonify({'ok': True})


# ============================================================
#   RATINGS ROUTES
# ============================================================

@command_bp.route('/data/ratings')
@owner_required
def data_ratings():
    db   = get_db()
    try:
        rows = db.execute('SELECT * FROM visitor_ratings ORDER BY id DESC').fetchall()
        result = [dict(r) for r in rows]
    except:
        result = []
    db.close()
    return jsonify(result)


@command_bp.route('/approve/rating', methods=['POST'])
@owner_required
def approve_rating():
    data = request.get_json() or {}
    db   = get_db()
    # Mark as approved
    db.execute('UPDATE visitor_ratings SET approved=1 WHERE id=?', (data['id'],))
    # Add to reviews table
    db.execute(
        'INSERT INTO reviews (name, role, content, rating, featured) VALUES (?,?,?,?,0)',
        (data.get('name'), 'Verified Client', data.get('comment') or 'Great work!', data.get('rating', 5))
    )
    log_activity(db, 'Rating Approved', data.get('name',''))
    db.commit()
    db.close()
    return jsonify({'ok': True})


@command_bp.route('/delete/rating', methods=['POST'])
@owner_required
def delete_rating():
    data = request.get_json() or {}
    db   = get_db()
    db.execute('DELETE FROM visitor_ratings WHERE id=?', (data['id'],))
    db.commit()
    db.close()
    return jsonify({'ok': True})

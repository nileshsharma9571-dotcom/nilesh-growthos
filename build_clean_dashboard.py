import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LEADS_FILE = os.path.join(DATA_DIR, "leads.json")
JOBS_FILE = os.path.join(DATA_DIR, "jobs.json")
PROFILE_FILE = os.path.join(DATA_DIR, "profile.json")
DASHBOARD_FILE = os.path.join(BASE_DIR, "dashboard.html")
INDEX_FILE = os.path.join(BASE_DIR, "index.html")

with open(LEADS_FILE, "r", encoding="utf-8") as f:
    leads = json.load(f)

with open(JOBS_FILE, "r", encoding="utf-8") as f:
    jobs = json.load(f)

wfh_jobs = [j for j in jobs if j.get("job_category") == "WFH" or "Remote" in j.get("location", "")]
office_jobs = [j for j in jobs if j.get("job_category") == "Office" or "Office" in j.get("type", "")]

leads_json_str = json.dumps(leads, indent=2, ensure_ascii=False)
jobs_json_str = json.dumps(jobs, indent=2, ensure_ascii=False)

html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GrowthOS Pro &bull; Nilesh Acharya (Digital Marketing Hub)</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #090d16;
      --card-bg: #111827;
      --card-inner: #0b111e;
      --card-border: #1e293b;
      --accent: #38bdf8;
      --accent-glow: rgba(56, 189, 248, 0.15);
      --green: #22c55e;
      --green-dark: #16a34a;
      --purple: #a855f7;
      --orange: #f97316;
      --text: #f8fafc;
      --text-muted: #94a3b8;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      padding: 16px 12px 60px;
    }}
    .container {{ max-width: 1200px; margin: 0 auto; }}

    /* Top Bar */
    header {{
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      padding: 16px 20px;
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 14px;
      margin-bottom: 20px;
    }}
    .profile-badge {{
      display: flex;
      align-items: center;
      gap: 14px;
    }}
    .avatar {{
      width: 48px;
      height: 48px;
      border-radius: 50%;
      background: linear-gradient(135deg, #0284c7, #38bdf8);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
      font-weight: 800;
      color: #fff;
      box-shadow: 0 0 15px rgba(56, 189, 248, 0.4);
    }}
    .user-info h1 {{ font-size: 19px; font-weight: 800; color: #fff; letter-spacing: -0.3px; }}
    .user-info p {{ font-size: 12.5px; color: var(--text-muted); margin-top: 2px; }}
    .header-actions {{ display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }}
    .badge-status {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: rgba(34, 197, 94, 0.12);
      border: 1px solid rgba(34, 197, 94, 0.3);
      color: #4ade80;
      padding: 6px 12px;
      border-radius: 9999px;
      font-size: 12px;
      font-weight: 700;
    }}
    .badge-status::before {{
      content: '';
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: #22c55e;
      box-shadow: 0 0 8px #22c55e;
    }}

    /* Metrics Bar */
    .metrics-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 14px;
      margin-bottom: 22px;
    }}
    .metric-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 16px 18px;
    }}
    .metric-card .label {{ font-size: 11.5px; font-weight: 700; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.5px; }}
    .metric-card .val {{ font-size: 26px; font-weight: 800; color: #fff; margin-top: 4px; }}
    .metric-card .sub {{ font-size: 11.5px; color: var(--accent); margin-top: 3px; }}

    /* Tabs */
    .nav-tabs {{
      display: flex;
      gap: 8px;
      margin-bottom: 20px;
      border-bottom: 1px solid var(--card-border);
      padding-bottom: 8px;
      overflow-x: auto;
    }}
    .tab-btn {{
      background: transparent;
      border: 1px solid transparent;
      color: var(--text-muted);
      font-size: 13.5px;
      font-weight: 700;
      padding: 10px 16px;
      border-radius: 8px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 7px;
      white-space: nowrap;
      transition: all 0.2s;
    }}
    .tab-btn:hover {{ background: #1e293b; color: #fff; }}
    .tab-btn.active {{
      background: var(--accent-glow);
      color: var(--accent);
      border-color: rgba(56, 189, 248, 0.4);
    }}
    .badge-count {{
      font-size: 11px;
      padding: 2px 7px;
      border-radius: 10px;
      background: rgba(255,255,255,0.1);
      color: inherit;
    }}

    /* Controls Bar */
    .controls-bar {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-bottom: 20px;
      align-items: center;
    }}
    .search-input {{
      flex: 1;
      min-width: 220px;
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 9px;
      padding: 10px 14px;
      color: #fff;
      font-size: 13.5px;
      outline: none;
    }}
    .search-input:focus {{ border-color: var(--accent); }}
    .filter-select {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 9px;
      padding: 10px 14px;
      color: #fff;
      font-size: 13px;
      outline: none;
      cursor: pointer;
    }}

    /* Cards Grid */
    .cards-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
      gap: 20px;
    }}
    @media (max-width: 600px) {{
      .cards-grid {{ grid-template-columns: 1fr; }}
    }}

    .card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 14px;
      padding: 20px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 16px;
      transition: transform 0.2s, border-color 0.2s;
    }}
    .card:hover {{
      border-color: rgba(56, 189, 248, 0.45);
      transform: translateY(-2px);
    }}

    .card-top {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 10px;
    }}
    .card-title {{ font-size: 16.5px; font-weight: 800; color: #fff; line-height: 1.3; }}
    .card-meta {{ font-size: 12.5px; color: var(--text-muted); margin-top: 4px; display: flex; gap: 6px; align-items: center; }}
    .tag {{
      font-size: 11px;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 6px;
      text-transform: uppercase;
      white-space: nowrap;
    }}
    .tag-blue {{ background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56,189,248,0.3); }}
    .tag-purple {{ background: rgba(168, 85, 247, 0.15); color: #c084fc; border: 1px solid rgba(168,85,247,0.3); }}
    .tag-green {{ background: rgba(34, 197, 94, 0.15); color: #4ade80; border: 1px solid rgba(34,197,94,0.3); }}
    .tag-orange {{ background: rgba(249, 115, 22, 0.15); color: #fb923c; border: 1px solid rgba(249,115,22,0.3); }}

    .audit-box {{
      background: var(--card-inner);
      border: 1px solid #1e293b;
      border-radius: 10px;
      padding: 12px;
      display: flex;
      flex-direction: column;
      gap: 8px;
      font-size: 12.5px;
    }}
    .audit-problem {{ color: #fb923c; line-height: 1.45; }}
    .audit-solution {{ color: #7dd3fc; line-height: 1.45; }}

    .pitch-box {{
      background: #070c16;
      border: 1px solid #1e293b;
      border-radius: 10px;
      overflow: hidden;
    }}
    .pitch-head {{
      background: #0f172a;
      padding: 8px 12px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid #1e293b;
    }}
    .pitch-head span {{ font-size: 11.5px; font-weight: 700; text-transform: uppercase; color: var(--accent); }}
    .btn-copy-action {{
      color: var(--accent);
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
    }}
    .pitch-text {{
      padding: 12px;
      font-size: 12px;
      line-height: 1.55;
      color: #cbd5e1;
      max-height: 130px;
      overflow-y: auto;
      white-space: pre-wrap;
    }}

    .card-btns {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }}
    .btn {{
      flex: 1;
      min-width: 120px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      padding: 10px 12px;
      border-radius: 8px;
      font-size: 12.5px;
      font-weight: 700;
      text-decoration: none;
      cursor: pointer;
      border: none;
      transition: all 0.15s;
    }}
    .btn-wa {{ background: #22c55e; color: #fff; }}
    .btn-wa:hover {{ background: #16a34a; }}
    .btn-call {{ background: #334155; color: #fff; flex: 0 0 auto; min-width: auto; padding: 10px 14px; }}
    .btn-call:hover {{ background: #475569; }}
    .btn-apply {{ background: #0284c7; color: #fff; }}
    .btn-apply:hover {{ background: #0369a1; }}
    .btn-outline {{
      background: transparent;
      color: #cbd5e1;
      border: 1px solid #334155;
      flex: 0 0 auto;
      min-width: auto;
      padding: 10px 12px;
    }}
    .btn-outline:hover {{ background: #1e293b; color: #fff; }}

    /* Resume Section */
    .resume-section {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 16px;
      padding: 24px;
    }}
    .resume-header {{
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      border-bottom: 1px solid var(--card-border);
      padding-bottom: 20px;
      margin-bottom: 22px;
    }}
    .resume-grid {{
      display: grid;
      grid-template-columns: 2fr 1fr;
      gap: 24px;
    }}
    @media (max-width: 800px) {{
      .resume-grid {{ grid-template-columns: 1fr; }}
    }}
    .resume-card {{
      background: var(--card-inner);
      border: 1px solid #1e293b;
      border-radius: 12px;
      padding: 18px;
      margin-bottom: 16px;
    }}
    .resume-card h3 {{
      font-size: 15px;
      font-weight: 800;
      color: var(--accent);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 12px;
      border-bottom: 1px solid #1e293b;
      padding-bottom: 6px;
    }}
    .exp-item {{
      margin-bottom: 14px;
      padding-bottom: 12px;
      border-bottom: 1px dashed #1e293b;
    }}
    .exp-item:last-child {{ border-bottom: none; margin-bottom: 0; padding-bottom: 0; }}
    .exp-title {{ font-size: 14.5px; font-weight: 700; color: #fff; }}
    .exp-sub {{ font-size: 12px; color: var(--text-muted); margin: 3px 0 6px; }}
    .exp-desc {{ font-size: 12.5px; color: #cbd5e1; line-height: 1.45; }}
    .cert-pill {{
      display: inline-block;
      background: rgba(56, 189, 248, 0.1);
      border: 1px solid rgba(56, 189, 248, 0.25);
      color: #7dd3fc;
      font-size: 12px;
      padding: 5px 10px;
      border-radius: 6px;
      margin: 4px;
      font-weight: 600;
    }}

    .hidden {{ display: none !important; }}
    .toast {{
      position: fixed;
      bottom: 20px;
      right: 20px;
      background: #22c55e;
      color: #fff;
      padding: 12px 20px;
      border-radius: 8px;
      font-weight: 700;
      box-shadow: 0 6px 25px rgba(0,0,0,0.6);
      display: none;
      z-index: 1000;
    }}
  </style>
</head>
<body>
  <div class="container">
    <!-- Header -->
    <header>
      <div class="profile-badge">
        <div class="avatar">NA</div>
        <div class="user-info">
          <h1>Nilesh Acharya &bull; Growth Command Center</h1>
          <p>Digital Marketer | Kotputli, Jaipur | +91 95713 34850</p>
        </div>
      </div>
      <div class="header-actions">
        <span class="badge-status">Hourly Drip Engine Active</span>
        <a href="data/Nilesh_Acharya_Resume.pdf" target="_blank" class="btn btn-outline" style="font-size:12px; padding:6px 12px;">
          &#128196; Download PDF Resume
        </a>
      </div>
    </header>

    <!-- Metrics Grid -->
    <div class="metrics-grid">
      <div class="metric-card">
        <div class="label">Review Gap Leads</div>
        <div class="val">{len(leads)}</div>
        <div class="sub">Clinics, Gyms, Coaching (Jaipur, Alwar, Gurgaon)</div>
      </div>
      <div class="metric-card">
        <div class="label">WFH Remote Jobs</div>
        <div class="val">{len(wfh_jobs)}</div>
        <div class="sub">90%+ Match (All-India Work From Home)</div>
      </div>
      <div class="metric-card">
        <div class="label">Nearby Office Jobs</div>
        <div class="val">{len(office_jobs)}</div>
        <div class="sub">Jaipur, Neemrana, Alwar, Gurugram, Delhi</div>
      </div>
      <div class="metric-card">
        <div class="label">Top Match Score</div>
        <div class="val" style="color: #4ade80;">96%</div>
        <div class="sub">80%+ Minimum Cutoff Verified</div>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="nav-tabs">
      <button class="tab-btn active" id="btn-tab-leads" onclick="switchTab('leads')">
        <span>&#128188; Client Leads (Review Gap &amp; Pitches)</span>
        <span class="badge-count" id="tab-lead-count">{len(leads)}</span>
      </button>
      <button class="tab-btn" id="btn-tab-wfh" onclick="switchTab('wfh')">
        <span>&#127968; Work From Home Jobs (WFH)</span>
        <span class="badge-count" id="tab-wfh-count">{len(wfh_jobs)}</span>
      </button>
      <button class="tab-btn" id="btn-tab-office" onclick="switchTab('office')">
        <span>&#127970; Nearby Office Jobs (Jaipur/NCR)</span>
        <span class="badge-count" id="tab-office-count">{len(office_jobs)}</span>
      </button>
      <button class="tab-btn" id="btn-tab-resume" onclick="switchTab('resume')">
        <span>&#128196; My Profile &amp; Verified Resume</span>
      </button>
    </div>

    <!-- Filter Controls -->
    <div class="controls-bar" id="controls-bar">
      <input type="text" id="search-input" class="search-input" placeholder="Search business, role, skill, or city (e.g. Jaipur, Alwar, Meta Ads)..." oninput="filterData()">
      <select id="batch-filter" class="filter-select" onchange="filterData()">
        <option value="all">All Hourly Batches</option>
        <option value="09:00 AM">09:00 AM Batch</option>
        <option value="11:00 AM">11:00 AM Batch</option>
        <option value="01:00 PM">01:00 PM Batch</option>
        <option value="03:00 PM">03:00 PM Batch</option>
        <option value="05:00 PM">05:00 PM Batch</option>
      </select>
    </div>

    <!-- Leads Container -->
    <div id="leads-container" class="cards-grid"></div>

    <!-- WFH Jobs Container -->
    <div id="wfh-container" class="cards-grid hidden"></div>

    <!-- Office Jobs Container -->
    <div id="office-container" class="cards-grid hidden"></div>

    <!-- Resume Section -->
    <div id="resume-container" class="resume-section hidden">
      <div class="resume-header">
        <div>
          <h2 style="font-size:22px; font-weight:800; color:#fff;">NILESH ACHARYA</h2>
          <p style="color:var(--text-muted); font-size:13.5px; margin-top:4px;">
            Digital Marketer &bull; Phone: <strong>+91 95713 34850</strong> &bull; Email: <strong>nileshsharma3011@gmail.com</strong> &bull; Kotputli, Jaipur
          </p>
        </div>
        <div>
          <a href="data/Nilesh_Acharya_Resume.pdf" target="_blank" class="btn btn-apply">
            &#128640; Download Verified PDF Resume
          </a>
        </div>
      </div>

      <div class="resume-grid">
        <div>
          <div class="resume-card">
            <h3>Work Experience</h3>
            <div class="exp-item">
              <div class="exp-title">Digital Marketing Executive @ Leelmax Infotech</div>
              <div class="exp-sub">Bhakrota, Jaipur &bull; 28 Jan 2025 – 27 May 2025 (4 months)</div>
              <div class="exp-desc">
                Managed end-to-end Ad Campaigns on Google Ads & Meta Ads. Handled client Social Media accounts (Instagram, LinkedIn). Assisted in WordPress Website Development, on-page SEO, landing page delivery, and campaign conversion optimization.
              </div>
            </div>
            <div class="exp-item">
              <div class="exp-title">Social Media Handler @ NFPCY Real Estate</div>
              <div class="exp-sub">Neemrana, Rajasthan &bull; 28 May 2025 – 1 July 2025 (1 month)</div>
              <div class="exp-desc">
                Managed company social media profiles, daily posting, property reels creation using Canva & AI tools. Engaged with prospective real-estate buyer leads via DMs to qualify budget and requirements.
              </div>
            </div>
          </div>

          <div class="resume-card">
            <h3>Core Technical Skills</h3>
            <div style="font-size:13px; color:#cbd5e1; line-height:1.6;">
              <strong style="color:#fff;">Specializations:</strong> SEO, Social Media Marketing (SMM), Google Ads, Meta Ads (Facebook & Instagram), B2B/B2C Lead Generation Funnels, WhatsApp Chatbot Automation, Keyword Research, WordPress Web Design, Google Analytics, Local Business SEO.<br><br>
              <strong style="color:#fff;">Tools:</strong> Canva, Filmora, Semrush, Google Ads, Ubersuggest, ChatGPT & AI Tools, Mailchimp, WordPress, Google Analytics, Meta Ads Manager, Google Keyword Planner.
            </div>
          </div>
        </div>

        <div>
          <div class="resume-card">
            <h3>Certifications</h3>
            <div style="display:flex; flex-direction:column; gap:6px;">
              <span class="cert-pill">&#9989; 9x Google Ads Certificates (Google)</span>
              <span class="cert-pill">&#9989; SEO Certificate (Semrush Academy)</span>
              <span class="cert-pill">&#9989; Email Marketing (HubSpot Academy)</span>
              <span class="cert-pill">&#9989; Amazon ATES Certificate (Amazon)</span>
              <span class="cert-pill">&#9989; 12th Pass (Ajmer Board, Rajasthan)</span>
            </div>
          </div>

          <div class="resume-card">
            <h3>Contact &amp; Dispatch Channels</h3>
            <div style="font-size:13px; color:#cbd5e1; line-height:1.6;">
              <strong>Direct Call / WhatsApp:</strong> +91 95713 34850<br>
              <strong>Job Apply Email:</strong> nileshsharma3011@gmail.com<br>
              <strong>Client Outreach Email:</strong> nileshsharma.digitalgrowth@gmail.com<br>
              <strong>Hometown:</strong> Kotputli, Jaipur, Rajasthan<br>
              <strong>Target Work Modes:</strong> Remote (WFH) &amp; Office (Jaipur, Gurugram, Delhi, Neemrana, Alwar)
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div id="toast" class="toast">Copied to clipboard!</div>

  <!-- Raw JSON embedded safely inside application/json tags -->
  <script id="leads-json" type="application/json">
{leads_json_str}
  </script>

  <script id="jobs-json" type="application/json">
{jobs_json_str}
  </script>

  <script>
    let leadsData = [];
    let jobsData = [];
    let currentTab = 'leads';

    try {{
      leadsData = JSON.parse(document.getElementById('leads-json').textContent.trim());
      jobsData = JSON.parse(document.getElementById('jobs-json').textContent.trim());
    }} catch (err) {{
      console.error('Error parsing data JSON:', err);
    }}

    function renderLeads(leads) {{
      const container = document.getElementById('leads-container');
      if (!leads || leads.length === 0) {{
        container.innerHTML = `<div style="grid-column: 1/-1; text-align:center; padding: 40px; color: var(--text-muted);">No business leads match your filter.</div>`;
        return;
      }}
      container.innerHTML = leads.map(l => `
        <div class="card">
          <div>
            <div class="card-top">
              <div>
                <div class="card-title">${{escapeHtml(l.business_name)}}</div>
                <div class="card-meta">
                  <span>&#128205; ${{escapeHtml(l.city)}}, ${{escapeHtml(l.state)}}</span>
                  <span>&bull;</span>
                  <span>${{escapeHtml(l.category)}}</span>
                </div>
              </div>
              <div style="display:flex; flex-direction:column; align-items:flex-end; gap:4px;">
                <span class="tag tag-orange">${{escapeHtml(l.batch_time || '09:00 AM')}}</span>
                <span class="tag ${{l.status === 'Shortlisted' ? 'tag-purple' : 'tag-blue'}}">${{escapeHtml(l.status || 'New')}}</span>
              </div>
            </div>

            <div class="audit-box" style="margin-top: 12px;">
              <div class="audit-problem">
                <strong>&#9888; Review Gap / Audit:</strong> ${{escapeHtml(l.reviews || '')}}<br>
                ${{escapeHtml(l.audit_problem || '')}}
              </div>
              <div class="audit-solution">
                <strong>&#10024; Low-Cost Growth Solution:</strong> ${{escapeHtml(l.solution_offered || '')}}
              </div>
            </div>
          </div>

          <div class="pitch-box">
            <div class="pitch-head">
              <span>&#128172; Radhe Radhe WhatsApp Pitch</span>
              <span class="btn-copy-action" onclick="copyLeadPitch('${{escapeQuotes(l.outreach_pitch)}}')">&#128203; Copy</span>
            </div>
            <div class="pitch-text">${{escapeHtml(l.outreach_pitch)}}</div>
          </div>

          <div class="card-btns">
            ${{l.wa_link ? `<a href="${{l.wa_link}}" target="_blank" class="btn btn-wa" title="Open 1-Click WhatsApp Chat">&#128172; 1-Click WhatsApp</a>` : ''}}
            <a href="tel:${{escapeHtml(l.phone || '').replace(/[^0-9]/g, '')}}" class="btn btn-call" title="Call Business Directly">
              &#128222; Call Owner
            </a>
            ${{l.maps_link ? `<a href="${{l.maps_link}}" target="_blank" class="btn btn-outline" title="Open Google Maps Profile" style="color:#38bdf8;">&#128205; Google Maps</a>` : ''}}
            <button class="btn btn-outline" onclick="copyLeadPitch('${{escapeQuotes(l.outreach_pitch)}}')" title="Copy pitch text">
              &#128203; Copy Pitch
            </button>
          </div>
        </div>
      `).join('');
    }}

    function renderJobCards(containerId, jobList) {{
      const container = document.getElementById(containerId);
      if (!jobList || jobList.length === 0) {{
        container.innerHTML = `<div style="grid-column: 1/-1; text-align:center; padding: 40px; color: var(--text-muted);">No matching job postings found.</div>`;
        return;
      }}
      container.innerHTML = jobList.map(j => `
        <div class="card">
          <div>
            <div class="card-top">
              <div>
                <div class="card-title">${{escapeHtml(j.title)}}</div>
                <div class="card-meta">
                  <span>&#127970; ${{escapeHtml(j.company)}}</span>
                  <span>&bull;</span>
                  <span>&#128205; ${{escapeHtml(j.location)}}</span>
                </div>
              </div>
              <div style="display:flex; flex-direction:column; align-items:flex-end; gap:4px;">
                <span class="tag tag-orange">${{escapeHtml(j.batch_time || '09:00 AM')}}</span>
                <span class="tag tag-green">${{escapeHtml(j.match_score || '90%')}}</span>
              </div>
            </div>

            <div style="display:flex; flex-wrap:wrap; gap:6px; margin: 10px 0;">
              <span class="tag tag-blue">${{escapeHtml(j.salary || '')}}</span>
              <span class="tag tag-purple">&#9201; ${{escapeHtml(j.experience || '1-3 Yrs')}}</span>
              <span class="tag tag-green">${{escapeHtml(j.type || 'Full-Time')}}</span>
            </div>

            <div style="display:flex; flex-wrap:wrap; gap:5px; margin-top: 6px;">
              ${{(j.key_skills || []).map(s => `<span style="font-size:11px; background:#1e293b; color:#cbd5e1; padding:2px 7px; border-radius:5px; border:1px solid #334155;">${{escapeHtml(s)}}</span>`).join('')}}
            </div>
          </div>

          <div class="pitch-box">
            <div class="pitch-head">
              <span>Recruiter Cover Note (Resume Attached)</span>
              <span class="btn-copy-action" onclick="copyLeadPitch('${{escapeQuotes(j.cover_note)}}')">&#128203; Copy</span>
            </div>
            <div class="pitch-text">${{escapeHtml(j.cover_note)}}</div>
          </div>

          <div class="card-btns">
            <a href="${{j.apply_link || '#'}}" target="_blank" class="btn btn-apply">
              &#128640; Direct 1-Click Apply
            </a>
            ${{j.phone ? `<a href="https://wa.me/${{j.phone.replace(/[^0-9]/g, '')}}?text=${{encodeURIComponent(j.wa_apply_text || '')}}" target="_blank" class="btn btn-wa" title="Apply via WhatsApp">&#128172; WhatsApp Apply</a>` : ''}}
            <button class="btn btn-outline" onclick="copyLeadPitch('${{escapeQuotes(j.cover_note)}}')">
              &#128203; Copy Cover Note
            </button>
          </div>
        </div>
      `).join('');
    }}

    function switchTab(tab) {{
      currentTab = tab;
      document.getElementById('btn-tab-leads').classList.toggle('active', tab === 'leads');
      document.getElementById('btn-tab-wfh').classList.toggle('active', tab === 'wfh');
      document.getElementById('btn-tab-office').classList.toggle('active', tab === 'office');
      document.getElementById('btn-tab-resume').classList.toggle('active', tab === 'resume');

      document.getElementById('leads-container').classList.toggle('hidden', tab !== 'leads');
      document.getElementById('wfh-container').classList.toggle('hidden', tab !== 'wfh');
      document.getElementById('office-container').classList.toggle('hidden', tab !== 'office');
      document.getElementById('resume-container').classList.toggle('hidden', tab !== 'resume');
      document.getElementById('controls-bar').classList.toggle('hidden', tab === 'resume');

      if (tab !== 'resume') {{
        filterData();
      }}
    }}

    function filterData() {{
      const q = (document.getElementById('search-input').value || '').toLowerCase().trim();
      const batch = document.getElementById('batch-filter').value;

      if (currentTab === 'leads') {{
        const filtered = leadsData.filter(l => {{
          const matchQ = !q || (l.business_name || '').toLowerCase().includes(q) ||
            (l.city || '').toLowerCase().includes(q) ||
            (l.category || '').toLowerCase().includes(q);

          const matchB = batch === 'all' || (l.batch_time || '').includes(batch);
          return matchQ && matchB;
        }});
        renderLeads(filtered);
      }} else if (currentTab === 'wfh') {{
        const wfhJobs = jobsData.filter(j => j.job_category === 'WFH' || (j.location || '').includes('Remote'));
        const filtered = wfhJobs.filter(j => {{
          const matchQ = !q || (j.title || '').toLowerCase().includes(q) ||
            (j.company || '').toLowerCase().includes(q) ||
            (j.key_skills || []).some(k => k.toLowerCase().includes(q));

          const matchB = batch === 'all' || (j.batch_time || '').includes(batch);
          return matchQ && matchB;
        }});
        renderJobCards('wfh-container', filtered);
      }} else if (currentTab === 'office') {{
        const officeJobs = jobsData.filter(j => j.job_category === 'Office' || !(j.location || '').includes('Remote'));
        const filtered = officeJobs.filter(j => {{
          const matchQ = !q || (j.title || '').toLowerCase().includes(q) ||
            (j.company || '').toLowerCase().includes(q) ||
            (j.location || '').toLowerCase().includes(q) ||
            (j.key_skills || []).some(k => k.toLowerCase().includes(q));

          const matchB = batch === 'all' || (j.batch_time || '').includes(batch);
          return matchQ && matchB;
        }});
        renderJobCards('office-container', filtered);
      }}
    }}

    function escapeQuotes(str) {{
      if (!str) return '';
      return String(str).replace(/\\\\/g, '\\\\\\\\').replace(/'/g, "\\\\'").replace(/"/g, '&quot;').replace(/\\n/g, '\\\\n');
    }}

    function escapeHtml(str) {{
      if (!str) return '';
      return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }}

    function copyLeadPitch(text) {{
      const formatted = text.replace(/\\\\n/g, '\\n');
      navigator.clipboard.writeText(formatted).then(() => {{
        showToast('Copied to clipboard!');
      }}).catch(() => {{
        showToast('Copied!');
      }});
    }}

    function showToast(msg) {{
      const toast = document.getElementById('toast');
      toast.textContent = msg;
      toast.style.display = 'block';
      setTimeout(() => {{ toast.style.display = 'none'; }}, 2200);
    }}

    // Initial render
    renderLeads(leadsData);
    renderJobCards('wfh-container', jobsData.filter(j => j.job_category === 'WFH' || (j.location || '').includes('Remote')));
    renderJobCards('office-container', jobsData.filter(j => j.job_category === 'Office' || !(j.location || '').includes('Remote')));
  </script>
</body>
</html>
'''

with open(DASHBOARD_FILE, "w", encoding="utf-8") as f:
    f.write(html_content)

with open(INDEX_FILE, "w", encoding="utf-8") as f:
    f.write(html_content)

print("Pro segregated dashboard (dashboard.html & index.html) generated successfully!")

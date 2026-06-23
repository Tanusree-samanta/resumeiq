/* ResumeIQ – Frontend Application Logic
 * Calls the FastAPI backend at /api/analyze
 * Falls back to direct Anthropic API if VITE_ANTHROPIC_KEY is set (dev only)
 */

const API_BASE = window.location.hostname === 'localhost'
  ? 'http://localhost:8000'
  : '';  // same-origin in production

let resumeText = '';
let pdfBase64  = '';

const fileInput  = document.getElementById('fileInput');
const dropZone   = document.getElementById('dropZone');
const analyzeBtn = document.getElementById('analyzeBtn');
const jobDescTA  = document.getElementById('jobDesc');

// ── Enable/disable button ─────────────────────────────────────────────────────
function checkReady() {
  analyzeBtn.disabled = !(resumeText || pdfBase64) || !jobDescTA.value.trim();
}
jobDescTA.addEventListener('input', checkReady);

// ── File handling ─────────────────────────────────────────────────────────────
fileInput.addEventListener('change', e => {
  const f = e.target.files[0];
  if (f) handleFile(f);
});

dropZone.addEventListener('dragover',  e => { e.preventDefault(); dropZone.classList.add('drag'); });
dropZone.addEventListener('dragleave', ()  => dropZone.classList.remove('drag'));
dropZone.addEventListener('drop', e => {
  e.preventDefault(); dropZone.classList.remove('drag');
  const f = e.dataTransfer.files[0];
  if (f) handleFile(f);
});

function handleFile(f) {
  document.getElementById('fileBadge').style.display = 'inline-flex';
  document.getElementById('fileName').textContent = f.name;
  dropZone.classList.add('has-file');
  document.getElementById('uploadIcon').textContent = '✅';

  if (f.type === 'application/pdf') {
    const reader = new FileReader();
    reader.onload = ev => {
      pdfBase64   = ev.target.result.split(',')[1];
      resumeText  = '';
      checkReady();
    };
    reader.readAsDataURL(f);
  } else {
    const reader = new FileReader();
    reader.onload = ev => {
      resumeText = ev.target.result;
      pdfBase64  = '';
      checkReady();
    };
    reader.readAsText(f);
  }
}

// ── Analyze ───────────────────────────────────────────────────────────────────
async function analyze() {
  const jd = jobDescTA.value.trim();
  if (!(resumeText || pdfBase64) || !jd) return;

  const errBox     = document.getElementById('errorBox');
  const resultsDiv = document.getElementById('results');

  analyzeBtn.disabled = true;
  analyzeBtn.classList.add('loading');
  analyzeBtn.innerHTML = '<span class="spinner"></span>Analyzing with AI…';
  errBox.style.display    = 'none';
  resultsDiv.style.display = 'none';

  try {
    const payload = {
      job_description: jd,
      resume_text:  resumeText  || null,
      resume_pdf:   pdfBase64   || null,
    };

    const res = await fetch(`${API_BASE}/api/analyze`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(payload),
    });

    if (!res.ok) {
      const e = await res.json().catch(() => ({}));
      throw new Error(e.detail || `HTTP ${res.status}`);
    }

    const result = await res.json();
    renderResults(result);

  } catch (err) {
    errBox.textContent  = '⚠️ ' + err.message;
    errBox.style.display = 'block';
  } finally {
    analyzeBtn.disabled = false;
    analyzeBtn.classList.remove('loading');
    analyzeBtn.innerHTML = 'Re-analyze';
    checkReady();
  }
}

// ── Render results ────────────────────────────────────────────────────────────
function tierColor(tier) {
  return { Excellent: '#3fb950', Strong: '#00e5cc', Good: '#f0b429', Fair: '#f0b429', Weak: '#f85149' }[tier] || '#8b949e';
}

function renderSkills(arr, cls) {
  return arr.slice(0, 20).map(s => `<span class="skill-tag ${cls}">${s}</span>`).join('');
}

function renderSuggestions(arr) {
  const icon = { high: '!', medium: '~', low: '✓' };
  return arr.map(s =>
    `<li class="suggestion-item">
       <span class="sug-icon sug-${s.priority}">${icon[s.priority] || '·'}</span>
       <span class="sug-text">${s.text}</span>
     </li>`
  ).join('');
}

function renderResults(r) {
  const score        = Math.min(100, Math.max(0, r.score || 0));
  const circumference = 2 * Math.PI * 52;
  const dashOffset   = circumference * (1 - score / 100);
  const tc = tierColor(r.tier);
  const tierBgMap = {
    Excellent: 'rgba(63,185,80,0.12)', Strong: 'rgba(0,229,204,0.12)',
    Good: 'rgba(240,180,41,0.12)',     Fair:  'rgba(240,180,41,0.12)',
    Weak: 'rgba(248,81,73,0.12)',
  };
  const tierBg  = tierBgMap[r.tier] || 'rgba(139,148,158,0.12)';
  const fitLabel = { Under: '📉 Possibly overqualified', Match: '🎯 Seniority match', Over: '📈 May be a stretch' }[r.seniority_fit] || '';

  document.getElementById('results').style.display = 'block';
  document.getElementById('results').innerHTML = `
<div class="panel" style="margin-bottom:1rem;">
  <div class="three-cols">
    <div class="score-ring-section" style="grid-column:1/2;padding:1.5rem 0.5rem;">
      <div class="score-ring-wrap">
        <svg width="140" height="140" viewBox="0 0 140 140">
          <circle cx="70" cy="70" r="52" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="10"/>
          <circle cx="70" cy="70" r="52" fill="none" stroke="${tc}" stroke-width="10"
            stroke-dasharray="${circumference.toFixed(2)}"
            stroke-dashoffset="${dashOffset.toFixed(2)}"
            stroke-linecap="round"
            style="transition:stroke-dashoffset 1.4s cubic-bezier(0.4,0,0.2,1)"
            id="scoreCircle"/>
        </svg>
        <div class="score-number">
          <span class="score-val">${score}</span>
          <span class="score-pct">/ 100</span>
        </div>
      </div>
      <span class="score-tier" style="background:${tierBg};color:${tc};border:1px solid ${tc}33;">${r.tier} Match</span>
      <div class="ring-label">Overall Score</div>
    </div>
    <div style="grid-column:2/4;display:flex;flex-direction:column;justify-content:center;gap:0.875rem;padding:1.5rem 1rem 1.5rem 0;">
      <div>
        <div class="section-label" style="margin-bottom:4px;">ATS Compatibility</div>
        <div style="display:flex;align-items:center;gap:10px;">
          <div class="progress-bar-wrap" style="flex:1"><div class="progress-bar" style="width:${r.ats_score || 0}%"></div></div>
          <span style="font-family:var(--mono);font-size:13px;color:var(--teal);min-width:36px">${r.ats_score || 0}%</span>
        </div>
      </div>
      <div>
        <div class="section-label" style="margin-bottom:4px;">Keyword Density</div>
        <div style="display:flex;align-items:center;gap:10px;">
          <div class="progress-bar-wrap" style="flex:1"><div class="progress-bar" style="width:${r.keyword_density || 0}%;background:var(--purple)"></div></div>
          <span style="font-family:var(--mono);font-size:13px;color:var(--purple);min-width:36px">${r.keyword_density || 0}%</span>
        </div>
      </div>
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:4px;">
        ${r.experience_years != null ? `<span class="meta-pill">⏱ ${r.experience_years}+ yrs detected</span>` : ''}
        ${fitLabel ? `<span class="meta-pill">${fitLabel}</span>` : ''}
        <span class="meta-pill">✅ ${(r.matched_skills||[]).length} skills matched</span>
        <span class="meta-pill">❌ ${(r.missing_skills||[]).length} gaps found</span>
      </div>
    </div>
  </div>
</div>

<div class="panel" style="margin-bottom:1rem;">
  <div class="section-head">
    <div class="section-head-icon" style="background:rgba(0,229,204,0.12);color:var(--teal);">💬</div>
    <span style="font-weight:500;font-size:14px;">Analysis Summary</span>
  </div>
  <div class="summary-text">${r.summary || ''}</div>
</div>

<div class="panel" style="margin-bottom:1rem;">
  <div class="section-head">
    <div class="section-head-icon" style="background:rgba(63,185,80,0.12);color:var(--green);">🔧</div>
    <span style="font-weight:500;font-size:14px;">Skills Breakdown</span>
  </div>
  ${(r.matched_skills||[]).length ? `
    <div class="section-label" style="color:var(--green);margin-top:0.75rem;">Matched (${r.matched_skills.length})</div>
    <div class="skills-grid">${renderSkills(r.matched_skills, 'skill-match')}</div>` : ''}
  ${(r.partial_skills||[]).length ? `
    <div class="divider"></div>
    <div class="section-label" style="color:var(--amber);">Partial / Implied (${r.partial_skills.length})</div>
    <div class="skills-grid">${renderSkills(r.partial_skills, 'skill-partial')}</div>` : ''}
  ${(r.missing_skills||[]).length ? `
    <div class="divider"></div>
    <div class="section-label" style="color:var(--red);">Missing / Gaps (${r.missing_skills.length})</div>
    <div class="skills-grid">${renderSkills(r.missing_skills, 'skill-missing')}</div>` : ''}
</div>

<div class="panel">
  <div class="section-head">
    <div class="section-head-icon" style="background:rgba(163,113,247,0.12);color:var(--purple);">💡</div>
    <span style="font-weight:500;font-size:14px;">Actionable Suggestions</span>
  </div>
  <ul class="suggestions-list">${renderSuggestions(r.suggestions || [])}</ul>
</div>`;

  document.getElementById('results').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

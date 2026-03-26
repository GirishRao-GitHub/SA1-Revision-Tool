import codecs
import re

path = r'g:\Girish\IAI\SP1 and SA1 Health and Care\Practice papers\Claude Widgets\IFoA SA1 Exam Revision Tool 2019-2025.html'

with codecs.open(path, 'r', 'utf-8') as f:
    text = f.read()

# 1. Add mode toggle CSS
css_add = """
/* MODE TOGGLE */
.mode-toggle { display: flex; align-items: center; justify-content: center; padding: 10px; background: var(--surface2); border-bottom: 1px solid var(--border); gap: 10px; }
.mode-btn { padding: 6px 12px; font-size: 12px; font-weight: 600; font-family: var(--sans); border-radius: 20px; border: 1px solid var(--border2); background: var(--surface); color: var(--text2); cursor: pointer; transition: all 0.2s; }
.mode-btn.active { background: var(--accent); color: #fff; border-color: var(--accent); box-shadow: 0 0 10px rgba(139,92,246,0.3); }
"""

if "/* MODE TOGGLE */" not in text:
    text = text.replace("/* SELECTORS */", css_add + "\n/* SELECTORS */")

# 2. Add Topbar Toggle and New Selectors
new_selectors = """    <div class="mode-toggle">
      <button id="btn-mode-chrono" class="mode-btn active" onclick="setMode('chrono')">Chronological</button>
      <button id="btn-mode-theme" class="mode-btn" onclick="setMode('theme')">Revise by Theme</button>
      <div id="data-status" style="margin-left:auto;font-size:11px;color:var(--text3);font-family:var(--mono);">Loading Sittings...</div>
    </div>

    <!-- CHRONOLOGICAL SELECTORS -->
    <div class="selectors" id="chrono-selectors">
      <div class="sel-group sel-chapter-wrap">
        <div class="sel-label">Sitting <span id="assign-timer" style="display:none;font-family:var(--mono);font-size:12px;font-weight:400;color:var(--text3);letter-spacing:.03em;">— 00:00:00</span></div>
        <select id="sel-assign" onchange="onAssignChange()" style="width:auto;" disabled>
          <option value="">— select —</option>
        </select>
      </div>
      <div class="sel-group sel-question-wrap">
        <div class="sel-label">Question
          <button id="btn-q-prev" onclick="navQuestion(-1)" disabled style="cursor:pointer;">◀</button>
          <button id="btn-q-next" onclick="navQuestion(1)" disabled style="cursor:pointer;">▶</button>
        </div>
        <select id="sel-question" onchange="onQuestionChange()" disabled>
          <option value="">— select —</option>
        </select>
      </div>
      <div class="sel-group sel-sub-wrap" id="sub-wrap" style="display:none;">
        <div class="scroller-ctrl">
          <div class="sel-label">Sub-question</div>
          <button class="scroll-btn" onclick="navSub(-1)" id="btn-s-prev">◀</button>
          <button class="scroll-btn" onclick="navSub(1)" id="btn-s-next">▶</button>
        </div>
        <select id="sel-sub" onchange="onSubChange()">
          <option value="">— part —</option>
        </select>
      </div>
      <div class="marks-stack" id="stack-chrono">
        <div id="total-marks-pill" class="marks-pill" style="display:none;">Overall: <span id="total-marks-val">0</span> marks</div>
        <div id="marks-pill" class="marks-pill" style="display:none;"></div>
      </div>
    </div>

    <!-- THEMATIC SELECTORS -->
    <div class="selectors" id="theme-selectors" style="display:none;">
      <div class="sel-group sel-chapter-wrap" style="min-width: 200px;">
        <div class="sel-label">Theme / Topic</div>
        <select id="sel-theme" onchange="onThemeChange()" style="width:auto;" disabled>
          <option value="">— select —</option>
        </select>
      </div>
      <div class="sel-group sel-question-wrap">
        <div class="sel-label">Matches
          <button id="btn-t-prev" onclick="navThemeMatch(-1)" disabled style="cursor:pointer;">◀</button>
          <button id="btn-t-next" onclick="navThemeMatch(1)" disabled style="cursor:pointer;">▶</button>
        </div>
        <select id="sel-match" onchange="onMatchChange()" disabled>
          <option value="">— select —</option>
        </select>
      </div>
      <div class="marks-stack" id="stack-theme"></div>
    </div>"""

# Replace the HTML selectively
start_marker_html = '<div class="selectors">'
end_marker_html = '<div class="scenario-wrap" id="scenario-wrap"'

s_html = text.find(start_marker_html)
e_html = text.find(end_marker_html)

if s_html != -1 and e_html != -1:
    text = text[:s_html] + new_selectors + "\n    " + text[e_html:]

# 3. Complete JS Rewrite Injection
new_js = """<script>
// ═══════════════════════════════════════════════════════════
// DATA STRATEGY (Dynamic Load)
// ═══════════════════════════════════════════════════════════
let SITTINGS = {};
let TAXONOMY = [];
let THEMATICS = []; // Array of matches representing sub-questions mapped to themes

// Configuration of papers to load (could be expanded)
const SITTING_FILES = ['201904.json']; 

let appMode = 'chrono'; // chrono, theme
let currentQ = null, currentSub = null, currentPoints = [];
let revealed = 0, hits = null, manualMode = false;
let timer = null, seconds = 0, limitSecs = 0, isPaused = false;
let assignTimer = null, assignSeconds = 0;

window.onload = async function() {
    try {
        const taxRes = await fetch('sa1_taxonomy.json');
        if (taxRes.ok) {
            TAXONOMY = await taxRes.json();
            populateThemes();
        }
    } catch(e) { console.warn("Failed to load taxonomy", e); }

    let loadedCount = 0;
    const ssel = document.getElementById('sel-assign');
    
    for (const f of SITTING_FILES) {
        try {
            const res = await fetch('data/' + f);
            if (res.ok) {
                const data = await res.json();
                const key = f.replace('.json', '');
                SITTINGS[key] = data;
                
                // Add to Chronological Dropdown
                const opt = document.createElement('option');
                opt.value = key; opt.textContent = data.label;
                ssel.appendChild(opt);
                
                // Index to Thematics
                indexThematics(key, data);
                loadedCount++;
            }
        } catch(e) { console.warn("Failed to load " + f, e); }
    }
    
    ssel.disabled = loadedCount === 0;
    document.getElementById('data-status').textContent = `Loaded ${loadedCount} Sittings`;
};

function indexThematics(sittingKey, sittingData) {
    if(!sittingData.questions) return;
    Object.keys(sittingData.questions).forEach(qk => {
        const qData = sittingData.questions[qk];
        // Does the parent question have themes?
        if (qData.themes && qData.themes.length > 0) {
            qData.themes.forEach(t => {
                THEMATICS.push({ theme: t, sitting: sittingKey, qk: qk, pk: null, label: `${sittingData.label} ${qData.label} (Whole)` });
            });
        }
        
        // Parts
        if (qData.parts) {
            Object.keys(qData.parts).forEach(pk => {
                const pData = qData.parts[pk];
                if (pData.themes && pData.themes.length > 0) {
                    pData.themes.forEach(t => {
                        THEMATICS.push({ theme: t, sitting: sittingKey, qk: qk, pk: pk, label: `${sittingData.label} ${qk} ${pk}` });
                    });
                }
            });
        }
    });
}

function populateThemes() {
    const tsel = document.getElementById('sel-theme');
    TAXONOMY.forEach(t => {
        const opt = document.createElement('option');
        opt.value = t; opt.textContent = t;
        tsel.appendChild(opt);
    });
    tsel.disabled = false;
}

function setMode(mode) {
    appMode = mode;
    document.getElementById('btn-mode-chrono').classList.toggle('active', mode==='chrono');
    document.getElementById('btn-mode-theme').classList.toggle('active', mode==='theme');
    document.getElementById('chrono-selectors').style.display = mode === 'chrono' ? 'flex' : 'none';
    document.getElementById('theme-selectors').style.display = mode === 'theme' ? 'flex' : 'none';
    
    // Move marks logic
    const ms = document.getElementById(mode === 'chrono' ? 'stack-chrono' : 'stack-theme');
    ms.appendChild(document.getElementById('total-marks-pill'));
    ms.appendChild(document.getElementById('marks-pill'));

    resetAll();
    
    if (mode === 'chrono') {
        onAssignChange();
    } else {
        onThemeChange();
    }
}

// ═══════════════════════════════════════════════════════════
// UI LOGIC (CHRONO)
// ═══════════════════════════════════════════════════════════
function onAssignChange() {
  if (!document.fullscreenElement) document.documentElement.requestFullscreen().catch(e => console.log("FS blocked"));
  const k = document.getElementById('sel-assign').value;
  const qsel = document.getElementById('sel-question');
  qsel.innerHTML = '<option value="">— select —</option>';
  if (k && SITTINGS[k]) {
    Object.keys(SITTINGS[k].questions).forEach(qk => {
      const opt = document.createElement('option');
      opt.value = qk; opt.textContent = SITTINGS[k].questions[qk].label;
      qsel.appendChild(opt);
    });
    qsel.disabled = false;
  } else {
    qsel.disabled = true;
  }
  resetAll();
  resetAssignTimer();
  document.getElementById('btn-q-prev').disabled = true;
  document.getElementById('btn-q-next').disabled = true;
  document.getElementById('btn-print-q').disabled = true;
  const stEl = document.getElementById('assign-timer');
  if (stEl) {
    stEl.style.display = k ? 'inline' : 'none';
    if (k) startAssignTimer();
  }
}

function onQuestionChange() {
  const ak = document.getElementById('sel-assign').value;
  const qk = document.getElementById('sel-question').value;
  const ssel = document.getElementById('sel-sub');
  const swrap = document.getElementById('sub-wrap');
  
  ssel.innerHTML = '<option value="">— part —</option>';
  swrap.style.display = 'none';
  currentQ = (ak && qk) ? SITTINGS[ak].questions[qk] : null;
  currentSub = null;

  if (currentQ && currentQ.parts) {
    Object.keys(currentQ.parts).forEach(pk => {
      const opt = document.createElement('option');
      opt.value = pk; opt.textContent = pk;
      ssel.appendChild(opt);
    });
    swrap.style.display = 'block';
    setupQuestion(null);
  } else if (currentQ) {
    setupQuestion(currentQ);
  } else {
    setupQuestion(null);
  }
  updateNavButtons();
}

function onSubChange() {
  const pk = document.getElementById('sel-sub').value;
  currentSub = (currentQ && pk) ? currentQ.parts[pk] : null;
  setupQuestion(currentSub || currentQ);
  updateSubNavButtons();
}

function navQuestion(dir) {
  const qsel = document.getElementById('sel-question');
  if (qsel.selectedIndex + dir >= 1 && qsel.selectedIndex + dir < qsel.options.length) {
    qsel.selectedIndex += dir;
    onQuestionChange();
  }
}

function navSub(dir) {
  const ssel = document.getElementById('sel-sub');
  if (ssel.selectedIndex + dir >= 1 && ssel.selectedIndex + dir < ssel.options.length) {
    ssel.selectedIndex += dir;
    onSubChange();
  }
}

function updateNavButtons() {
  const qsel = document.getElementById('sel-question');
  document.getElementById('btn-q-prev').disabled = qsel.selectedIndex <= 1;
  document.getElementById('btn-q-next').disabled = qsel.selectedIndex >= qsel.options.length - 1;
}

function updateSubNavButtons() {
  const ssel = document.getElementById('sel-sub');
  const sprev = document.getElementById('btn-s-prev');
  const snext = document.getElementById('btn-s-next');
  if (sprev) sprev.disabled = ssel.selectedIndex <= 1;
  if (snext) snext.disabled = ssel.selectedIndex >= ssel.options.length - 1;
}

// ═══════════════════════════════════════════════════════════
// UI LOGIC (THEMATIC)
// ═══════════════════════════════════════════════════════════
function onThemeChange() {
    const t = document.getElementById('sel-theme').value;
    const msel = document.getElementById('sel-match');
    msel.innerHTML = '<option value="">— select —</option>';
    
    if (t) {
        const matches = THEMATICS.filter(x => x.theme === t);
        matches.forEach((m, i) => {
            const opt = document.createElement('option');
            opt.value = i; // Store index in filtered array
            opt.textContent = m.label;
            opt.dataset.json = JSON.stringify(m);
            msel.appendChild(opt);
        });
        msel.disabled = false;
    } else {
        msel.disabled = true;
    }
    resetAll();
    currentQ = null;
    currentSub = null;
    updateThemeNavButtons();
}

function onMatchChange() {
    const msel = document.getElementById('sel-match');
    const opt = msel.options[msel.selectedIndex];
    if (msel.selectedIndex === 0 || !opt.dataset.json) {
        currentQ = null;
        currentSub = null;
        setupQuestion(null);
        updateThemeNavButtons();
        return;
    }
    
    const m = JSON.parse(opt.dataset.json);
    currentQ = SITTINGS[m.sitting].questions[m.qk];
    currentSub = m.pk ? currentQ.parts[m.pk] : null;
    
    setupQuestion(currentSub || currentQ);
    updateThemeNavButtons();
}

function navThemeMatch(dir) {
    const msel = document.getElementById('sel-match');
    if (msel.selectedIndex + dir >= 1 && msel.selectedIndex + dir < msel.options.length) {
        msel.selectedIndex += dir;
        onMatchChange();
    }
}

function updateThemeNavButtons() {
  const msel = document.getElementById('sel-match');
  document.getElementById('btn-t-prev').disabled = msel.selectedIndex <= 1;
  document.getElementById('btn-t-next').disabled = msel.selectedIndex >= msel.options.length - 1;
}

// ═══════════════════════════════════════════════════════════
// CORE SETUP
// ═══════════════════════════════════════════════════════════
function setupQuestion(q) {
  stopTimer();
  revealed = 0; hits = null; manualMode = false;
  document.getElementById('points-outer').innerHTML = '';
  document.getElementById('points-outer').style.display = 'none';
  document.getElementById('empty-pane').style.display = 'flex';
  document.getElementById('loading-pane').classList.remove('active');
  document.getElementById('summary').classList.remove('show');
  document.getElementById('extras-section').style.display = 'none';
  document.getElementById('btn-save-sm').style.display = 'none';
  document.getElementById('review-controls').style.display = 'none';
  document.getElementById('pbar').style.width = '0%';
  document.getElementById('pcnt').textContent = '0';
  document.getElementById('ptotal').textContent = '0';
  
  const ab = document.getElementById('answer-box');
  const nb = document.getElementById('notes-box');
  const nw = document.getElementById('notes-wrap');
  const synw = document.getElementById('synopsis-wrap');
  ab.readOnly = false;
  nw.style.display = 'none';
  synw.style.display = 'none';
  nb.value = '';
  
  if (!q) {
    document.getElementById('right-empty-pane').style.display = 'flex';
    document.getElementById('timer-zone').style.display = 'none';
    document.getElementById('question-text').style.display = 'none';
    document.getElementById('answer-wrap').style.display = 'none';
    document.getElementById('scenario-wrap').style.display = 'none';
    document.getElementById('marks-pill').style.display = 'none';
    document.getElementById('total-marks-pill').style.display = 'none';
    return;
  }

  document.getElementById('right-empty-pane').style.display = 'none';
  document.getElementById('timer-zone').style.display = 'flex';
  document.getElementById('question-text').style.display = 'block';
  document.getElementById('answer-wrap').style.display = 'flex';
  document.getElementById('question-text').innerHTML = q.question || q.label;
  
  const totalMarksFill = document.getElementById('total-marks-pill');
  if (currentQ && currentQ.marks) {
    totalMarksFill.style.display = 'inline-block';
    document.getElementById('total-marks-val').textContent = currentQ.marks;
  } else {
    totalMarksFill.style.display = 'none';
  }

  const mp = document.getElementById('marks-pill');
  mp.textContent = q.marks + ' marks';
  mp.style.display = 'inline-block';

  // THEMATIC CONTEXT PRESERVATION: If a sub-question is selected, load the Master Scenario AND previous sub-questions for context.
  const sw = document.getElementById('scenario-wrap');
  const sb = document.getElementById('scenario-body');
  const sa = document.getElementById('scenario-arrow');
  
  let fullContext = "";
  if (currentQ.scenario) fullContext += currentQ.scenario + "<br><br>";
  
  // In thematic mode, pulling previous context is super helpful
  if (appMode === 'theme' && currentSub && currentQ.parts) {
      let priorContext = "";
      for (const pk of Object.keys(currentQ.parts)) {
          if (pk === currentSub.partLabel || currentQ.parts[pk] === currentSub) break; // Reached current
          priorContext += `<b>${pk}</b> ` + currentQ.parts[pk].question + "<br><br>";
      }
      if (priorContext) {
          fullContext += `<i>--- Previous Sub-Question Context ---</i><br>` + priorContext;
      }
  }

  if (fullContext) {
    sw.style.display = 'block';
    sb.innerHTML = fullContext;
    sb.classList.add('open');
    sa.innerHTML = '&#9660;';
  } else {
    sw.style.display = 'none';
  }

  let ak, qk, sk;
  if(appMode === 'chrono'){
      ak = document.getElementById('sel-assign').value;
      qk = document.getElementById('sel-question').value;
      sk = document.getElementById('sel-sub').value;
  } else {
      const mopt = document.getElementById('sel-match').selectedOptions[0];
      if (mopt && mopt.dataset.json) {
         const mj = JSON.parse(mopt.dataset.json);
         ak = mj.sitting; qk = mj.qk; sk = mj.pk;
      }
  }

  ab.value = localStorage.getItem(ansKey(ak, qk, sk)) || '';
  
  seconds = 0;
  // Standard SA1 marking speed: 1.8 mins/mark 
  limitSecs = Math.ceil(q.marks * 1.8 * 60);
  updateTimerDisplay();
  document.getElementById('btn-pause').disabled = true;
  document.getElementById('timer-status').textContent = 'Starts when you type';
  document.getElementById('timer-status').className = 'timer-status';
  
  const savedElapsed = localStorage.getItem(elapsedKey(ak, qk, sk));
  if (savedElapsed) {
    seconds = parseInt(savedElapsed, 10);
    updateTimerDisplay();
    document.getElementById('timer-status').textContent = 'Timer paused';
  }

  const nbVal = localStorage.getItem(notesKey(ak, qk, sk));
  if (nbVal) {
    nb.value = nbVal;
  }

  document.getElementById('btn-skip').disabled = false;
  document.getElementById('btn-print-q').disabled = false;
}

function toggleScenario() {
  const b = document.getElementById('scenario-body');
  const a = document.getElementById('scenario-arrow');
  b.classList.toggle('open');
  a.innerHTML = b.classList.contains('open') ? '&#9660;' : '&#9654;';
}

function exitTool() {
  if (confirm("Close the SA1 Exam Revision Tool? Progress is saved locally.")) {
    window.close();
  }
}

// TIMER
function startTimerIfNeeded() { if (!timer && !isPaused) startTimer(); }
function startTimer() {
  if (timer) return;
  startAssignTimer();
  timer = setInterval(() => {
    seconds++;
    updateTimerDisplay();
    // Use proper key saving based on mode
    let ak, qk, sk;
    if(appMode === 'chrono'){
        ak = document.getElementById('sel-assign').value; qk = document.getElementById('sel-question').value; sk = document.getElementById('sel-sub').value;
    } else {
        const mopt = document.getElementById('sel-match').selectedOptions[0];
        if(mopt && mopt.dataset.json){ const mj = JSON.parse(mopt.dataset.json); ak=mj.sitting; qk=mj.qk; sk=mj.pk; }
    }
    saveElapsed(ak, qk, sk, seconds);
  }, 1000);
  document.getElementById('btn-pause').disabled = false;
  document.getElementById('btn-pause').textContent = 'Pause';
  document.getElementById('timer-status').textContent = 'Timer running...';
}
function stopTimer() { clearInterval(timer); timer = null; }
function togglePause() {
  if (isPaused) { isPaused = false; startTimer(); }
  else { isPaused = true; stopTimer(); document.getElementById('btn-pause').textContent = 'Resume'; document.getElementById('timer-status').textContent = 'Timer paused'; }
}
function updateTimerDisplay() {
  const m = Math.floor(seconds / 60), s = seconds % 60;
  document.getElementById('timer-display').textContent = m + ':' + pad(s);
  document.getElementById('countdown-input').value = Math.ceil(limitSecs / 60);
  const fill = document.getElementById('timer-bar-fill');
  const pc = Math.min(100, (seconds / limitSecs) * 100);
  fill.style.width = pc + '%';
  fill.className = 'timer-bar-fill' + (pc > 100 ? ' red' : pc > 80 ? ' amber' : '');
  const td = document.getElementById('timer-display');
  td.className = 'timer-display' + (pc > 100 ? ' red' : pc > 80 ? ' amber' : '');
  if (pc > 100) document.getElementById('timer-status').textContent = 'Time limit exceeded!';
}

function startAssignTimer() {
  if (assignTimer) return;
  assignTimer = setInterval(() => {
    assignSeconds++;
    const h = Math.floor(assignSeconds / 3600), m = Math.floor((assignSeconds % 3600) / 60), s = assignSeconds % 60;
    const stEl = document.getElementById('assign-timer');
    if(stEl) stEl.textContent = '— ' + pad(h) + ':' + pad(m) + ':' + pad(s);
  }, 1000);
}
function resetAssignTimer() { clearInterval(assignTimer); assignTimer = null; assignSeconds = 0; const e = document.getElementById('assign-timer'); if(e) e.textContent = '— 00:00:00'; }

// REVIEW ENGINE
function skipToReveal() {
  manualMode = true; stopTimer();
  document.getElementById('answer-box').readOnly = true;
  document.getElementById('notes-wrap').style.display = 'flex';
  
  const target = currentSub || currentQ;
  if (target && target.synopsis) {
    document.getElementById('synopsis-wrap').style.display = 'flex';
    document.getElementById('synopsis-text').textContent = target.synopsis;
  } else {
    document.getElementById('synopsis-wrap').style.display = 'none';
  }

  document.getElementById('btn-skip').disabled = true;

  document.getElementById('empty-pane').style.display = 'none';
  document.getElementById('points-outer').style.display = 'flex';
  document.getElementById('review-controls').style.display = 'flex';
  document.getElementById('btn-compile').style.display = 'inline-block';
  document.getElementById('btn-next').disabled = false;
  
  currentPoints = [];
  if (target && target.sections) {
      Object.keys(target.sections).forEach(head => {
        currentPoints.push({ type: 'head', text: head });
        target.sections[head].forEach(p => currentPoints.push({ type: 'point', text: p }));
      });
  }
  document.getElementById('ptotal').textContent = currentPoints.filter(p => p.type === 'point').length;
  revealed = 0;
  next();
}

function next() {
  if (revealed >= currentPoints.length) return;
  const p = currentPoints[revealed];
  renderPoint(p, revealed);
  revealed++;
  updateProgress();
  document.getElementById('btn-next').disabled = (revealed >= currentPoints.length);
  document.getElementById('btn-prev').disabled = false;
}

function prev() {
  if (revealed <= 1) return;
  revealed--;
  const outer = document.getElementById('points-outer');
  outer.removeChild(outer.lastChild);
  updateProgress();
  document.getElementById('btn-next').disabled = false;
  document.getElementById('btn-prev').disabled = (revealed <= 1);
}

function updateProgress() {
  const pts = currentPoints.filter(p => p.type === 'point');
  const total = pts.length;
  const revPts = currentPoints.slice(0, revealed).filter(p => p.type === 'point').length;
  document.getElementById('pcnt').textContent = revPts;
  document.getElementById('ptotal').textContent = total;
  document.getElementById('pbar').style.width = total > 0 ? (revPts / total * 100) + '%' : '0%';
}

function renderPoint(p, idx) {
  const list = document.getElementById('points-outer');
  const block = document.createElement('div');
  block.className = 'point-block';
  if (p.type === 'head') {
    block.innerHTML = `<div class="section-label">${p.text}</div>`;
  } else {
    const row = document.createElement('div');
    row.className = 'self-row';
    row.id = 'row_' + idx;
    const cb = document.createElement('input');
    cb.type = 'checkbox'; cb.className = 'self-cb'; cb.id = 'cb_' + idx;
    const lbl = document.createElement('label');
    lbl.className = 'examiner-text'; lbl.style.border = 'none'; lbl.style.background = 'none';
    lbl.textContent = p.text; lbl.htmlFor = 'cb_' + idx;
    const note = document.createElement('input');
    note.type = 'text'; note.className = 'self-note'; note.id = 'note_' + idx;
    note.placeholder = 'Add a quick note...';
    cb.onchange = () => {
      row.classList.toggle('checked', cb.checked);
      row.classList.toggle('unchecked', !cb.checked);
      note.classList.toggle('visible', !cb.checked);
    };
    row.appendChild(cb); row.appendChild(lbl); row.appendChild(note);
    block.appendChild(row);
    note.addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); document.getElementById('answer-box').focus(); } });
  }
  list.appendChild(block);
  block.classList.add('new');
  setTimeout(() => block.classList.remove('new'), 400);
  block.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function compileSelfAssess() {
  let hit = 0, miss = 0;
  currentPoints.forEach((p, i) => {
    if (p.type === 'point') {
      const cb = document.getElementById('cb_' + i);
      if (cb && cb.checked) hit++; else miss++;
    }
  });
  
  document.getElementById('s-hit').textContent = hit;
  document.getElementById('s-miss').textContent = miss;
  document.getElementById('s-extra').textContent = 0;
  document.getElementById('summary').classList.add('show');
  
  document.getElementById('review-controls').style.display = 'flex';
  document.getElementById('btn-prev').disabled = true;
  document.getElementById('btn-next').disabled = true;
  document.getElementById('btn-compile').style.display = 'none';

  document.getElementById('btn-save-sm').style.display = 'inline-block';
  const tb = document.getElementById('time-badge');
  tb.style.display = 'inline-block';
  tb.textContent = 'Time: ' + Math.floor(seconds/60) + ':' + pad(seconds%60) + ' / ' + Math.ceil(limitSecs/60) + ' min';
  tb.className = 'time-badge' + (seconds > limitSecs ? ' red' : '');
}

function resetAll() {
  stopTimer();
  document.getElementById('answer-box').value = '';
  // Avoid clearing localstorage lightly, but user triggers 'New' reset. Let's just reset UI.
  setupQuestion(currentSub || currentQ);
}

// HELPERS
function pad(n) { return n < 10 ? '0' + n : '' + n; }
function ansKey(ak, qk, sk) { return `sa1_e_ans_${ak}_${qk}_${sk}`; }
function elapsedKey(ak, qk, sk) { return `sa1_e_elapsed_${ak}_${qk}_${sk}`; }
function notesKey(ak, qk, sk) { return `sa1_e_notes_${ak}_${qk}_${sk}`; }

function getActiveKeys() {
    let ak=null, qk=null, sk=null;
    if(appMode==='chrono'){
        ak = document.getElementById('sel-assign').value; qk = document.getElementById('sel-question').value; sk = document.getElementById('sel-sub').value;
    } else {
        const mopt = document.getElementById('sel-match').selectedOptions[0];
        if(mopt && mopt.dataset.json){ const mj = JSON.parse(mopt.dataset.json); ak=mj.sitting; qk=mj.qk; sk=mj.pk; }
    }
    return {ak,qk,sk};
}

function saveAnswer() {
  const k = getActiveKeys();
  if(!k.ak) return;
  try { localStorage.setItem(ansKey(k.ak, k.qk, k.sk), document.getElementById('answer-box').value); } catch(e) {}
}
function saveNotes() {
  const k = getActiveKeys();
  if(!k.ak) return;
  try { localStorage.setItem(notesKey(k.ak, k.qk, k.sk), document.getElementById('notes-box').value); } catch(e) {}
}
function saveElapsed(ak, qk, sk, secs) { if(!ak)return; try { localStorage.setItem(elapsedKey(ak, qk, sk), String(secs)); } catch(e) {} }

function handleAnswerTab(e) {
  if (e.key === 'Tab') {
    const nextBtn = document.getElementById('btn-next');
    if (nextBtn && !nextBtn.disabled && document.getElementById('review-controls').style.display !== 'none') {
      e.preventDefault(); next();
      setTimeout(() => { const n = document.getElementById('note_' + (revealed - 1)); if (n && manualMode) n.focus(); }, 50);
    }
  }
}

// Event Listeners (Keyboard)
document.addEventListener('keydown', e => {
  const active = document.activeElement;
  if (active && (active.tagName === 'TEXTAREA' || active.tagName === 'INPUT')) return;
  if (e.code === 'Space' || e.code === 'Enter') { e.preventDefault(); next(); }
  if (e.key === 'ArrowLeft' || e.code === 'Backspace') { e.preventDefault(); prev(); }
  if (manualMode && (e.key === '1' || e.key === '0')) {
    const cb = document.getElementById('cb_' + (revealed - 1));
    if (cb) { cb.checked = (e.key === '1'); cb.dispatchEvent(new Event('change')); }
  }
  if (e.key === 'Tab') {
    const nextBtn = document.getElementById('btn-next');
    if (nextBtn && !nextBtn.disabled && document.getElementById('review-controls').style.display !== 'none') {
      e.preventDefault(); next();
      setTimeout(() => { const n = document.getElementById('note_' + (revealed-1)); if(n) n.focus(); }, 50);
    }
  }
});
</script>
"""

s_js = text.find("<script>")
e_js = text.find("</script>") + 9

if s_js != -1 and e_js != -1:
    text = text[:s_js] + new_js + text[e_js:]

# Save heavily modified content
with codecs.open(path, 'w', 'utf-8') as f:
    f.write(text)

print('Successfully injected Thematic UI and script logic.')

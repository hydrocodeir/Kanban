/*
  Jalali Datepicker (Robust)
  - نمایش تقویم شمسی با شروع هفته از شنبه
  - خروجی برای بک‌اند: میلادی ISO (YYYY-MM-DD) در input مخفی
  - نمایش: YYYY/MM/DD (شمسی) با اعداد فارسی
  - تبدیل‌ها بر اساس الگوریتم معتبر jalaali-js (g2d/d2g/j2d/d2j)
*/

(function(){
  const DOW = ["ش","ی","د","س","چ","پ","ج"]; // Sat..Fri
  const MONTHS = ["فروردین","اردیبهشت","خرداد","تیر","مرداد","شهریور","مهر","آبان","آذر","دی","بهمن","اسفند"];

  function pad2(n){ return String(n).padStart(2,"0"); }
  function toFaDigits(s){ return String(s).replace(/\d/g, d => "۰۱۲۳۴۵۶۷۸۹"[Number(d)]); }
  function div(a,b){ return ~~(a/b); }
  function mod(a,b){ return a - ~~(a/b)*b; }

  // ---------- jalaali-js core ----------
  function jalCal(jy){
    const breaks = [-61, 9, 38, 199, 426, 686, 756, 818, 1111, 1181, 1210,
      1635, 2060, 2097, 2192, 2262, 2324, 2394, 2456, 3178];
    const bl = breaks.length;
    let gy = jy + 621;
    let leapJ = -14;
    let jp = breaks[0];
    let jm, jump, leap, n, i;

    if (jy < jp || jy >= breaks[bl-1]) throw new Error("Invalid Jalali year " + jy);

    for (i = 1; i < bl; i++){
      jm = breaks[i];
      jump = jm - jp;
      if (jy < jm) break;
      leapJ = leapJ + div(jump,33)*8 + div(mod(jump,33),4);
      jp = jm;
    }
    n = jy - jp;
    leapJ = leapJ + div(n,33)*8 + div(mod(n,33)+3,4);
    if (mod(jump,33) === 4 && jump - n === 4) leapJ += 1;

    const leapG = div(gy,4) - div((div(gy,100)+1)*3,4) - 150;
    const march = 20 + leapJ - leapG;

    if (jump - n < 6) n = n - jump + div(jump+4,33)*33;
    leap = mod(mod(n+1,33)-1,4);
    if (leap === -1) leap = 4;

    return { leap, gy, march };
  }

  function isLeapJalaaliYear(jy){ return jalCal(jy).leap === 0; }
  function jalaaliMonthLength(jy, jm){
    if (jm <= 6) return 31;
    if (jm <= 11) return 30;
    return isLeapJalaaliYear(jy) ? 30 : 29;
  }

  function g2d(gy, gm, gd){
    let d = div((gy + div(gm - 8, 6) + 100100) * 1461, 4)
          + div(153 * mod(gm + 9, 12) + 2, 5)
          + gd - 34840408;
    d = d - div(div(gy + 100100 + div(gm - 8, 6), 100) * 3, 4) + 752;
    return d;
  }

  function d2g(jdn){
    let j = 4 * jdn + 139361631;
    j = j + div(div(4 * jdn + 183187720, 146097) * 3, 4) * 4 - 3908;
    const i = div(mod(j, 1461), 4) * 5 + 308;
    const gd = div(mod(i, 153), 5) + 1;
    const gm = mod(div(i, 153), 12) + 1;
    const gy = div(j, 1461) - 100100 + div(8 - gm, 6);
    return { gy, gm, gd };
  }

  function j2d(jy, jm, jd){
    const r = jalCal(jy);
    return g2d(r.gy, 3, r.march) + (jm - 1) * 31 - div(jm, 7) * (jm - 7) + (jd - 1);
  }

  function d2j(jdn){
    const g = d2g(jdn);
    let jy = g.gy - 621;
    const r = jalCal(jy);
    const jdn1f = g2d(g.gy, 3, r.march);
    let k = jdn - jdn1f;
    let jm, jd;

    if (k >= 0){
      if (k <= 185){
        jm = 1 + div(k, 31);
        jd = mod(k, 31) + 1;
        return { jy, jm, jd };
      } else {
        k -= 186;
        jm = 7 + div(k, 30);
        jd = mod(k, 30) + 1;
        return { jy, jm, jd };
      }
    } else {
      jy -= 1;
      k += 179;
      if (r.leap === 1) k += 1;
      jm = 7 + div(k, 30);
      jd = mod(k, 30) + 1;
      return { jy, jm, jd };
    }
  }

  function toJalaali(gy, gm, gd){ return d2j(g2d(gy, gm, gd)); }
  function toGregorian(jy, jm, jd){ return d2g(j2d(jy, jm, jd)); }

  // ---------- helpers ----------
  function parseISODate(s){
    if (!s) return null;
    const m = String(s).trim().match(/^(\d{4})-(\d{2})-(\d{2})$/);
    if (!m) return null;
    return { y:+m[1], m:+m[2], d:+m[3] };
  }
  function formatISO(gy, gm, gd){ return `${gy}-${pad2(gm)}-${pad2(gd)}`; }

  // ---------- Datepicker UI ----------
  let pop = null;
  let activeInput = null;
  let activeHidden = null;
  let selectedJ = null;
  let viewJ = null;

  function closePop(){
    if(pop){
      pop.remove();
      pop = null;
    }
    activeInput = null;
    activeHidden = null;
    selectedJ = null;
    viewJ = null;
  }

  function buildPop(){
    pop = document.createElement("div");
    pop.className = "jdp-pop";
    pop.innerHTML = `
      <div class="jdp-head">
        <button type="button" class="jdp-btn" data-act="prev" aria-label="ماه قبل">‹</button>
        <div class="title" id="jdpTitle"></div>
        <button type="button" class="jdp-btn" data-act="next" aria-label="ماه بعد">›</button>
      </div>
      <div class="jdp-grid" id="jdpGrid"></div>
      <div class="jdp-foot">
        <span class="jdp-link" data-act="today">امروز</span>
        <span class="jdp-link" data-act="clear">پاک کردن</span>
      </div>
    `;
    document.body.appendChild(pop);

    pop.addEventListener("click", (e)=>{
      const t = e.target;
      if(!t) return;
      const act = t.getAttribute("data-act");
      const day = t.getAttribute("data-day");
      if(act === "prev") shiftMonth(-1);
      else if(act === "next") shiftMonth(1);
      else if(act === "today") pickToday();
      else if(act === "clear") clearDate();
      else if(day) selectDay(parseInt(day,10));
    });
  }

  function positionPop(input){
    const r = input.getBoundingClientRect();
    const top = r.bottom + 8 + window.scrollY;
    const left = Math.min(window.innerWidth - 300, Math.max(8, r.right - 290 + window.scrollX));
    pop.style.top = `${top}px`;
    pop.style.left = `${left}px`;
  }

  function render(){
    if(!pop || !viewJ) return;
    pop.querySelector("#jdpTitle").textContent = `${MONTHS[viewJ.jm-1]} ${toFaDigits(viewJ.jy)}`;

    const grid = pop.querySelector("#jdpGrid");
    grid.innerHTML = "";

    // weekday header
    for(const d of DOW){
      const el = document.createElement("div");
      el.className = "jdp-dow";
      el.textContent = d;
      grid.appendChild(el);
    }

    // first day-of-week of jalali month
    const g1 = toGregorian(viewJ.jy, viewJ.jm, 1);
    const dt = new Date(g1.gy, g1.gm-1, g1.gd);
    // getDay: 0 Sun..6 Sat, we want offset for starting at Sat
    const dow = dt.getDay();
    const offset = (dow + 1) % 7;

    for(let i=0; i<offset; i++){
      const b = document.createElement("div");
      b.className = "jdp-day is-disabled";
      grid.appendChild(b);
    }

    const mlen = jalaaliMonthLength(viewJ.jy, viewJ.jm);
    const now = new Date();
    const todayJ = toJalaali(now.getFullYear(), now.getMonth()+1, now.getDate());

    for(let d=1; d<=mlen; d++){
      const cell = document.createElement("div");
      cell.className = "jdp-day";
      cell.setAttribute("data-day", String(d));
      cell.textContent = toFaDigits(d);

      if(todayJ.jy===viewJ.jy && todayJ.jm===viewJ.jm && todayJ.jd===d){
        cell.classList.add("is-today");
      }
      if(selectedJ && selectedJ.jy===viewJ.jy && selectedJ.jm===viewJ.jm && selectedJ.jd===d){
        cell.classList.add("is-selected");
      }
      grid.appendChild(cell);
    }
  }

  function shiftMonth(delta){
    if(!viewJ) return;
    let jy=viewJ.jy, jm=viewJ.jm + delta;
    if(jm === 0){ jm = 12; jy -= 1; }
    if(jm === 13){ jm = 1; jy += 1; }
    viewJ = {jy, jm};
    render();
  }

  function selectDay(d){
    if(!viewJ || !activeInput || !activeHidden) return;
    selectedJ = {jy:viewJ.jy, jm:viewJ.jm, jd:d};

    const jTxt = `${toFaDigits(selectedJ.jy)}/${toFaDigits(pad2(selectedJ.jm))}/${toFaDigits(pad2(selectedJ.jd))}`;
    activeInput.value = jTxt;

    const g = toGregorian(selectedJ.jy, selectedJ.jm, selectedJ.jd);
    activeHidden.value = formatISO(g.gy, g.gm, g.gd);

    render();
    setTimeout(closePop, 120);
  }

  function pickToday(){
    const now = new Date();
    const j = toJalaali(now.getFullYear(), now.getMonth()+1, now.getDate());
    viewJ = {jy:j.jy, jm:j.jm};
    selectedJ = {jy:j.jy, jm:j.jm, jd:j.jd};
    // ensure active inputs exist
    selectDay(j.jd);
  }

  function clearDate(){
    if(activeInput) activeInput.value = "";
    if(activeHidden) activeHidden.value = "";
    closePop();
  }

  function openFor(input){
    const targetId = input.getAttribute("data-target");
    if(!targetId) return;
    const hidden = document.getElementById(targetId);
    if(!hidden) return;

    closePop();
    buildPop();

    activeInput = input;
    activeHidden = hidden;

    const parsed = parseISODate(hidden.value);
    if(parsed){
      const j = toJalaali(parsed.y, parsed.m, parsed.d);
      viewJ = {jy:j.jy, jm:j.jm};
      selectedJ = {jy:j.jy, jm:j.jm, jd:j.jd};
      input.value = `${toFaDigits(j.jy)}/${toFaDigits(pad2(j.jm))}/${toFaDigits(pad2(j.jd))}`;
    } else {
      const now = new Date();
      const j = toJalaali(now.getFullYear(), now.getMonth()+1, now.getDate());
      viewJ = {jy:j.jy, jm:j.jm};
      selectedJ = null;
    }

    positionPop(input);
    render();
  }

  function bindDateInputs(root){
    const scope = root || document;
    scope.querySelectorAll(".jalali-date").forEach((inp)=>{
      if(inp.dataset.jdpBound === "1") return;
      inp.dataset.jdpBound = "1";
      inp.addEventListener("focus", ()=>openFor(inp));
      inp.addEventListener("click", ()=>openFor(inp));
      inp.addEventListener("keydown", (e)=>{ if(e.key === "Escape") closePop(); });
    });
  }

  function renderDueDates(root){
    const scope = root || document;
    scope.querySelectorAll(".due-date[data-greg]").forEach((el)=>{
      const greg = el.getAttribute("data-greg");
      const parsed = parseISODate(greg);
      if(!parsed) return;
      const j = toJalaali(parsed.y, parsed.m, parsed.d);
      const txt = `${toFaDigits(j.jy)}/${toFaDigits(pad2(j.jm))}/${toFaDigits(pad2(j.jd))}`;
      const span = el.querySelector(".due-date-text");
      if(span) span.textContent = txt;
    });
  }

  // close on outside click / scroll / resize
  document.addEventListener("mousedown", (e)=>{
    if(!pop) return;
    if(pop.contains(e.target)) return;
    if(activeInput && activeInput.contains(e.target)) return;
    closePop();
  });
  window.addEventListener("scroll", ()=>{ if(pop) closePop(); }, true);
  window.addEventListener("resize", ()=>{ if(pop) closePop(); });

  
  function toFaDigitsLocal(s){ return String(s).replace(/\d/g, d => "۰۱۲۳۴۵۶۷۸۹"[Number(d)]); }

  function renderRemainingBadges(root){
    const scope = root || document;
    const badges = scope.querySelectorAll(".due-remaining[data-greg]");
    const now = new Date();
    // normalize to midnight local time
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    badges.forEach((b)=>{
      const iso = b.getAttribute("data-greg");
      if(!iso) return;
      const m = String(iso).match(/^(\d{4})-(\d{2})-(\d{2})$/);
      if(!m) { b.textContent = ""; return; }
      const y=+m[1], mo=+m[2]-1, d=+m[3];
      const due = new Date(y, mo, d);
      const diffMs = due.getTime() - today.getTime();
      const diffDays = Math.round(diffMs / 86400000);

      b.classList.remove("text-bg-danger","text-bg-warning","text-bg-success","text-bg-light");
      if(diffDays > 0){
        b.classList.add(diffDays <= 2 ? "text-bg-warning" : "text-bg-success");
        b.textContent = toFaDigitsLocal(`${diffDays} روز مانده`);
      } else if(diffDays === 0){
        b.classList.add("text-bg-warning");
        b.textContent = "امروز";
      } else {
        b.classList.add("text-bg-danger");
        b.textContent = toFaDigitsLocal(`${Math.abs(diffDays)} روز تأخیر`);
      }
    });
  }

  // Public hook
  window.KanbanUI = window.KanbanUI || {};
  window.KanbanUI.updateCounts = function(){
    try{
      document.querySelectorAll('.kanban-col').forEach((col)=>{
        const colId = col.getAttribute('data-col-id') || col.getAttribute('data-col-id');
        const list = col.querySelector('.task-list');
        const count = list ? list.querySelectorAll('.task-card').length : 0;
        const badge = col.querySelector('.col-count');
        if(badge) badge.textContent = String(count);
      });
    }catch(e){}
  };

  window.KanbanUI.closeCollapse = function(id){
    try{
      const el = document.getElementById(id);
      if(!el || !window.bootstrap) return;
      const inst = bootstrap.Collapse.getOrCreateInstance(el, {toggle:false});
      inst.hide();
    }catch(e){}
  };
  window.KanbanUI.init = function(root){
    bindDateInputs(root || document);
    renderDueDates(root || document);
    renderRemainingBadges(root || document);
  };
})();


const API="/api";
let token=localStorage.getItem("k360_token"), me=null, currentPage="dashboard", selectedTrainee=null;

const navItems={
 admin:[["dashboard","Dashboard"],["trainees","Trainees"],["employment","Employment"],["followups","Follow-ups"],["skills","Skill Gaps"],["providers","Providers"],["courses","Courses"],["districts","Districts"],["analytics","Analytics"],["impact","Impact"],["actions","Action Center"],["alerts","Alerts"],["reports","Reports"],["privacy","Privacy"]],
 provider:[["dashboard","Dashboard"],["trainees","Trainees"],["employment","Placements"],["followups","Follow-ups"],["courses","Course Outcomes"],["skills","Skill Gaps"],["reports","Reports"]],
 officer:[["trainees","My Trainees"],["followups","Follow-ups"],["employment","Employment Updates"],["privacy","Consent"],["alerts","Tasks"]],
 trainee:[["trainees","My Journey"],["followups","Follow-ups"],["employment","Employment"],["skills","Skills"],["privacy","Consent"]]
};

async function api(path,opts={}){
  opts.headers={...(opts.headers||{}),Authorization:`Bearer ${token}`};
  if(opts.body && typeof opts.body!=="string"){opts.headers["Content-Type"]="application/json";opts.body=JSON.stringify(opts.body)}
  const r=await fetch(API+path,opts); if(!r.ok){let e={detail:"Request failed"};try{e=await r.json()}catch{};throw new Error(e.detail||"Request failed")} return r.json();
}
function toast(msg){const x=document.getElementById("toast");x.textContent=msg;x.classList.add("show");setTimeout(()=>x.classList.remove("show"),2400)}
function closeModal(){document.getElementById("modal").classList.add("hidden")}
function openModal(html){document.getElementById("modalContent").innerHTML=html;document.getElementById("modal").classList.remove("hidden")}
function money(n){return n?"₹"+Number(n).toLocaleString("en-IN"):"—"}
function esc(s){return String(s??"").replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[m]))}
function status(s){let c=["EMPLOYED","Verified","Completed"].includes(s)?"success":["Pending","Partially Verified","SELF_EMPLOYED","APPRENTICE"].includes(s)?"warn":["UNREACHABLE","Conflict Detected"].includes(s)?"danger":"info";return `<span class="status ${c}">${esc(s)}</span>`}

async function boot(){
  if(!token){showLogin();return}
  try{me=await api("/me");showApp()}catch{localStorage.removeItem("k360_token");token=null;showLogin()}
}
function showLogin(){document.getElementById("loginView").classList.remove("hidden");document.getElementById("appView").classList.add("hidden")}
function showApp(){
  document.getElementById("loginView").classList.add("hidden");document.getElementById("appView").classList.remove("hidden");
  renderNav(); navigate("dashboard");
}
function renderNav(){
  const n=document.getElementById("nav");n.innerHTML=(navItems[me.role]||navItems.admin).map(([id,label])=>`<button data-page="${id}" class="${id===currentPage?"active":""}">${label}</button>`).join("");
  n.querySelectorAll("button").forEach(b=>b.onclick=()=>navigate(b.dataset.page));
  const sb=document.querySelector(".sidebar");if(sb){if(me?.role==="admin")sb.classList.add("sidebar-admin");else sb.classList.remove("sidebar-admin")}
}
async function navigate(page){
  currentPage=page;renderNav();
  const c=document.getElementById("content");c.innerHTML=`<div class="empty">Loading intelligence…</div>`;
  try{
    if(page==="dashboard")return dashboard();
    if(page==="trainees")return traineeList();
    if(page==="employment")return employment();
    if(page==="followups")return followups();
    if(page==="skills")return skills();
    if(page==="providers")return providers();
    if(page==="districts")return districts();
    if(page==="analytics")return analytics();
    if(page==="impact")return impact();
    if(page==="actions")return actions();
    if(page==="alerts")return alerts();
    if(page==="reports")return reports();
    if(page==="privacy")return privacy();
    if(page==="courses")return courses();
    return dashboard();
  }catch(e){c.innerHTML=`<div class="card"><b>Unable to load this view</b><p class="muted">${esc(e.message)}</p></div>`}
}

async function dashboard(district=""){
 const d=await api("/dashboard"+(district?"?district="+encodeURIComponent(district):"")); const a=await api("/alerts"); const r=await api("/recommendations"); const ret=await api("/analytics/retention"); const w=await api("/analytics/wages"); const dists=await api("/districts");
 document.getElementById("content").innerHTML=`
 <div class="page-head"><div><h1>Programme Command Dashboard</h1><p>Maharashtra Skill & Employment Intelligence · <b>DEMO / SYNTHETIC DATA</b></p></div><div class="head-actions"><select class="select" id="districtFilter"><option value="">All districts</option>${dists.map(x=>`<option ${x.district===district?"selected":""}>${esc(x.district)}</option>`).join("")}</select><button class="primary" onclick="downloadReport()">Export Report</button></div></div>
 <div class="metric-grid">
 ${metric("Total trainees",d.total.toLocaleString(),"↗ 8.4% vs previous cohort","trainees")}
 ${metric("Certified trainees",d.certified.toLocaleString(),"Completion pipeline","trainees")}
 ${metric("Placement rate",d.placement_rate+"%","Outcome conversion","analytics")}
 ${metric("Employment rate",d.employment_rate+"%","Current employed","employment")}
 ${metric("6M retention",d.retention_6+"%","Longitudinal signal","analytics")}
 ${metric("Average wage",money(d.avg_wage),"Current monthly","analytics")}
 ${metric("Wage growth","+"+d.wage_growth+"%","M0 → M12","analytics")}
 ${metric("Verified employment",d.verified.toLocaleString(),"Evidence-backed","employment")}
 </div>
 <div class="grid-2">
  <div class="card"><div class="card-head"><h3>Outcome journey</h3><span>System-wide cohort view</span></div><div class="timeline">${["Enrolled","Training","Assessed","Certified","Placement","Employed","3M follow-up","6M follow-up","12M follow-up"].map((x,i)=>`<div class="event"><div class="dot"></div><b>${x}</b><span>${i<5?"Completed":"Longitudinal"}</span></div>`).join("")}</div></div>
  <div class="card"><div class="card-head"><h3>High-priority alert</h3><span>Evidence-linked</span></div><div class="insight"><div class="tag">RETENTION · HIGH</div><b>6-month retention falling in Advanced CNC cohort.</b><p>Open the affected cohort, inspect Provider B and trace the evidence to trainee outcomes.</p><button class="primary" style="margin-top:12px" onclick="navigate('analytics')">Open cohort analysis →</button></div></div>
 </div>
 <div class="grid-2">
  <div class="card"><div class="card-head"><h3>Retention curve</h3><span>Click analytics for cohort drill-down</span></div><div class="chart">${ret.map(x=>`<div class="bar" style="height:${x.rate*1.85}px"><strong>${x.rate}%</strong><small>M${x.month}</small></div>`).join("")}</div></div>
  <div class="card"><div class="card-head"><h3>Wage progression</h3><span>Average monthly salary</span></div><div class="chart">${w.map(x=>`<div class="bar" style="height:${Math.max(25,x.avg/160)}px"><strong>${money(x.avg)}</strong><small>${x.month}</small></div>`).join("")}</div></div>
 </div>
 <div class="grid-2">
  <div class="card"><div class="card-head"><h3>Actionable insights</h3><span>${r.length} recommendations</span></div>${r.slice(0,3).map(insightCard).join("")}</div>
  <div class="card"><div class="card-head"><h3>Notifications</h3><button class="link-btn" onclick="navigate('alerts')">View all</button></div>${a.slice(0,4).map(x=>`<div class="action"><div><span class="priority ${x.severity==='HIGH'?'high':x.severity==='MEDIUM'?'medium':'low'}">${x.severity}</span><h4>${esc(x.message)}</h4></div><button class="link-btn" onclick="navigate('${x.target.split('/')[0]}')">Open</button></div>`).join("")}</div>
 </div>`;
 const df=document.getElementById("districtFilter");if(df){df.onchange=e=>dashboard(e.target.value)}
}
function metric(label,value,delta,target){return `<div class="metric" onclick="navigate('${target}')"><div class="label">${label}</div><div class="value">${value}</div><div class="delta">${delta}</div></div>`}
function insightCard(r){return `<div class="insight"><div class="tag">${r.priority} PRIORITY</div><b>${esc(r.title)}</b><p>${esc(r.reason)}</p></div>`}

async function traineeList(){
 const rows=await api("/trainees?limit=80");
 document.getElementById("content").innerHTML=`<div class="page-head"><div><h1>Trainee Outcomes</h1><p>Consent-based records and longitudinal outcome evidence.</p></div><button class="primary" onclick="openTraineeForm()">+ Add outcome record</button></div>
 <div class="card"><div class="filterbar"><input class="filter-input" style="max-width:320px" id="tSearch" placeholder="Search name or trainee ID…"><button class="primary" onclick="searchTrainees()">Search</button><button class="select" onclick="navigate('trainees')">Clear</button></div>
 <div class="table-wrap"><table class="data-table"><thead><tr><th>Trainee</th><th>Course</th><th>District</th><th>Provider</th><th>Outcome</th><th>Verification</th><th>Consent</th></tr></thead><tbody id="traineeRows">${rows.map(t=>`<tr><td><button class="link-btn" onclick="openTrainee(${t.id})">${esc(t.name)}</button><div class="muted">${t.trainee_id}</div></td><td>${esc(t.course)}</td><td>${esc(t.district)}</td><td>${esc(t.provider)}</td><td>${status(t.status)}</td><td>${status(t.verification)}</td><td>${t.consent?'✓ Active':'Revoked'}</td></tr>`).join("")}</tbody></table></div></div>`;
}
async function searchTrainees(){const q=document.getElementById("tSearch").value;const rows=await api("/trainees?limit=80&search="+encodeURIComponent(q));document.getElementById("traineeRows").innerHTML=rows.map(t=>`<tr><td><button class="link-btn" onclick="openTrainee(${t.id})">${esc(t.name)}</button><div class="muted">${t.trainee_id}</div></td><td>${esc(t.course)}</td><td>${esc(t.district)}</td><td>${esc(t.provider)}</td><td>${status(t.status)}</td><td>${status(t.verification)}</td><td>${t.consent?'✓ Active':'Revoked'}</td></tr>`).join("")}

async function openTrainee(id){
 selectedTrainee=id;const t=await api("/trainees/"+id);
 openModal(`<div class="page-head"><div><div class="eyebrow" style="margin:0;color:var(--teal)">${t.trainee_id}</div><h1>${esc(t.name)}</h1><p>${esc(t.course)} · ${esc(t.provider)} · ${esc(t.district)}</p></div><div>${status(t.employment_status)}</div></div>
 <div class="profile-grid">
 ${kv("Age / Gender",t.age+" · "+t.gender)}${kv("Education",t.education)}${kv("Location",t.location)}${kv("Attendance",t.attendance+"%")}${kv("Assessment",t.assessment+"%")}${kv("Certification",t.certified?"Certified":"Not certified")}
 ${kv("Employer",t.employer||"—")}${kv("Job role",t.job_role)}${kv("Salary",money(t.salary))}${kv("Source",t.source)}${kv("Verification",t.verification)}${kv("Confidence",t.confidence+"%")}
 </div>
 <h3 style="margin-top:25px">Longitudinal outcome timeline</h3>
 <div class="timeline">${timelineEvent("Enrolled",new Date(t.enrolled_at).toLocaleDateString())}${timelineEvent("Training completed",new Date(t.completed_at).toLocaleDateString())}${timelineEvent("Certified",t.certified?"Confirmed":"Pending")}${timelineEvent("Placement",t.employment_status)}${timelineEvent("3-month follow-up",t.retention_3?"Retention confirmed":"Review")}${timelineEvent("6-month follow-up",t.retention_6?"Retention confirmed":"Review")}${timelineEvent("12-month follow-up",t.retention_12?"Retention confirmed":"Review")}</div>
 <h3 style="margin-top:25px">Wage progression</h3><div class="chart">${t.salary_history.map(x=>`<div class="bar" style="height:${Math.max(30,x.salary/150)}px"><strong>${money(x.salary)}</strong><small>${x.month}</small></div>`).join("")}</div>
 <h3>Outcome signals</h3>${signal("Trainee declaration",true)}${signal("Employer confirmation",t.verification==="Verified")}${signal("Salary provided",!!t.salary)}${signal("Joining date available",!!t.joining_date)}
 <div class="card" style="margin-top:15px;background:#f7fbfb"><b>Employment confidence: ${t.confidence}%</b><div class="progress" style="margin-top:8px"><i style="width:${t.confidence}%"></i></div><p class="footer-note">Explainable confidence combines declared outcome, verification state, salary and joining-date evidence.</p></div>
 <div class="head-actions" style="margin-top:18px"><button class="primary" onclick="startFollowup(${t.id})">Start Follow-up</button><button class="select" onclick="verifyTrainee(${t.id})">Verify employment</button><button class="select" onclick="toggleConsent(${t.id},${t.consent})">${t.consent?"Revoke consent":"Restore consent"}</button></div>`);
}
function kv(k,v){return `<div class="kv"><label>${k}</label><b>${esc(v)}</b></div>`}
function timelineEvent(a,b){return `<div class="event"><div class="dot"></div><b>${a}</b><span>${b}</span></div>`}
function signal(a,b){return `<div class="signal"><div class="check">${b?"✓":"!"}</div><span>${a}</span></div>`}

async function startFollowup(id){
 const t=await api("/trainees/"+id); const f=t.followups.find(x=>x.status==="Pending")||t.followups[0];
 if(!f){toast("No follow-up record available");return}
 openModal(`<h2>6-Month Employment Outcome Survey</h2><p class="muted">${esc(t.name)} · ${esc(f.kind)} · ${esc(f.channel)} <span class="status info">SIMULATED CONNECTOR</span></p>
 <label>Are you currently employed?<select id="fuStatus" class="filter-input"><option>Completed</option><option>Unreachable</option><option>Escalated</option></select></label>
 <label>Monthly salary<input id="fuSalary" class="filter-input" type="number" value="${t.salary||18000}"></label>
 <label>Is the current job related to your training?<select id="fuRelevant" class="filter-input"><option value="true">Yes</option><option value="false">No</option></select></label>
 <label>Officer notes<textarea id="fuNotes" class="filter-input" rows="4">Current outcome reviewed during assisted follow-up.</textarea></label>
 <div class="head-actions" style="margin-top:18px"><button class="select" onclick="saveDraft()">Save Draft</button><button class="primary" onclick="completeFollowup(${f.id})">Complete Follow-up</button></div>`);
}
async function completeFollowup(fid){try{await api("/followups/"+fid+"/complete",{method:"POST",body:{status:document.getElementById("fuStatus").value,notes:document.getElementById("fuNotes").value,salary:Number(document.getElementById("fuSalary").value),relevant:document.getElementById("fuRelevant").value==="true"}});closeModal();toast("Follow-up completed and outcome updated");if(selectedTrainee)openTrainee(selectedTrainee)}catch(e){toast(e.message)}}
function saveDraft(){localStorage.setItem("k360_followup_draft",JSON.stringify({saved:new Date().toISOString()}));toast("Draft saved locally · Pending Sync")}

async function toggleConsent(id,current){try{await api("/trainees/"+id+"/consent",{method:"POST",body:{employment_tracking:!current,followup:!current,analytics:!current}});toast(current?"Consent revoked. Future follow-ups disabled.":"Consent restored.");openTrainee(id)}catch(e){toast(e.message)}}
async function verifyTrainee(id){try{await api("/employment/"+id+"/verify",{method:"POST",body:{status:"Verified"}});toast("Employment record verified");openTrainee(id)}catch(e){toast(e.message)}}

async function employment(){
 const rows=await api("/employment");
 document.getElementById("content").innerHTML=`<div class="page-head"><div><h1>Employment Verification Center</h1><p>Multiple signals, explicit sources and explainable confidence.</p></div><button class="select" onclick="navigate('employment')">Refresh</button></div>
 <div class="card"><div class="table-wrap"><table class="data-table"><thead><tr><th>Trainee</th><th>Employer</th><th>Role</th><th>Salary</th><th>Source</th><th>Status</th><th>Confidence</th><th></th></tr></thead><tbody>${rows.map(x=>`<tr><td><button class="link-btn" onclick="openTrainee(${x.id})">${esc(x.trainee)}</button></td><td>${esc(x.employer)}</td><td>${esc(x.role)}</td><td>${money(x.salary)}</td><td>${esc(x.source)}</td><td>${status(x.verification)}</td><td>${x.confidence}%</td><td><button class="link-btn" onclick="verifyTrainee(${x.id})">Verify</button></td></tr>`).join("")}</tbody></table></div></div>
 <div class="grid-3"><div class="card"><h3>Verified</h3><div class="value" style="font-size:30px">Evidence-backed</div><p class="muted">Employer + trainee signals.</p></div><div class="card"><h3>Pending</h3><div class="value" style="font-size:30px">Needs action</div><p class="muted">Request employer confirmation.</p></div><div class="card"><h3>Integrity</h3><div class="value" style="font-size:30px">Source visible</div><p class="muted">No invisible inference.</p></div></div>`;
}

async function followups(){
 const rows=await api("/followups");const c=await api("/campaigns");
 document.getElementById("content").innerHTML=`<div class="page-head"><div><h1>Follow-Up Center</h1><p>Automated + assisted longitudinal outcome collection.</p></div><button class="primary" onclick="launchCampaign()">Launch Campaign</button></div>
 <div class="grid-3">${mini("Due today",rows.filter(x=>x.status==="Pending").length,"Needs action")}${mini("Completed",rows.filter(x=>x.status==="Completed").length,"Outcome records")}${mini("Unreachable",rows.filter(x=>x.status==="Unreachable").length,"Escalate")}</div>
 <div class="grid-2"><div class="card"><div class="card-head"><h3>Pending follow-ups</h3><span>Field officer queue</span></div><div class="table-wrap"><table class="data-table"><thead><tr><th>Trainee</th><th>Milestone</th><th>Due</th><th>Channel</th><th></th></tr></thead><tbody>${rows.filter(x=>x.status!=="Completed").slice(0,20).map(x=>`<tr><td><button class="link-btn" onclick="openTrainee(${x.trainee_id})">${esc(x.trainee)}</button></td><td>${x.kind}</td><td>${x.due}</td><td>${x.channel}</td><td><button class="link-btn" onclick="startFollowup(${x.trainee_id})">Start</button></td></tr>`).join("")}</tbody></table></div></div>
 <div class="card"><div class="card-head"><h3>6-Month Employment Outcome Survey</h3><span class="status info">SIMULATED</span></div><p class="muted">WhatsApp · SMS · IVR · Phone Call · Field Officer</p><div class="progress"><i style="width:${c.progress/c.target*100}%"></i></div><div class="grid-3">${mini("Target",c.target.toLocaleString(),"trainees")}${mini("Responses",c.responses.toLocaleString(),"captured")}${mini("Pending",c.pending.toLocaleString(),"remaining")}</div><div class="head-actions" style="margin-top:15px"><button class="select" onclick="launchCampaign()">Launch / Continue</button><button class="select" onclick="toast('Responses panel opened')">View Responses</button><button class="select" onclick="toast('Unreachable queue escalated')">Escalate</button></div></div></div>`;
}
function mini(a,b,c){return `<div class="metric" style="cursor:default"><div class="label">${a}</div><div class="value">${b}</div><div class="delta">${c}</div></div>`}
async function launchCampaign(){const c=await api("/campaigns",{method:"POST"});toast("Campaign launched. Progress updated.");followups()}

async function skills(){
 const rows=await api("/skills");
 document.getElementById("content").innerHTML=`<div class="page-head"><div><h1>Skill Gap Intelligence</h1><p>Current workforce skills vs training proficiency vs employment requirements.</p></div><span class="status info">SYNTHETIC DEMO</span></div>
 <div class="grid-2"><div class="card"><div class="card-head"><h3>Priority skill gaps</h3><span>Gap = requirement − certified proficiency</span></div>${rows.map(x=>`<div style="margin:17px 0"><div style="display:flex;justify-content:space-between;font-size:12px"><b>${esc(x.skill)}</b><span class="${x.gap>25?'high':x.gap>12?'medium':'low'}">${x.gap>25?'HIGH':x.gap>12?'MEDIUM':'LOW'} · ${x.gap} pts</span></div><div class="progress" style="margin-top:7px"><i style="width:${Math.min(100,x.required)}"></i></div><div class="muted" style="font-size:10px;margin-top:4px">Demand ${x.demand}% · Certified ${x.certified}% · Required ${x.required}%</div></div>`).join("")}</div>
 <div class="card"><h3>Evidence → action</h3><div class="insight"><div class="tag">HIGH GAP</div><b>PLC Programming</b><p>Employment requirements exceed certified proficiency. Recommended action: add advanced PLC programming to the next training cycle.</p><button class="primary" onclick="navigate('actions')" style="margin-top:10px">Open Action Center</button></div><div class="insight"><div class="tag">HIGH GAP</div><b>CNC Programming</b><p>Strong placement exists, but skill relevance indicates curriculum depth is limiting progression.</p></div></div></div>`;
}
async function providers(){
 const rows=await api("/providers");
 document.getElementById("content").innerHTML=`<div class="page-head"><div><h1>Provider Performance</h1><p>Compare outcome conversion, retention, wages and verification.</p></div></div><div class="card"><div class="table-wrap"><table class="data-table"><thead><tr><th>Provider</th><th>Trainees</th><th>Completion</th><th>Placement</th><th>Employment</th><th>6M Retention</th><th>Avg Wage</th><th>Verification</th><th>Impact</th></tr></thead><tbody>${rows.map(x=>`<tr><td><b>${esc(x.provider)}</b></td><td>${x.trainees}</td><td>${x.completion}%</td><td>${x.placement}%</td><td>${x.employment}%</td><td>${x.retention}%</td><td>${money(x.wage)}</td><td>${x.verification}%</td><td><span class="status ${x.impact>75?'success':x.impact>60?'warn':'danger'}">${x.impact}</span></td></tr>`).join("")}</tbody></table></div><p class="footer-note">Impact score is calculated from visible placement, retention, verification and wage components.</p></div>`;
}
async function districts(){
 const rows=await api("/districts");
 document.getElementById("content").innerHTML=`<div class="page-head"><div><h1>District Intelligence</h1><p>Prototype district heatmap/table · synthetic Maharashtra demonstration dataset.</p></div></div><div class="card"><div class="table-wrap"><table class="data-table"><thead><tr><th>District</th><th>Trainees</th><th>Placement</th><th>Employment</th><th>6M Retention</th><th>Avg Wage</th><th>Unreachable</th></tr></thead><tbody>${rows.map(x=>`<tr><td><b>${esc(x.district)}</b></td><td>${x.trainees}</td><td>${x.placement}%</td><td>${x.employment}%</td><td>${x.retention}%</td><td>${money(x.wage)}</td><td>${x.unreachable}</td></tr>`).join("")}</tbody></table></div></div>`;
}
async function analytics(){
 const n=await api("/analytics/nonplacement"), r=await api("/analytics/retention"), w=await api("/analytics/wages");
 document.getElementById("content").innerHTML=`<div class="page-head"><div><h1>Outcome Analytics</h1><p>Longitudinal cohort analysis across placement, retention and wage progression.</p></div></div>
 <div class="grid-2"><div class="card"><div class="card-head"><h3>Why trainees were not placed</h3><span>Pareto-style distribution</span></div>${n.slice(0,8).map(x=>`<div style="margin:14px 0;cursor:pointer" onclick="navigate('trainees')"><div style="display:flex;justify-content:space-between;font-size:11px"><b>${esc(x.reason)}</b><span>${x.percent}%</span></div><div class="progress"><i style="width:${x.percent*2.2}%"></i></div></div>`).join("")}</div>
 <div class="card"><div class="card-head"><h3>Retention curve</h3><span>Eligible employed cohort</span></div>${r.map(x=>`<div style="display:flex;align-items:center;gap:12px;margin:24px 0"><b style="width:35px">M${x.month}</b><div class="progress" style="flex:1"><i style="width:${x.rate}%"></i></div><b>${x.rate}%</b></div>`).join("")}</div></div>
 <div class="card" style="margin-top:16px"><div class="card-head"><h3>Wage progression</h3><span>Average salary by follow-up point</span></div><div class="chart">${w.map(x=>`<div class="bar" style="height:${Math.max(35,x.avg/150)}px"><strong>${money(x.avg)}</strong><small>${x.month}</small></div>`).join("")}</div></div>`;
}
async function impact(){const p=await api("/providers");document.getElementById("content").innerHTML=`<div class="page-head"><div><h1>Programme Impact</h1><p>Evidence chain: Training → Employment → Retention → Wage → Relevance → Action.</p></div></div><div class="grid-3">${mini("Reach","1,200+","synthetic trainees")}${mini("Outcome","Placement + retention","longitudinal")}${mini("Value","Actionable","programme improvement")}</div><div class="card" style="margin-top:16px"><h3>Why KAUSHAL360?</h3><div class="grid-3" style="margin-top:15px">${["Longitudinal outcome tracking","Consent-first design","Employment verification","Self-employment + apprenticeship","Wage progression","Retention analytics","Skill-gap intelligence","Provider accountability","Evidence-based recommendations"].map(x=>`<div class="kv"><b>✓ ${x}</b></div>`).join("")}</div></div>`}
async function actions(){const r=await api("/recommendations");document.getElementById("content").innerHTML=`<div class="page-head"><div><h1>Action Center</h1><p>Turn evidence into programme and curriculum decisions.</p></div></div><div class="card">${r.map(x=>`<div class="action"><div><div class="priority ${x.priority==="HIGH"?"high":x.priority==="MEDIUM"?"medium":"low"}">${x.priority} PRIORITY</div><h4>${esc(x.title)}</h4><p>${esc(x.reason)}</p></div><button class="primary" onclick="actionRun('${esc(x.action)}')">${esc(x.action)}</button></div>`).join("")}</div>`}
function actionRun(a){if(a==="Launch Campaign")launchCampaign();else toast(a+" opened · evidence linked")}
async function alerts(){const a=await api("/alerts");document.getElementById("content").innerHTML=`<div class="page-head"><div><h1>Alert Center</h1><p>Every alert links to an underlying operational view.</p></div></div><div class="card">${a.map(x=>`<div class="action"><div><span class="priority ${x.severity==="HIGH"?"high":x.severity==="MEDIUM"?"medium":"low"}">${x.severity}</span><h4>${esc(x.message)}</h4></div><button class="primary" onclick="navigate('${x.target.split('/')[0]}')">Open evidence</button></div>`).join("")}</div>`}
async function reports(){document.getElementById("content").innerHTML=`<div class="page-head"><div><h1>Impact Reports</h1><p>Print-ready programme evidence and downloadable report.</p></div></div><div class="grid-2"><div class="card"><h3>Programme Impact Report</h3><p class="muted">Executive summary, reach, completion, placement, employment, retention, wage progression, skill gaps, provider/district comparison and recommendations.</p><button class="primary" onclick="downloadReport()">Generate / Download Report</button><button class="select" style="margin-left:8px" onclick="window.print()">Preview / Print</button></div><div class="scenario"><b>Judge Demo Scenarios</b><select id="scenario"><option>High Skill Gap</option><option>Low Retention</option><option>Wage Growth Success</option><option>High Unreachable Trainees</option><option>Provider Underperformance</option></select><button class="primary" style="margin-top:10px;width:100%" onclick="loadScenario()">Load Scenario</button><p class="footer-note">Scenarios alter the demonstration narrative; underlying records remain synthetic.</p></div></div>`}
function downloadReport(){window.location="/api/report?token="+encodeURIComponent(token||"");toast("Report generated")}
function loadScenario(){toast("Scenario loaded: "+document.getElementById("scenario").value);navigate("dashboard")}
async function privacy(){const rows=await api("/trainees?limit=20");document.getElementById("content").innerHTML=`<div class="page-head"><div><h1>Privacy & Consent Center</h1><p>Consent is an operational control, not decorative text.</p></div></div><div class="grid-3">${mini("Consent given",rows.filter(x=>x.consent).length,"active records")}${mini("Consent revoked",rows.filter(x=>!x.consent).length,"follow-up disabled")}${mini("Data usage","3 purposes","employment · follow-up · analytics")}</div><div class="card" style="margin-top:16px"><div class="card-head"><h3>Trainee consent records</h3><span>Click a trainee to manage</span></div><table class="data-table"><thead><tr><th>Trainee</th><th>Employment tracking</th><th>Follow-up</th><th>Programme analytics</th><th></th></tr></thead><tbody>${rows.slice(0,15).map(x=>`<tr><td>${esc(x.name)}</td><td>${x.consent?"✓":"—"}</td><td>${x.consent?"✓":"—"}</td><td>${x.consent?"✓":"—"}</td><td><button class="link-btn" onclick="openTrainee(${x.id})">Manage</button></td></tr>`).join("")}</tbody></table></div>`}
async function courses(){
 const rows=await api("/courses");
 document.getElementById("content").innerHTML=`<div class="page-head"><div><h1>Course Outcomes</h1><p>Curriculum relevance, completion pipelines and longitudinal employment metrics.</p></div></div><div class="card"><div class="table-wrap"><table class="data-table"><thead><tr><th>Course</th><th>Programme</th><th>Provider</th><th>Trainees</th><th>Completion</th><th>Placement</th><th>6M Retention</th><th>Avg Wage</th></tr></thead><tbody>${rows.map(c=>`<tr><td><b>${esc(c.name)}</b><div class="muted">${c.duration_weeks} weeks</div></td><td>${esc(c.programme)}</td><td>${esc(c.provider)}</td><td>${c.total_trainees}</td><td>${c.completion_rate}%</td><td>${c.placement_rate}%</td><td>${c.retention_6_rate}%</td><td>${money(c.avg_salary)}</td></tr>`).join("")}</tbody></table></div></div>`
}
async function openTraineeForm(){
 const dists=await api("/districts"); const provs=await api("/providers"); const crss=await api("/courses");
 openModal(`<h2>Add Trainee Outcome Record</h2><p class="muted">Consent-backed vocational outcome registration.</p>
 <label>Full Name *<input id="newTName" class="filter-input" placeholder="e.g. Ramesh Kulkarni" required></label>
 <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
   <label>District *<select id="newTDist" class="filter-input">${dists.map((d,i)=>`<option value="${i+1}">${esc(d.district)}</option>`).join("")}</select></label>
   <label>Provider *<select id="newTProv" class="filter-input">${provs.map(p=>`<option value="${p.id}">${esc(p.provider)}</option>`).join("")}</select></label>
 </div>
 <label>Course *<select id="newTCourse" class="filter-input">${crss.map(c=>`<option value="${c.id}">${esc(c.name)}</option>`).join("")}</select></label>
 <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
   <label>Outcome Status<select id="newTStatus" class="filter-input"><option value="EMPLOYED">EMPLOYED</option><option value="APPRENTICE">APPRENTICE</option><option value="SELF_EMPLOYED">SELF_EMPLOYED</option><option value="SEEKING">SEEKING</option></select></label>
   <label>Monthly Salary (₹)<input id="newTSalary" type="number" class="filter-input" placeholder="22000" value="22000"></label>
 </div>
 <div class="head-actions" style="margin-top:20px">
   <button type="button" class="select" onclick="closeModal()">Cancel</button>
   <button type="button" class="primary" onclick="submitNewTrainee()">Save Trainee</button>
 </div>`);
}
async function submitNewTrainee(){
 try{
   const name=document.getElementById("newTName").value.trim();
   if(!name){toast("Please enter a trainee name");return}
   const body={
     name:name,
     district_id:Number(document.getElementById("newTDist").value),
     provider_id:Number(document.getElementById("newTProv").value),
     course_id:Number(document.getElementById("newTCourse").value),
     employment_status:document.getElementById("newTStatus").value,
     salary:Number(document.getElementById("newTSalary").value)||undefined,
     certified:true,
     consent:true
   };
   const res=await api("/trainees",{method:"POST",body});
   closeModal();
   toast("Trainee created: "+res.trainee_id);
   traineeList();
 }catch(e){toast("Error: "+e.message)}
}
document.getElementById("loginForm").onsubmit=async e=>{e.preventDefault();try{const x=await api("/login",{method:"POST",body:{email:document.getElementById("email").value,password:document.getElementById("password").value}});token=x.token;localStorage.setItem("k360_token",token);me=x;showApp()}catch(e){document.getElementById("loginError").textContent=e.message}}
document.querySelectorAll("[data-demo]").forEach(b=>b.onclick=()=>{const x={admin:["admin@kaushal360.demo","admin123"],provider:["provider@kaushal360.demo","provider123"],officer:["officer@kaushal360.demo","officer123"],trainee:["trainee@kaushal360.demo","trainee123"]}[b.dataset.demo];document.getElementById("email").value=x[0];document.getElementById("password").value=x[1]})
document.getElementById("logoutBtn").onclick=async()=>{try{if(token)await api("/logout",{method:"POST"})}catch{}localStorage.removeItem("k360_token");token=null;showLogin()}
document.getElementById("resetBtn").onclick=async()=>{if(confirm("Reset the synthetic demo dataset?")){await fetch(API+"/reset",{method:"POST"});toast("Demo reset complete");navigate("dashboard")}}
document.getElementById("globalSearch").oninput=async e=>{const q=e.target.value.trim(),box=document.getElementById("searchResults");if(!q){box.classList.add("hidden");return}const x=await api("/search?q="+encodeURIComponent(q));box.classList.remove("hidden");box.innerHTML=[["Trainees",x.trainees],["Providers",x.providers],["Employers",x.employers],["Courses",x.courses]].filter(g=>g[1].length).map(([g,items])=>`<div class="search-group">${g}</div>${items.map(v=>`<button class="search-result" onclick="${g==="Trainees"?`openTrainee(${v.id});`:`toast('${esc(v.name)}')`};document.getElementById('searchResults').classList.add('hidden')">${esc(v.name)}</button>`).join("")}`).join("")||"<div class='empty'>No matches</div>"}
document.getElementById("notifBtn").onclick=()=>navigate("alerts");
document.getElementById("userBtn").onclick=()=>toast(`${me?.name||"User"} · ${me?.role||""}`);
boot();

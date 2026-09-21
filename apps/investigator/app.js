'use strict';
(() => {
  const $ = id => document.getElementById(id);
  const ns = 'http://www.w3.org/2000/svg';
  let data = null, view = 'execution';
  function el(tag, text, cls) { const e = document.createElement(tag); if (text !== undefined) e.textContent = text; if (cls) e.className = cls; return e; }
  function svg(tag, attrs, text) { const e = document.createElementNS(ns, tag); for (const [k,v] of Object.entries(attrs)) e.setAttribute(k, String(v)); if (text !== undefined) e.textContent = text; return e; }
  function validate(d) {
    if (!d || d.schema !== 'investigator-v1' || !['recorded-live','offline-test'].includes(d.mode)) throw Error('Unsupported artifact schema or mode');
    if (!/^[a-f0-9]{40}$/.test(d.commit) || !d.issue || typeof d.issue.title !== 'string') throw Error('Missing immutable source identity');
    for (const name of ['execution','evidence']) {
      const g=d[name]; if (!g || !Array.isArray(g.nodes) || !Array.isArray(g.edges) || g.nodes.length>400 || g.edges.length>800) throw Error('Graph budget or schema invalid');
      const ids = new Set(g.nodes.map(n=>n.id)); if(ids.size!==g.nodes.length) throw Error('Duplicate graph nodes');
      for(const n of g.nodes) if(typeof n.id!=='string'||typeof n.label!=='string'||!n.source) throw Error('Unbound graph node');
      for(const edge of g.edges) if(!ids.has(edge.source)||!ids.has(edge.target)||!['observed','hypothesis'].includes(edge.label)) throw Error('Unbound graph edge');
    }
    if(!Array.isArray(d.reports)||d.reports.length>2||!Array.isArray(d.observations)) throw Error('Malformed report');
    return d;
  }
  function inspect(node) {
    $('node-title').textContent = node.label;
    $('node-kind').textContent = node.kind + ' · ' + node.id;
    let observation = node.observation;
    if (view === 'execution' && Number.isInteger(observation.observation_index)) observation = data.observations[observation.observation_index];
    $('detail').textContent = JSON.stringify({source:node.source,observation},null,2);
    document.querySelectorAll('.node').forEach(e=>e.classList.toggle('selected',e.dataset.id===node.id));
  }
  function draw() {
    const g=data[view], root=$('graph'); root.replaceChildren();
    $('count').textContent=g.nodes.length+' nodes · '+g.edges.length+' edges';
    const width=840, positions=new Map(); let height;
    if(view==='execution') {
      g.nodes.forEach((n,i)=>positions.set(n.id,{x:25+(i%3)*275,y:25+Math.floor(i/3)*95}));
      height=Math.max(460,Math.ceil(g.nodes.length/3)*95+30);
    } else {
      const rows=[0,0,0,0];
      g.nodes.forEach(n=>{const col=n.kind==='issue'||n.kind==='commit'?0:n.kind==='result'||n.kind==='check'?1:n.kind==='report'?3:2;positions.set(n.id,{x:12+col*208,y:25+rows[col]++*76});});
      height=Math.max(460,Math.max(...rows)*76+40);
    }
    root.setAttribute('viewBox',`0 0 ${width} ${height}`); root.style.height=height+'px';
    for(const edge of g.edges){const a=positions.get(edge.source),b=positions.get(edge.target);const w=view==='execution'?240:186;const line=svg('path',{d:`M ${a.x+w/2} ${a.y+52} C ${a.x+w/2} ${a.y+70}, ${b.x+w/2} ${b.y-18}, ${b.x+w/2} ${b.y}`,class:'edge '+(edge.label==='hypothesis'?'hypothesis':'')});line.append(svg('title',{},edge.label+': '+edge.relation));root.append(line);}
    for(const n of g.nodes){const p=positions.get(n.id),w=view==='execution'?240:186;const group=svg('g',{class:'node',transform:`translate(${p.x},${p.y})`,tabindex:0,role:'button','aria-label':n.kind+': '+n.label});group.dataset.id=n.id;group.append(svg('rect',{width:w,height:52,rx:3}),svg('text',{x:12,y:17,class:'kind'},n.id+' / '+n.kind),svg('text',{x:12,y:36},n.label.length>26?n.label.slice(0,25)+'…':n.label));group.append(svg('title',{},n.label));group.addEventListener('click',()=>inspect(n));group.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();inspect(n);}});root.append(group);}
    for(const name of ['execution','evidence']) $(name).setAttribute('aria-pressed',String(view===name));
  }
  function reports() {
    const box=$('report');box.replaceChildren();const report=data.reports.find(r=>r.phase==='final report');
    if(!report){box.textContent='No final report. The investigation stopped without substituting a successful result.';return;}
    box.append(el('p',report.content.summary));
    for(const claim of report.content.claims){const row=el('div',undefined,'claim');row.append(el('p',claim.text));for(const id of claim.citations){const button=el('button','['+id+']','cite');button.addEventListener('click',()=>{view='evidence';draw();const node=data.evidence.nodes.find(n=>n.id===id);if(node)inspect(node);});row.append(button);}box.append(row);}
    box.append(el('h3','Limitations'));const list=el('ul');for(const text of report.content.limitations)list.append(el('li',text));box.append(list);
  }
  function load(d){data=validate(d);$('title').textContent=data.issue.title;$('scope').textContent=data.issue.url+' · '+data.commit;$('mode').textContent=data.mode==='recorded-live'?'RECORDED LIVE':'OFFLINE TEST · PROVIDER DOUBLES';$('status').textContent=data.outcome.status+' / '+data.outcome.reason+' · Jev '+data.metrics.jev_calls+' · Qwen '+data.metrics.qwen_calls+' · '+data.metrics.elapsed_seconds+'s';$('empty').hidden=true;$('canvas').hidden=false;for(const n of ['execution','evidence'])$(n).disabled=false;draw();reports();}
  $('load').addEventListener('change',async e=>{try{const f=e.target.files[0];if(!f)return;if(f.size>524288)throw Error('Artifact exceeds 512 KiB');load(JSON.parse(await f.text()));}catch(error){$('status').textContent='Not loaded: '+error.message;}});
  for(const n of ['execution','evidence'])$(n).addEventListener('click',()=>{view=n;draw();});
  if(window.INVESTIGATION)try{load(window.INVESTIGATION);}catch(error){$('status').textContent='Not loaded: '+error.message;}
})();

/* Home page motion: hero parallax, client marquee, product journey (moon, layers, portal). Ported from the Lune Landing design export. */
(() => {
if(!document.querySelector("[data-journey]")) return;
const sm=(a,b,x)=>{const t=Math.max(0,Math.min(1,(x-a)/(b-a)));return t*t*(3-2*t)};
const cl=x=>Math.max(0,Math.min(1,x));
const ease=t=>t<.5?2*t*t:1-Math.pow(-2*t+2,2)/2;
const easeOut=t=>1-Math.pow(1-t,3);
// [scroll, x, y, radius, phase]
// The intake step (scroll 0.9 to 2.1) sits between the problem and the product overview: the moon moves to the centre and grows while descriptions go in.
const KEYS=[[-1,.74,.5,.05,.03],[0.3,.74,.5,.075,.05],[0.75,.74,.5,.08,.055],[1.25,.5,.58,.13,.07],[1.95,.5,.58,.175,.11],[2.6,.82,.3,.1,.12],[3.85,.72,.52,.17,.25],[5.05,.28,.5,.22,.5],[6.25,.72,.52,.27,.75],[7.45,.28,.5,.31,1],[8.15,.5,.5,.3,1],[9.3,.5,.5,.62,1]];
const CH=[{c:3.85,t:'Enrich'},{c:5.05,t:'Analytics'},{c:6.25,t:'PFM'},{c:7.45,t:'Pulse'}];
const COLORS={Mint:'#E7F6F1',White:'#FFFFFF',Sea:'#E3EFEE'};
const CRATERS=[[0.0,0.35,0.22,0.55],[0.9,-0.2,0.18,0.5],[-0.8,0.1,0.26,0.45],[1.9,0.45,0.15,0.5],[2.6,-0.4,0.24,0.5],[-1.7,-0.45,0.2,0.55],[-2.5,0.3,0.17,0.45],[0.4,-0.6,0.12,0.5],[-0.3,-0.1,0.1,0.4],[1.4,0.15,0.11,0.45],[3.0,0.05,0.2,0.45],[-1.2,0.6,0.14,0.5]];

class Landing {
  constructor(){ this.props={focusBlur:true,portalColor:"Mint"}; }
  componentDidMount(){
    const q=s=>document.querySelector(s), qa=s=>[...document.querySelectorAll(s)];
    this.stage=q('[data-journey]'); this.cv=q('[data-moon]'); this.ctx=this.cv.getContext('2d'); this.sticky=this.cv.parentElement;
    this.portal=q('[data-portal]'); this.pill=q('[data-pill]'); this.pillN=q('[data-pill-n]'); this.pillT=q('[data-pill-t]'); this.ticks=qa('[data-tick]');
    this.layers=qa('[data-layer]').map(el=>({el,c:+el.dataset.c,w:+el.dataset.w,first:!!el.dataset.first,pieces:[...el.querySelectorAll('[data-d]')].map(p=>({el:p,d:+p.dataset.d,fly:+p.dataset.d>=0.5}))}));
    this.layers.forEach(L=>{const fl=L.pieces.filter(p=>p.fly).sort((a,b)=>a.d-b.d); fl.forEach((p,i)=>p.ord=fl.length>1?i/(fl.length-1):0);});
    this.drifts=qa('[data-drift]').map((el,i)=>({el,d:+el.dataset.drift,o:+el.dataset.o,off:(i*0.379)%1,stream:i%2===0}));
    this.drifts.forEach(d=>d.el.setAttribute('aria-hidden','true'));
    this.layers.forEach(L=>{ L.el.style.visibility='visible'; });
    this.pill.style.pointerEvents='none';
    // A link in a stage that is not on screen can get keyboard focus. Scroll to that stage so the person sees it.
    this.stage.addEventListener('focusin',e=>{ const L=this.layers.find(l=>l.el.contains(e.target)); if(!L) return; const top=this.stage.getBoundingClientRect().top+scrollY; const y=top+innerHeight*L.c; if(Math.abs(scrollY-y)>innerHeight*0.2) scrollTo(0,y); });
    this.buildIntake(q('[data-intake]'));
    this.hp=qa('[data-hp]').map(el=>({el,d:+el.dataset.hp}));
    this.marq=q('[data-marquee]'); this.nav=q('[data-nav]');
    if(!matchMedia('(prefers-reduced-motion: reduce)').matches) qa('[data-hero-chip]').sort((a,b)=>a.dataset.heroChip-b.dataset.heroChip).forEach((el,i)=>el.animate([{opacity:0,translate:'0 36px',scale:0.94},{opacity:1,translate:'0 0',scale:1}],{duration:1300,delay:250+i*320,easing:'cubic-bezier(.16,1,.3,1)',fill:'backwards'}));
    this.reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
    this.applyColor(); this.buildPts(); this.resize();
    this.onResize=()=>this.resize(); addEventListener('resize',this.onResize);
    this.tm=[setTimeout(()=>this.measure(),400),setTimeout(()=>this.measure(),1500)];
    this.t0=performance.now();
    const loop=()=>{try{this.frame()}catch(e){console.error(e)} this.raf=requestAnimationFrame(loop)}; loop();
  }
  componentDidUpdate(){ this.applyColor(); }
  componentWillUnmount(){ cancelAnimationFrame(this.raf); removeEventListener('resize',this.onResize); this.tm.forEach(clearTimeout); }
  applyColor(){ const c=COLORS[this.props.portalColor]||COLORS.Mint; document.querySelectorAll('[data-portalbg]').forEach(e=>e.style.background=c); }
  buildPts(){
    const n=Math.max(300,Math.min(5000,this.props.particleDensity??2200)); this.nPts=n;
    const cols=Math.round(Math.sqrt(4*n/Math.PI)), step=2/cols, rowH=step*0.866, pts=[];
    let r=0;
    for(let y=-1+rowH/2;y<1;y+=rowH,r++){
      for(let x=-1+step/2+(r%2?step/2:0);x<1;x+=step){
        const d2=x*x+y*y; if(d2>0.985) continue;
        const z=Math.sqrt(1-d2), lat=Math.asin(y), lon=Math.atan2(x,z);
        pts.push({x,y,z,lat,lon,cl:Math.cos(lat),rnd:Math.random()});
      }
    }
    this.pts=pts; this.cols=cols;
  }
  buildIntake(box){
    // Raw card descriptions that travel into the moon as the user scrolls.
    // Set A: a steady flow from the right while the problem copy is on screen. Set B: a flood from all sides in the intake step.
    this.intakeBox=box; this.intake=[]; if(!box||this.reduce) return;
    const raw=this.drifts.map(d=>d.el.textContent); let seed=7; const rnd=()=>(seed=(seed*16807)%2147483647)/2147483647;
    const add=(a,s0,dur,i)=>{
      const el=document.createElement('span'); el.textContent=raw[i%raw.length];
      el.style.cssText='position:absolute;left:0;top:0;opacity:0;white-space:nowrap;will-change:transform,opacity;font-family:var(--font-mono);font-size:12.5px;letter-spacing:.04em;color:var(--neutral-700);background:rgba(255,255,255,.82);border:1px solid var(--neutral-100);border-radius:8px;padding:6px 10px;box-shadow:0 8px 20px -12px rgba(0,46,42,.25)';
      box.append(el);
      this.intake.push({el,a,s0,dur,ang:(-20+rnd()*220)*Math.PI/180,angR:(rnd()-0.5)*Math.PI*0.6,dist:0.3+rnd()*0.32,curve:(rnd()-0.5)*90,vis:false});
    };
    for(let i=0;i<14;i++) add(true,0.05+i/14*0.75,0.5,i*3);
    for(let i=0;i<44;i++) add(false,0.9+i/44*0.74+rnd()*0.03,0.42,i);
  }
  resize(){
    const dpr=Math.min(devicePixelRatio||1,2), W=this.cv.clientWidth, H=this.cv.clientHeight;
    this.W=W; this.H=H; this.cv.width=W*dpr; this.cv.height=H*dpr; this.ctx.setTransform(dpr,0,0,dpr,0,0);
    this.measure();
  }
  fit(){
    const H=this.sticky.clientHeight;
    this.layers.forEach(L=>{ const inner=L.el.firstElementChild; if(!inner||inner.dataset.d) return;
      inner.style.transform='none'; const h=inner.offsetHeight, k=h>H?Math.max(0.6,H/h):1;
      inner.style.transformOrigin='50% 50%'; inner.style.transform=k<1?`scale(${k.toFixed(3)})`:'none'; });
  }
  measure(){
    this.fit();
    const sr=this.sticky.getBoundingClientRect();
    this.drifts.forEach(d=>{d.el.style.transform='none'; d.bx=d.el.offsetLeft+d.el.offsetWidth/2; d.by=d.el.offsetTop+d.el.offsetHeight/2;});
    this.layers.forEach(L=>L.pieces.forEach(p=>{p.el.style.transform='none'; const r=p.el.getBoundingClientRect(); p.cx=r.left+r.width/2-sr.left; p.cy=r.top+r.height/2-sr.top;}));
  }
  measureLayer(L){
    const sr=this.sticky.getBoundingClientRect();
    L.pieces.forEach(p=>{const t=p.el.style.transform; p.el.style.transform='none'; const r=p.el.getBoundingClientRect(); p.cx=r.left+r.width/2-sr.left; p.cy=r.top+r.height/2-sr.top; p.el.style.transform=t;});
  }
  moonAt(s){
    if(s<=KEYS[0][0]) return KEYS[0].slice();
    for(let i=1;i<KEYS.length;i++){ if(s<=KEYS[i][0]){const a=KEYS[i-1],b=KEYS[i],t=ease((s-a[0])/(b[0]-a[0]));const o=a.map((v,j)=>v+(b[j]-v)*t);o[2]-=Math.sin(Math.PI*t)*Math.abs(b[1]-a[1])*0.3;return o;} }
    return KEYS[KEYS.length-1].slice();
  }
  litPath(ctx,mx,my,R,th){
    const c=Math.cos(th), rx=Math.max(0.001,R*Math.abs(c));
    ctx.beginPath(); ctx.arc(mx,my,R,-Math.PI/2,Math.PI/2,false);
    if(c<0) ctx.ellipse(mx,my,rx,R,0,Math.PI/2,-Math.PI/2,true); else ctx.ellipse(mx,my,rx,R,0,Math.PI/2,3*Math.PI/2,false);
    ctx.closePath();
  }
  frame(){
    const vh=innerHeight, time=(performance.now()-this.t0)/1000;
        if(Math.abs(this.cv.clientWidth-this.W)>1||Math.abs(this.cv.clientHeight-this.H)>1) this.resize();
    const sy=scrollY;
    if(sy<vh*1.5) this.hp.forEach(h=>h.el.style.transform=`translate3d(0,${(-sy*h.d).toFixed(1)}px,0)`);
    if(this.marq&&!this.reduce){const half=this.marq.scrollWidth/2; if(half>0) this.marq.style.transform=`translate3d(${-((time*30)%half)}px,0,0)`;}
    const rect=this.stage.getBoundingClientRect();
    { const sN=-rect.top/vh, inJ=sN>0.15&&sN<8.9, dy=sy-(this.lastY??sy); this.lastY=sy;
      if(!inJ) this.navUp=false; else if(dy<-3) this.navUp=true; else if(dy>3) this.navUp=false;
      const hide=inJ&&!this.navUp;
      if(this.navHidden!==hide){ this.navHidden=hide; this.nav.style.transform=hide?'translateY(-130%)':'none'; this.nav.style.opacity=hide?'0':'1'; this.nav.style.pointerEvents=hide?'none':'auto'; this.nav.inert=hide; } }
    if(rect.bottom<0||rect.top>vh) return;
    const s=-rect.top/vh, W=this.W, H=this.H, blur=(this.props.focusBlur??true)&&!this.reduce;
    const narrow=W<860, k=this.moonAt(s);
    const mx=(narrow?0.5:k[1])*W, my=(narrow?0.74:k[2])*H, R=k[3]*Math.min(W*1.15,H)*(narrow?0.8:1), ph=k[4];

    // layers: copy fades in place; graphic pieces are born in the moon and settle into place
    for(const L of this.layers){
      let u=(s-L.c)/L.w; if(L.first&&u<0) u=0; u=Math.max(-1,Math.min(1,u));
      const a=Math.abs(u), v=Math.sign(u)*(a<0.5?0:(a-0.5)/0.5), av=Math.abs(v);
      const lop=v>0?1-sm(0.2,0.8,v):(av>=0.999?0:1);
      if(lop>=0.01&&L.hidden!==false){ L.hidden=false; this.measureLayer(L); } else if(lop<0.01) L.hidden=true;
      L.el.style.opacity=lop.toFixed(3); L.el.style.visibility='visible'; L.el.style.pointerEvents=lop>0.6&&av<0.3?'auto':'none';
      if(lop<0.01) continue;
      const e=v<0?1-av:1, ef=u<0?1-cl((a-0.1)/0.9):1;
      for(const p of L.pieces){
        if(this.reduce){p.el.style.opacity=sm(0,0.6,e).toFixed(3); continue;}
        if(!p.fly){
          const pe=sm(0.15,0.75,e);
          p.el.style.opacity=pe.toFixed(3); p.el.style.transform='none';
          const b=blur?(1-pe)*3:0; p.el.style.filter=b>0.2?`blur(${b.toFixed(1)}px)`:'none';
        } else {
          const pe=cl((ef-p.ord*0.45)/0.55), kk=easeOut(pe);
          const tx=(mx-p.cx)*(1-kk), ty=(my-p.cy)*(1-kk), sc=0.04+0.96*kk;
          p.el.style.opacity=sm(0,0.25,pe).toFixed(3); p.el.style.transformOrigin='50% 50%';
          p.el.style.transform=pe>=1?'none':`translate3d(${tx.toFixed(1)}px,${ty.toFixed(1)}px,0) scale(${sc.toFixed(3)})`;
          const b=blur?(1-kk)*1.5:0; p.el.style.filter=b>0.2?`blur(${b.toFixed(1)}px)`:'none';
        }
      }
    }

    // raw descriptions: a big burst into the moon at the start, then a thinner stream through the chapters
    const pull=sm(-0.6,0.15,s);
    let hold=0; for(const L of this.layers){const dd=Math.abs(s-L.c)/L.w; hold=Math.max(hold,1-sm(0.45,0.75,dd));}
    const streamOn=sm(0.3,0.6,s)*(1-sm(7.7,8.1,s))*(1-hold);
    for(const d of this.drifts){
      let kk, op;
      if(s<0.3){ kk=pull; op=d.o*(1-sm(0.6,1,pull)); }
      else if(d.stream){ const t=((s-0.3)*0.85+d.off)%1; kk=t*t; op=d.o*0.75*streamOn*sm(0,0.15,t)*(1-sm(0.7,0.95,t)); }
      else { kk=1; op=0; }
      const tx=(mx-d.bx)*kk, ty=(my-d.by)*kk+(s<0?-s*d.d*120:0);
      d.el.style.transform=`translate3d(${tx.toFixed(1)}px,${ty.toFixed(1)}px,0) scale(${(1-kk*0.85).toFixed(3)})`;
      d.el.style.opacity=(op*(narrow?0.35:1)).toFixed(3);
    }

    // intake: each description moves from its start point into the moon; scroll position sets the progress
    if(this.intake.length){
      const on=s>-0.1&&s<2.2;
      if(this.intakeOn!==on){ this.intakeOn=on; this.intakeBox.style.visibility=on?'visible':'hidden'; }
      if(on){
        const base=Math.max(W,H*1.2);
        for(const it of this.intake){
          const p=(narrow&&it.a)?0:(s-it.s0)/it.dur;
          if(p<=0||p>=1){ if(it.vis){ it.vis=false; it.el.style.opacity='0'; } continue; }
          it.vis=true;
          const side=it.a&&!narrow, ang=side?it.angR:it.ang, dist=it.dist*base*(side?0.62:1)*(1-Math.pow(p,1.7));
          const x=mx+Math.cos(ang)*dist, y=my+Math.sin(ang)*dist*0.72+Math.sin(Math.PI*p)*it.curve;
          it.el.style.opacity=(sm(0,0.14,p)*(1-sm(0.84,1,p))).toFixed(3);
          it.el.style.transform=`translate3d(${x.toFixed(1)}px,${y.toFixed(1)}px,0) translate(-50%,-50%) scale(${(1-0.72*sm(0.45,1,p)).toFixed(3)})`;
        }
      }
    }

    // moon
    const ctx=this.ctx; ctx.clearRect(0,0,W,H);
    // On narrow screens the moon is behind the copy, so it is faint. It is at full strength only in the intake step, where no copy is near it.
    ctx.globalAlpha=narrow?0.14+0.86*sm(0.95,1.25,s)*(1-sm(2.0,2.3,s)):1;
    const g=sm(0.88,1,ph), pulse=0.5+0.5*Math.sin(time*1.8), two=Math.PI*2;
    const th=Math.PI*(1-ph), lx=Math.sin(th), lz=Math.cos(th);
    const feed=sm(0.95,1.25,s)*(1-sm(1.95,2.2,s)), glow=0.12+0.25*ph+feed*(0.22+0.12*pulse);
    const hal=ctx.createRadialGradient(mx+R*0.25,my,R*0.8,mx,my,R*1.9);
    hal.addColorStop(0,`rgba(16,163,127,${(glow*0.6).toFixed(3)})`); hal.addColorStop(1,'rgba(16,163,127,0)');
    ctx.fillStyle=hal; ctx.beginPath(); ctx.arc(mx,my,R*1.9,0,two); ctx.fill();
    // dark body
    const dk=ctx.createRadialGradient(mx-R*0.3,my-R*0.3,R*0.1,mx,my,R);
    dk.addColorStop(0,'rgba(0,46,42,0.10)'); dk.addColorStop(1,'rgba(0,46,42,0.20)');
    ctx.fillStyle=dk; ctx.beginPath(); ctx.arc(mx,my,R,0,two); ctx.fill();
    // lit body — glossy gradient toward the light
    ctx.save(); this.litPath(ctx,mx,my,R,th); ctx.clip();
    const hx=mx+R*0.42, hy=my-R*0.4;
    const lit=ctx.createRadialGradient(hx,hy,R*0.02,mx,my,R*1.05);
    lit.addColorStop(0,'#F2FFF6'); lit.addColorStop(0.18,'#99F2AC'); lit.addColorStop(0.55,'#10A37F'); lit.addColorStop(1,'#0A634D');
    ctx.fillStyle=lit; ctx.fillRect(mx-R,my-R,2*R,2*R);
    ctx.restore();
    // gloss: soft specular highlight + rim light
    ctx.save(); this.litPath(ctx,mx,my,R,th); ctx.clip();
    const sp=ctx.createRadialGradient(hx,hy,0,hx,hy,R*0.6);
    sp.addColorStop(0,'rgba(255,255,255,0.7)'); sp.addColorStop(0.4,'rgba(255,255,255,0.18)'); sp.addColorStop(1,'rgba(255,255,255,0)');
    ctx.fillStyle=sp; ctx.fillRect(mx-R,my-R,2*R,2*R);
    ctx.restore();
    ctx.lineWidth=Math.max(1,R/110); ctx.strokeStyle='rgba(153,242,172,0.55)';
    ctx.beginPath(); ctx.arc(mx,my,R-ctx.lineWidth/2,-Math.PI/2+0.15,Math.PI/2-0.15); ctx.stroke();
    ctx.lineWidth=1; ctx.strokeStyle='rgba(0,46,42,0.14)'; ctx.beginPath(); ctx.arc(mx,my,R,0,two); ctx.stroke();

    ctx.globalAlpha=1;

    // portal
    const pk=sm(8.05,9.2,s), pr=pk*pk*Math.hypot(W,H)*1.05;
    this.portal.style.opacity=pk>0.001?'1':'0';
    this.portal.style.width=this.portal.style.height=(2*pr).toFixed(1)+'px';
    this.portal.style.transform=`translate3d(${(mx-pr).toFixed(1)}px,${(my-pr).toFixed(1)}px,0)`;

    const vis=sm(3.1,3.4,s)*(1-sm(7.9,8.2,s));
    this.pill.style.opacity=vis.toFixed(3);
    let ai=0; CH.forEach((c,i)=>{ if(s>=c.c-0.6) ai=i; });
    if(this.ai!==ai){ this.ai=ai; this.pillT.textContent=CH[ai].t; }
    this.ticks.forEach((t,i)=>{ const f=Math.max(0,Math.min(1,(s-(CH[i].c-0.6))/1.2)); t.style.width=(f*100).toFixed(1)+'%'; });
  }
  renderVals(){ return {}; }
}
const start=()=>new Landing().componentDidMount();
if(document.readyState==="loading") addEventListener("DOMContentLoaded",start); else start();
})();

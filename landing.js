/* Home page motion: hero parallax, client marquee and the product journey (moon, layers, portal).
   Ported from the Lune Landing design export, then reworked:
   - Focal moment: card descriptions go into the moon, and the four products come out of it.
     Each description that reaches the moon makes it glow and swell a little, so the person sees the moon take it in.
   - The loop does work only when something changes: a new scroll position, a new window size,
     a visible marquee, or the moon feed. It stops while the tab is hidden.
   - The canvas clears only the area the moon used in the last frame.
   - The end circle (portal) grows with a transform, not with width and height.
   - Reduced motion: no moon, no flying descriptions, no parallax. Stages cross-fade, and the mint end colour fades in. */
(() => {
if(!document.querySelector("[data-journey]")) return;
const sm=(a,b,x)=>{const t=Math.max(0,Math.min(1,(x-a)/(b-a)));return t*t*(3-2*t)};
const cl=x=>Math.max(0,Math.min(1,x));
const ease=t=>t<.5?2*t*t:1-Math.pow(-2*t+2,2)/2;
const easeOut=t=>1-Math.pow(1-t,3);
// [scroll, x, y, radius, phase]. Scroll is in window heights from the top of the journey.
// The intake step (scroll 0.9 to 2.1) sits between the problem and the product overview: the moon moves to the centre and grows while descriptions go in.
const KEYS=[[-1,.74,.5,.05,.2],[0.3,.74,.5,.075,.22],[0.75,.74,.5,.08,.25],[1.25,.5,.58,.13,.32],[1.95,.5,.58,.175,.42],[2.6,.82,.3,.1,.42],[3.85,.72,.52,.17,.5],[5.05,.28,.5,.22,.62],[6.25,.72,.52,.27,.82],[7.45,.28,.5,.31,1],[8.0,.5,.5,.3,1],[8.75,.5,.5,.62,1]];
const CH=[{c:3.85,t:'Enrich'},{c:5.05,t:'Analytics'},{c:6.25,t:'PFM'},{c:7.45,t:'Pulse'}];
const END=8.55;          // the header comes back and the journey ends after this point
const PORTAL=[7.85,8.7]; // the mint circle grows over this range

class Landing {
  mount(){
    const q=s=>document.querySelector(s), qa=s=>[...document.querySelectorAll(s)];
    this.reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
    this.stage=q('[data-journey]'); this.cv=q('[data-moon]'); this.ctx=this.cv.getContext('2d'); this.sticky=this.cv.parentElement;
    this.portal=q('[data-portal]'); this.pill=q('[data-pill]'); this.pillT=q('[data-pill-t]'); this.ticks=qa('[data-tick]');
    this.layers=qa('[data-layer]').map(el=>({el,c:+el.dataset.c,w:+el.dataset.w,first:!!el.dataset.first,pieces:[...el.querySelectorAll('[data-d]')].map(p=>({el:p,d:+p.dataset.d,fly:+p.dataset.d>=0.5}))}));
    this.layers.forEach(L=>{const fl=L.pieces.filter(p=>p.fly).sort((a,b)=>a.d-b.d); fl.forEach((p,i)=>p.ord=fl.length>1?i/(fl.length-1):0); L.el.style.visibility='visible';});
    this.drifts=qa('[data-drift]').map((el,i)=>({el,d:+el.dataset.drift,o:+el.dataset.o,off:(i*0.379)%1,stream:i%2===0}));
    this.drifts.forEach(d=>d.el.setAttribute('aria-hidden','true'));
    this.pill.style.pointerEvents='none';
    // A link in a stage that is not on screen can get keyboard focus. Scroll to that stage so the person sees it.
    this.stage.addEventListener('focusin',e=>{ const L=this.layers.find(l=>l.el.contains(e.target)); if(!L) return; const top=this.stage.getBoundingClientRect().top+scrollY; const y=top+innerHeight*L.c; if(Math.abs(scrollY-y)>innerHeight*0.2) scrollTo(0,y); });
    this.hp=this.reduce?[]:qa('[data-hp]').map(el=>({el,d:+el.dataset.hp}));
    this.marq=q('[data-marquee]'); this.nav=q('[data-nav]');
    if(this.reduce) this.drifts.forEach(d=>{d.el.style.opacity='0';});
    this.buildIntake(q('[data-intake]'));
    this.pearl=(window.LuneMoon&&!/[?&]moon2d\b/.test(location.search))?window.LuneMoon.create():null;   // ?moon2d forces the 2D moon
    // The marquee moves only while it is on screen.
    this.marqOn=false; const still=/[?&]still\b/.test(location.search);
    if(this.marq&&!this.reduce&&!still&&'IntersectionObserver' in window) new IntersectionObserver(es=>{ this.marqOn=es[0].isIntersecting; this.wake(); }).observe(this.marq.parentElement);
    this.resize();
    addEventListener('resize',()=>{ this.resize(); this.wake(); });
    new MutationObserver(()=>this.wake()).observe(document.documentElement,{attributes:true,attributeFilter:['class']});   // the pause control
    addEventListener('scroll',()=>this.wake(),{passive:true});
    document.addEventListener('visibilitychange',()=>{ if(!document.hidden) this.wake(); });
    setTimeout(()=>{ this.measure(); this.force=true; this.wake(); },400);
    setTimeout(()=>{ this.measure(); this.force=true; this.wake(); },1500);
    this.t0=performance.now(); this.force=true; this.wake();
    const at=new URLSearchParams(location.search).get('s');
    if(at!==null){ const go=()=>scrollTo(0,this.stage.getBoundingClientRect().top+scrollY+innerHeight*(+at));
      const later=()=>setTimeout(()=>{ go(); setTimeout(go,400); },200);
      if(document.readyState==='complete') later(); else addEventListener('load',later); }
  }
  // One animation frame runs only when it has work. A frame asks for the next one only while something still moves.
  wake(){ if(this.raf||document.hidden) return; this.raf=requestAnimationFrame(()=>{ this.raf=0; let more=false; try{ more=this.frame(); }catch(e){ console.error(e); } if(more) this.wake(); }); }
  buildIntake(box){
    // Raw card descriptions that travel into the moon as the user scrolls.
    // Set A: a steady flow from the right while the problem copy is on screen. Set B: a flood from all sides in the intake step.
    this.intakeBox=box; this.intake=[]; if(!box) return;
    const raw=this.drifts.map(d=>d.el.textContent); let seed=7; const rnd=()=>(seed=(seed*16807)%2147483647)/2147483647;
    const add=(a,s0,dur,i)=>{
      const el=document.createElement('span'); el.textContent=raw[i%raw.length];
      el.style.cssText='position:absolute;left:0;top:0;opacity:0;white-space:nowrap;font-family:var(--font-mono);font-size:12.5px;letter-spacing:.04em;color:var(--neutral-700);background:rgba(255,255,255,.82);border:1px solid var(--neutral-100);border-radius:8px;padding:6px 10px;box-shadow:0 8px 20px -12px rgba(0,46,42,.25)';
      box.append(el);
      this.intake.push({el,a,s0,dur,ang:(-20+((i*137.508)%220))*Math.PI/180,angR:-(8+rnd()*52)*Math.PI/180,dist:0.32+(i%4)*0.08+rnd()*0.04,curve:(rnd()-0.5)*70,vis:false});
    };
    if(this.reduce){ for(let i=0;i<12;i++) add(false,0,1,i); return; }   // reduced motion: twelve still descriptions around a still moon
    for(let i=0;i<14;i++) add(true,0.05+i/14*0.75,0.5,i*3);
    for(let i=0;i<32;i++) add(false,0.9+i/32*0.76+rnd()*0.03,0.36,i);
  }
  resize(){
    const dpr=Math.min(devicePixelRatio||1,2), W=this.cv.clientWidth, H=this.cv.clientHeight;
    this.W=W; this.H=H; this.cv.width=W*dpr; this.cv.height=H*dpr; this.ctx.setTransform(dpr,0,0,dpr,0,0); this.box=null;
    // The portal has a fixed size that covers the stage. Scroll sets its scale.
    this.PR=Math.hypot(W,H)*1.05; this.portal.style.width=this.portal.style.height=(2*this.PR).toFixed(0)+'px';
    this.measure(); this.force=true;
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
  // Returns true while the next frame must run without a new scroll (the marquee).
  frame(){
    const vh=innerHeight, time=(performance.now()-this.t0)/1000, sy=scrollY;
    if(Math.abs(this.cv.clientWidth-this.W)>1||Math.abs(this.cv.clientHeight-this.H)>1) this.resize();
    const moved=sy!==this.lastY||this.force;
    let more=false;
    if(this.marq&&this.marqOn&&!document.documentElement.classList.contains('paused')){ const half=this.marq.scrollWidth/2; if(half>0) this.marq.style.transform=`translate3d(${-((time*30)%half).toFixed(1)}px,0,0)`; more=true; }
    if(moved&&sy<vh*1.5) this.hp.forEach(h=>h.el.style.transform=`translate3d(0,${(-sy*h.d).toFixed(1)}px,0)`);
    const rect=this.stage.getBoundingClientRect();
    { const sN=-rect.top/vh, inJ=sN>0.15&&sN<END, dy=sy-(this.lastY??sy);
      if(!inJ) this.navUp=false; else if(dy<-3) this.navUp=true; else if(dy>3) this.navUp=false;
      const hide=inJ&&!this.navUp;
      if(this.navHidden!==hide){ this.navHidden=hide; this.nav.style.transform=hide?'translateY(-130%)':'none'; this.nav.style.opacity=hide?'0':'1'; this.nav.style.pointerEvents=hide?'none':'auto'; this.nav.inert=hide; } }
    this.lastY=sy;
    if(rect.bottom<0||rect.top>vh){ this.force=false; return more; }
    const s=-rect.top/vh, feed=sm(0.95,1.25,s)*(1-(this.reduce?sm(1.72,1.92,s):sm(1.95,2.2,s)));
    if(!moved) return more;              // nothing changed in the journey
    this.force=false;
    const W=this.W, H=this.H, blur=!this.reduce;
    const narrow=W<860, k=this.moonAt(s);
    const mx=(narrow?0.5:k[1])*W, my=(narrow?0.74:k[2])*H, ph=k[4];
    let R=k[3]*Math.min(W*1.15,H)*(narrow?0.8:1);

    if(moved){
      // layers: copy fades in place; graphic pieces are born in the moon and settle into place
      for(const L of this.layers){
        let u=(s-L.c)/L.w; if(L.first&&u<0) u=0; u=Math.max(-1,Math.min(1,u));
        const a=Math.abs(u), v=Math.sign(u)*(a<0.5?0:(a-0.5)/0.5), av=Math.abs(v);
        const lop=v>0?1-sm(0.2,0.8,v):(av>=0.999?0:1);
        if(lop>=0.01&&L.hidden!==false){ L.hidden=false; this.measureLayer(L); } else if(lop<0.01) L.hidden=true;
        L.el.style.opacity=lop.toFixed(3); L.el.style.pointerEvents=lop>0.6&&av<0.3?'auto':'none';
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

      // raw descriptions in the background: a burst into the moon at the start, then a thin stream through the chapters
      if(!this.reduce){
        const pull=sm(-0.6,0.15,s);
        let hold=0; for(const L of this.layers){const dd=Math.abs(s-L.c)/L.w; hold=Math.max(hold,1-sm(0.45,0.75,dd));}
        const streamOn=sm(0.3,0.6,s)*(1-sm(7.6,7.95,s))*(1-hold);
        for(const d of this.drifts){
          let kk, op;
          if(s<0.3){ kk=pull; op=d.o*(1-sm(0.6,1,pull)); }
          else if(d.stream){ const t=((s-0.3)*0.85+d.off)%1; kk=t*t; op=d.o*0.75*streamOn*sm(0,0.15,t)*(1-sm(0.7,0.95,t)); }
          else { kk=1; op=0; }
          const tx=(mx-d.bx)*kk, ty=(my-d.by)*kk+(s<0?-s*d.d*120:0);
          d.el.style.transform=`translate3d(${tx.toFixed(1)}px,${ty.toFixed(1)}px,0) scale(${(1-kk*0.85).toFixed(3)})`;
          d.el.style.opacity=(op*(narrow?0.35:1)).toFixed(3);
        }
      }
    }

    // intake: each description moves from its start point into the moon; scroll position sets the progress.
    // A description that reaches the moon adds to "absorb", which makes the moon glow and swell.
    let absorb=0;
    if(this.intake.length){
      const on=s>-0.1&&s<2.2;
      if(this.intakeOn!==on){ this.intakeOn=on; this.intakeBox.style.visibility=on?'visible':'hidden'; }
      if(on&&this.reduce){
        if(moved){ const base=Math.max(W,H*1.2), cx=0.5*W, cy=(narrow?0.62:0.58)*H;
          for(const it of this.intake){ const d=it.dist*base*0.55, x=cx+Math.cos(it.ang)*d, y=cy+Math.sin(it.ang)*d*0.72;
            it.el.style.opacity=(0.9*feed).toFixed(3); it.el.style.transform=`translate3d(${x.toFixed(1)}px,${y.toFixed(1)}px,0) translate(-50%,-50%) scale(.82)`; } }
      } else if(on){
        const base=Math.max(W,H*1.2);
        for(const it of this.intake){
          const p=(narrow&&it.a)?0:(s-it.s0)/it.dur;
          if(p>0.72&&p<1.12&&!it.a) absorb+=sm(0.72,0.92,p)*(1-sm(0.95,1.12,p));
          if(p<=0||p>=1){ if(it.vis){ it.vis=false; it.el.style.opacity='0'; it.el.style.willChange=''; } continue; }
          if(!it.vis){ it.vis=true; it.el.style.willChange='transform,opacity'; }
          if(!moved) continue;
          const side=it.a&&!narrow, ang=side?it.angR:it.ang, dist=it.dist*base*(side?0.62:1)*(1-Math.pow(p,1.7));
          const x=mx+Math.cos(ang)*dist, y=my+Math.sin(ang)*dist*0.72+Math.sin(Math.PI*p)*it.curve;
          it.el.style.opacity=(sm(0,0.14,p)*(1-sm(0.84,1,p))).toFixed(3);
          it.el.style.transform=`translate3d(${x.toFixed(1)}px,${y.toFixed(1)}px,0) translate(-50%,-50%) scale(${(1-0.72*sm(0.45,1,p)).toFixed(3)})`;
        }
      }
    }
    absorb=Math.min(1,absorb/2.2);
    R*=1+0.05*absorb;

    // moon. The canvas clears only the area of the last frame.
    let mxD=mx, myD=my, alpha=(narrow?0.14+0.86*sm(0.95,1.25,s)*(1-sm(2.0,2.3,s)):1)*(1-sm(PORTAL[0]+0.05,PORTAL[0]+0.4,s)), phD=ph;
    if(this.reduce){ mxD=0.5*W; myD=(narrow?0.62:0.58)*H; R=0.16*Math.min(W*1.15,H); alpha=feed; phD=0.1; }
    if(moved||absorb>0){
      const ctx=this.ctx, two=Math.PI*2, hr=R*1.95+8, mx=mxD, my=myD, ph=phD;
      if(this.box) ctx.clearRect(...this.box); else ctx.clearRect(0,0,W,H);
      this.box=[mx-hr,my-hr,2*hr,2*hr];
      // On narrow screens the moon is behind the copy, so it is faint. It is at full strength only in the intake step, where no copy is near it.
      ctx.globalAlpha=alpha;
      // A smooth moon: a pale mint disc, a lit side with a soft edge, a soft highlight and a thin rim.
      // When a description reaches the moon ("absorb"), the glow gets brighter and the moon swells a little. No hard strokes.
      const th=Math.PI*(1-ph);
      const glow=0.08+0.12*ph+feed*0.18+0.34*absorb;
      const hal=ctx.createRadialGradient(mx,my,R*0.85,mx,my,R*1.9);
      hal.addColorStop(0,`rgba(16,163,127,${Math.min(0.5,glow*0.5).toFixed(3)})`); hal.addColorStop(0.45,`rgba(16,163,127,${Math.min(0.2,glow*0.2).toFixed(3)})`); hal.addColorStop(1,'rgba(16,163,127,0)');
      ctx.fillStyle=hal; ctx.beginPath(); ctx.arc(mx,my,R*1.9,0,two); ctx.fill();
      const sprite=this.pearl&&this.pearl.draw(R,ph,absorb,s);
      if(sprite){
        const u=this.pearl.used;
        ctx.drawImage(sprite,0,sprite.height-u,u,u,mx-R,my-R,2*R,2*R);
      } else {
      const hx=mx+R*0.38, hy=my+R*0.36;
      ctx.save(); ctx.beginPath(); ctx.arc(mx,my,R,0,two); ctx.clip();
      // body: the dark side is a pale mint, not grey
      const body=ctx.createRadialGradient(mx-R*0.25,my-R*0.3,R*0.1,mx,my,R*1.05);
      body.addColorStop(0,'#0B3D37'); body.addColorStop(0.65,'#002E2A'); body.addColorStop(1,'#00221F');
      ctx.fillStyle=body; ctx.fillRect(mx-R,my-R,2*R,2*R);
      // lit side: its edge is blurred, so light turns into shade without a line
      const lit=ctx.createRadialGradient(hx,hy,R*0.04,mx,my,R*1.1);
      lit.addColorStop(0,'#6FB3AC'); lit.addColorStop(0.35,'#469A93'); lit.addColorStop(1,'#0A634D');
      if('filter' in ctx) ctx.filter=`blur(${Math.min(18,Math.max(2,R*0.07)).toFixed(1)}px)`;
      ctx.fillStyle=lit; this.litPath(ctx,mx,my,R,th); ctx.fill();
      if('filter' in ctx) ctx.filter='none';
      // soft highlight
      const sp=ctx.createRadialGradient(hx,hy,0,hx,hy,R*0.7);
      sp.addColorStop(0,'rgba(153,242,172,0.18)'); sp.addColorStop(0.5,'rgba(153,242,172,0.05)'); sp.addColorStop(1,'rgba(255,255,255,0)');
      ctx.fillStyle=sp; ctx.fillRect(mx-R,my-R,2*R,2*R);
      // inner shade at the edge gives the disc volume
      const edge=ctx.createRadialGradient(mx,my,R*0.78,mx,my,R);
      edge.addColorStop(0,'rgba(0,46,42,0)'); edge.addColorStop(1,'rgba(0,46,42,0.10)');
      ctx.fillStyle=edge; ctx.fillRect(mx-R,my-R,2*R,2*R);
      ctx.restore();
      // thin rim, with a soft mint glow while descriptions go in
      ctx.save(); ctx.lineWidth=1.2; ctx.strokeStyle=`rgba(16,163,127,${(0.22+0.25*absorb).toFixed(3)})`;
      if(absorb>0.02){ ctx.shadowColor=`rgba(153,242,172,${(0.9*absorb).toFixed(3)})`; ctx.shadowBlur=R*0.18; }
      ctx.beginPath(); ctx.arc(mx,my,R-0.6,0,two); ctx.stroke(); ctx.restore();
      }
      ctx.globalAlpha=1;
    }

    // portal: the mint circle grows from the moon and becomes the next section. Reduced motion: the colour fades in.
    if(moved){
      const pk=sm(PORTAL[0],PORTAL[1],s);
      if(this.reduce){
        this.portal.style.opacity=pk.toFixed(3);
        this.portal.style.transform=`translate3d(${(W/2-this.PR).toFixed(1)}px,${(H/2-this.PR).toFixed(1)}px,0) scale(1)`;
      } else {
        const sc=pk*pk;
        this.portal.style.opacity=pk>0.001?'1':'0';
        this.portal.style.transform=`translate3d(${(mx-this.PR).toFixed(1)}px,${(my-this.PR).toFixed(1)}px,0) scale(${sc.toFixed(4)})`;
      }

      const vis=sm(3.1,3.4,s)*(1-sm(7.8,8.05,s));
      this.pill.style.opacity=vis.toFixed(3);
      let ai=0; CH.forEach((c,i)=>{ if(s>=c.c-0.6) ai=i; });
      if(this.ai!==ai){ this.ai=ai; this.pillT.textContent=CH[ai].t; }
      this.ticks.forEach((t,i)=>{ const f=Math.max(0,Math.min(1,(s-(CH[i].c-0.6))/1.2)); t.style.width=(f*100).toFixed(1)+'%'; });
    }
    return more;
  }
}
const start=()=>new Landing().mount();
if(document.readyState==="loading") addEventListener("DOMContentLoaded",start); else start();
})();

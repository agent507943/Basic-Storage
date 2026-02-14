document.addEventListener('DOMContentLoaded', function(){
  const svg = document.getElementById('diagram');
  const viewport = document.getElementById('viewport');
  const infoName = document.getElementById('comp-name');
  const infoDesc = document.getElementById('comp-desc');
  const compImage = document.getElementById('comp-image');
  const reviewCountEl = document.getElementById('review-count');
  const quizPanel = document.getElementById('quiz');
  const quizPrompt = document.getElementById('quiz-prompt');
  const quizTarget = document.getElementById('quiz-target');
  const quizFeedback = document.getElementById('quiz-feedback');
  const mcqChoices = document.getElementById('mcq-choices');
  const wiringBoard = document.getElementById('wiring-board');
  const wiringSvg = document.getElementById('wiring-svg');
  const addReviewBtn = document.getElementById('add-review');
  const endQuizBtn = document.getElementById('end-quiz');
  const studySection = document.getElementById('study');
  const showStudyBtn = document.getElementById('show-study');
  const tooltip = document.getElementById('tooltip');

  let components = COMPONENTS || [];
  let questions = QUESTIONS || [];
  let quizState = null; // {type:'find'|'mcq'|'wiring', question: {...}}

  // viewport transform state
  let scale = 1, tx = 0, ty = 0;

  function applyTransform(){
    viewport.setAttribute('transform', `translate(${tx} ${ty}) scale(${scale})`);
  }

  // Helpers: convert screen point to svg coords
  function screenToSvg(x,y, targetSvg){
    const pt = targetSvg.createSVGPoint();
    pt.x = x; pt.y = y;
    return pt.matrixTransform(targetSvg.getScreenCTM().inverse());
  }

  // Zoom with wheel
  svg.addEventListener('wheel', function(e){
    e.preventDefault();
    const dir = e.deltaY > 0 ? 0.9 : 1.1;
    const mouse = screenToSvg(e.clientX, e.clientY, svg);
    const newScale = Math.max(0.4, Math.min(3, scale * dir));
    // adjust tx/ty to zoom on pointer
    tx = mouse.x - (mouse.x - tx) * (newScale/scale);
    ty = mouse.y - (mouse.y - ty) * (newScale/scale);
    scale = newScale;
    applyTransform();
  }, {passive:false});

  // Pan with middle mouse or shift+drag, with inertia
  let panning = false, panStart = null;
  let lastMoves = [];
  svg.addEventListener('mousedown', function(e){
    if(e.button === 1 || e.shiftKey){
      panning = true;
      panStart = {x: e.clientX, y: e.clientY, tx, ty};
      lastMoves = [{t:Date.now(), x:e.clientX, y:e.clientY}];
      e.preventDefault();
    }
  });
  window.addEventListener('mousemove', function(e){
    if(!panning) return;
    const now = Date.now();
    lastMoves.push({t: now, x: e.clientX, y: e.clientY});
    if(lastMoves.length > 6) lastMoves.shift();
    const dx = (e.clientX - panStart.x) / scale;
    const dy = (e.clientY - panStart.y) / scale;
    tx = panStart.tx + dx; ty = panStart.ty + dy;
    applyTransform();
  });
  window.addEventListener('mouseup', function(e){
    if(panning){
      // compute velocity
      if(lastMoves.length >= 2){
        const a = lastMoves[0];
        const b = lastMoves[lastMoves.length-1];
        const dt = (b.t - a.t) / 1000 || 0.001;
        const vx = (b.x - a.x) / dt / scale;
        const vy = (b.y - a.y) / dt / scale;
        applyInertia(vx, vy);
      }
    }
    panning = false; panStart = null; lastMoves = [];
  });

  function applyInertia(vx, vy){
    const friction = 0.92; // decay per frame
    let animVx = vx, animVy = vy;
    function step(){
      animVx *= friction; animVy *= friction;
      tx += animVx * (1/60); ty += animVy * (1/60);
      applyTransform();
      if(Math.abs(animVx) > 0.5 || Math.abs(animVy) > 0.5){
        requestAnimationFrame(step);
      }
    }
    requestAnimationFrame(step);
  }

  // Touch: single-finger pan or two-finger pinch-zoom
  let touchState = null;
  svg.addEventListener('touchstart', function(e){
    if(e.touches.length === 1){
      const t = e.touches[0];
      touchState = {mode:'pan', x:t.clientX, y:t.clientY, tx, ty};
    } else if(e.touches.length === 2){
      const a = e.touches[0], b = e.touches[1];
      const dx = b.clientX - a.clientX, dy = b.clientY - a.clientY;
      const dist = Math.hypot(dx,dy);
      const center = {x:(a.clientX+b.clientX)/2, y:(a.clientY+b.clientY)/2};
      touchState = {mode:'pinch', dist, center, scale, tx, ty};
    }
    e.preventDefault();
  }, {passive:false});

  svg.addEventListener('touchmove', function(e){
    if(!touchState) return;
    if(touchState.mode === 'pan' && e.touches.length===1){
      const t = e.touches[0];
      const dx = (t.clientX - touchState.x) / scale;
      const dy = (t.clientY - touchState.y) / scale;
      tx = touchState.tx + dx; ty = touchState.ty + dy;
      applyTransform();
    } else if(touchState.mode === 'pinch' && e.touches.length===2){
      const a = e.touches[0], b = e.touches[1];
      const dx = b.clientX - a.clientX, dy = b.clientY - a.clientY;
      const dist = Math.hypot(dx,dy);
      const newScale = Math.max(0.4, Math.min(3, touchState.scale * (dist / touchState.dist)));
      // zoom on center
      const center = {x:(a.clientX+b.clientX)/2, y:(a.clientY+b.clientY)/2};
      const mouse = screenToSvg(center.x, center.y, svg);
      tx = mouse.x - (mouse.x - touchState.tx) * (newScale / touchState.scale);
      ty = mouse.y - (mouse.y - touchState.ty) * (newScale / touchState.scale);
      scale = newScale; applyTransform();
    }
    e.preventDefault();
  }, {passive:false});

  svg.addEventListener('touchend', function(e){ touchState = null; }, {passive:false});

  // SVG namespace helper
  const NS = 'http://www.w3.org/2000/svg';
  function mk(tag, attrs, parent){
    const e = document.createElementNS(NS, tag);
    if(attrs) for(const [k,v] of Object.entries(attrs)) e.setAttribute(k, String(v));
    if(parent) parent.appendChild(e);
    return e;
  }
  function txt(str, attrs, parent){
    const t = mk('text', attrs, parent);
    t.textContent = str;
    return t;
  }

  // ─── Component-specific drawing functions ───

  function drawDesktopTower(g,x,y,w,h){
    mk('rect',{x,y,width:w,height:h,fill:'url(#gd)',stroke:'#666','stroke-width':1.5,rx:4,filter:'url(#shd)'},g);
    mk('rect',{x:x+3,y:y+3,width:w-6,height:h-6,fill:'none',stroke:'#4a4a4a',rx:2},g);
    // Optical drive bay
    mk('rect',{x:x+8,y:y+10,width:w-16,height:16,fill:'#1e1e1e',stroke:'#555',rx:1},g);
    mk('rect',{x:x+w-22,y:y+13,width:8,height:10,fill:'#333',stroke:'#555',rx:1},g);
    txt('5.25" Bay',{x:x+12,y:y+21,fill:'#888','font-size':'6'},g);
    // HDD bays
    for(let i=0;i<3;i++){
      const by=y+32+i*14;
      mk('rect',{x:x+8,y:by,width:w-16,height:10,fill:'#1a1a1a',stroke:'#404040',rx:1},g);
      mk('circle',{cx:x+14,cy:by+5,r:2,fill:i===0?'#33ff88':'#444'},g);
      txt('HDD '+(i+1),{x:x+20,y:by+8,fill:'#666','font-size':'5'},g);
    }
    // Power button
    const pbx=x+w/2, pby=y+82;
    mk('circle',{cx:pbx,cy:pby,r:10,fill:'#333',stroke:'#666','stroke-width':1.5},g);
    mk('circle',{cx:pbx,cy:pby,r:4,fill:'#00dd66',filter:'url(#glow)'},g);
    mk('line',{x1:pbx,y1:pby-5,x2:pbx,y2:pby-2,stroke:'#ccc','stroke-width':1.5,'stroke-linecap':'round'},g);
    // USB 3.0 ports
    txt('USB 3.0',{x:x+8,y:y+103,fill:'#4488ff','font-size':'6','font-weight':'bold'},g);
    mk('rect',{x:x+8,y:y+106,width:24,height:10,fill:'#0a0a0a',stroke:'#3377dd','stroke-width':1,rx:1},g);
    mk('rect',{x:x+36,y:y+106,width:24,height:10,fill:'#0a0a0a',stroke:'#3377dd','stroke-width':1,rx:1},g);
    // Audio jacks
    txt('Audio',{x:x+8,y:y+127,fill:'#888','font-size':'6'},g);
    mk('circle',{cx:x+14,cy:y+135,r:5,fill:'#0a0a0a',stroke:'#55cc55','stroke-width':1.5},g);
    mk('circle',{cx:x+30,cy:y+135,r:5,fill:'#0a0a0a',stroke:'#ff5577','stroke-width':1.5},g);
    txt('Out',{x:x+8,y:y+146,fill:'#55cc55','font-size':'5'},g);
    txt('Mic',{x:x+24,y:y+146,fill:'#ff5577','font-size':'5'},g);
    // Ventilation grille
    for(let i=0;i<6;i++){
      mk('line',{x1:x+8,y1:y+155+i*6,x2:x+w-8,y2:y+155+i*6,stroke:'#3a3a3a','stroke-width':1,'stroke-dasharray':'3,2'},g);
    }
    // Labels
    txt('DESKTOP TOWER',{x:x+w/2,y:y-5,fill:'#88aacc','font-size':'10','text-anchor':'middle','font-weight':'bold','letter-spacing':'1'},g);
    txt('Front Panel',{x:x+w/2,y:y+h+12,fill:'#556677','font-size':'8','text-anchor':'middle'},g);
  }

  function drawMotherboard(g,x,y,w,h){
    mk('rect',{x,y,width:w,height:h,fill:'url(#gm)',stroke:'#2a7a3a','stroke-width':1.5,rx:2,filter:'url(#shd)'},g);
    // PCB traces
    for(let i=0;i<9;i++) mk('line',{x1:x+15+i*32,y1:y,x2:x+15+i*32,y2:y+h,stroke:'#1a6a28','stroke-width':'0.3'},g);
    for(let i=0;i<7;i++) mk('line',{x1:x,y1:y+12+i*30,x2:x+w,y2:y+12+i*30,stroke:'#1a6a28','stroke-width':'0.3'},g);
    // CPU Socket
    const cpuX=x+30,cpuY=y+25;
    mk('rect',{x:cpuX,y:cpuY,width:55,height:45,fill:'#0e3b18',stroke:'#888','stroke-width':1.5},g);
    mk('rect',{x:cpuX+5,y:cpuY+5,width:45,height:35,fill:'#222',stroke:'#aaa',rx:1},g);
    for(let px=0;px<4;px++) for(let py=0;py<3;py++) mk('circle',{cx:cpuX+12+px*10,cy:cpuY+12+py*10,r:1.2,fill:'#c8a800'},g);
    txt('CPU Socket',{x:cpuX,y:cpuY-3,fill:'#88cc88','font-size':'7','font-weight':'bold'},g);
    txt('LGA 1700',{x:cpuX+5,y:cpuY+43,fill:'#7a7a7a','font-size':'5'},g);
    // Cooler mount holes
    mk('circle',{cx:cpuX-5,cy:cpuY-3,r:2,fill:'none',stroke:'#666'},g);
    mk('circle',{cx:cpuX+60,cy:cpuY-3,r:2,fill:'none',stroke:'#666'},g);
    mk('circle',{cx:cpuX-5,cy:cpuY+48,r:2,fill:'none',stroke:'#666'},g);
    mk('circle',{cx:cpuX+60,cy:cpuY+48,r:2,fill:'none',stroke:'#666'},g);
    // RAM slots
    const ramX=x+105,ramY=y+18;
    for(let i=0;i<4;i++){
      const sx=ramX+i*12;
      mk('rect',{x:sx,y:ramY,width:8,height:60,fill:'#111',stroke:i<2?'#4488ff':'#222','stroke-width':i<2?1:0.5,rx:1},g);
      mk('rect',{x:sx+2,y:ramY+26,width:4,height:3,fill:'#0e3b18'},g);
    }
    txt('DDR5 DIMM',{x:ramX,y:ramY-4,fill:'#88cc88','font-size':'7','font-weight':'bold'},g);
    // 24-pin ATX power
    const atxX=x+175,atxY=y+18;
    mk('rect',{x:atxX,y:atxY,width:22,height:48,fill:'#222',stroke:'#888',rx:1},g);
    for(let r=0;r<11;r++){mk('rect',{x:atxX+3,y:atxY+2+r*4,width:3,height:2.5,fill:'#c8a800'},g);mk('rect',{x:atxX+16,y:atxY+2+r*4,width:3,height:2.5,fill:'#c8a800'},g);}
    txt('24-pin ATX',{x:atxX-2,y:atxY-3,fill:'#cc8844','font-size':'6'},g);
    // SATA ports
    const sataX=x+30,sataY=y+100;
    for(let i=0;i<4;i++) mk('rect',{x:sataX+i*22,y:sataY,width:16,height:8,fill:'#111',stroke:'#cc3333','stroke-width':1,rx:1},g);
    txt('SATA III',{x:sataX,y:sataY-4,fill:'#cc8888','font-size':'7','font-weight':'bold'},g);
    txt('6 Gb/s',{x:sataX,y:sataY+16,fill:'#5a8a5a','font-size':'5'},g);
    // PCIe x16 slot
    const pciX=x+15,pciY=y+135;
    mk('rect',{x:pciX,y:pciY,width:130,height:10,fill:'#111',stroke:'#666',rx:1},g);
    mk('rect',{x:pciX+125,y:pciY-2,width:6,height:14,fill:'#888',rx:1},g);
    txt('PCIe x16 (GPU)',{x:pciX,y:pciY-3,fill:'#88cc88','font-size':'6'},g);
    // Chipset heatsink
    const chX=x+130,chY=y+120;
    mk('rect',{x:chX,y:chY,width:28,height:22,fill:'#555',stroke:'#777',rx:2},g);
    for(let f=0;f<5;f++) mk('line',{x1:chX+3+f*6,y1:chY+3,x2:chX+3+f*6,y2:chY+19,stroke:'#666','stroke-width':1},g);
    txt('Chipset',{x:chX,y:chY-3,fill:'#aaa','font-size':'5'},g);
    // I/O panel
    const ioX=x+w-38,ioY=y+5;
    mk('rect',{x:ioX,y:ioY,width:33,height:h-10,fill:'#2a2a2a',stroke:'#666',rx:1},g);
    mk('rect',{x:ioX+4,y:ioY+4,width:10,height:6,fill:'#111',stroke:'#4488ff'},g);
    mk('rect',{x:ioX+18,y:ioY+4,width:10,height:6,fill:'#111',stroke:'#4488ff'},g);
    mk('rect',{x:ioX+4,y:ioY+16,width:14,height:12,fill:'#111',stroke:'#ff8800'},g);
    mk('rect',{x:ioX+4,y:ioY+34,width:16,height:6,fill:'#111',stroke:'#888'},g);
    mk('circle',{cx:ioX+8,cy:ioY+50,r:3,fill:'#111',stroke:'#55cc55'},g);
    mk('circle',{cx:ioX+20,cy:ioY+50,r:3,fill:'#111',stroke:'#ff5577'},g);
    txt('I/O Panel',{x:ioX+2,y:ioY+72,fill:'#888','font-size':'5'},g);
    // BIOS battery
    mk('circle',{cx:x+180,cy:y+110,r:7,fill:'#888',stroke:'#aaa'},g);
    txt('CR2032',{x:x+174,y:y+124,fill:'#5a8a5a','font-size':'5'},g);
    // Labels
    txt('MOTHERBOARD',{x:x+w/2,y:y-5,fill:'#66cc66','font-size':'11','text-anchor':'middle','font-weight':'bold','letter-spacing':'1'},g);
    txt('ATX Form Factor',{x:x+w/2,y:y+h+12,fill:'#3a6a3a','font-size':'8','text-anchor':'middle'},g);
  }

  function drawServerRack(g,x,y,w,h){
    mk('rect',{x,y,width:w,height:h,fill:'url(#gs)',stroke:'#4a6070','stroke-width':2,rx:3,filter:'url(#shd)'},g);
    // Rack rails
    mk('rect',{x:x+2,y:y,width:8,height:h,fill:'#1a2530',stroke:'#3a5060'},g);
    mk('rect',{x:x+w-10,y:y,width:8,height:h,fill:'#1a2530',stroke:'#3a5060'},g);
    for(let sh=0;sh<8;sh++){mk('circle',{cx:x+6,cy:y+12+sh*25,r:2,fill:'#111',stroke:'#555'},g);mk('circle',{cx:x+w-6,cy:y+12+sh*25,r:2,fill:'#111',stroke:'#555'},g);}
    // Server 1 - 2U drive bays
    const s1y=y+8;
    mk('rect',{x:x+14,y:s1y,width:w-28,height:48,fill:'#1e2d3a',stroke:'#3a5868',rx:2},g);
    for(let d=0;d<4;d++){
      mk('rect',{x:x+18+d*28,y:s1y+5,width:24,height:26,fill:'#111',stroke:'#445',rx:1},g);
      mk('circle',{cx:x+30+d*28,cy:s1y+36,r:2,fill:d===0?'#33ff88':'#444'},g);
    }
    txt('Drive Bays (Hot-Swap)',{x:x+18,y:s1y+46,fill:'#5a8aaa','font-size':'6'},g);
    // Server 2 - NICs
    const s2y=y+62;
    mk('rect',{x:x+14,y:s2y,width:w-28,height:34,fill:'#1e2d3a',stroke:'#3a5868',rx:2},g);
    for(let n=0;n<4;n++){
      mk('rect',{x:x+20+n*26,y:s2y+6,width:20,height:14,fill:'#111',stroke:n===0?'#22aaff':'#445',rx:1},g);
      mk('circle',{cx:x+24+n*26,cy:s2y+24,r:1.5,fill:n<2?'#00ff66':'#444'},g);
    }
    txt('Network Interfaces',{x:x+18,y:s2y+5,fill:'#5a8aaa','font-size':'6'},g);
    // Management
    const s3y=y+103;
    mk('rect',{x:x+14,y:s3y,width:w-28,height:28,fill:'#1e2d3a',stroke:'#3a5868',rx:2},g);
    mk('rect',{x:x+20,y:s3y+6,width:16,height:12,fill:'#111',stroke:'#ffaa22',rx:1},g);
    txt('iLO/IPMI',{x:x+40,y:s3y+16,fill:'#aa8844','font-size':'7'},g);
    // PSU
    const psy=y+138;
    mk('rect',{x:x+14,y:psy,width:w-28,height:38,fill:'#222',stroke:'#555',rx:2},g);
    mk('circle',{cx:x+38,cy:psy+19,r:12,fill:'#1a1a1a',stroke:'#444'},g);
    mk('circle',{cx:x+38,cy:psy+19,r:6,fill:'#111',stroke:'#333'},g);
    for(let b=0;b<6;b++){const a=b*60*Math.PI/180;mk('line',{x1:x+38+Math.cos(a)*3,y1:psy+19+Math.sin(a)*3,x2:x+38+Math.cos(a)*10,y2:psy+19+Math.sin(a)*10,stroke:'#333','stroke-width':2},g);}
    txt('PSU 800W',{x:x+58,y:psy+22,fill:'#cc6644','font-size':'7'},g);
    mk('rect',{x:x+w-48,y:psy+8,width:28,height:18,fill:'#111',stroke:'#666',rx:2},g);
    txt('AC IN',{x:x+w-46,y:psy+20,fill:'#888','font-size':'6'},g);
    // Empty slots
    for(let e=0;e<1;e++){const ey=y+182+e*24;mk('rect',{x:x+14,y:ey,width:w-28,height:14,fill:'#151f28',stroke:'#2a3a48',rx:1,'stroke-dasharray':'4,2'},g);txt('Empty',{x:x+w/2,y:ey+10,fill:'#2a3a48','font-size':'6','text-anchor':'middle'},g);}
    // Title
    txt('SERVER RACK',{x:x+w/2,y:y-5,fill:'#66aadd','font-size':'11','text-anchor':'middle','font-weight':'bold','letter-spacing':'1'},g);
  }

  function drawNetworkSwitch(g,x,y,w,h){
    mk('rect',{x,y,width:w,height:h,fill:'url(#gw)',stroke:'#4a6070','stroke-width':1.5,rx:3,filter:'url(#shd)'},g);
    // Brand area
    mk('rect',{x:x+4,y:y+4,width:55,height:14,fill:'#28394a',rx:2},g);
    txt('48-Port',{x:x+8,y:y+14,fill:'#5588aa','font-size':'7','font-weight':'bold'},g);
    // Port rows
    const pW=12,pH=10,gap=3,startX=x+65;
    for(let p=0;p<16;p++){
      const px=startX+p*(pW+gap);
      mk('rect',{x:px,y:y+6,width:pW,height:pH,fill:'#0a0a0a',stroke:'#445',rx:1},g);
      mk('circle',{cx:px+pW/2,cy:y+4,r:1,fill:p<6?'#00ff66':'#333'},g);
      mk('rect',{x:px,y:y+22,width:pW,height:pH,fill:'#0a0a0a',stroke:'#445',rx:1},g);
      mk('circle',{cx:px+pW/2,cy:y+34,r:1,fill:'#333'},g);
    }
    // Port numbers
    for(let p=0;p<16;p+=4) txt(String(p+1),{x:startX+p*(pW+gap),y:y+46,fill:'#5a7a8a','font-size':'5'},g);
    // SFP uplinks
    const sfpX=x+w-50;
    mk('rect',{x:sfpX,y:y+6,width:18,height:10,fill:'#0a0a0a',stroke:'#ff8800',rx:1},g);
    mk('rect',{x:sfpX+22,y:y+6,width:18,height:10,fill:'#0a0a0a',stroke:'#ff8800',rx:1},g);
    txt('SFP+',{x:sfpX,y:y+28,fill:'#ff8800','font-size':'6'},g);
    // Console port
    mk('rect',{x:x+4,y:y+24,width:16,height:10,fill:'#111',stroke:'#22aaff',rx:1},g);
    txt('CON',{x:x+6,y:y+32,fill:'#2288aa','font-size':'5'},g);
    // Power LED
    mk('circle',{cx:x+8,cy:y+46,r:2,fill:'#00dd66'},g);
    txt('PWR',{x:x+13,y:y+49,fill:'#558866','font-size':'5'},g);
    // Title
    txt('NETWORK SWITCH',{x:x+w/2,y:y-5,fill:'#88aacc','font-size':'10','text-anchor':'middle','font-weight':'bold','letter-spacing':'1'},g);
  }

  function drawRouterDiag(g,x,y,w,h){
    mk('rect',{x,y,width:w,height:h,fill:'url(#gr)',stroke:'#99aabb','stroke-width':1.5,rx:6,filter:'url(#shd)'},g);
    // Antennas (inside top of component area)
    mk('rect',{x:x+40,y:y+4,width:4,height:30,fill:'#777',rx:2},g);
    mk('rect',{x:x+w-44,y:y+4,width:4,height:30,fill:'#777',rx:2},g);
    mk('circle',{cx:x+42,cy:y+3,r:3,fill:'#888'},g);
    mk('circle',{cx:x+w-42,cy:y+3,r:3,fill:'#888'},g);
    // Status LEDs
    const ledX=x+15;
    const leds=[{l:'PWR',c:'#00dd66'},{l:'WAN',c:'#ffaa00'},{l:'LAN',c:'#00aaff'},{l:'WiFi',c:'#00dd66'},{l:'SYS',c:'#ff6600'}];
    leds.forEach((led,i)=>{
      mk('circle',{cx:ledX+i*24,cy:y+45,r:3,fill:led.c,filter:'url(#glow)',opacity:0.8},g);
      txt(led.l,{x:ledX+i*24-6,y:y+56,fill:'#667','font-size':'5'},g);
    });
    // WAN port (yellow)
    const wanX=x+15,wanY=y+65;
    mk('rect',{x:wanX,y:wanY,width:28,height:20,fill:'#111',stroke:'#ffcc00','stroke-width':2,rx:2},g);
    txt('WAN',{x:wanX+3,y:wanY+14,fill:'#ffcc00','font-size':'8','font-weight':'bold'},g);
    // LAN ports (blue)
    for(let i=0;i<4;i++){
      const lx=x+55+i*30;
      mk('rect',{x:lx,y:wanY,width:26,height:20,fill:'#111',stroke:'#2288cc','stroke-width':1.5,rx:2},g);
      txt('LAN'+(i+1),{x:lx+2,y:wanY+14,fill:'#66aadd','font-size':'6'},g);
    }
    // USB port
    mk('rect',{x:x+w-40,y:wanY,width:18,height:12,fill:'#111',stroke:'#4488ff',rx:1},g);
    txt('USB',{x:x+w-38,y:wanY+10,fill:'#4488ff','font-size':'5'},g);
    // Reset
    mk('circle',{cx:x+w-15,cy:wanY+16,r:2,fill:'#666',stroke:'#888'},g);
    txt('RST',{x:x+w-22,y:wanY+26,fill:'#888','font-size':'4'},g);
    // Bottom brand bar
    mk('rect',{x:x+w/2-35,y:y+95,width:70,height:16,fill:'#bcc8d4',rx:4},g);
    txt('Wireless Router',{x:x+w/2,y:y+106,fill:'#556677','font-size':'8','text-anchor':'middle'},g);
    // Cable connections visual
    for(let i=0;i<3;i++){
      mk('line',{x1:x+24+i*30,y1:y+h-8,x2:x+24+i*30,y2:y+h+2,stroke:'#556','stroke-width':1.5,'stroke-linecap':'round'},g);
    }
    // Title
    txt('ROUTER',{x:x+w/2,y:y-5,fill:'#88aacc','font-size':'10','text-anchor':'middle','font-weight':'bold','letter-spacing':'1'},g);
  }

  // ─── Main render function ───
  function renderHotspots(){
    while(viewport.firstChild) viewport.removeChild(viewport.firstChild);

    // SVG defs: gradients, filters
    const defs = mk('defs',null,viewport);
    let gr;
    gr=mk('linearGradient',{id:'gd',x1:0,y1:0,x2:0,y2:1},defs);mk('stop',{offset:'0%','stop-color':'#4a4a4a'},gr);mk('stop',{offset:'100%','stop-color':'#2a2a2a'},gr);
    gr=mk('linearGradient',{id:'gm',x1:0,y1:0,x2:1,y2:1},defs);mk('stop',{offset:'0%','stop-color':'#1a5c2a'},gr);mk('stop',{offset:'100%','stop-color':'#0e3b18'},gr);
    gr=mk('linearGradient',{id:'gs',x1:0,y1:0,x2:0,y2:1},defs);mk('stop',{offset:'0%','stop-color':'#2c3e50'},gr);mk('stop',{offset:'100%','stop-color':'#1a252f'},gr);
    gr=mk('linearGradient',{id:'gw',x1:0,y1:0,x2:0,y2:1},defs);mk('stop',{offset:'0%','stop-color':'#34495e'},gr);mk('stop',{offset:'100%','stop-color':'#2c3e50'},gr);
    gr=mk('linearGradient',{id:'gr',x1:0,y1:0,x2:1,y2:0},defs);mk('stop',{offset:'0%','stop-color':'#e8f0f8'},gr);mk('stop',{offset:'100%','stop-color':'#d0dce8'},gr);
    // Glow filter
    let flt=mk('filter',{id:'glow'},defs);mk('feGaussianBlur',{stdDeviation:'2',result:'blur'},flt);const fm=mk('feMerge',null,flt);mk('feMergeNode',{in:'blur'},fm);mk('feMergeNode',{in:'SourceGraphic'},fm);
    // Shadow filter
    flt=mk('filter',{id:'shd',x:'-5%',y:'-5%',width:'110%',height:'110%'},defs);mk('feDropShadow',{dx:2,dy:3,stdDeviation:3,'flood-opacity':'0.4','flood-color':'#000'},flt);

    // Dark background
    mk('rect',{x:0,y:0,width:720,height:400,fill:'#0d1117',rx:4},viewport);
    // Subtle grid
    for(let gx=0;gx<720;gx+=30) mk('line',{x1:gx,y1:0,x2:gx,y2:400,stroke:'#161b22','stroke-width':'0.3'},viewport);
    for(let gy=0;gy<400;gy+=30) mk('line',{x1:0,y1:gy,x2:720,y2:gy,stroke:'#161b22','stroke-width':'0.3'},viewport);

    // Connection indicator lines between components
    mk('line',{x1:155,y1:120,x2:165,y2:120,stroke:'#1e4d6e','stroke-width':1.5,'stroke-dasharray':'4,3'},viewport);
    mk('line',{x1:450,y1:120,x2:460,y2:120,stroke:'#1e4d6e','stroke-width':1.5,'stroke-dasharray':'4,3'},viewport);
    mk('line',{x1:250,y1:220,x2:250,y2:232,stroke:'#1e4d6e','stroke-width':1.5,'stroke-dasharray':'4,3'},viewport);
    mk('line',{x1:580,y1:220,x2:580,y2:232,stroke:'#1e4d6e','stroke-width':1.5,'stroke-dasharray':'4,3'},viewport);

    components.forEach(c=>{
      const {x,y:cy,w,h}=c.svg;
      const cg=mk('g',{'data-comp':c.id},viewport);

      switch(c.id){
        case 'desktop_front':     drawDesktopTower(cg,x,cy,w,h);    break;
        case 'desktop_motherboard':drawMotherboard(cg,x,cy,w,h);    break;
        case 'server_rack':       drawServerRack(cg,x,cy,w,h);      break;
        case 'switch':            drawNetworkSwitch(cg,x,cy,w,h);   break;
        case 'router':            drawRouterDiag(cg,x,cy,w,h);      break;
        default:
          mk('rect',{x,y:cy,width:w,height:h,fill:'#333',stroke:'#666',rx:4,filter:'url(#shd)'},cg);
          txt(c.name,{x:x+w/2,y:cy-6,fill:'#aaa','font-size':'10','text-anchor':'middle'},cg);
      }

      // Transparent click-target overlay
      const ov=mk('rect',{x,y:cy,width:w,height:h,fill:'transparent',cursor:'pointer'},cg);
      ov.classList.add('hot');
      ov.dataset.name=c.name;
      ov.dataset.id=c.id;
      ov.addEventListener('click',()=>onHotClick(c));
      ov.addEventListener('mousemove',(ev)=>showTooltip(ev,c));
      ov.addEventListener('mouseleave',hideTooltip);

      // Connector endpoints with labels
      if(Array.isArray(c.connectors)){
        c.connectors.forEach(conn=>{
          mk('circle',{cx:conn.x,cy:conn.y,r:7,fill:'none',stroke:'rgba(0,200,255,0.25)','stroke-width':1},viewport);
          const dot=mk('circle',{cx:conn.x,cy:conn.y,r:4},viewport);
          dot.classList.add('connector');
          dot.dataset.connector=c.id+'.'+conn.id;
          dot.dataset.name=conn.name||conn.id;
          dot.addEventListener('mousemove',(ev)=>showTooltip(ev,{name:c.name+' \u2192 '+(conn.name||conn.id)}));
          dot.addEventListener('mouseleave',hideTooltip);
          txt(conn.id.replace(/_/g,' '),{x:conn.x+8,y:conn.y+3,fill:'#5a8ea8','font-size':'7','font-family':'Consolas,monospace'},viewport);
        });
      }
    });

    // Legend
    txt('Click any component for details  \u00b7  Shift+drag to pan  \u00b7  Scroll to zoom',{x:360,y:395,fill:'#2d3d4d','font-size':'9','text-anchor':'middle'},viewport);
  }

  function showTooltip(e, c){
    tooltip.style.display = 'block';
    tooltip.textContent = c.name || 'component';
    tooltip.style.left = (e.clientX + 12) + 'px';
    tooltip.style.top = (e.clientY + 12) + 'px';
  }
  function hideTooltip(){ tooltip.style.display='none'; }

  function onHotClick(c){
    infoName.textContent = c.name;
    infoDesc.textContent = c.desc || '';
    if(c.image){
      // inline SVG for richer interactivity when available
      const url = '/static/images/' + c.image;
      if(c.image.toLowerCase().endsWith('.svg')){
        fetch(url).then(r=>r.text()).then(svgText=>{
          compImage.innerHTML = svgText;
          compImage.style.display = 'block';
          // attach listeners to any .conn elements in inlined svg
          const inlined = compImage.querySelectorAll('.conn');
          inlined.forEach(el=>{
            el.addEventListener('mousemove', (ev)=> showTooltip(ev, {name: el.dataset.conn || el.getAttribute('data-conn')}));
            el.addEventListener('mouseleave', hideTooltip);
            el.addEventListener('click', ()=>{
              // on click, expose connector id to the user and add to review
              const id = el.dataset.conn || el.getAttribute('data-conn');
              infoDesc.textContent = (c.desc || '') + '\nConnector: ' + id;
            });
          });
        }).catch(()=>{ compImage.innerHTML = '<img src="'+url+'"/>'; compImage.style.display='block'; });
      } else {
        compImage.innerHTML = '<img src="'+url+'" style="max-width:100%"/>';
        compImage.style.display = 'block';
      }
    } else { compImage.style.display = 'none'; compImage.innerHTML = ''; }

    if(quizState){
      if(quizState.type === 'find'){
        if(c.id === quizState.question.component_id){
          quizFeedback.textContent = 'Correct!';
        } else {
          quizFeedback.textContent = 'Incorrect — ' + c.name;
        }
      }
    }
  }

  // Quiz flows
  function startQuiz(){
    // choose random question
    if(!questions || questions.length===0){ alert('No questions loaded'); return; }
    const q = questions[Math.floor(Math.random()*questions.length)];
    quizState = {type: q.type || 'find', question: q};
    quizPanel.classList.remove('hidden');
    quizFeedback.textContent = '';
    mcqChoices.innerHTML = '';
    wiringBoard.style.display = 'none';

    if(q.type === 'mcq'){
      quizPrompt.textContent = q.prompt || 'Choose the correct answer';
      q.choices.forEach((ch, i)=>{
        const btn = document.createElement('button'); btn.textContent = ch; btn.className='mcq-btn';
        btn.addEventListener('click', ()=>{
          if(i === q.answer){ quizFeedback.textContent = 'Correct'; }
          else { quizFeedback.textContent = 'Incorrect'; }
        });
        mcqChoices.appendChild(btn);
      });
    } else if(q.type === 'wiring'){
      quizPrompt.textContent = q.prompt || 'Connect the correct pins';
      wiringBoard.style.display = 'block';
      setupWiring(q);
    } else { // find-by-click
      quizPrompt.textContent = q.prompt || 'Find the highlighted component';
      // highlight target by storing component id in quizState.question.component_id
      // if question provides component_id use it, else pick random
      if(!q.component_id){ q.component_id = components[Math.floor(Math.random()*components.length)].id; }
      quizState.question = q;
    }
  }

  function setupWiring(q){
    // clear wiring svg
    while(wiringSvg.firstChild) wiringSvg.removeChild(wiringSvg.firstChild);
    // create map of connectors from components
    const connMap = {};
    components.forEach(c=>{
      if(!Array.isArray(c.connectors)) return;
      c.connectors.forEach(co=>{
        const id = c.id + '.' + co.id;
        connMap[id] = {x: co.x, y: co.y, name: co.name || id};
      });
    });

    // draw connectors involved in question
    const involved = new Set();
    (q.pairs||[]).forEach(p=>{ involved.add(p.from); involved.add(p.to); });
    Object.keys(connMap).forEach(id=>{
      if(!involved.has(id)) return;
      const c = connMap[id];
      const el = document.createElementNS('http://www.w3.org/2000/svg','circle');
      el.setAttribute('cx', c.x); el.setAttribute('cy', c.y); el.setAttribute('r',6);
      el.classList.add('w-connector'); el.dataset.conn = id;
      wiringSvg.appendChild(el);
      el.addEventListener('mousedown', wiringStart);
      el.addEventListener('mousemove', (ev)=> showTooltip(ev, {name: id}));
      el.addEventListener('mouseleave', hideTooltip);
    });

    // wiring drag state and multiple wires
    let wires = [];

    function wiringStart(e){
      e.preventDefault();
      const target = e.target;
      const fromConn = target.dataset.conn;
      const startPt = screenToSvg(e.clientX, e.clientY, wiringSvg);

      // create curved path
      const path = document.createElementNS('http://www.w3.org/2000/svg','path');
      path.setAttribute('d', `M ${startPt.x} ${startPt.y} Q ${(startPt.x+startPt.x)/2} ${(startPt.y+startPt.y)/2} ${startPt.x} ${startPt.y}`);
      path.setAttribute('stroke','#333'); path.setAttribute('stroke-width',2); path.setAttribute('fill','none');
      wiringSvg.appendChild(path);

      const connectorEls = Array.from(wiringSvg.querySelectorAll('.w-connector'));

      function nearestConnector(px, py){
        let best = null, bestDist = Infinity;
        connectorEls.forEach(el=>{
          const cx = parseFloat(el.getAttribute('cx'));
          const cy = parseFloat(el.getAttribute('cy'));
          const dx = px - cx, dy = py - cy;
          const d = Math.sqrt(dx*dx+dy*dy);
          if(d < bestDist){ bestDist = d; best = {el, cx, cy, id: el.dataset.conn, d}; }
        });
        return {best, bestDist};
      }

      function updatePath(x2,y2){
        const x1 = parseFloat(path.getAttribute('d').split(' ')[1]);
        const y1 = parseFloat(path.getAttribute('d').split(' ')[2]);
        const cx = (x1 + x2)/2;
        const cy = (y1 + y2)/2 - 20; // slight curve
        path.setAttribute('d', `M ${x1} ${y1} Q ${cx} ${cy} ${x2} ${y2}`);
      }

      function move(e){
        const p = screenToSvg(e.clientX, e.clientY, wiringSvg);
        // snap to nearest connector within threshold (15px)
        const {best, bestDist} = nearestConnector(p.x, p.y);
        if(best && bestDist < 15){
          updatePath(best.cx, best.cy);
        } else {
          updatePath(p.x, p.y);
        }
      }

      function up(ev){
        window.removeEventListener('mousemove', move);
        window.removeEventListener('mouseup', up);
        const p = screenToSvg(ev.clientX, ev.clientY, wiringSvg);
        const {best, bestDist} = nearestConnector(p.x, p.y);
        const toConn = (best && bestDist < 15) ? best.id : null;
        // validate
        const ok = (q.pairs||[]).some(p=> p.from === fromConn && p.to === toConn);

        if(ok){ path.setAttribute('stroke','#2a9d8f'); quizFeedback.textContent='Correct connection'; }
        else { path.setAttribute('stroke','#e63946'); quizFeedback.textContent='Incorrect connection'; }

        // keep the path to allow multiple wires
        wires.push({from: fromConn, to: toConn, ok, path});

        // persist attempt to backend
        fetch('/api/wiring_attempt', {method:'POST', headers:{'content-type':'application/json'}, body:JSON.stringify({question_id: q.id, from: fromConn, to: toConn, ok})})
          .then(r=>r.json()).then(res=>{ /* optionally update UI */ });

      }

      window.addEventListener('mousemove', move);
      window.addEventListener('mouseup', up);
    }
  }

  addReviewBtn.addEventListener('click', ()=>{
    const name = infoName.textContent;
    if(!name || name === 'Click a component') return;
    fetch('/api/review/add', {method:'POST', headers:{'content-type':'application/json'}, body:JSON.stringify({name})})
      .then(r=>r.json()).then(j=>{ reviewCountEl.textContent = 'Review: ' + (j.count||0); });
  });

  endQuizBtn.addEventListener('click', ()=>{ quizState = null; quizPanel.classList.add('hidden'); quizFeedback.textContent=''; });

  document.getElementById('start-quiz').addEventListener('click', startQuiz);
  showStudyBtn.addEventListener('click', ()=>{ studySection.classList.toggle('hidden'); });

  renderHotspots();
  applyTransform();
  // init editor UI
  initEditor();
});

// Editor functions
function initEditor(){
  const select = document.getElementById('component-select');
  const editor = document.getElementById('editor');
  const editorCanvas = document.getElementById('editor-canvas');
  const uploadBtn = document.getElementById('upload-btn');
  const uploadFile = document.getElementById('upload-file');
  const saveBtn = document.getElementById('save-connectors');
  const refreshBtn = document.getElementById('refresh-coords');
  const msg = document.getElementById('editor-msg');

  // populate select
  (window.COMPONENTS || []).forEach(c=>{
    const opt = document.createElement('option'); opt.value = c.id; opt.textContent = c.name; select.appendChild(opt);
  });

  select.addEventListener('change', ()=>{ loadEditorComponent(select.value); editor.classList.remove('hidden'); });

  uploadBtn.addEventListener('click', ()=>{
    const file = uploadFile.files[0];
    if(!file){ msg.textContent = 'Choose a file first'; return; }
    const fd = new FormData(); fd.append('file', file);
    fetch('/api/upload_image', {method:'POST', body: fd}).then(r=>r.json()).then(j=>{
      if(j.ok){ msg.textContent = 'Uploaded to static/images/' + j.path; }
      else msg.textContent = 'Upload error: ' + (j.error||'');
    });
  });

  saveBtn.addEventListener('click', ()=>{
    // collect connector positions from editorCanvas svg (elements with data-conn)
    const svg = editorCanvas.querySelector('svg');
    if(!svg){ msg.textContent = 'No SVG loaded'; return; }
    const compId = select.value;
    const connEls = svg.querySelectorAll('[data-conn]');
    const connectors = [];
    connEls.forEach(el=>{
      const id = (el.getAttribute('data-conn')||'').split('.').pop();
      const cx = parseFloat(el.getAttribute('cx') || (parseFloat(el.getAttribute('x')||0) + (parseFloat(el.getAttribute('width')||0)/2)) );
      const cy = parseFloat(el.getAttribute('cy') || (parseFloat(el.getAttribute('y')||0) + (parseFloat(el.getAttribute('height')||0)/2)) );
      // map from svg coords into main diagram coords using component svg box
      const comp = (window.COMPONENTS || []).find(c=>c.id===compId);
      if(!comp) return;
      const svgW = svg.viewBox.baseVal.width || parseFloat(svg.getAttribute('width')) || 1;
      const svgH = svg.viewBox.baseVal.height || parseFloat(svg.getAttribute('height')) || 1;
      const bx = comp.svg.x || 0; const by = comp.svg.y || 0; const bw = comp.svg.w || comp.svg.width || 100; const bh = comp.svg.h || comp.svg.height || 100;
      const sx = bx + (cx / svgW) * bw;
      const sy = by + (cy / svgH) * bh;
      connectors.push({id: id, x: Math.round(sx*10)/10, y: Math.round(sy*10)/10});
    });
    fetch('/api/components/save', {method:'POST', headers:{'content-type':'application/json'}, body:JSON.stringify({id: select.value, connectors})})
      .then(r=>r.json()).then(j=>{ if(j.ok) msg.textContent='Saved'; else msg.textContent='Save error'; });
  });

  refreshBtn.addEventListener('click', ()=>{
    msg.textContent = 'Refreshing...';
    fetch('/api/components/refresh', {method:'POST'}).then(r=>r.json()).then(j=>{ msg.textContent = 'Updated ' + (j.updated_components||0) + ' components'; window.location.reload(); });
  });
}

function loadEditorComponent(compId){
  const comp = (window.COMPONENTS || []).find(c=>c.id===compId);
  const editorCanvas = document.getElementById('editor-canvas');
  editorCanvas.innerHTML = '';
  if(!comp) return;
  if(!comp.image){ editorCanvas.textContent = 'No image for component'; return; }
  const url = '/static/images/' + comp.image;
  fetch(url).then(r=>r.text()).then(svgText=>{
    editorCanvas.innerHTML = svgText;
    const svg = editorCanvas.querySelector('svg');
    if(!svg) return;
    // make connectors draggable
    const connEls = svg.querySelectorAll('[data-conn]');
    connEls.forEach(el=>{
      makeConnectorDraggable(el, svg);
    });
  }).catch(()=>{ // fallback to image tag
    editorCanvas.innerHTML = '<img src="'+url+'" style="max-width:100%">';
  });
}

function makeConnectorDraggable(el, svg){
  el.style.cursor = 'move';
  let dragging = false;
  function down(e){ e.preventDefault(); dragging = true; }
  function move(e){ if(!dragging) return; const p = svg.createSVGPoint(); p.x = e.clientX; p.y = e.clientY; const c = p.matrixTransform(svg.getScreenCTM().inverse()); el.setAttribute('cx', c.x); el.setAttribute('cy', c.y); }
  function up(e){ dragging = false; }
  el.addEventListener('mousedown', down);
  window.addEventListener('mousemove', move);
  window.addEventListener('mouseup', up);
  // touch support
  el.addEventListener('touchstart', function(e){ e.preventDefault(); dragging = true; }, {passive:false});
  window.addEventListener('touchmove', function(ev){ if(!dragging) return; const t = ev.touches[0]; const p = svg.createSVGPoint(); p.x = t.clientX; p.y = t.clientY; const c = p.matrixTransform(svg.getScreenCTM().inverse()); el.setAttribute('cx', c.x); el.setAttribute('cy', c.y); }, {passive:false});
  window.addEventListener('touchend', function(){ dragging = false; }, {passive:false});
}

/* ALBAZ-NE V2.2 — GitHub Pages 3D boot fix
   UI/runtime only. Scientific equations and map calculations are untouched. */
(function(){
  let tries = 0;

  function emergencyGlobe(note){
    try{
      const canvas = document.getElementById('globeCanvas');
      const stage = document.getElementById('globeStage');
      if(!canvas || !stage) return;
      const dpr = window.devicePixelRatio || 1;
      const rect = stage.getBoundingClientRect();
      const w = Math.max(320, Math.round(rect.width || stage.clientWidth || 960));
      const h = Math.max(420, Math.round(window.innerWidth <= 760 ? 520 : 720));
      canvas.width = Math.round(w*dpr);
      canvas.height = Math.round(h*dpr);
      canvas.style.width = w+'px';
      canvas.style.height = h+'px';

      const ctx = canvas.getContext('2d');
      ctx.setTransform(dpr,0,0,dpr,0,0);
      ctx.clearRect(0,0,w,h);
      const bg = ctx.createLinearGradient(0,0,0,h);
      bg.addColorStop(0,'#061220');
      bg.addColorStop(1,'#081421');
      ctx.fillStyle = bg;
      ctx.fillRect(0,0,w,h);

      const cx=w/2, cy=h*.54, r=Math.min(w*.32,h*.30);
      const g=ctx.createRadialGradient(cx-r*.35,cy-r*.42,r*.15,cx,cy,r);
      g.addColorStop(0,'#55c3ff');
      g.addColorStop(.42,'#24699d');
      g.addColorStop(1,'#0b2036');
      ctx.beginPath();
      ctx.arc(cx,cy,r,0,Math.PI*2);
      ctx.fillStyle=g;
      ctx.fill();

      ctx.strokeStyle='rgba(255,255,255,.28)';
      ctx.lineWidth=1;
      for(let k=-2;k<=2;k++){
        ctx.beginPath();
        ctx.ellipse(cx,cy+k*r*.18,r*Math.sqrt(Math.max(.15,1-k*k*.032)),r*.12,0,0,Math.PI*2);
        ctx.stroke();
      }
      ctx.strokeStyle='rgba(255,224,145,.68)';
      ctx.lineWidth=2;
      ctx.beginPath();
      ctx.arc(cx,cy,r,0,Math.PI*2);
      ctx.stroke();

      ctx.fillStyle='#ffe6a5';
      ctx.font='bold 18px Tahoma,Arial,sans-serif';
      ctx.textAlign='center';
      ctx.fillText('ALBAZ-NE V2.2 3D Globe',cx,Math.max(28,cy-r-22));
      if(note){
        ctx.fillStyle='rgba(255,255,255,.78)';
        ctx.font='13px Tahoma,Arial,sans-serif';
        ctx.fillText('3D fallback active — reload once for the full basemap texture.',cx,cy+r+34);
      }
    }catch(_e){}
  }

  function forceBoot(){
    tries++;
    const stage=document.getElementById('globeStage');
    const canvas=document.getElementById('globeCanvas');
    if(!stage || !canvas){
      if(tries<12) setTimeout(forceBoot,120);
      return;
    }
    try{
      if(document.body){
        document.body.classList.add('sao-view-3d');
        document.body.classList.remove('sao-view-2d');
      }
      stage.style.display='block';
      const mapCanvas=document.getElementById('mapCanvas');
      if(mapCanvas) mapCanvas.style.display='none';

      if(typeof window.resizeGlobeCanvas==='function') window.resizeGlobeCanvas();
      if(typeof window.initGlobeInteraction==='function') window.initGlobeInteraction();

      requestAnimationFrame(function(){
        try{
          if(typeof window.renderGlobeScene==='function') window.renderGlobeScene();
          else emergencyGlobe(true);
        }catch(err){
          console.error('ALBAZ 3D render error:',err);
          emergencyGlobe(true);
        }
      });
    }catch(err){
      console.error('ALBAZ 3D boot error:',err);
      emergencyGlobe(true);
    }
  }

  if(document.readyState==='loading'){
    document.addEventListener('DOMContentLoaded',forceBoot,{once:true});
  }else{
    forceBoot();
  }

  window.addEventListener('load',function(){
    setTimeout(forceBoot,80);
    setTimeout(forceBoot,700);
  },{once:true});

  document.addEventListener('visibilitychange',function(){
    if(!document.hidden) setTimeout(forceBoot,60);
  });

  if('ResizeObserver' in window){
    const stage=document.getElementById('globeStage');
    if(stage){
      let timer=0;
      new ResizeObserver(function(){
        clearTimeout(timer);
        timer=setTimeout(function(){
          if(typeof window.CURRENT_VIEW_MODE==='undefined' || window.CURRENT_VIEW_MODE==='3d') forceBoot();
        },80);
      }).observe(stage);
    }
  }
})();
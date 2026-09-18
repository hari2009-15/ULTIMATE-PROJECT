import argparse, http.server, json, platform, secrets, subprocess, threading, webbrowser
TOKEN = secrets.token_urlsafe(16)
FIRED = False
ARGS = None
def power_off():
    s = platform.system()
    cmds = {
        "Windows": [["shutdown", "/s", "/t", "0"] + (["/f"] if ARGS.force else [])],
        "Darwin": [["osascript", "-e", 'tell application "System Events" to shut down']],
    }.get(s, [["systemctl", "poweroff"], ["shutdown", "-h", "now"]])
    for c in cmds:
        try:
            if subprocess.run(c).returncode == 0:
                return
        except FileNotFoundError:
            pass
class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass
    def host_ok(self):
        return self.headers.get("Host", "").split(":")[0] in ("127.0.0.1", "localhost")
    def do_GET(self):
        if self.path != "/" or not self.host_ok():
            return self.send_error(404)
        body = PAGE.replace("__TOKEN__", TOKEN).replace("__GRACE__", str(ARGS.grace)).encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def do_POST(self):
        global FIRED
        if self.path != "/shutdown" or not self.host_ok() or self.headers.get("X-Token") != TOKEN or FIRED:
            return self.send_error(403)
        FIRED = True
        body = json.dumps({"dry": ARGS.dry_run}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
        if not ARGS.dry_run:
            threading.Timer(0.2, power_off).start()
PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Verify you are human</title>
<style>
:root{--ply:#e2c9a0;--ply2:#cfae7c;--walnut:#4a2f1c;--brass:#b08d3c;--paper:#f6f1e6;--ink:#2a2118;--red:#c8322b;--ok:#3d7a4a}
*{box-sizing:border-box}
body{margin:0;min-height:100vh;display:grid;place-items:center;padding:16px;color:var(--ink);
 background:repeating-linear-gradient(90deg,var(--ply) 0 38px,var(--ply2) 38px 40px);
 font:16px/1.4 "Trebuchet MS",system-ui,sans-serif}
#card{width:min(100%,380px);background:var(--paper);border:3px solid var(--walnut);border-radius:6px;box-shadow:0 10px 0 var(--walnut)}
header{background:var(--walnut);color:#f6e7c1;padding:12px 16px;display:flex;justify-content:space-between;align-items:center}
h3{margin:0;font:700 19px Rockwell,"Roboto Slab",Georgia,serif}
#clock{font:700 22px Rockwell,Georgia,serif;color:#e9c46a;font-variant-numeric:tabular-nums}
#track{height:8px;background:#d9cdb2}#bar{height:100%;width:100%;background:var(--brass)}
#stage{padding:16px;min-height:290px}
#stage p{margin:0 0 12px}
footer{padding:10px 16px;border-top:2px solid #d9cdb2;font-size:13px}
#msg{color:var(--red);font-weight:700;min-height:20px;padding:0 16px}
button{font:inherit;padding:10px 16px;background:var(--walnut);color:#f6e7c1;border:0;border-radius:4px;cursor:pointer}
button:focus-visible,input:focus-visible{outline:3px solid var(--brass);outline-offset:2px}
input[type=text],#in{width:100%;font:700 20px Georgia,serif;letter-spacing:.3em;text-align:center;padding:8px;margin:10px 0;border:2px solid var(--walnut);border-radius:4px;background:#fff}
#in{text-transform:uppercase}#in::placeholder{letter-spacing:.05em;font-size:15px;font-weight:400;text-transform:none}
.row{display:flex;gap:8px}.ghost{background:transparent;color:var(--walnut);border:2px solid var(--walnut)}
canvas{width:100%;border:2px solid var(--walnut);border-radius:4px}
.chk{display:flex;align-items:center;gap:14px;border:2px solid var(--walnut);padding:18px;border-radius:4px;font-size:19px;cursor:pointer;background:#fff}
.chk input{width:30px;height:30px;accent-color:var(--walnut)}
.fine{font-size:14px;margin-top:14px}.warn{background:#f3d9a4;border-left:6px solid var(--red);padding:8px 10px;font-size:14px}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin-bottom:12px}
.t{aspect-ratio:1;font-size:36px;padding:0;background:#e8dcc0;border:3px solid transparent;transition:transform .12s}
.t.sel{border-color:var(--brass);transform:scale(.88);background:#f3d9a4}
input[type=range]{width:100%;accent-color:var(--walnut)}.val{font:700 34px Rockwell,Georgia,serif;text-align:center;margin:6px 0 12px}
.sw{position:relative;width:132px;height:64px;margin:34px auto;border:3px solid var(--walnut);border-radius:32px;background:#b9aa8d;cursor:pointer}
.sw i{position:absolute;top:4px;left:4px;width:50px;height:50px;border-radius:50%;background:var(--red);transition:left .25s,background .25s}
.sw.on i{left:70px;background:var(--ok)}
.hand{position:absolute;top:4px;left:100%;font-size:40px;line-height:1;opacity:0;transition:transform .35s,opacity .2s}
.hand.out{opacity:1;transform:translateX(-50px)}.hand.push{opacity:1;transform:translateX(-104px)}
.shake{animation:sh .35s}@keyframes sh{25%{transform:translateX(-8px)}75%{transform:translateX(8px)}}
#end{position:fixed;inset:0;z-index:100;background:#15100b;color:#f6e7c1;display:grid;align-content:center;justify-items:center;text-align:center;padding:24px;gap:10px}
#end h1{margin:0;font:700 clamp(28px,6vw,54px) Rockwell,Georgia,serif;color:#e9c46a}
#end h2{margin:0;font:400 clamp(20px,4vw,32px) Rockwell,Georgia,serif}
#end p{max-width:52ch;margin:0}#cd{font:700 96px Rockwell,Georgia,serif;color:var(--red)}
#bg{position:fixed;inset:0;width:100%;height:100%;z-index:0;pointer-events:none}
#card{position:relative;z-index:1}body{animation:pan 12s linear infinite}@keyframes pan{to{background-position:80px 0}}
#mute{position:fixed;top:12px;right:12px;z-index:1000;padding:8px 12px}
#cur{position:fixed;left:0;top:0;z-index:1001;pointer-events:none;opacity:0;font-size:32px;line-height:1}
#cur span{display:block;transition:transform .08s}#cur.dn span{transform:scale(.8) rotate(-14deg)}
body.fc,body.fc *{cursor:none!important}
.opts{display:grid;grid-template-columns:1fr 1fr;gap:8px}.o{background:#e8dcc0;color:var(--ink);border:2px solid var(--walnut);text-align:left;font-size:15px}
.stroop{font:700 44px Rockwell,Georgia,serif;text-align:center;margin:6px 0 14px}
.cnt{font-size:26px;line-height:1.3;letter-spacing:.1em;text-align:center;margin:6px 0 10px;word-break:break-all}
.rx{width:100%;height:110px;font-size:26px;background:var(--red)}.rx.g{background:var(--ok)}
.g4{grid-template-columns:repeat(4,1fr)}.g4 .t{font-size:28px}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
</style></head><body>
<canvas id="bg"></canvas><div id="cur"><span>👆</span></div><button id="mute" aria-label="Toggle music">🔊</button>
<main id="card">
 <header><h3>Verify you are human</h3><span id="clock">1:00</span></header>
 <div id="track"><div id="bar"></div></div>
 <div id="stage"></div><div id="msg"></div>
 <footer>Protected by Shannon&trade;. Passing this test really shuts down your computer.</footer>
</main>
<script>
const TOKEN="__TOKEN__",GRACE=__GRACE__,$=s=>document.querySelector(s),card=$('#card'),TOTAL=60000,BONUS=3000,shuf=a=>a.sort(()=>Math.random()-.5);
let deadline=0,stage=0,raf=0,done=false,speed=1,tempo=100,AC,mg,mtimer,muted=false,step=0,nextT=0;
const S=[s0,sCode,sGrid,sMath,sStroop,sSeq,sOdd,sCount,sTrivia,sScramble,sReact,sBig,sRev,sDial,sSwitch],next=()=>go(stage+1,1);
/* ---------- sound: generated live, no files ---------- */
const CH=[[110,[220,261.6,329.6]],[87.3,[174.6,220,261.6]],[130.8,[261.6,329.6,392]],[98,[196,246.9,293.7]]];
function note(f,t,d,type,v,dest){const o=AC.createOscillator(),g=AC.createGain();o.type=type;o.frequency.value=f;g.gain.setValueAtTime(v,t);g.gain.exponentialRampToValueAtTime(.001,t+d);o.connect(g);g.connect(dest||mg);o.start(t);o.stop(t+d)}
function sched(){const dur=30/tempo;while(nextT<AC.currentTime+.2){const c=CH[(step>>3)&3],i=step&7;
 if(i%4==0)note(c[0],nextT,dur*3.5,'triangle',.55);
 note(c[1][[0,1,2,1,0,1,2,1][i]]*(i==7?2:1),nextT,dur*.9,'square',.1);nextT+=dur;step++}}
function music(){const AX=window.AudioContext||window.webkitAudioContext;if(AC||!AX)return;AC=new AX();AC.resume();mg=AC.createGain();mg.gain.value=muted?0:.2;mg.connect(AC.destination);nextT=AC.currentTime+.1;mtimer=setInterval(sched,50)}
function blip(f,d,type){if(AC&&!muted)note(f,AC.currentTime,d||.1,type||'square',.15,AC.destination)}
function down(){clearInterval(mtimer);if(!AC||muted)return;const t=AC.currentTime,o=AC.createOscillator(),g=AC.createGain();o.type='sawtooth';o.frequency.setValueAtTime(900,t);o.frequency.exponentialRampToValueAtTime(30,t+.6);g.gain.setValueAtTime(.3,t);g.gain.linearRampToValueAtTime(0,t+.6);o.connect(g);g.connect(AC.destination);o.start(t);o.stop(t+.7)}
$('#mute').onclick=e=>{muted=!muted;e.target.textContent=muted?'🔇':'🔊';if(mg)mg.gain.value=muted?0:.2}
/* ---------- animated background: a field of Ultimate Machines flipping themselves ---------- */
const bg=$('#bg'),bx=bg.getContext('2d'),RM=matchMedia('(prefers-reduced-motion:reduce)').matches;let sws=[];
function rs(){bg.width=innerWidth;bg.height=innerHeight;sws=Array.from({length:Math.max(12,innerWidth/80|0)},()=>({x:Math.random()*bg.width,y:Math.random()*bg.height,s:20+Math.random()*28,v:.2+Math.random()*.6,k:0,p:Math.random()*9}))}
function draw(t){bx.clearRect(0,0,bg.width,bg.height);
 for(const o of sws){o.y-=o.v*speed;if(o.y<-60){o.y=bg.height+60;o.x=Math.random()*bg.width}
  const on=Math.sin(t/900+o.p)>0,w=o.s*2,h=o.s;o.k+=((on?1:0)-o.k)*.18;
  bx.fillStyle='rgba(74,47,28,.22)';bx.beginPath();(bx.roundRect||bx.rect).call(bx,o.x,o.y,w,h,h/2);bx.fill();
  bx.fillStyle=on?'rgba(61,122,74,.7)':'rgba(200,50,43,.7)';bx.beginPath();bx.arc(o.x+h/2+o.k*(w-h),o.y+h/2,h/2-3,0,7);bx.fill()}
 if(!RM)requestAnimationFrame(draw)}
addEventListener('resize',rs);rs();draw(0);
/* ---------- custom cursor: the finger ---------- */
if(matchMedia('(pointer:fine)').matches){document.body.classList.add('fc');const cu=$('#cur');
 addEventListener('mousemove',e=>{cu.style.transform=`translate(${e.clientX-16}px,${e.clientY-4}px)`;cu.style.opacity=1});
 addEventListener('mousedown',()=>cu.classList.add('dn'));addEventListener('mouseup',()=>cu.classList.remove('dn'))}
/* ---------- clock + flow ---------- */
function start(){deadline=performance.now()+TOTAL;tick()}
function tick(){const left=Math.max(0,deadline-performance.now()),s=Math.ceil(left/1000),f=1-left/TOTAL;
 $('#bar').style.width=left/TOTAL*100+'%';$('#clock').textContent=Math.floor(s/60)+':'+String(s%60).padStart(2,'0');
 tempo=100+f*80;speed=1+f*3;if(left<=0&&!done)return fail();raf=requestAnimationFrame(tick)}
function go(n,ok){if(ok){deadline=Math.min(deadline+BONUS,performance.now()+TOTAL);blip(880,.08)}stage=n;$('#stage').onclick=null;$('#msg').textContent='';S[n]()}
function wrong(m,keep){deadline-=5000;blip(120,.25,'sawtooth');if(!keep)go(stage);$('#msg').textContent=m+' Minus 5 seconds.';card.classList.remove('shake');void card.offsetWidth;card.classList.add('shake')}
function fail(){done=true;cancelAnimationFrame(raf);down();$('#msg').textContent='';
 $('#stage').innerHTML='<p><b>Robot detected.</b> Only a slow machine takes this long. You are not the Shannon Box yet.</p><button onclick="location.reload()">Try again</button>'}
/* ---------- question helpers ---------- */
function typed(q,ans,mode,pre,after){$('#stage').innerHTML=`<p>${q}</p>${pre||''}<input type="text" id="in" inputmode="${mode}" maxlength="12" autocomplete="off" autocapitalize="characters" spellcheck="false" placeholder="type here"><div class="row"><button id="ok">Verify</button></div>`;
 const i=$('#in'),ok=()=>i.value.trim().toUpperCase()===ans,chk=()=>ok()?next():(wrong('Nope. Same question, try again.',true),i.select());
 i.oninput=()=>{if(ok())next()};i.onkeydown=e=>{if(e.key==='Enter')chk()};$('#ok').onclick=chk;
 $('#stage').onclick=e=>{if(e.target.tagName!=='BUTTON')i.focus()};if(after)after();i.focus()}
function mcq(q,opts,ok,pre){$('#stage').innerHTML=`<p>${q}</p>${pre||''}<div class="opts">${opts.map((o,i)=>`<button class="o" data-i="${i}">${o}</button>`).join('')}</div>`;
 document.querySelectorAll('.o').forEach(b=>b.onclick=()=>+b.dataset.i===ok?next():wrong('Wrong answer.'))}
/* ---------- the tests ---------- */
function s0(){$('#stage').innerHTML=`<label class="chk"><input type="checkbox" id="c"> I'm not a robot</label>
 <p class="fine">You get one minute for ${S.length-1} quick tests. Right answers give +${BONUS/1000}s. Wrong answers cost 5s.</p>
 <div class="warn"><b>Warning:</b> if you pass, this computer will actually power off within ${GRACE} seconds. Save your work first. You can abort with Esc.</div>`;
 $('#c').onchange=e=>{e.target.disabled=true;music();blip(660,.1);start();setTimeout(()=>go(1),450)}}
function sCode(){const A='ABCDEFGHJKMNPQRSTUVWXYZ23456789';let code='';for(let i=0;i<5;i++)code+=A[Math.random()*A.length|0];
 typed('Type the 5 wobbly characters.',code,'text','<canvas id="cv" width="300" height="90"></canvas><button id="rf" class="ghost" type="button">New image</button>',()=>{
  const c=$('#cv').getContext('2d');c.fillStyle='#efe6d0';c.fillRect(0,0,300,90);
  for(let i=0;i<4;i++){c.strokeStyle=`hsla(${Math.random()*360},30%,45%,.45)`;c.beginPath();c.moveTo(0,Math.random()*90);c.bezierCurveTo(100,Math.random()*90,200,Math.random()*90,300,Math.random()*90);c.stroke()}
  [...code].forEach((ch,i)=>{c.save();c.translate(34+i*58,58+Math.random()*10-5);c.rotate(Math.random()*.6-.3);c.font=`bold ${42+(Math.random()*6|0)}px Georgia`;c.fillStyle='#2a2118';c.textAlign='center';c.fillText(ch,0,0);c.restore()});
  $('#rf').onclick=sCode})}
function sGrid(){const G={'something you can <b>turn off</b>':['💡','🔌','📺','🔦','📻','🎚️'],'an <b>animal</b>':['🐈','🐧','🐘','🐢','🦉','🦊'],'something you can <b>eat</b>':['🍕','🍎','🍩','🍔','🌮','🍇'],'a <b>vehicle</b>':['🚲','🚗','🚀','🚂','🛵','🚁'],'a <b>plant</b>':['🌵','🌻','🌲','🌷','🌴','🍀']};
 const ks=Object.keys(G),k=ks[Math.random()*ks.length|0],n=3+(Math.random()*2|0),neg=shuf(ks.filter(x=>x!==k).flatMap(x=>G[x]));
 const tiles=shuf([...shuf(G[k].slice()).slice(0,n).map(e=>[e,1]),...neg.slice(0,9-n).map(e=>[e,0])]);
 $('#stage').innerHTML=`<p>Select every square with ${k}.</p><div class="grid">${tiles.map(t=>`<button class="t">${t[0]}</button>`).join('')}</div><button id="ok">Verify</button>`;
 const bs=[...document.querySelectorAll('.t')];bs.forEach(b=>b.onclick=()=>b.classList.toggle('sel'));
 $('#ok').onclick=()=>bs.every((b,i)=>b.classList.contains('sel')==!!tiles[i][1])?next():wrong('Wrong squares.')}
function sMath(){const x=Math.random()<.5,r=()=>x?3+(Math.random()*7|0):10+(Math.random()*30|0),a=r(),b=r();typed(`Quick sum: <b>${a} ${x?'×':'+'} ${b}</b> = ?`,String(x?a*b:a+b),'numeric')}
function sRev(){const w=shuf(['ROBOT','SHANNON','SWITCH','BUTTON','HUMAN','MACHINE'])[0];typed(`Type <b>${w}</b> backwards.`,[...w].reverse().join(''),'text')}
function sStroop(){const C=[['RED','#c8322b'],['GREEN','#3d7a4a'],['BLUE','#2b5fc8'],['PURPLE','#7a3fa0']],p=shuf(C.slice()),o=shuf(C.map(c=>c[0]));
 mcq('Click the <b>ink color</b>, not the word.',o,o.indexOf(p[1][0]),`<div class="stroop" style="color:${p[1][1]}">${p[0][0]}</div>`)}
function sOdd(){const P=[['🙂','🙃'],['🔴','🟠'],['⬛','⬜'],['🌚','🌝']],[a,b]=shuf([...shuf(P.slice())[0]]),k=Math.random()*16|0;
 $('#stage').innerHTML=`<p>Click the one that is <b>different</b>.</p><div class="grid g4">${Array.from({length:16},(_,i)=>`<button class="t">${i===k?b:a}</button>`).join('')}</div>`;
 document.querySelectorAll('.t').forEach((t,i)=>t.onclick=()=>i===k?next():wrong('That one matches the others.'))}
function sTrivia(){const Q=[['Who built a machine whose only job is to turn itself off?','Claude Shannon','Claude Monet','Claude Debussy','Jean-Claude Van Damme'],
 ['What does an Ultimate Machine do when you switch it on?','Switches itself off','Makes toast','Calls your boss','Files a complaint'],
 ["Which unit did Shannon's 1948 paper make famous?",'The bit','The bagel','The bolt','The barrel'],
 ['Complete the classic IT advice: turn it off and back...','on','out','up','down'],
 ['Are you a robot?','No','Yes','Beep boop','Define robot'],
 ['How long is the countdown?','One minute','One year','One sandwich','One eternity'],
 ['What does a CAPTCHA try to tell apart?','Humans and computers','Cats and dogs','Tea and coffee','Left and right']],
 [q,c,...w]=shuf(Q.slice())[0],o=shuf([c,...w]);mcq(q,o,o.indexOf(c))}
function sSeq(){const a=2+(Math.random()*8|0),d=2+(Math.random()*6|0),g=Math.random()<.4,r=2+(Math.random()*2|0),
 q=Array.from({length:4},(_,i)=>g?a*r**i:a+d*i),n=g?a*r**4:a+d*4,o=shuf([n,n+1,n-1,n+2].map(String));
 mcq(`What comes next? <b>${q.join(', ')}, ?</b>`,o,o.indexOf(String(n)))}
function sCount(){const E=shuf(['🔌','💡','🌵','🍕']),T=E[0],n=3+(Math.random()*6|0),
 cells=shuf([...Array(n).fill(T),...Array.from({length:20-n},()=>E[1+(Math.random()*3|0)])]);
 typed(`How many <b>${T}</b> are there?`,String(n),'numeric',`<div class="cnt">${cells.join('')}</div>`)}
function sScramble(){const w=shuf(['SWITCH','ROBOT','SHANNON','BUTTON','HUMAN','MACHINE','SIGNAL','CIRCUIT'])[0];let x;do{x=shuf([...w]).join('')}while(x===w);
 typed(`Unscramble: <b>${x}</b>`,w,'text')}
function sReact(){$('#stage').innerHTML='<p>Wait for the light to turn <b>green</b>, then press it.</p><button id="rx" class="rx">Wait...</button>';
 const b=$('#rx');let on=false;setTimeout(()=>{if(b.isConnected){on=true;b.classList.add('g');b.textContent='NOW!'}},700+Math.random()*900);
 b.onclick=()=>on?next():wrong('Too early. Patience is a human virtue.')}
function sBig(){const v=[];while(v.length<5){const n=10+(Math.random()*990|0);if(!v.includes(n))v.push(n)}const m=Math.max(...v);
 $('#stage').innerHTML=`<p>Click the <b>largest</b> number.</p><div class="opts">${v.map(n=>`<button class="o" style="font-size:${14+(Math.random()*20|0)}px">${n}</button>`).join('')}</div>`;
 document.querySelectorAll('.o').forEach((b,i)=>b.onclick=()=>v[i]===m?next():wrong('That is not the largest.'))}
function sDial(){const t=10+(Math.random()*80|0);
 $('#stage').innerHTML=`<p>Turn the dial to exactly <b>${t}</b>. Arrow keys help.</p><input type="range" id="r" min="0" max="100" value="50"><div class="val" id="v">50</div><button id="ok">Verify</button>`;
 const r=$('#r'),chk=()=>+r.value===t?next():wrong('That is not '+t+'.');r.oninput=()=>$('#v').textContent=r.value;r.onkeydown=e=>{if(e.key==='Enter')chk()};r.focus();$('#ok').onclick=chk}
function sSwitch(){$('#stage').innerHTML='<p>Last one. Flip the switch to prove you are human.</p><div class="sw" id="sw" role="button" tabindex="0" aria-label="Flip switch"><i></i><span class="hand" id="hand">👈</span></div>';
 const sw=$('#sw'),h=$('#hand'),flip=()=>{if(sw.classList.contains('on'))return;done=true;cancelAnimationFrame(raf);sw.classList.add('on');blip(520,.1);
  setTimeout(()=>h.classList.add('out'),150);
  setTimeout(()=>{h.classList.remove('out');h.classList.add('push');sw.classList.remove('on')},450);
  setTimeout(reveal,950)};
 sw.onclick=flip;sw.onkeydown=e=>(e.key==='Enter'||e.key===' ')&&flip()}
/* ---------- the punchline ---------- */
function reveal(){down();const e=document.createElement('div');e.id='end';
 e.innerHTML=`<h1>Human confirmed.</h1><h2>Your computer is the Shannon Box.</h2><p>Claude Shannon built a machine whose only purpose was to switch itself off. You just made yours do the same.</p><div id="cd">${GRACE}</div><button id="ab">Abort. I have unsaved work. (Esc)</button>`;
 document.body.append(e);if(GRACE<=0)return poweroff();let n=GRACE;
 const ab=()=>{clearInterval(iv);location.reload()},iv=setInterval(()=>{n--;$('#cd').textContent=n;if(n<=0){clearInterval(iv);poweroff()}},1000);
 $('#ab').onclick=ab;addEventListener('keydown',ev=>{if(ev.key==='Escape'&&$('#ab'))ab()})}
async function poweroff(){const a=$('#ab');if(a)a.remove();$('#cd').textContent='👈';let m='Goodbye.';
 try{const r=await fetch('/shutdown',{method:'POST',headers:{'X-Token':TOKEN}}),j=await r.json();if(j.dry)m='Dry run: a real run would have powered off right here.'}
 catch(x){m='Could not reach the machine. It may already be off.'}
 $('#end p').textContent=m}
go(0);
</script></body></html>"""
def main():
    global ARGS
    p = argparse.ArgumentParser(description="The Shannon Box: a CAPTCHA that turns your PC off.")
    p.add_argument("--dry-run", action="store_true", help="play the whole game but skip the actual shutdown")
    p.add_argument("--grace", type=int, default=3, help="seconds to abort after winning (default 3, 0 = instant)")
    p.add_argument("--force", action="store_true", help="Windows only: force-close apps for an instant shutdown")
    ARGS = p.parse_args()
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
    url = f"http://127.0.0.1:{srv.server_address[1]}/"
    print(f"Shannon Box running at {url}" + ("  [DRY RUN]" if ARGS.dry_run else "  [LIVE: winning shuts down this PC]"))
    print("Ctrl+C to quit.")
    webbrowser.open(url)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
if __name__ == "__main__":
    main()

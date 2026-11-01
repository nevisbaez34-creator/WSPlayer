# pip install pywebview requests
import sys, os, re, secrets, mimetypes, threading, requests, webview
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import quote, urlparse

CDN = "https://cdn.jsdelivr.net/gh/nevisbaez34-creator/QPlay-mfull/qplay.mfull.js"

HTML = r"""<!DOCTYPE html><html><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<script src="/qplay.mfull.js"></script>
<style>
 *{box-sizing:border-box}
 html,body{margin:0;height:100%;background:#1c1c1c;color:#fff;font-family:Arial,sans-serif;font-size:13px;overflow:hidden}
 body{display:flex;flex-direction:column}
 #main{flex:1;display:flex;min-height:0}
 #stage{position:relative;flex:1;min-width:0;background:#000}
 #vid{position:absolute;inset:0}
 #toast{display:none;position:absolute;left:10px;bottom:10px;max-width:80%;padding:7px 10px;font-size:12px;z-index:5}
 #toast.ok{background:#1f5f2c}#toast.err{background:#7a1f1f}
 #side{width:290px;background:#242424;display:flex;flex-direction:column;border-left:1px solid #111}
 #side.hide{display:none}
 #tabs{display:flex}
 .tab{flex:1;background:#2c2c2c;padding:8px 2px;font-size:12px}
 .tab.on{background:#3a3a3a}
 .panel{display:none;padding:10px;overflow:auto;flex:1}
 .panel.on{display:block}
 #bar{padding:8px 10px;background:#1c1c1c}
 .row{display:flex;align-items:center;gap:6px;margin-top:6px}
 button{background:#333;color:#fff;border:0;padding:6px 10px;font-weight:bold;cursor:pointer;font-family:inherit;font-size:12px}
 button:hover{background:#444}
 button.act{background:#2d6cdf}
 button.rec{background:#b32020}
 input[type=text]{flex:1;background:#2b2b2b;color:#fff;border:0;padding:7px;min-width:60px}
 select{background:#2b2b2b;color:#fff;border:0;padding:5px}
 #seek{width:100%}
 #time{font-family:monospace;min-width:100px;text-align:center}
 #title{flex:1;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;color:#aaa}
 #vol{width:110px}
 ul{list-style:none;margin:8px 0;padding:0}
 li{padding:6px;cursor:pointer;border-bottom:1px solid #333;word-break:break-all}
 li:hover{background:#2f2f2f}li.cur{background:#2d6cdf}
 .eqrow,.set{display:flex;align-items:center;gap:6px;margin:8px 0}
 .eqrow span:first-child{width:52px}.eqrow input{flex:1}.eqrow span:last-child{width:46px;text-align:right}
 .tool{display:block;width:100%;margin:6px 0;text-align:left}
 hr{border:0;border-top:1px solid #333;margin:10px 0}
 small{color:#888}
</style></head><body>
<div id="main">
 <div id="stage"><div id="vid"></div><div id="toast"></div></div>
 <div id="side">
  <div id="tabs">
   <button class="tab on" data-p="p-list">Lista</button>
   <button class="tab" data-p="p-eq">EQ</button>
   <button class="tab" data-p="p-set">Ajustes</button>
   <button class="tab" data-p="p-tools">Herram.</button>
  </div>
  <div class="panel on" id="p-list">
   <div class="row" style="margin-top:0">
    <button id="bprev2">⏮</button><button id="bnext2">⏭</button>
    <button id="bshuf">🔀 Aleatorio</button><button id="brep">🔁 No repetir</button>
   </div>
   <ul id="list"></ul>
   <small id="cnt">Lista vacía</small>
   <div class="row"><button id="bclear">Vaciar lista</button></div>
  </div>
  <div class="panel" id="p-eq">
   <div id="eqbox"></div>
   <button id="eqreset">Restablecer</button>
   <p><small>El ecualizador y el volumen extra usan Web Audio: funcionan con archivos locales y enlaces con CORS.</small></p>
  </div>
  <div class="panel" id="p-set">
   <div class="set">Velocidad <input id="rate" type="range" min="0.25" max="4" step="0.05" value="1" style="flex:1">
    <span id="ratelbl">1.00x</span></div>
   <button id="ratereset">Velocidad 1x</button>
   <div class="set"><label><input type="checkbox" id="pitch"> Vincular tono y velocidad</label></div>
   <hr>
   <div class="set"><label><input type="checkbox" id="autoplay" checked> Reproducción automática</label></div>
   <div class="set"><label><input type="checkbox" id="loop"> Bucle (loop)</label></div>
   <div class="set">Ajuste de imagen
    <select id="fit"><option>contain</option><option>cover</option><option>fill</option><option>none</option><option>scale-down</option></select></div>
   <hr><small id="ver"></small>
  </div>
  <div class="panel" id="p-tools">
   <button class="tool" id="bsnap">📷 Captura (PNG)</button>
   <button class="tool" id="brec">⏺ Grabar</button>
   <button class="tool" id="bpip">🖼 Picture-in-Picture</button>
   <button class="tool" id="bfs">⛶ Pantalla completa</button>
   <hr>
   <button class="tool" id="bsub">💬 Subtítulo desde archivo</button>
   <div class="row"><input type="text" id="suburl" placeholder="URL de subtítulos (.vtt)">
    <input type="text" id="sublang" value="es" style="flex:0 0 36px"></div>
   <button class="tool" id="bsubu">💬 Añadir subtítulo por URL</button>
  </div>
 </div>
</div>
<div id="bar">
 <input id="seek" type="range" min="0" max="100" step="0.1" value="0">
 <div class="row">
  <button id="bprev">⏮</button><button id="brw">⏪10</button>
  <button id="bplay">▶</button>
  <button id="bfw">10⏩</button><button id="bnext">⏭</button>
  <span id="time">00:00 / 00:00</span>
  <span id="title"></span>
  <button id="bmute">🔊</button>
  <input id="vol" type="range" min="0" max="300" value="100" title="Volumen (hasta 300%)">
  <span id="vollbl" style="width:38px">100%</span>
  <button id="bside">☰</button>
 </div>
 <div class="row">
  <button id="bfile">📁 Cargar archivo</button>
  <input type="text" id="url" placeholder="Pega aquí el enlace...">
  <button id="blink">🔗 Cargar enlace</button>
  <button id="badd">＋ A la lista</button>
 </div>
</div>
<script>
const q = new QPlay('#vid', {autoplay:true, controls:false, crossOrigin:'anonymous', objectFit:'contain', loop:false});
const $ = id => document.getElementById(id);
const quiet = () => {};
const fmt = s => { s = isFinite(s) ? Math.max(0, Math.floor(s)) : 0;
  return String(Math.floor(s/60)).padStart(2,'0') + ':' + String(s%60).padStart(2,'0'); };
let dragging=false, dur=0, names=[], currentName='', toastT;
const eq=[0,0,0,0,0]; let wantRate=1, wantMuted=false;
$('ver').textContent = 'QPlay.js v' + QPlay.version;

function msg(t, ok){ const m=$('toast'); m.textContent=t; m.className=ok?'ok':'err'; m.style.display='block';
  clearTimeout(toastT); toastT=setTimeout(()=>m.style.display='none',5000); }
function labelFromUrl(u){ try{ const p=new URL(u).pathname.split('/').filter(Boolean).pop(); return decodeURIComponent(p||u);}catch(_){return u;} }
const isMedia = () => q.activeElement instanceof HTMLMediaElement;

// ---------- Volumen (0-300%) ----------
function applyVolume(){
  const v = $('vol').value/100;
  if (v <= 1) { q.setVolume(v); q.setExtraVolume(1); } else { q.setVolume(1); q.setExtraVolume(v); }
  $('vollbl').textContent = Math.round(v*100) + '%';
}
function nudgeVol(d){ const v=$('vol'); v.value=Math.max(0,Math.min(300,+v.value+d)); applyVolume(); }
$('vol').oninput = applyVolume;
$('bmute').onclick = () => {
  if (isMedia()) wantMuted = q.toggleMute(); else wantMuted = !wantMuted;
  $('bmute').textContent = wantMuted ? '🔇' : '🔊';
};

// QPlay crea un elemento nuevo en cada load: se reaplica el estado
function applyState(){
  if (!isMedia()) return;
  applyVolume();
  q.activeElement.muted = wantMuted;
  q.setPlaybackRate(wantRate);
  eq.forEach((g,i)=>q.setEQ(i,g));
}

// ---------- Reproducción ----------
function togglePlay(){ if(!isMedia()) return; if(q.activeElement.paused) Promise.resolve(q.play()).catch(quiet); else q.pause(); }
$('bplay').onclick = togglePlay;
$('brw').onclick = () => q.rewind(10);
$('bfw').onclick = () => q.forward(10);
$('bnext').onclick = $('bnext2').onclick = () => q.next().catch(quiet);
$('bprev').onclick = $('bprev2').onclick = () => q.previous().catch(quiet);

$('seek').addEventListener('input', () => { dragging = true; });
$('seek').addEventListener('change', e => { if (dur) q.seek(dur * parseFloat(e.target.value) / 100); dragging = false; });

// ---------- Eventos de QPlay ----------
q.on('play',  () => $('bplay').textContent = '⏸');
q.on('pause', () => $('bplay').textContent = '▶');
q.on('timeupdate', d => {
  dur = d.duration || 0;
  if (!dragging && dur) $('seek').value = d.progress;
  $('time').textContent = fmt(d.currentTime) + ' / ' + fmt(dur);
});
q.on('volumechange', d => $('bmute').textContent = d.muted ? '🔇' : '🔊');
q.on('ratechange', d => $('ratelbl').textContent = d.rate.toFixed(2) + 'x');
q.on('error', e => msg(e.message || 'Error de reproducción', false));
q.on('trackchange', () => {
  applyState(); renderList();
  $('title').textContent = (names[q.currentIndex] ?? currentName) || '';
  $('seek').value = 0; dur = 0;
});
q.on('recordingstart', () => { $('brec').textContent='⏹ Detener grabación'; $('brec').classList.add('rec'); });
q.on('recordingstop',  () => { $('brec').textContent='⏺ Grabar'; $('brec').classList.remove('rec'); });

// ---------- Cargar ----------
function loadSingle(u, name){
  q.playlist = []; q.currentIndex = -1; names = [];
  currentName = name || labelFromUrl(u);
  renderList(); q.load(u).catch(quiet);
}
$('bfile').onclick = async () => {
  const files = await window.pywebview.api.open_files();   // explorador, sin filtro
  if (!files || !files.length) return;
  if (files.length === 1) { loadSingle(files[0].url, files[0].name); return; }
  names = files.map(f => f.name); renderList();
  q.loadPlaylist(files.map(f => f.url), 0).catch(quiet);
};
function getLink(){ const u=$('url').value.trim(); if(!u) msg('Escribe o pega un enlace primero.', false); return u; }
$('blink').onclick = () => { const u=getLink(); if(u) loadSingle(u); };
$('url').addEventListener('keydown', e => { if (e.key==='Enter') $('blink').click(); });
$('badd').onclick = () => {
  const u=getLink(); if(!u) return;
  q.playlist.push(u); names.push(labelFromUrl(u)); renderList();
  if (!q.activeElement) q.playIndex(q.playlist.length-1).catch(quiet);
};

// ---------- Lista ----------
function renderList(){
  const ul=$('list'); ul.innerHTML='';
  names.forEach((n,i)=>{ const li=document.createElement('li'); li.textContent=(i+1)+'. '+n;
    if (i===q.currentIndex) li.className='cur'; li.onclick=()=>q.playIndex(i).catch(quiet); ul.appendChild(li); });
  $('cnt').textContent = names.length ? names.length + ' elementos' : 'Lista vacía';
}
$('bshuf').onclick = () => { const on=q.toggleShuffle(); $('bshuf').classList.toggle('act', on); };
$('brep').onclick = () => { const m=q.setRepeatMode();
  $('brep').textContent = '🔁 ' + ({off:'No repetir', all:'Todo', one:'Uno'}[m]); $('brep').classList.toggle('act', m!=='off'); };
$('bclear').onclick = () => { q.destroy(); q.playlist=[]; q.currentIndex=-1; names=[]; currentName=''; $('title').textContent=''; renderList(); };

// ---------- Ecualizador ----------
['60 Hz','230 Hz','910 Hz','3.6 kHz','14 kHz'].forEach((b,i)=>{
  const r=document.createElement('div'); r.className='eqrow';
  r.innerHTML=`<span>${b}</span><input type="range" min="-20" max="20" step="0.5" value="0" id="eq${i}"><span id="eqv${i}">0 dB</span>`;
  $('eqbox').appendChild(r);
  $('eq'+i).oninput = e => { eq[i]=parseFloat(e.target.value); q.setEQ(i,eq[i]); $('eqv'+i).textContent=eq[i]+' dB'; };
});
$('eqreset').onclick = () => eq.forEach((_,i)=>{ $('eq'+i).value=0; $('eq'+i).oninput({target:$('eq'+i)}); });

// ---------- Ajustes ----------
$('rate').oninput = e => { wantRate=parseFloat(e.target.value); q.setPlaybackRate(wantRate); $('ratelbl').textContent=wantRate.toFixed(2)+'x'; };
$('ratereset').onclick = () => { $('rate').value=1; $('rate').oninput({target:$('rate')}); };
$('pitch').onchange = e => q.linkPitchAndSpeed(e.target.checked);
$('autoplay').onchange = e => q.options.autoplay = e.target.checked;
$('loop').onchange = e => { q.options.loop=e.target.checked; if (isMedia()) q.activeElement.loop=e.target.checked; };
$('fit').onchange = e => { q.options.objectFit=e.target.value; if (q.activeElement) q.activeElement.style.objectFit=e.target.value; };

// ---------- Herramientas ----------
async function saveBlob(blob, name){
  const token = await window.pywebview.api.pick_save(name);
  if (!token) return;
  const r = await fetch('/save/' + token, {method:'POST', body:blob});
  msg(r.ok ? 'Guardado correctamente' : 'No se pudo guardar el archivo', r.ok);
}
$('bsnap').onclick = async () => {
  const b = await q.snapshot();
  if (b) saveBlob(b, 'captura.png'); else msg('No se pudo capturar (solo video/imagen y sin bloqueo CORS).', false);
};
$('brec').onclick = async () => {
  try {
    if (!q.isRecording) q.startRecording();
    else { const b = await q.stopRecording(); await saveBlob(b, 'grabacion.webm'); }
  } catch(e){ msg(e.message || String(e), false); }
};
$('bpip').onclick = async () => { const on = await q.togglePiP(); msg(on ? 'Picture-in-Picture activado' : 'PiP desactivado o no disponible', on); };
$('bfs').onclick = () => window.pywebview.api.toggle_fullscreen();
$('bsub').onclick = async () => {
  const s = await window.pywebview.api.pick_subtitle();
  if (!s) return;
  try { await q.loadLocalSubtitle(new File([s.text], s.name, {type:'text/plain'})); msg('Subtítulo cargado: ' + s.name, true); }
  catch(e){ msg(e.message || String(e), false); }
};
$('bsubu').onclick = () => {
  const u=$('suburl').value.trim(); if(!u) return msg('Pega la URL del subtítulo.', false);
  q.addSubtitleTrack(u, labelFromUrl(u), $('sublang').value.trim() || 'es');
};

// ---------- Interfaz ----------
document.querySelectorAll('.tab').forEach(t => t.onclick = () => {
  document.querySelectorAll('.tab,.panel').forEach(x => x.classList.remove('on'));
  t.classList.add('on'); $(t.dataset.p).classList.add('on');
});
$('bside').onclick = () => $('side').classList.toggle('hide');
document.addEventListener('click', e => { if (e.target.tagName==='BUTTON') e.target.blur(); });
document.querySelectorAll('input[type=range]').forEach(r => r.addEventListener('pointerup', () => setTimeout(()=>r.blur(),0)));
document.addEventListener('keydown', e => {
  const t=e.target; if (t.tagName==='INPUT' && t.type==='text') return;
  const k=e.key.toLowerCase(); let h=true;
  if (k===' ') togglePlay();
  else if (k==='arrowright') q.forward(10);
  else if (k==='arrowleft') q.rewind(10);
  else if (k==='arrowup') nudgeVol(5);
  else if (k==='arrowdown') nudgeVol(-5);
  else if (k==='m') $('bmute').click();
  else if (k==='f') $('bfs').click();
  else if (k==='n') q.next().catch(quiet);
  else if (k==='p') q.previous().catch(quiet);
  else h=false;
  if (h) e.preventDefault();
});
</script></body></html>"""


class Server(BaseHTTPRequestHandler):
    js = ""
    media = {}   # id -> ruta de archivo local
    saves = {}   # token -> ruta de destino (un solo uso)

    @classmethod
    def load_cdn(cls):
        try:
            res = requests.get(CDN, timeout=15)
            res.raise_for_status()
            cls.js = res.text
        except Exception as e:
            sys.exit(f"No se pudo descargar QPlay desde el CDN: {e}")

    def cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, HEAD, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")

    def send_bytes(self, ctype, data):
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.cors()
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(data)

    def do_OPTIONS(self):
        self.send_response(204)
        self.cors()
        self.end_headers()

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        path = urlparse(self.path).path
        try:
            if path == "/qplay.mfull.js":
                self.send_bytes("application/javascript; charset=utf-8", self.js.encode("utf-8"))
            elif path in ("/", "/index.html"):
                self.send_bytes("text/html; charset=utf-8", HTML.encode("utf-8"))
            elif path.startswith("/media/"):
                parts = path.split("/")  # ['', 'media', id, nombre]
                fp = Server.media.get(parts[2]) if len(parts) >= 3 else None
                if fp and os.path.isfile(fp):
                    self.serve_media(fp)
                else:
                    self.send_error(404)
            else:
                self.send_error(404)
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass

    def do_POST(self):
        m = re.match(r"^/save/([A-Za-z0-9_-]+)$", urlparse(self.path).path)
        dest = Server.saves.pop(m.group(1), None) if m else None
        if not dest:
            self.send_error(403)
            return
        try:
            left = int(self.headers.get("Content-Length", 0))
            with open(dest, "wb") as f:
                while left > 0:
                    chunk = self.rfile.read(min(65536, left))
                    if not chunk:
                        break
                    f.write(chunk)
                    left -= len(chunk)
            self.send_bytes("text/plain", b"ok")
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError):
            pass

    def serve_media(self, fp):
        size = os.path.getsize(fp)
        start, end = 0, size - 1
        rng = self.headers.get("Range")
        partial = False
        if rng:
            m = re.match(r"bytes=(\d*)-(\d*)", rng)
            if m:
                s, e = m.groups()
                if s == "" and e:
                    start = max(size - int(e), 0)
                elif s:
                    start = int(s)
                    if e:
                        end = min(int(e), size - 1)
                partial = True
        if start > end or start >= size:
            self.send_response(416)
            self.send_header("Content-Range", f"bytes */{size}")
            self.end_headers()
            return
        length = end - start + 1
        self.send_response(206 if partial else 200)
        self.send_header("Content-Type", mimetypes.guess_type(fp)[0] or "application/octet-stream")
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(length))
        if partial:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.cors()
        self.end_headers()
        if self.command == "HEAD":
            return
        with open(fp, "rb") as f:
            f.seek(start)
            left = length
            while left > 0:
                chunk = f.read(min(65536, left))
                if not chunk:
                    break
                self.wfile.write(chunk)
                left -= len(chunk)

    def log_message(self, *args):
        pass


def _dlg(kind):
    fd = getattr(webview, "FileDialog", None)
    return getattr(fd, kind) if fd else getattr(webview, kind + "_DIALOG")


def _ass_time(s):
    h, m, rest = s.strip().split(":")
    sec, _, cs = rest.partition(".")
    return f"{int(h):02d}:{m}:{sec}.{cs.ljust(3, '0')[:3]}"


def ass_to_vtt(text):
    cols, in_ev, out = None, False, ["WEBVTT", ""]
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("["):
            in_ev = s.lower() == "[events]"
            continue
        if not in_ev:
            continue
        low = s.lower()
        if low.startswith("format:"):
            cols = [c.strip().lower() for c in s[7:].split(",")]
        elif low.startswith("dialogue:") and cols:
            parts = s[9:].lstrip().split(",", len(cols) - 1)
            try:
                st = _ass_time(parts[cols.index("start")])
                en = _ass_time(parts[cols.index("end")])
                txt = re.sub(r"\{[^}]*\}", "", parts[cols.index("text")])
                txt = txt.replace("\\N", "\n").replace("\\n", "\n")
            except (ValueError, IndexError):
                continue
            out += [f"{st} --> {en}", txt, ""]
    return "\n".join(out)


class API:
    def __init__(self, port):
        self.port = port

    def open_files(self):
        res = webview.windows[0].create_file_dialog(_dlg("OPEN"), allow_multiple=True)  # sin filtro
        out = []
        for p in res or []:
            fid = secrets.token_hex(6)
            Server.media[fid] = p
            name = os.path.basename(p)
            out.append({"name": name, "url": f"http://127.0.0.1:{self.port}/media/{fid}/{quote(name)}"})
        return out

    def pick_subtitle(self):
        res = webview.windows[0].create_file_dialog(
            _dlg("OPEN"),
            file_types=("Subtítulos (*.vtt;*.srt;*.ass;*.ssa;*.sub)", "Todos los archivos (*.*)"))
        if not res:
            return None
        p = res[0]
        raw = open(p, "rb").read()
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = raw.decode("cp1252", errors="replace")
        name = os.path.basename(p)
        if name.lower().endswith((".ass", ".ssa")):
            text = ass_to_vtt(text)
            name = os.path.splitext(name)[0] + ".vtt"
        return {"name": name, "text": text}

    def pick_save(self, suggested="archivo"):
        res = webview.windows[0].create_file_dialog(_dlg("SAVE"), save_filename=suggested)
        if not res:
            return None
        path = res[0] if isinstance(res, (list, tuple)) else res
        token = secrets.token_urlsafe(12)
        Server.saves[token] = path
        return token

    def toggle_fullscreen(self):
        webview.windows[0].toggle_fullscreen()


if __name__ == "__main__":
    Server.load_cdn()
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), Server)  # puerto libre
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()

    webview.create_window("WSPlayer", url=f"http://127.0.0.1:{port}/",
                          js_api=API(port), width=1000, height=650,
                          min_size=(720, 500), background_color="#000000")
    webview.start()  # en el hilo principal

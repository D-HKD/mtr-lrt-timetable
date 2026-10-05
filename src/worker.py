from workers import WorkerEntrypoint, Response
from urllib.parse import urlparse
import json

LR_STATIONS = [
    {"name": "輕鐵｜天水圍站", "type": "lr", "id": 1027},
    {"name": "輕鐵｜天榮站", "type": "lr", "id": 1017},
    {"name": "輕鐵｜豐年路站", "type": "lr", "id": 1044},
    {"name": "輕鐵｜元朗站", "type": "lr", "id": 1045},
]
TML_STATIONS = [
    {"name": "屯馬綫｜屯門站", "type": "tml", "code": "TUM"},
    {"name": "屯馬綫｜天水圍站", "type": "tml", "code": "TIS"},
    {"name": "屯馬綫｜朗屏站", "type": "tml", "code": "LOP"},
    {"name": "屯馬綫｜元朗站", "type": "tml", "code": "YUL"},
]
ALL_STATIONS = LR_STATIONS + TML_STATIONS

HTML = """
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>輕鐵｜屯馬綫 到站預報</title>
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
<meta http-equiv="Pragma" content="no-cache"/>
<meta http-equiv="Expires" content="0"/>
<style>
:root {
    --mtr-red: #9D232B;
    --bg: #f4f5f7;
    --card: #ffffff;
    --text: #222222;
    --text-secondary: #606060;
    --border: #e2e2e2;
}
.dark-mode {
    --bg: #111111;
    --card: #1f1f1f;
    --text: #eeeeee;
    --text-secondary: #aaaaaa;
    --border: #333333;
}
*{box-sizing:border-box;margin:0;padding:0;font-family: -apple-system, BlinkMacSystemFont, "Noto Sans HK", sans-serif;}
body{background:var(--bg);color:var(--text);padding:14px;max-width:720px;margin:0 auto;transition: 0.25s background,0.25s color;}
header{
    background:var(--mtr-red);
    color:white;
    padding:14px 16px;
    border-radius:12px;
    margin-bottom:14px;
}
.header-top{
    display:flex;
    justify-content:space-between;
    align-items:center;
    flex-wrap:wrap;
    gap:10px;
}
.header-title{font-size:20px;font-weight:bold;}
.header-info{font-size:13px;opacity:0.9;margin-top:4px;}
.ctrl-bar{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px;}
button{
    background:rgba(255,255,255,0.22);
    color:white;
    border:0;
    padding:6px 10px;
    border-radius:8px;
    font-size:14px;
    cursor:pointer;
}
button:active{background:rgba(255,255,255,0.35);}
.station-card{
    background:var(--card);
    border:1px solid var(--border);
    border-radius:12px;
    padding:16px;
    margin-bottom:12px;
}
.station-name{
    color:var(--mtr-red);
    font-size:18px;
    font-weight:bold;
    margin-bottom:10px;
}
.train-item{
    padding:5px 0;
    font-size:16px;
}
.no-data{color:var(--text-secondary);}
</style>
</head>
<body>
<header>
    <div class="header-top">
        <div>
            <div class="header-title">輕鐵｜屯馬綫 到站預報</div>
            <div class="header-info">自動更新｜每30秒</div>
        </div>
        <div class="ctrl-bar">
            <button onclick="renderPage()">手動重新整理</button>
            <button onclick="toggleDark()">切換深色模式</button>
            <button onclick="toggleSound()">提示音效：關</button>
        </div>
    </div>
</header>
<div id="stationList"></div>

<script>
const stations = %s;
let soundOn = localStorage.getItem("sound") === "1";
let dark = localStorage.getItem("dark") === "1";
const container = document.getElementById("stationList");
const soundBtn = document.querySelector('button[onclick="toggleSound()"]');

if(dark) document.body.classList.add("dark-mode");
updateSoundBtn();

function toggleDark(){
    document.body.classList.toggle("dark-mode");
    localStorage.setItem("dark", document.body.classList.contains("dark-mode") ? "1":"0");
}
function toggleSound(){
    soundOn = !soundOn;
    localStorage.setItem("sound", soundOn?"1":"0");
    updateSoundBtn();
}
function updateSoundBtn(){
    soundBtn.innerText = `提示音效：${soundOn ? "開":"關"}`;
}
function playBeep(){
    if(!soundOn) return;
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.connect(gain);gain.connect(audioCtx.destination);
    osc.frequency.value=880;gain.gain.value=0.1;
    osc.start();osc.stop(audioCtx.currentTime+0.15);
}

async function getData(){
    try {
        const res = await fetch("/api/get");
        return await res.json();
    } catch(e) {
        console.error("API錯誤",e);
        return {};
    }
}
async function renderPage(){
    const data = await getData();
    let html = "";
    for(const s of stations){
        const info = data[s.name] || {trains:[]};
        html += `<div class="station-card">
            <div class="station-name">${s.name}</div>`;
        if(info.trains.length>0){
            for(const t of info.trains){
                html += `<div class="train-item">${t.dest}：${t.time}</div>`;
            }
            playBeep();
        }else{
            html += `<div class="no-data">暫無到站資料（可能已收車）</div>`;
        }
        html += `</div>`;
    }
    container.innerHTML = html;
}

renderPage();
setInterval(renderPage,30000);
</script>
</body>
</html>
"""

async def fetch_etd(station):
    if station["type"] == "lr":
        url = f"https://api.mtr.com.hk/opendata/lightrail/v1/station/{station['id']}/etd"
    else:
        url = f"https://api.mtr.com.hk/opendata/tml/v1/station/{station['code']}/etd"
    headers = {"User-Agent":"Mozilla/5.0"}
    resp = await fetch(url, headers=headers)
    if not resp.ok:
        return {"trains":[]}
    j = await resp.json()
    trains = []
    for item in j.get("etds",[]):
        trains.append({"dest":item["dest"], "time":f"{item['time']} 分鐘"})
    return {"trains":trains}

class Handler(WorkerEntrypoint):
    async def on_fetch(self, req):
        path = urlparse(req.url).path
        if path == "/api/get":
            out = {}
            for s in ALL_STATIONS:
                out[s["name"]] = await fetch_etd(s)
            return Response(json.dumps(out), headers={"Content-Type":"application/json;charset=utf-8"})
        else:
            page = HTML % json.dumps(ALL_STATIONS)
            return Response(page, headers={
                "Content-Type":"text/html;charset=utf-8",
                "Cache-Control": "no-cache, no-store, must-revalidate"
            })

def main():
    return Handler()

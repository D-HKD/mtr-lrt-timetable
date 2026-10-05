from workers import WorkerEntrypoint, Response
import json

# 車站清單（你原本揀嗰啲）
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

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>港鐵輕鐵/屯馬綫到站預報</title>
<style>
/* MTR主色 + 深色模式設定 */
:root {
    --mtr-red: #9D232B;
    --bg: #ffffff;
    --card-bg: #ffffff;
    --text: #222222;
    --text-light: #666666;
    --border: #e5e7eb;
}
@media (prefers-color-scheme: dark) {
    :root {
        --bg: #121212;
        --card-bg: #1e1e1e;
        --text: #f0f0f0;
        --text-light: #aaaaaa;
        --border: #333333;
    }
}
*{box-sizing:border-box;margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;}
body{background:var(--bg);color:var(--text);padding:16px;max-width:700px;margin:0 auto;transition:background 0.3s,color 0.3s;}
header{margin-bottom:20px;}
h1{color:var(--mtr-red);font-size:22px;font-weight:700;}
.subtitle{color:var(--text-light);font-size:14px;margin-top:4px;}
.station-card{
    background:var(--card-bg);
    border:1px solid var(--border);
    border-radius:12px;
    padding:18px;
    margin-bottom:14px;
    box-shadow:0 2px 6px rgba(0,0,0,0.06);
}
.station-title{
    color:var(--mtr-red);
    font-size:18px;
    font-weight:bold;
    margin-bottom:10px;
}
.arrival-item{
    padding:6px 0;
    font-size:16px;
    color:var(--text);
}
.nodata{color:var(--text-light);}
#loading{display:none;}
/* 防閃：只更新內容，唔成頁重刷 */
</style>
</head>
<body>
<header>
    <h1>港鐵到站預報</h1>
    <div class="subtitle">天水圍 / 天榮 / 豐年路 / 元朗｜屯馬綫屯門、天水圍、朗屏、元朗</div>
</header>
<div id="container"></div>
<script>
const stations = %s;
const container = document.getElementById("container");

async function fetchData() {
    const res = await fetch("/api/data");
    return await res.json();
}
async function render() {
    const data = await fetchData();
    let html = "";
    for(const s of stations) {
        const stationData = data[s.name];
        html += `<div class="station-card">
            <div class="station-title">${s.name}</div>`;
        if(stationData && stationData.trains && stationData.trains.length>0) {
            for(const t of stationData.trains) {
                html += `<div class="arrival-item">${t.dest}：${t.time}</div>`;
            }
        } else {
            html += `<div class="nodata">暫無到站資料（可能已收車）</div>`;
        }
        html += `</div>`;
    }
    container.innerHTML = html;
}
// 每30秒更新，唔會成頁閃
render();
setInterval(render, 30000);
</script>
</body>
</html>
"""

async def fetch_mtr_data(station):
    station_type = station["type"]
    if station_type == "lr":
        url = f"https://api.mtr.com.hk/opendata/lightrail/v1/station/{station['id']}/etd"
    else:
        url = f"https://api.mtr.com.hk/opendata/tml/v1/station/{station['code']}/etd"
    headers = {"User-Agent":"Mozilla/5.0 (HK MTR ETD Client)"}
    resp = await fetch(url, headers=headers)
    if not resp.ok:
        return {"trains":[]}
    j = await resp.json()
    trains = []
    if station_type == "lr":
        for entry in j.get("etds",[]):
            trains.append({"dest":entry["dest"], "time":f"{entry['time']} 分鐘"})
    else:
        for entry in j.get("etds",[]):
            trains.append({"dest":entry["dest"], "time":f"{entry['time']} 分鐘"})
    return {"trains":trains}

class Handler(WorkerEntrypoint):
    async def on_fetch(self, request):
        path = urlparse(request.url).path
        if path == "/api/data":
            result = {}
            for s in ALL_STATIONS:
                result[s["name"]] = await fetch_mtr_data(s)
            return Response(json.dumps(result), headers={"Content-Type":"application/json"})
        else:
            page = HTML_TEMPLATE % json.dumps(ALL_STATIONS)
            return Response(page, headers={"Content-Type":"text/html;charset=utf-8"})

def main():
    return Handler()

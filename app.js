// 👉 呢度要改！換成你部署完 Cloudflare Worker 個URL
const WORKER_URL = "https://mtr-lrt-proxy.xxx.workers.dev";

// 車站對照
const TML_STATIONS = [
    {code:"TUM", name:"屯門"},
    {code:"TIS", name:"天水圍"},
    {code:"LOP", name:"朗屏"},
    {code:"YUL", name:"元朗"},
];
const LRT_STATIONS = [
    {code:"LR1027", name:"天水圍站"},
    {code:"LR1017", name:"天榮站"},
    {code:"LR1044", name:"豐年路站"},
    {code:"LR1045", name:"元朗站"},
];

function updateClock(){
    const now = new Date();
    document.getElementById("pageTime").textContent = now.toLocaleTimeString("zh-HK");
}

async function fetchAll(){
    try{
        const res = await fetch(WORKER_URL);
        const raw = await res.json();
        renderTML(raw);
        renderLRT(raw);
    }catch(e){
        console.error(e);
    }
}

// 渲染屯馬綫
function renderTML(data){
    let html = "";
    TML_STATIONS.forEach(s=>{
        const d = data[s.code];
        html += `<div class="station-block">
            <div class="station-name">${s.name} <small>${s.code}</small></div>`;
        if(d && d.status === 1 && d.schedule?.length>0){
            d.schedule.forEach(item=>{
                html += `
                <div class="train-row">
                    <div class="train-left">
                        <div class="dest">往 ${item.dest_ch}</div>
                    </div>
                    <div class="train-min">${item.time_ch}</div>
                </div>`
            })
        }else{
            html += `<div class="train-row"><div>暫無班次</div></div>`
        }
        html += "</div>"
    })
    document.getElementById("tmlPanel").innerHTML = html;
}

// 渲染輕鐵
function renderLRT(data){
    let html = "";
    LRT_STATIONS.forEach(s=>{
        const d = data[s.code];
        html += `<div class="station-block">
            <div class="station-name">${s.name} <small>${s.code.replace("LR","")}</small></div>`;
        if(d && d.status ===1 && d.platform_list?.length>0){
            d.platform_list.forEach(plat=>{
                plat.route_list.forEach(rt=>{
                    html += `
                    <div class="train-row">
                        <div class="train-left">
                            <div class="route-tag">${rt.route_no}</div>
                            <div>
                                <div class="dest">${rt.dest_ch}</div>
                                <div class="platform">月台${plat.platform}</div>
                            </div>
                        </div>
                        <div class="train-min">${rt.time_ch}</div>
                    </div>`
                })
            })
        }else{
            html += `<div class="train-row"><div>暫無班次</div></div>`
        }
        html += "</div>"
    })
    document.getElementById("lrtPanel").innerHTML = html;
}

// 每30秒自動刷新
fetchAll();
updateClock();
setInterval(fetchAll,30000);
setInterval(updateClock,1000);

// ========= 改呢度！呢個係你嘅Cloudflare Worker網址 =========
const PROXY_BASE = "https://mtr-proxy.idyl-2014061.workers.dev";
// =====================================================

// 車站清單（你指定嘅全部站）
const STATIONS = [
  {name:"輕鐵｜天水圍站", api:"https://rt.data.gov.hk/v1/transport/mtr/lrt/getSchedule?station_id=1027"},
  {name:"輕鐵｜天榮站", api:"https://rt.data.gov.hk/v1/transport/mtr/lrt/getSchedule?station_id=1017"},
  {name:"輕鐵｜豐年路站", api:"https://rt.data.gov.hk/v1/transport/mtr/lrt/getSchedule?station_id=1044"},
  {name:"輕鐵｜元朗站", api:"https://rt.data.gov.hk/v1/transport/mtr/lrt/getSchedule?station_id=1045"},
  {name:"屯馬綫｜屯門站", api:"https://rt.data.gov.hk/v1/transport/mtr/mtr/getSchedule?line=TML&station=TUM"},
  {name:"屯馬綫｜天水圍站", api:"https://rt.data.gov.hk/v1/transport/mtr/mtr/getSchedule?line=TML&station=TIS"},
  {name:"屯馬綫｜朗屏站", api:"https://rt.data.gov.hk/v1/transport/mtr/mtr/getSchedule?line=TML&station=LOP"},
  {name:"屯馬綫｜元朗站", api:"https://rt.data.gov.hk/v1/transport/mtr/mtr/getSchedule?line=TML&station=YUL"},
];

const stationSel = document.getElementById("stationSel");
const resultBox = document.getElementById("resultBox");
const refreshBtn = document.getElementById("refreshBtn");
document.getElementById("proxyUrl").textContent = PROXY_BASE;

// 填入下拉選單
STATIONS.forEach((s,idx)=>{
  const opt = document.createElement("option");
  opt.value = idx;
  opt.textContent = s.name;
  stationSel.appendChild(opt);
});

async function loadTimetable(){
  resultBox.innerHTML = `<div class="loading">載入實時班次⋯</div>`;
  const selIdx = stationSel.value;
  const station = STATIONS[selIdx];
  const targetUrl = encodeURIComponent(station.api);
  const fetchUrl = `${PROXY_BASE}?target=${targetUrl}`;
  try{
    const res = await fetch(fetchUrl);
    const data = await res.json();
    renderResult(station.name, data, station.type);
  }catch(e){
    resultBox.innerHTML = `<div class="error">讀取失敗：${e.message}<br>檢查Worker網址同API狀態</div>`;
  }
}

// 渲染班次，自動分開輕鐵 / 屯馬綫兩種API格式
function renderResult(stationName, data, type){
  let html = `<div class="station-title">${stationName}</div>`;

  // 輕鐵處理（用route）
  if(stationName.includes("輕鐵")){
    if (!data || !data.route || data.route.length === 0) {
      html += `<div>暫時冇班次資料</div>`;
      resultBox.innerHTML = html;
      return;
    }
    data.route.forEach(routeItem => {
      const routeNo = routeItem.route_no;
      const dest = routeItem.dest;
      if(routeItem.arrival && routeItem.arrival.length>0){
        routeItem.arrival.forEach(arr =>{
          const time = arr.time;
          html += `
          <div class="train-item">
            <div class="train-dir">${routeNo}號線｜往：${dest}</div>
            <div class="train-time">到站：${time}</div>
          </div>`;
        })
      }
    })
  }
  // 屯馬綫處理（用schedule）
  else{
    if(!data || !data.schedule || data.schedule.length ===0){
      html += `<div>暫時冇班次資料</div>`;
      resultBox.innerHTML = html;
      return;
    }
    data.schedule.forEach(item=>{
      const dest = item.dest || item.destination;
      const time = item.time;
      html += `
      <div class="train-item">
        <div class="train-dir">往：${dest}</div>
        <div class="train-time">到站：${time}</div>
      </div>`;
    })
  }

  resultBox.innerHTML = html;
}

stationSel.addEventListener("change", loadTimetable);
refreshBtn.addEventListener("click", loadTimetable);
// 開頁自動載入
loadTimetable();

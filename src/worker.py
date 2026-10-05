from workers import WorkerEntrypoint, Response
import json

# 港鐵API清單
MTR_API_LIST = {
    "TUM": "https://rt.data.gov.hk/v1/transport/mtr/mtr/getSchedule?line=TML&station=TUM",
    "TIS": "https://rt.data.gov.hk/v1/transport/mtr/mtr/getSchedule?line=TML&station=TIS",
    "LOP": "https://rt.data.gov.hk/v1/transport/mtr/mtr/getSchedule?line=TML&station=LOP",
    "YUL": "https://rt.data.gov.hk/v1/transport/mtr/mtr/getSchedule?line=TML&station=TML&station=YUL",
    "LR1027": "https://rt.data.gov.hk/v1/transport/mtr/lrt/getSchedule?station_id=1027",
    "LR1017": "https://rt.data.gov.hk/v1/transport/mtr/lrt/getSchedule?station_id=1017",
    "LR1044": "https://rt.data.gov.hk/v1/transport/mtr/lrt/getSchedule?station_id=1044",
    "LR1045": "https://rt.data.gov.hk/v1/transport/mtr/lrt/getSchedule?station_id=1045",
}

class Handler(WorkerEntrypoint):
    async def on_fetch(self, request):
        # CORS Header
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,OPTIONS",
            "Cache-Control": "no-store, no-cache, must-revalidate",
            "Content-Type": "application/json;charset=utf-8"
        }
        if request.method == "OPTIONS":
            return Response("", headers=headers)

        # 一次攞晒全部車站資料
        result = {}
        for key, url in MTR_API_LIST.items():
            resp = await fetch(url)
            data = await resp.json()
            result[key] = data

        return Response(json.dumps(result, ensure_ascii=False), headers=headers)

export default Handler

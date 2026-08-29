import asyncio
import time
import httpx
from typing import Dict, List, Union

async def check_ip_gen204(ip: str, port: int = 443, host_header: str = "www.google.com", timeout: float = 3.0) -> Dict[str, Union[str, float, bool]]:
    start_time = time.perf_counter()
    transport = httpx.AsyncHTTPTransport(verify=False)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Host": host_header
    }

    url = f"https://{ip}:{port}/gen_204" if port != 443 else f"https://{ip}/gen_204"

    try:
        async with httpx.AsyncClient(transport=transport, timeout=timeout, headers=headers) as client:
            response = await client.get(url)
            latency = (time.perf_counter() - start_time) * 1000
            
            if response.status_code == 204:
                return {"ip": ip, "working": True, "latency": round(latency, 2), "status": 204}
            else:
                return {"ip": ip, "working": False, "latency": round(latency, 2), "status": response.status_code}
    except Exception as e:
        return {"ip": ip, "working": False, "latency": -1, "error": str(type(e).__name__)}

async def bulk_test_ips(ip_list: List[str], max_concurrent: int = 50) -> List[Dict]:
    semaphore = asyncio.Semaphore(max_concurrent)

    async def sem_check(ip):
        async with semaphore:
            return await check_ip_gen204(ip)

    tasks = [sem_check(ip) for ip in ip_list]
    return await asyncio.gather(*tasks)

import asyncio
import random
from typing import Any, Union

from aiolimiter import AsyncLimiter
import aiohttp

requests_per_second = 45
limiter = AsyncLimiter(requests_per_second + 1, 1.0185)


async def request(method, url, headers, json=None, return_json=False):
    async with limiter:
        resp = await method(url, headers=headers, json=json)
        if return_json and resp.status in [200, 201, 204]:
            return await resp.json()
        if resp.status == 429:
            resp_json = await resp.json()
            retry_after = float(resp_json.get("retry_after", 0))
            print(f"Rate limited. Sleeping {retry_after}s")
            if 0 < retry_after < 15:
                await asyncio.sleep(retry_after)
                return await request(method, url, headers, json, return_json)
        if resp.status in [200, 201, 204]:
            return None
        text = await resp.text()
        raise Exception(f"HTTP {resp.status}: {text}")


async def _wait_for_tasks_end():
    amount = requests_per_second
    if requests_per_second >= 50:
        amount -= 10
    while not limiter.has_capacity(amount):
        await asyncio.sleep(0.001)


async def create_tasks(
    urls: list[str],
    method,
    headers: dict,
    json: Union[dict, list[dict]] = None,
    return_json: bool = False,
):
    if not urls:
        return []

    random.shuffle(urls)
    json_list = json if isinstance(json, list) else [json] * len(urls)

    tasks = []
    for i in range(0, len(urls), requests_per_second):
        chunk_urls = urls[i : requests_per_second + i]
        chunk_jsons = json_list[i : requests_per_second + i]
        for url, req_json in zip(chunk_urls, chunk_jsons):
            tasks.append(
                asyncio.create_task(
                    request(method, url, headers, req_json, return_json)
                )
            )
        await asyncio.sleep(0.25)
        await _wait_for_tasks_end()

    return await asyncio.gather(*tasks, return_exceptions=True)

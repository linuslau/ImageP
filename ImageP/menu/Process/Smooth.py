import asyncio

async def menu_click_async():
    # 异步操作，比如等待一定时间
    print("Call await asyncio.sleep(5)")
    await asyncio.sleep(5)
    print("Async menu click handled")


async def handle_click_async():
    # 异步操作，比如异步I/O
    await asyncio.sleep(1)
    print("Async handle click processed")

def menu_click():
    print("Sync menu click handled")

def handle_click():
    print("Sync handle click processed")
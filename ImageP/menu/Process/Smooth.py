import asyncio
import time

def menu_click():
    print("Sync menu click handled")

def handle_click():
    print("Sync handle click processed")

async def menu_click_async():
    # 异步操作，比如等待一定时间
    print("Call await asyncio.sleep(5)")
    await asyncio.sleep(5)
    print("Async menu click handled")

async def handle_click_async():
    # 异步操作，比如异步I/O
    await asyncio.sleep(1)
    print("handle_click_async processed")

def menu_click_thread():
    # 模拟异步操作，通过线程睡眠来代替asyncio
	print("Call time.sleep(5)")
	time.sleep(5)
	print("menu_click_thread processed")

def handle_click_thread():
    # 模拟异步操作，通过线程睡眠来代替
    time.sleep(1)
    print("handle_click_thread processed")


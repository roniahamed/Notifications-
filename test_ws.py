import asyncio
import websockets


async def test():
    try:
        async with websockets.connect(
            "ws://localhost:8003/ws/notifications/"
        ) as websocket:
            print("Connected!")
    except Exception as e:
        print(f"Failed: {e}")


asyncio.run(test())

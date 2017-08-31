import asyncio
import random
import websockets
from cpu import CPU
import json

cpu = CPU()
choices = 'sit ead there here '.split()
async def test(websocket, path):
    while True:
        await websocket.send(json.dumps(dict(data=cpu.get_info())))
        await asyncio.sleep(2)

start_server= websockets.serve(test, '0.0.0.0', 5000)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

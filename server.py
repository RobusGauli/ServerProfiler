import asyncio
import random
import websockets
from cpu import CPU
import json
import functools
cpu = CPU()
choices = 'sit ead there here '.split()
import logging
logger = logging.getLogger('websockets.server')
logger.setLevel(logging.ERROR)
logger.addHandler(logging.StreamHandler())

#a global dictionnary of path and its function
producer = {}

def register(path):
    def _decs(func):
        #register the function
        global producer
        producer[path] = func
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return _decs

@register('/cpu')
def get_cpu_info():
    return dict(data=cpu.get_info())

@register('/cpumeta')
def get_cpu_meta():
    _data = {
        'os_name': cpu.os_name,
        'l_num_cores': cpu.l_num_cores,
        'p_num_cores': cpu.p_num_cores
    }
    
    return dict(data=_data)

async def producer_handler(websocket, path):
    
    while True:
        result = producer.get(path)()
        await websocket.send(json.dumps(result))
        await asyncio.sleep(2)

start_server= websockets.serve(producer_handler, '0.0.0.0', 5000)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

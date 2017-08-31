import asyncio
import random
import websockets
import json
import functools
import itertools

from serverprofiler.cpu import CPU
from serverprofiler.memory import Memory
from serverprofiler.process import Process

from aiohttp import web
from sanic import Sanic
from sanic.response import text

app = Sanic(__name__)

@app.route('/')
async def test(request):
    return text('adasdfdfd')



cpu = CPU()
memory = Memory()
process = Process()


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


@register('/processes')
def get_processes_info():
    return dict(data=list(itertools.islice(process.all_user_processes(), 20)))

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

@register('/memory')
def get_memory_info():
    _data = {
        'total': str(memory.total) + ' MB',
        'available': str(memory.available) + ' MB',
        'use_percentage': str(memory.use_percentage) + ' %',
        'health': memory.health
    }
    return dict(data=_data)


async def producer_handler(websocket, path):
    
    while True:
        result = producer.get(path)()
        await websocket.send(json.dumps(result))
        await asyncio.sleep(1)

start_server = websockets.serve(producer_handler, '0.0.0.0', 5000)
sanic_server = app.create_server('0.0.0.0', port=8000)
task = asyncio.ensure_future(sanic_server)
asyncio.get_event_loop().run_until_complete(asyncio.gather(start_server, task))
asyncio.get_event_loop().run_forever()

import json
import websockets
import asyncio

class SlaveServer(object):
    '''This acts as a slave node in the cluster, whose job is to send the data to the master node.'''

    def __init__(self, config):
        self.config = config
    
    
    async def producer_handler(self):

        async with websockets.connect('ws://%s/' % self.config.get('PROFILER_REGISTER_TO')) as websocket:
            print('Connected to server node %s at port %d' % (websocket.host, websocket.port))
            while True:
                try:
                    id = self.config.get('PROFILER_REGISTER_AS', 'Unknown')
                    await websocket.send('{"id": "%s", "data": "sample data from %s"}' % (id, id))
                    await asyncio.sleep(0.5)
                    
                except websockets.exceptions.ConnectionClosed:
                    print('Connection closed by the parent')
                    #if the connection is closed by the client
                    break
                    #again goes to eh outer loop and starts the connection again
                except Exception:
                    raise
                    print('Connection lost')
                    break

import json
import websockets
import asyncio

from serverprofiler.node import Node

class SlaveServer(object):
    '''This acts as a slave node in the cluster, whose job is to send the data to the master node.'''

    def __init__(self, config):
        self.config = config
        self.node = None
    
    
    async def producer_handler(self):
        '''This will send the data to the master node. This information will be the slave information'''
        
        if self.config.get('PROFILER_REGISTER_AS') == 'client':
            extra_headers = [('mode', 'receiver')]
        else:
            self.node = Node(self.config.get('PROFILER_REGISTER_AS'))
            extra_headers = [('mode', 'sender')]
        while True:
            async with websockets.connect('ws://%s/' % self.config.get('PROFILER_REGISTER_TO'), extra_headers=extra_headers) as websocket:
                print('Connected to server node %s at port %d' % (websocket.host, websocket.port))
                while True:
                    try:
                        id = self.config.get('PROFILER_REGISTER_AS', 'Unknown')
                        if id == 'client':
                            message = await websocket.recv()
                            print(message)
                        else:
                            await websocket.send(json.dumps(self.node.get_info()))
                            await asyncio.sleep(2)
                        
                    except websockets.exceptions.ConnectionClosed:
                        #raise
                        await websocket.close()
                        print('Connection closed by the parent')
                        #if the connection is closed by the client
                        break
                        #again goes to eh outer loop and starts the connection again
                    except Exception:
                        #raise
                        await websocket.close()
                        print('Connection lost')
                        break

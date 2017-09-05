import json
import time
import websockets
import asyncio
import argparse

class Proxy(object):
    '''A proxy  server that recieves data from all the master nodes and acts as a interface between mobile client'''
    DEFAULT_PORT = '5000'
    DEFAULT_HOST = 'localhost'

    @classmethod
    def from_cli(cls):
        self = cls(config=None)
        return self

    def __init__(self, config=None):
        self.config = config or self._load_from_cli()
        self.received_data = ''
        


    def _load_from_cli(self):
        config = {}
        for key, val in vars(self._get_args()).items():
            key = 'PROFILER_' + key.upper()
            config[key] = val
        return config
        
    def _get_args(self):

        parser = argparse.ArgumentParser()
        parser.add_argument(
            '-host',
            action='store',
            type=str,
            dest='host',
            help='A Host to connect to'
        )

        parser.add_argument(
            '-p', '--port',
            action='store',
            type=int,
            dest='port',
            help='A port to bind to'
        )

        return parser.parse_args()




    async def receiver(self):
        
        extra_headers = [('mode', 'receiver')]
        
           
        async with websockets.connect('ws://%s:%s/' % (self.config.get('PROFILER_HOST'), self.config.get('PROFILER_PORT')), 
            extra_headers=extra_headers) as websocket:
            print('Connected to server node %s at port %d' % (websocket.host, websocket.port))
            while True:
                try:
                    message = await websocket.recv()
                    self.received_data = message
                    print(self.received_data)
                    
                except websockets.exceptions.ConnectionClosed:
                    raise
                    print('Connection closed by the parent')
                    #if the connection is closed by the client
                    break
                    #again goes to eh outer loop and starts the connection again
                except Exception:
                    raise
                    print('Connection lost')
                    break
    
    
    async def proxy_sender(self, websocket, path):
        #wheh someone wants to connect to the server node, it must register itseld as a clients
        try:
            while True:
                #any connection 
                await websocket.send(self.received_data)

        except Exception:
            raise
    
    def run(self):
         
        asyncio.get_event_loop().run_until_complete(self.receiver())

        # else:

        #     sanic_server = self.http_server.create_server('0.0.0.0', port=8000)
        #     sanic_task = asyncio.ensure_future(sanic_server)

        #     #run in the parent mode 
        #     #take the configuration from the command line if provied else use default host and port
        #     #iniate the master server\
        #     self.master_server = MasterServer(
        #         self.clients_alias,
        #         snapshot_interval=5
        #     )
        #     parent_server = websockets.serve(
        #         self.master_server.consumer_handler,
        #         self.config.get('PROFILER_HOST', self.DEFAULT_HOST),
        #         self.config.get('PROFILER_PORT', self.DEFAULT_PORT)
        #     ) 
        #     asyncio.get_event_loop().\
        #     run_until_complete(asyncio.gather(parent_server, sanic_task))
        #     asyncio.get_event_loop().run_forever()



if __name__ == '__main__':
    p = Proxy.from_cli()
    p.run()
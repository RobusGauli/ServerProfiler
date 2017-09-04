import asyncio
import websockets
import json
import functools
import itertools
import argparse
import os
import random
import sys
import time

from sanic import Sanic
from sanic.response import text, json as jsonify

from serverprofiler.master import MasterServer
from serverprofiler.slave import SlaveServer

class ServerProfiler:
    DEFAULT_PORT = 5000
    DEFAULT_HOST = '0.0.0.0'
    LOCAL_NODE = 'localhost'
    
    @classmethod
    def create_from_cli_args(cls):
        return cls(config=None)

    def __init__(self, config=None):
        #this object will kep track of all the nodes
        #including the agent nodes and parent Node
        self.nodes = {}
        
        # we will make sure that only one instance of the node
        #is active at any request to the web socket
        
        #get the config object(dict)
        self.config = self._load_args_config()
        self.app = None

        self.client_ws = {}
        self.clients = set()
        self.clients_alias = None

        self.http_server = Sanic(__name__)
        self.master_server = None
        self._create_app()
        


    
    async def change(self, request):
        return text('hi there')

    def _load_args_config(self):
        #return a configuration dictionary
        config = {}
        for key, val in vars(self._get_args()).items():
            if val:
                key = 'PROFILER_%s' % key.upper()
                config[key] = val
        return config
        
    
    def _get_args(self):
        parser = argparse.ArgumentParser(
            description='Server Profiler..'
        )
        parser.add_argument(
            '-p', '--port',
            action='store',
            type=int,
            default=None,
            dest='port',
            help='port to listen on. Defaults to 5000'
        )
        parser.add_argument(
            '-host',
            action='store',
            type=str,
            default=None,
            dest='host',
            help='host to bind to. Defaults to 0.0.0.0 (all interfaces)'
        )
        parser.add_argument(
            '-a', '--agent',
            action='store_true',
            dest='agent',			
            help='Enables client Node mode. This configures the node as a producer'
        )

        parser.add_argument(
            '--register-to',
            action='store',
            dest='register_to',
            help='Register this node as a client node to parent node.(Example: 123.234.23.23:5000(Parent\'s Node address)'
        )
        parser.add_argument(
            '-as', '--register-as',
            action='store',
            dest='register_as',
            help='Alias for the agent Node'
        )

        parser.add_argument(
            '-c', '--clients-config',
            action='store',
            dest='clients_config',
            help='Configuration file of clients registered'
        )


        return parser.parse_args()
    
    def _create_app(self):
        #based on the configuration chooose if the node is the host node or
        # the client node
        #by default it acts as a host node
        #until the configuration says it to be a client node
        is_agent = self.config.get('PROFILER_AGENT')	
        if is_agent:
            #print('i am an agent so i need the way to make sense to produce to consumer')
            parent_host_port = self.config.get('PROFILER_REGISTER_TO')
            if not parent_host_port:
                print('Please specify the parent host and port')
                sys.exit(0)
            

            self._run_as_agent()
            #also if this is agent node than it needs to act to know the 
        else:
            #if we have to run from the parent, then we need atleast one client in the set of client alias
            if not self.config.get('PROFILER_CLIENTS_CONFIG'):
                print('Please specify the client configuration file')
                sys.exit(0)
            #self.http_server = Sanic(__name__)
            async def change(request):
                return jsonify(self.master_server.snapshot)
            self.http_server.route('/')(change)

            self._load_client_aliases() 
            self._run_as_parent()

    def _load_client_aliases(self):
        if not os.path.exists(self.config['PROFILER_CLIENTS_CONFIG']):
            raise ValueError('File not found at the specified path')
        data = json.loads(open(self.config['PROFILER_CLIENTS_CONFIG']).read())
        self.clients_alias = set(data['allowed'])
        

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
                    print('Connection lost')
                    break

                
   

    def _run_as_agent(self):
        pass
    
    def _run_as_parent(self):
        pass
    
    def run(self):
        if self.config.get('PROFILER_AGENT', None):

            self.slave_server = SlaveServer(
                config=self.config
            )
            asyncio.get_event_loop().run_until_complete(self.slave_server.producer_handler())
            
        else:

            sanic_server = self.http_server.create_server('0.0.0.0', port=8000)
            sanic_task = asyncio.ensure_future(sanic_server)

            #run in the parent mode 
            #take the configuration from the command line if provied else use default host and port
            #iniate the master server\
            self.master_server = MasterServer(
                self.clients_alias,
                snapshot_interval=5
            )
            parent_server = websockets.serve(
                self.master_server.consumer_producer_handler,
                self.config.get('PROFILER_HOST', self.DEFAULT_HOST),
                self.config.get('PROFILER_PORT', self.DEFAULT_PORT)
            ) 
            asyncio.get_event_loop().\
            run_until_complete(asyncio.gather(parent_server, sanic_task))
            asyncio.get_event_loop().run_forever()


  
if __name__ == '__main__':
    #create a isntance from the command line
    profiler = ServerProfiler.create_from_cli_args()
    profiler.run()

    #print(profiler.__dict__)


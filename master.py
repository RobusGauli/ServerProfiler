import json
import time
import websockets
import asyncio

class MasterServer(object):
    '''A websocket server that recieves data from all the agent nodes and collect the info'''

    def __init__(self, clients_alias, *, snapshot_interval=5):
        self.clients_alias = clients_alias
        self.snapshot_interval = snapshot_interval
        self._current_connected_clients = 0
        self._snapshot = {}
        self._captured_clients = set()
        
        self._end_time = time.time() + self.snapshot_interval

        self.data = ''

        self.mobile = None
    
    @property
    def snapshot(self):
        return self._snapshot

    @classmethod
    def _process_request(cls, mapping):
        s = dict(mapping)
        return s.get('mode')
    
    async def producer_handler(self, websocket, path):
        while True:
            await websocket.send(self.data)

    async def consumer_handler(self, websocket, path):
        #wheh someone wants to connect to the server node, it must register itseld as a clients
        mode = self._process_request(websocket.request_headers._headers)
        print(mode, type(mode))
        if mode == 'receiver':
            self.mobile = websocket
            

        #send all hi to every client connected when the connectiosn reaches 5
        if mode != 'receiver':
            self._current_connected_clients += 1
       
        print('Got connection from client host %s and port%s' % (websocket.host, websocket.port))
        
        while True:
            #once the websocket is connected send the continue message
            #websocket.send('continue')
            try:
                print(self._current_connected_clients)
                print('right ehere')
                received = await websocket.recv()
                try:
                    data = json.loads(received)
                except json.JSONDecodeError:
                    #cant decode the shit
                    await websocket.send('failed to parse the json payload')
                    self._current_connected_clients -= 1
                    await websocket.close()
                    continue
                if isinstance(data, dict):
                    client_id = data.get('id')
                    
                        

                    if not client_id:
                        await websocket.send("please send the id param.")
                        self._current_connected_clients -= 1
                        await websocket.close()
                        continue
                    
                
                
                    elif client_id not in self.clients_alias:
                        print('client failed to authentic')
                        await websocket.send('failed to authorize you')
                        #self._current_connected_clients -= 1
                        await websocket.close()
                        continue
                    
                print(data, self._current_connected_clients)
                if self.mobile:
                    print('trying to send')
                    await self.mobile.send(received)

                if time.time() >= self._end_time:
                    if len(self._captured_clients) != self._current_connected_clients:
                        self._snapshot[client_id] = data
                        self._snapshot[client_id]['id']+= str(time.time()) 
                        self._captured_clients.add(client_id)
                    else:
                    #self._snap_shot = data
                    #print('took snapshot')
                        self._end_time = time.time() + self.snapshot_interval
                        #and finally clear the clients
                        self._captured_clients.clear()

            
            except websockets.exceptions.ConnectionClosed:
                #raise
                print('Connection closed')
                #await websocket.close()
                self._current_connected_clients -= 1
                break
            except Exception:
                #await websocket.close()
                self._current_connected_clients -= 1
                #raise
                break 

    async def handler(self, websocket, path):
        consumer_task = asyncio.ensure_future(
            self.consumer_handler(websocket, path)
        )

        producer_task = asyncio.ensure_future(
            self.producer_handler(websocket, path)
        )
        
        done, pending = await asyncio.wait(
            [consumer_task, producer_task],
            return_when=asyncio.FIRST_COMPLETED,
        )

        for task in pending:
            task.cancel()

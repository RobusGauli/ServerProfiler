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
    
    @property
    def snapshot(self):
        return self._snapshot
    
    async def producer_handler(self, websocket):
        while True:
            await websocket.send(self.data)

    async def consumer_handler(self, websocket):
        #wheh someone wants to connect to the server node, it must register itseld as a clients

        #send all hi to every client connected when the connectiosn reaches 5
        self._current_connected_clients += 1
        print('Got connection from client host %s and port%s' % (websocket.host, websocket.port))
        try:
            while True:
                #once the websocket is connected send the continue message
                #websocket.send('continue')
                print(self._current_connected_clients)
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
                

                
                
                if client_id not in self.clients_alias:
                    print('client failed to authentic')
                    await websocket.send('failed to authorize you')
                    #self._current_connected_clients -= 1
                    await websocket.close()
                    continue
                

                self.data = data
                print(self.data)
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
            print('Connection closed')
            self._current_connected_clients -= 1
        except Exception:
            self._current_connected_clients -= 1
            raise 
    
    async def handler(self, websocket, path):
        consumer_task = asyncio.ensure_future(
            self.consumer_handler(websocket)
        )

        producer_task = asyncio.ensure_future(
            self.producer_handler(websocket)
        )
        
        done, pending = await asyncio.wait(
            [consumer_task, producer_task],
            return_when=asyncio.FIRST_COMPLETED,
        )

        for task in pending:
            task.cancel()

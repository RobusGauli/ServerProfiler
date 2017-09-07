import websockets
import json
import asyncio


class WebSocketProxy(object):

    proxied_host = 'localhost'
    proxied_port = 9000
    


    
    def run(self):
        server = websockets.serve(self.dispatcher, self.proxied_host, self.proxied_port)
        asyncio.get_event_loop().run_until_complete(server)
        asyncio.get_event_loop().run_forever()

    
    def dispatch(self, middleware_websocket):
        @asyncio.coroutine
        def dispatcher(self, client_websocket, path):
            while True:
                val = yield from middleware_websocket.recv()
                print(val)
                yield from client_websocket.send(val)
        return dispatcher

    @asyncio.coroutine
    def dispatcher(self, client_websocket, path):

        #some client wants to connect then i will first go to the master server create a new websocket connecion
        middleware_websocket = yield from websockets.connect('ws://localhost:5000/', extra_headers=[('mode', 'receiver')])
        yield from self.serve_client(client_websocket, middleware_websocket)
    

    def serve_client(self, client_websocket, middlerwaire_websocket):
        while True:
            #first get the value from the middleware socket
            try:
                val_from_middleware = yield from middlerwaire_websocket.recv()
                print(val_from_middleware)
            #now send that ot the  client
                yield from client_websocket.send(val_from_middleware)
            except Exception:
                raise

class W(object):

    @asyncio.coroutine
    def middleware(self):
        middleware_socket = yield from websockets.connect('ws://localhost:5000/', extra_headers = [('mode', 'receiver')])
        return middleware_socket

    def dispatch(self, middleware_websocket):
        @asyncio.coroutine
        def dispatcher(client, path):
            while True:
                msg = yield from middleware_websocket.recv()
                print(msg)
                yield from client.send(msg)
        return dispatcher

    def run(self):
        middleware_websocket = asyncio.get_event_loop().run_until_complete(self.middleware())
        coroutine = self.dispatch(middleware_websocket)
        server = websockets.serve(coroutine, 'localhost', 12000)
        asyncio.get_event_loop().run_until_complete(server)
        asyncio.get_event_loop().run_forever()
            
    

if __name__ == '__main__':
    W().run()
import websockets
import json
import asyncio


class WebSocketProxy(object):

    proxied_host = 'localhost'
    proxied_port = 9000
    


    @asyncio.coroutine
    def proxy_dispatcher(self, proxy_websocket, path):

        proxied_websocket = yield from websockets.connect(self.proxied_url_value)
        yield from self.process_requests(proxy_websocket, proxied_websocket)
    
    def connect_to_proxy_server(self, proxy_websocket, proxied_url_value):
        try:
            proxied_web_socket = yield from websockets.connect(proxied_url_value)
        except Exception:
            raise
        return proxied_web_socket

    def process_requests(self, proxy_websocket, proxied_websocket):
        while True:
            request_for_proxy = yield from proxy_websocket.recv()
            yield from proxied_websocket.send(request_for_proxy)
    
    def run(self):
        server = websockets.serve(self.dispatcher, self.host, self.port)
        asyncio.get_event_loop().run_until_complete(server)
        asyncio.get_event_loop().run_forever()

    
    @asyncio.coroutine
    def dispatcher(self, client_websocket, path):

        #some client wants to connect then i will first go to the master server create a new websocket connecion
        middleware_websocket = yield from websockets.connect('ws://localhost:5000/')
        yield from self.serve_client(client_websocket, middleware_websocket)
    

    def serve_client(self, client_websocket, middlerwaire_websocket):
        while True:
            #first get the value from the middleware socket
            try:
                val_from_middleware = yield from middlerwaire_websocket.recv()
            #now send that ot the  client
                yield from client_websocket.send(val_from_middleware)
            except Exception:
                raise
    
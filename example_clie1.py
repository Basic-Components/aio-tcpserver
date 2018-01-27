import asyncio


class EchoClientProtocol(asyncio.Protocol):
    def __init__(self, message, loop):
        self.message = message
        self.loop = loop

    def connection_made(self, transport):
        #transport.write(self.message.encode())
        self.transport = transport
        self.remote = transport.get_extra_info('peername')
        print('con to {}'.format(self.remote))

    def data_received(self, data):
        print('Data received: {!r}'.format(data.decode()))
        if data == b"123":
            self.transport.write(b"234")
        if data == b"end":
            self.transport.write(b"end")

    def connection_lost(self, exc):
        print('The server closed the connection')
        print('Stop the event loop')
        self.loop.stop()


loop = asyncio.get_event_loop()
message = 'Hello World!'
coro = loop.create_connection(lambda: EchoClientProtocol(message, loop),
                              '127.0.0.1', 5000)
loop.run_until_complete(coro)
loop.run_forever()
loop.close()

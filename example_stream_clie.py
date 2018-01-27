import asyncio
import msgpack
import uuid


class EchoClientProtocol(asyncio.StreamReaderProtocol):

    def __init__(self, loop):
        self.loop = loop
        self._connection_lost = None
        self._paused = None
        self._stream_writer = None
        self._stream_reader = asyncio.StreamReader(loop=self.loop)
        self.tasks = {}

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        self.transport = transport
        self._connection_lost = False
        self._paused = False
        self._stream_writer = asyncio.StreamWriter(
            transport, self, self._stream_reader, self.loop)
        asyncio.ensure_future(self.init_connection())
        asyncio.ensure_future(self.get_response())

    async def get_response(self):
        while True:
            data = await self._stream_reader.readuntil(b"##end##")
            data = data[:-7]
            response = msgpack.unpackb(data, encoding='utf-8')
            print("recived:")
            print(response)
            # self._stream_writer.write(msgpack.packb(response)+b"##end##")
            # await self._stream_writer.drain()

    async def init_connection(self):
        request = {
            "test": 123,
            'conn': True
        }
        print("send init message")
        self._stream_writer.write(msgpack.packb(request) + b"##end##")
        await self._stream_writer.drain()

    def connection_lost(self, exc):
        print('The server closed the connection')
        print('Stop the event loop')
        self._connection_lost = True
        self.loop.stop()


loop = asyncio.get_event_loop()
coro = loop.create_connection(lambda: EchoClientProtocol(loop),
                              '127.0.0.1', 5000)
loop.run_until_complete(coro)
loop.run_forever()
loop.close()

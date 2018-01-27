import asyncio
import msgpack
import time
from aio_tcpserver import tcp_server, listener


# @listener("before_server_start")
# async def beat(loop):
#     print(time.time())
#     print("ping")


class EchoServerProtocol(asyncio.StreamReaderProtocol):
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self._connection_lost = None
        self._paused = None
        self._stream_writer = None
        self._stream_reader = asyncio.StreamReader(loop=self.loop)

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        self.transport = transport
        self._connection_lost = False
        self._paused = False
        self._stream_writer = asyncio.StreamWriter(
            transport, self, self._stream_reader, self.loop)
        asyncio.ensure_future(self.get_request())

    async def get_request(self):
        while True:
            data = await self._stream_reader.readuntil(b"##end##")
            data = data[:-7]
            response = msgpack.unpackb(data, encoding='utf-8')
            print("request:")
            print(response)
            print("send answor")
            self._stream_writer.write(msgpack.packb(response) + b"##end##")
            await self._stream_writer.drain()


def main():
    tcp_server(EchoServerProtocol, worker=1)


if __name__ == '__main__':
    main()

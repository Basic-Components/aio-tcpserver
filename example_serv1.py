import asyncio
import time
from aio_tcpserver import tcp_server, listener


# @listener("before_server_start")
# async def beat(loop):
#     print(time.time())
#     print("ping")


class EchoServerClientProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        self.transport = transport
        transport.write(b"123")

    def data_received(self, data):
        message = data.decode()
        print('Data received: {!r}'.format(message))
        if message == "234":
            print('recv: {!r}'.format(message))
            print('Send: {!r}'.format(b"end"))
            self.transport.write(b"end")
        if message == "end":
            print('recv: {!r}'.format(message))
            print('Close the client socket')
            self.transport.close()


def main():
    tcp_server(EchoServerClientProtocol,worker=3)


if __name__ == '__main__':
    main()
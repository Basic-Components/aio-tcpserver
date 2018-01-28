
aio-tcpserver
===============================

* version: 0.0.3

* status: dev

* author: hsz

* email: hsz1273327@gmail.com

Desc
--------------------------------

A tcp sever for running `asyncio.Protocol`. The inspiration comes from sanic,

only support python 3.6+


keywords:tcp-server,asyncio


Feature
----------------------
* with multiple worker
* for asyncio.Protocol
* can be closed by ctrl+C in windows
* with hooks

Example
-------------------------------

server.py

.. code:: python

    import asyncio
    import time
    from aio_tcpserver import tcp_server, listener

    @listener("before_server_start")
    async def beat(loop):
        print(time.time())
        print("ping")

    class EchoServerClientProtocol(asyncio.Protocol):
        def connection_made(self, transport):
            peername = transport.get_extra_info('peername')
            print('Connection from {}'.format(peername))
            self.transport = transport

        def data_received(self, data):
            message = data.decode()
            print('Data received: {!r}'.format(message))

            print('Send: {!r}'.format(message))
            self.transport.write(data)

            print('Close the client socket')
            self.transport.close()

    def main():
        tcp_server(EchoServerClientProtocol, worker=3)


    if __name__ == '__main__':
        main()


client.py


.. code:: python

    import asyncio

    class EchoClientProtocol(asyncio.Protocol):
        def __init__(self, message, loop):
            self.message = message
            self.loop = loop

        def connection_made(self, transport):
            transport.write(self.message.encode())
            print('Data sent: {!r}'.format(self.message))

        def data_received(self, data):
            print('Data received: {!r}'.format(data.decode()))

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





Install
--------------------------------

- ``python -m pip install aio-tcpserver``


Documentation
--------------------------------

`Documentation on Readthedocs <https://github.com/Basic-Components/aio-tcpserver>`_.




import asyncio
from asyncio import StreamReader, StreamWriter
import uvloop

# https://github.com/magicstack/uvloop
# Там есть бенчмарки


async def connected(reader: StreamReader, writer: StreamWriter):
    line = await reader.readline()
    writer.write(line)
    await writer.drain()
    writer.close()
    await writer.wait_closed()


async def main():
    server = await asyncio.start_server(connected, port=9000)
    print("Server run")
    print(asyncio.get_running_loop())
    # <uvloop.Loop running=True closed=False debug=False>
    await server.serve_forever()


uvloop.install()  # <- переключает реализацию цикла событий

# Переключение можно было бы сделать и вручную
# loop = uvloop.new_event_loop()
# asyncio.set_event_loop(loop)

asyncio.run(main())

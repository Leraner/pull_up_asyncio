import asyncio
from asyncio.subprocess import Process


# Если надо интегрировать программу, которая написана на другом языке,
# то можно использовать подпроцесс. Он запускает отдельный подпроцесс 
# другого языка через консоль



async def main():
    process: Process = await asyncio.create_subprocess_exec("ls", "-l")
    print(f"pid процесса: {process.pid}")
    # wait() - блокирует программу, пока процесс не завершится
    status_code = await process.wait()
    print(f"Код состояния: {status_code}")


asyncio.run(main())

import asyncio
from asyncio.subprocess import Process


async def main():
    process: Process = await asyncio.create_subprocess_exec("sleep", "3")
    print(f"pid процесса: {process.pid}")
    try:
        # wait() - блокирует программу, пока процесс не завершится
        # wait_for(process.wait(), timeout=1.0) - wait_for не останавливает процесс, 
        # он ждёт 1с и вызывает исключение asyncio.TimeoutError. 
        # Поэтому в except мы явно убиваем процесс с помощью process.terminate() или process.kill()
        status_code = await asyncio.wait_for(process.wait(), timeout=1.0)
        print(status_code)
    except asyncio.TimeoutError:
        print("Тайм-аут, завершаю принудительно...")
        process.terminate()  # Посылает сигнал - SIGTERM
        # process.kill() # Посылает сигнал - SIGKILL
        status_code = await process.wait()
        print(status_code)


asyncio.run(main())

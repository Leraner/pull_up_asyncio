import asyncio
from asyncio import StreamWriter, StreamReader, Event
from asyncio.subprocess import Process


# Запускаем процесс. 
# Запускаем сопрограмму output_consumer - принимает всё, что подпроцесс отдаёт
# Запускаем сопрограмму input_writer - отправляет данные в подпроцесс


async def output_consumer(input_ready_event: Event, stdout: StreamReader):
    while (data := await stdout.read(1024)) != b"":
        print(data.decode())
        if data.decode().endswith("Введите текст: "):
            # Говорим, что произошло событие
            input_ready_event.set()


async def input_writer(text_data, input_ready_event: Event, stdin: StreamWriter):
    for text in text_data:
        # Ждём события
        await input_ready_event.wait()
        stdin.write(text.encode())
        await stdin.drain()
        # Говорим событию, что работа закончена
        input_ready_event.clear()


async def main():
    subprocess_file_path = (
        "examples/chapter_013/listenings/chapter_13_listening_13_13.py"
    )
    program = [
        "python3",
        subprocess_file_path,
    ]
    process: Process = await asyncio.create_subprocess_exec(
        *program, stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE
    )

    input_ready_event = Event()

    text_input = ["one\n", "two\n", "three\n", "four\n", "quit\n"]

    if process.stdin is not None and process.stdout is not None:
        await asyncio.gather(
            output_consumer(input_ready_event, process.stdout),
            input_writer(text_input, input_ready_event, process.stdin),
            process.wait(),
        )


asyncio.run(main())

import asyncio
from asyncio import StreamWriter, StreamReader
from asyncio.subprocess import Process


async def consume_and_send(text_list, stdout: StreamReader, stdin: StreamWriter):
    for text in text_list:
        line = await stdout.read(2048)
        print(line.decode())
        stdin.write(text.encode())
        await stdin.drain()


async def main():
    subprocess_file_path = (
        "examples/chapter_013/listenings/chapter_13_listening_13_11.py"
    )
    program = [
        "python3",
        subprocess_file_path,
    ]
    process: Process = await asyncio.create_subprocess_exec(
        *program, stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE
    )

    text_input = ["one\n", "two\n", "three\n", "four\n", "quit\n"]

    if process.stdin is not None and process.stdout is not None:
        await asyncio.gather(
            consume_and_send(text_input, process.stdout, process.stdin), process.wait()
        )


asyncio.run(main())

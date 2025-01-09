import asyncio
from asyncio.subprocess import Process


async def main():
    subprocess_file_path = (
        "examples/chapter_013/listenings/chapter_13_listening_13_9.py"
    )
    program = [
        "python3",
        subprocess_file_path,
    ]

    process: Process = await asyncio.subprocess.create_subprocess_exec(
        *program,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
    )

    # Передём имя Zoot в виде байтов в input в подпроцессе
    stdout, stderr = await process.communicate(b"Zoot")

    print(stdout.decode())
    print(stderr)


asyncio.run(main())

import asyncio
from asyncio.subprocess import Process


async def main():
    subprocess_file_path = (
        "examples/chapter_013/listenings/chapter_13_listening_13_4.py"
    )
    program = [
        "python3",
        subprocess_file_path,
    ]

    process: Process = await asyncio.subprocess.create_subprocess_exec(
        *program, stdout=asyncio.subprocess.PIPE
    )

    print(f"pid процесса: {process.pid}")

    # process.communicate() - создаёт несколько задач, которые постоянно читают
    # стандартный вывод во внутренний буфер, избегая тем самым взаимоблокировки

    # Хотя проблему взаимоблокировки мы решили,
    # то сейчас мы не можем интерактивно обрабатывать данные из стандартного вывода.

    # Если требуется реагировать на данные, выводимые приложением
    # (например завершать работу или запускать новую задачу, встретив определенное сообщение),
    # то следует использовать wait, но при этом аккуратно читать из потокового читателя,
    # чтобы избежать взаимоблокировки.

    # Также communicate() - буфферизирует в памяти все данные из стандартного вывода и
    # стандартного вывода для ошибок. Если процесс порождает большой объем памяти,
    # то возникает риск нехватки памяти

    stdout, stderr = await process.communicate()

    # stdout - то, что выводит подпроцесс в консоль
    # stderr - ошибка если возникло исключение в подпроцессе
    print(stdout)
    print(stderr)

    print(f"Процесс вернул: {process.returncode}")


asyncio.run(main())

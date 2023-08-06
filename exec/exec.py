import subprocess


async def execute_dmenu(
    input_string: str, cmd: tuple[str, ...] = ("dmenu", "-i", "-l", "20")
) -> str:
    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    output, _ = process.communicate(input=input_string.rstrip("\n").encode())
    return output.decode().rstrip("\n")


async def execute_mpv(path: str) -> None:
    subprocess.run(("mpv", "--osc", "--fs", path.strip("\n")))


async def execute_notify_send(msg: str) -> None:
    subprocess.run(("notify-send", msg))

import subprocess
from typing import Literal


def dmenu(input: bytes, position: Literal["vertical", "horizontal"] = "vertical") -> str:
    cmd = ("dmenu", "-i")
    if position == "vertical":
        cmd += ("-l", "20")

    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    output, _ = process.communicate(input=input)
    return output.decode().strip("\n")


def mpv(path: str) -> None:
    subprocess.run(("mpv", "--osc", "--fs", path.strip("\n")))


def notify_send(msg: str) -> None:
    subprocess.run(("send2notify", msg))

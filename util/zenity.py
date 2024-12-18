import subprocess
from os import popen


def info(title : str, description: str):
    with subprocess.Popen(['/usr/bin/zenity', '--info' , f'{title}', f'--text="{description}"']) as p:
        return_code = p.wait()
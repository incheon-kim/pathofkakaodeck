import psutil, subprocess, os
from util import zenity

def start_wait_stdout(bin : str, str : str):
    proc = subprocess.Popen(
        bin,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.DEVNULL,
        text=True,
        bufsize=1,
        start_new_session=True,
    )

    try:
        for line in iter(proc.stdout.readline, ''):
            print (line, end='')
            if str in line:
                break
    except Exception as e:
        print(f'error {e}')
    finally:
        proc.stdout.close()
        proc.stdout = subprocess.DEVNULL
        proc.stderr.close()
        proc.stderr = subprocess.DEVNULL
        

def kill_and_wait(proc_name : str):
    targets = filter(lambda proc: proc.name().lower().contains(proc_name.lower()), psutil.process_iter(attrs=["name"]))
    
    if len(targets) == 0:
        zenity.info("Path of Kakao", f'"{proc_name}" 을 찾을 수 없습니다. 수동으로 종료해주세요.')
        return
    
    for proc in targets:
        proc.kill()
        proc.wait()
        

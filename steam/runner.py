import subprocess, os, select, logging, psutil
from pathlib import Path
from urllib.parse import unquote
from steam import shortcuts
from util import zenity
from common import constants

def _get_user_id() -> str:
    userdata_path = Path.home() / '.steam' / 'steam' / 'userdata'
    for dir in userdata_path.iterdir():
        if dir.is_dir():
            return dir.name
    return None

def _write_to_fifo() -> bool:
    fifo_path = Path("/tmp/poe2fifo")
    if not fifo_path.exists():
        return False
    
    with open(fifo_path, mode="w") as fifo:
        fifo.write("TOKEN ACQUIRED")
        fifo.flush()

    return True

def handle_scheme(scheme_url : str):
    logging.info(f'scheme({scheme_url})')
    token, userid = parse_url(scheme_url)
    if not token or not userid:
        zenity.info(constants.APP_NAME, f'시작 옵션 파싱 실패!\r\n{scheme_url}')
        return
    
    logging.info(f'token({token})')
    logging.info(f'userid({userid})')

    if shortcuts.update_launch_option(_get_user_id(), f'--kakao {token} {userid}'):
        _write_to_fifo()
        launch_appid(get_appid)
    else:
        zenity.info(constants.APP_NAME, '시작 옵션 업데이트 실패!')

def parse_url(url : str) -> tuple[str, str]:
    splitted = unquote(url).split('|')
    if len(splitted) != 6:
        return None, None
    return splitted[3], splitted[4]

def launch_appid(appid : str):
    subprocess.Popen(
        ['xdg-open', f'steam://rungameid/{appid}/'], 
        start_new_session=True, 
        stdout=subprocess.DEVNULL, 
        stdin=subprocess.DEVNULL, 
        stderr=subprocess.DEVNULL
    )

def get_appid() -> str:
    try:
        file_path = Path.home() / '.poe2kakaoappid'
        if not file_path.exists():
            return None
        return file_path.read_text()
    except Exception as e:
        return None
    
def try_acquire(timeout=60):
    browser = open_browser()
    if browser is None:
        zenity.info(constants.APP_NAME, "Chrome 또는 Firefox를 찾을 수 없습니다.")
        return

    fifo_path = Path("/tmp/poe2fifo")
    if not fifo_path.exists():
        os.mkfifo(fifo_path)    
    fifo_fd = os.open(fifo_path, os.O_RDONLY | os.O_NONBLOCK)
    try:
        ready_fifo, _, _ = select.select([fifo_fd], [], [], timeout)
        if not ready_fifo:
            zenity.info(constants.APP_NAME, "타임아웃 60초가 지났습니다. 브라우저를 종료합니다.")
        else:
            data = os.read(fifo_fd, 1024)
            if data:
                logging.info(data.decode('utf-8'))
            else:
                logging.info("got data from pipe but couldn't read data")
    except Exception as e:
        logging.error("Reading pipe error, {e}")
    finally:
        # kill all browser related processes
        browsers = filter(lambda proc: browser in proc.name(), psutil.process_iter())
        for proc in browsers:
            if proc.is_running():
                proc.kill()
        logging.info('kill signal to browser')

        if fifo_fd is not None:
            os.close(fifo_fd)
            os.remove(fifo_path)


def open_browser() -> str:
    firefox_cmd = ["/usr/bin/flatpak", "run", 'org.mozilla.firefox', 'poe2.game.daum.net']
    chrome_cmd = ["/usr/bin/flatpak", "run", 'com.google.Chrome', 'poe2.game.daum.net']

    if check_flatpak("com.google.Chrome"):
        subprocess.Popen(
            chrome_cmd,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
            stdin = subprocess.PIPE,
            )
        return "chrome"
    elif check_flatpak("org.mozilla.firefox"):
        subprocess.Popen(
            firefox_cmd,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
            stdin = subprocess.PIPE,
            )
        return "firefox"
    else:
        return None

def check_flatpak(app_id : str) -> bool:
    try:
        result = subprocess.run(
            ["flatpak", "list", "--app"],
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
            text = True,
            check = True
        )

        for app in result.stdout.splitlines():
            if app_id in app:
                return True
        else:
            return False
    except:
        return False
import subprocess, os, select, time
from pathlib import Path
from urllib.parse import unquote
from steam import shortcuts, steam_instance
from util import zenity
from common import constants


def handle_scheme(scheme_url : str):
    token, userid = parse_url(scheme_url)
    if not token or not userid:
        zenity.info(constants.APP_NAME, f'시작 옵션 파싱 실패!\r\n{scheme_url}')
        return
    
    if shortcuts.update_launch_option('', f'--kakao {token} {userid}'):
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
        return

    fifo_path = Path("/tmp/poe2_fifo")
    if not fifo_path.exists():
        os.mkfifo(fifo_path)    
    fifo_fd = os.open(fifo_path, os.O_RDONLY | os.O_NONBLOCK)
    try:
        ready, _, _ = select.select([fifo_fd], [], [], 60)
        if not ready:
            zenity.info(constants.APP_NAME, "타임아웃 60초가 지났습니다. 브라우저를 종료합니다.")
        browser.kill()
    except:
        pass
    finally:
        if fifo_fd is not None:
            os.close(fifo_fd)
    browser.wait()


def open_browser() -> subprocess.Popen[bytes]:
    firefox_cmd = ["/usr/bin/flatpak", "run", 'org.mozilla.firefox', 'poe2.game.daum.net']
    chrome_cmd = ["/usr/bin/flatpak", "run", 'com.google.Chrome', 'poe2.game.daum.net']

    if check_flatpak("com.google.Chrome"):
        return subprocess.Popen(
            chrome_cmd,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
            stdin = subprocess.PIPE,
            )
    elif check_flatpak("org.mozilla.firefox"):
        return subprocess.Popen(
            firefox_cmd,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
            stdin = subprocess.PIPE,
            )
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
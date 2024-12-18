import psutil
from util import zenity, ProcessUtil

def kill_steam():
    ProcessUtil.kill_and_wait("steam")

def start_steam():
    ProcessUtil.start_wait_stdout("/usr/bin/steam", "BuildCompleteAppOverviewChange")
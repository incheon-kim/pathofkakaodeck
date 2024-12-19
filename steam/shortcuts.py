import vdf, os, logging
from pathlib import Path
from util import zenity
from common import constants

# InstallConfigStore.Software.Value.Steam.CompatToolMapping
# "appid"
#       "name" "proton_experimental"
#       "config" ""
#       "priority" "250"

def _get_shortcuts_path(user_id : str) -> Path:
    return Path.home() / '.steam' / 'steam' / 'userdata' / user_id / 'config' / 'shortcuts.vdf'

def _get_root_config_path() -> Path:
    return Path.home() / '.steam' / 'root' / 'config' / 'config.vdf'

def _write_appid(appid : int):
    file_path = Path.home() / ".poe2appid"
    if not file_path.exists():
        file_path.touch()
    file_path.write_text(str(appid))

def _get_file_path(file_name : str) -> str:
    try:
        for root, _, files in os.walk("/home/deck"):
            for file in files:
                if file == file_name:
                    return os.path.join(root, file)
        else:
            return None
    except Exception as e:
        return None

def update_launch_option(user_id : str, launch_option : str, proton : str = "proton_experimental"):
    logging.debug(f'user_id({user_id}) option({launch_option})')
    # vdf 파일 오픈
    try:
        with _get_shortcuts_path(user_id).open("rb") as f:
            shortcuts = vdf.binary_load(f)
            with (Path.home() / f'shortcuts.vdf.bak').open('wb') as bf:
                f.seek(os.SEEK_SET)
                bf.write(f.read())
        with _get_root_config_path().open('r') as f:
            root_config = vdf.load(f)
    except Exception as e:
        logging.error(f'vdf 파일 열기 실패, {e}')
        zenity.Info(constants.APP_NAME, f'Steam 설정 파일 열기 실패!\r\n{e}')
        return False
    
    logging.info("VDF 파일 열기 완료")

    # 탐색 및 수정 시작
    try:
        for game in shortcuts.get("shortcuts", {}).values():
            appid = int(game.get("appid", "")) + 2**32 # signed to unsigned 32-bit
            exe_path = game.get("Exe", "")
            if "PathOfExile_x64_KG.exe" in exe_path:
                logging.info('exe found')
                # 런치 옵션 세팅
                game["LaunchOptions"] = launch_option or ""

                # 프로톤 세팅
                compat_mapping = root_config.get("InstallConfigStore", {}) \
                                            .get("Software", {}) \
                                            .get("Valve", {}) \
                                            .get("Steam", {}) \
                                            .get("CompatToolMapping", {})
                if compat_mapping == {}:
                    zenity.info(constants.APP_NAME, "Proton 설정을 실패했습니다. 수동으로 Proton 설정해주세요.")
                else:
                    app_compat = compat_mapping.get(appid, {
                        "name": "",
                        "config": "",
                        "priority" : "250"
                    })
                    app_compat["name"] = proton
                    compat_mapping[appid] = app_compat
                break
        else:
            # shortcuts 내에서 PathOfExile_x64_KG.exe를 찾지 못함
            logging.info('exe not found')
            appid = constants.DEFAULT_APP_ID_UNSIGNED
            binary_path = _get_file_path("PathOfExile_x64_KG.exe")
            game_entry = {
                "appid": constants.DEFAULT_APP_ID,
                "appname": constants.DEFAULT_APP_NAME,
                "exe": f'"{binary_path}"',
                "StartDir" : os.path.dirname(binary_path),
                "icon": "",
                "ShortcutPath": "",
                "IsHidden": 0,
                "AllowDesktopConfig": 1,
                "AllowOverlay" : 1,
                "OpenVR": 0,
                "Devkit" : 0,
                "DevkitGameID": "",
                "DevkitOverrideAppID": 0,
                "LastPlayTime": 0,
                "FlatpakAppID": "",
                "tags" : {},
            }
            shortcuts["shortcuts"][str(len(shortcuts["shortcuts"]))] = game_entry
            compat_mapping = root_config.get("InstallConfigStore", {}) \
                                        .get("Software", {}) \
                                        .get("Valve", {}) \
                                        .get("Steam", {}) \
                                        .get("CompatToolMapping", {})
            if compat_mapping == {}:
                zenity.info(constants.APP_NAME, "Proton 설정을 실패했습니다. 수동으로 Proton 설정해주세요.")
            else:
                app_compat = compat_mapping.get(appid, {
                    "name": "",
                    "config": "",
                    "priority" : "250"
                })
                app_compat["name"] = proton
                compat_mapping[appid] = app_compat
    except Exception as e:
        logging.error(f'설정 파일 수정 실패, {e}')
        zenity.Info(constants.APP_NAME, f'Steam 설정 파일 수정 실패!\r\n{e}')
        return False
    
    try:
        with _get_shortcuts_path(user_id).open("wb") as f:
            vdf.binary_dump(shortcuts, f)
        with _get_root_config_path().open('w') as f:
            vdf.dump(root_config, f)
        _write_appid(appid)
    except Exception as e:
        logging.error(f'설정 파일 저장 실패, {e}')
        zenity.Info(constants.APP_NAME, f'Steam 설정 파일 저장 실패!\r\n{e}')
        return False
    
    # 모든 절차 완료
    return True

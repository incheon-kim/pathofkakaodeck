from pathlib import Path

def create_handler(exec: str, venv: str) -> bool:
    try:
        local_applications_dir = get_local_applications()
        target_file = local_applications_dir / f'Daum Game Starter Handler (POE2).desktop'

        txt = f"""
            [Desktop Entry]
            Name=Daum Game Starter Handler (POE2)
            Comment="POE2 Kakao Starter Token Acquire Handler"
            Exec={venv} {exec}/main.py --scheme %u
            Terminal=false
            Type=Application
            MimeType=x-scheme-handler/daumgamestarter
            Icon=application-default-icon
            Categories=Utility;
        """
        print(txt)
        target_file.write_text(txt)
        
        return True
    except Exception as err:
        print(err)
        return False

def create_application(exec: str, venv: str) -> bool:
    try:
        local_applications_dir = get_local_applications()
        target_file = local_applications_dir / f'Path of Kakao.desktop'

        txt = f"""
            [Desktop Entry]
            Name=Path of Kakao
            Comment="Kakao POE2 Token Acqure"
            Exec={venv} {exec}/main.py --run
            Terminal=false
            Type=Application
            Icon=application-default-icon
            Categories=Game;
        """
        print(txt)
        target_file.write_text(txt)

        return True
    except Exception as err:
        print(err)
        return False

def get_local_applications() -> Path:
    home = Path.home()
    local_applications_dir = home / ".local" / "share" / "applications"
    return local_applications_dir
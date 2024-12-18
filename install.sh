#! /bin/bash

if [ "$(id -u)" -ne 0 ]
  then echo "'sudo sh install.sh' 명령어로 실행해주세요."
  exit
fi

SCRIPT_DIR=$(dirname $(realpath $0))
VENV_DIR="$SCRIPT_DIR/venv"
echo "$SCRIPT_DIR"

# create virutal environment if not exists
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "Python 가상환경 생성중..."
    python -m venv "$SCRIPT_DIR/venv"
else
    echo "yes virutalenv"
fi

# check pip
if [ ! -f "$SCRIPT_DIR/venv/bin/pip"]; then
    echo "Python 환경 구성중..."
    if [ ! -f "$VENV_DIR/bin/pip" ]; then
        echo "Python 환경 구성중...(pip)"
        curl https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py
        if [ $? -ne 0 ]; then
            echo "Python 환경 구성 실패! (pip)"
            exit 1
        fi
        "$VENV_DIR/bin/python" /tmp/get-pip.py
        if [ $? -ne 0 ]; then
            echo "Python 환경 구성 실패! (pip)"
            exit 1
        fi
    fi
fi

# update pip
"$VENV_DIR/bin/pip" install --upgrade pip

# python dependencies
"$VENV_DIR/bin/pip" install argparse vdf 

# create url scheme handler
"$VENV_DIR/bin/python" "$SCRIPT_DIR/main.py" --install scheme --dir "$SCRIPT_DIR" --venv "$VENV_DIR/bin/python"

# create launcher for non-steam game
"$VENV_DIR/bin/python" "$SCRIPT_DIR/main.py" --install launcher --dir "$SCRIPT_DIR" --venv "$VENV_DIR/bin/python"

# update desktop environment applications database
update-desktop-database
#!/bin/bash
#
# Can be run for updates too.

err_report() {
    echo "[ERROR] on line $1"
    exit 1
}

trap 'err_report $LINENO' ERR

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Check Python version
echo "[INFO] Checking Python version..."
PYTHON_VERSION=$(python --version | awk '{ print $NF }')
REQUIRED_VERSION="3.8.5"
if [[ $PYTHON_VERSION != $REQUIRED_VERSION ]]; then
    min=$(echo $PYTHON_VERSION $REQUIRED_VERSION| awk '{if ($1 < $2) print $1; else print $2}')
    if [[ "$min" == "$PYTHON_VERSION" ]]; then
        echo "[ERROR] Please install Python 3.8.5 or higher."
        exit 1
    fi
fi

echo "[INFO] Installing apt-get packages..."
sudo apt-get -y -qq install python-usb mpg123

echo "[INFO] Installing Python packages..."
pip install -q -r requirements.txt

if [ ! -f /etc/udev/rules.d/99-lego.rules ]; then
    echo "[INFO] Install USB device rules..."
    sudo cp ${DIR}/99-lego.rules /etc/udev/rules.d
    sudo udevadm control --reload-rules && sudo udevadm trigger
fi

if [ ! -f ${DIR}/tags.yml ]; then
    echo "[INFO] Initial tags.yml created. You can edit this file as tag UIDs are discovered." 
    cp ${DIR}/tags.yml-sample ${DIR}/tags.yml
fi
if [ ! -f ${DIR}/config.yml ]; then
    echo "[INFO] Edit the config.py with your Spotify API app credentials before starting."
    cp ${DIR}/config.py-sample ${DIR}/config.py
fi

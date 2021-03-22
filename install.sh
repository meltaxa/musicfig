#!/bin/bash
#
# Can be run for updates too.

for i in "$@"; do
    case $i in
        -d|--docker)
            DOCKER=yes
            shift
            ;;
        -h|--help)
            echo "usage: $0 [-d|--docker]"
            echo "    -d|--docker    Bootstrap Raspberry Pi before using Docker image."
            exit 0
    esac
done

err_report() {
    echo "[ERROR] on line $1"
    exit 1
}

trap 'err_report $LINENO' ERR

DIR="$(pwd)"

check_python_version() {
    # Check Python version
    [[ "$DOCKER" ]] && return
    echo "[INFO] Checking Python version..."
    PYTHON_VERSION=$(python3 --version | awk '{ print $NF }')
    REQUIRED_VERSION="3.7.3"
    if [[ $PYTHON_VERSION != $REQUIRED_VERSION ]]; then
        min=$(echo $PYTHON_VERSION $REQUIRED_VERSION| awk '{if ($1 < $2) print $1; else print $2}')
        if [[ "$min" == "$PYTHON_VERSION" ]]; then
            echo "[ERROR] Please install Python 3.7.3 or higher."
            exit 1
        fi
    fi
}

git_pull() {
    # Get latest code
    [[ "$DOCKER" ]] && return
    echo "[INFO] Retrieve app updates"
    git pull | sed -e 's/^/[INFO] /g'
}

apt_get() {
    [[ "$DOCKER" ]] && return
    echo "[INFO] Installing apt-get packages..."
    sudo apt-get -y -qq install python-usb mpg123
}

pip_install() {
    [[ "$DOCKER" ]] && return
    echo "[INFO] Installing Python packages..."
    pip install -q -r requirements.txt
}

setup_usb() {
    if [ ! -f /etc/udev/rules.d/99-lego.rules ]; then
        echo "[INFO] Install USB device rules..."
        sudo cp ${DIR}/99-lego.rules /etc/udev/rules.d
        sudo udevadm control --reload-rules && sudo udevadm trigger
    fi
}

setup_files() {
    if [[ "$DOCKER" ]]; then
        curl -s -O https://raw.githubusercontent.com/meltaxa/musicfig/master/config.py-sample
        curl -s -O https://raw.githubusercontent.com/meltaxa/musicfig/master/tags.yml-sample
    fi
    if [ ! -f ${DIR}/tags.yml ]; then
        echo "[INFO] Initial example ${DIR}/tags.yml created. Edit this file as tag UIDs are discovered." 
        cp ${DIR}/tags.yml-sample ${DIR}/tags.yml
    fi
    if [ ! -f ${DIR}/config.py ]; then
        echo "[OPTIONAL] Edit the ${DIR}/config.py with your Spotify API app credentials before starting."
        cp ${DIR}/config.py-sample ${DIR}/config.py
    fi
}

install_startup() {
    [[ "$DOCKER" ]] && return
    # Install startup service
    PYTHON_PATH=$(which python3)
    MUSICFIG_DIR=$(pwd)
    cp musicfig.service musicfig.service-temp
    sed -i "s!%MUSICFIG_DIR%!${MUSICFIG_DIR}!ig" musicfig.service-temp
    sed -i "s!%PYTHON_PATH%!${PYTHON_PATH}!ig" musicfig.service-temp
    sudo cp musicfig.service-temp /etc/systemd/system/musicfig.service
    rm -f musicfig.service-temp
    sudo chown root:root /etc/systemd/system/musicfig.service
    sudo chmod 644 /etc/systemd/system/musicfig.service
    sudo systemctl daemon-reload
    sudo systemctl enable musicfig.service
    echo "[INFO] Starting Musicfig server"
    sudo systemctl restart musicfig.service
    echo "[INFO] See the musicfig.log file for application logs."
}

check_python_version
git_pull
apt_get
pip_install
setup_usb
setup_files
install_startup

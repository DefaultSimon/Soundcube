#!/usr/bin/env bash

# Show welcome message
echo "Welcome to the Soundcube Dependency Installer!"
echo "!! CAREFUL: This script needs sudo permissions !!"
echo "This script will install necessary dependencies for Soundcube to work, including:"
echo "vlc, git, nano, htop, openssl and pulseaudio"
echo "along with: NodeJS 11 and Python 3.7 and their dependencies"
echo "If you have any of these installed, please install dependencies manually, looking at the individual steps in this script."
echo "Otherwise, press ENTER to start."

# Wait for ENTER
read -n 1 -s

mkdir tempPython
cd tempPython

# Install apt dependencies
echo "[Installer] Installing dependencies with apt-get..."
sudo apt-get update -y
sudo apt-get install -y vlc git nano htop openssl pulseaudio

# Install NodeJS 11
echo "[Installer] Installing NodeJS"
# Binary distribution from https://github.com/nodesource/distributions/blob/master/README.md
curl -sL https://deb.nodesource.com/setup_11.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Python 3.7
echo "[Installer] Installing Python dependencies..."
sudo apt-get install -y build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev libffi-dev uuid-dev

echo "[Installer] Downloading Python source..."
wget https://www.python.org/ftp/python/3.7.3/Python-3.7.3.tar.xz
tar xf Python-3.7.3.tar.xz
cd Python-3.7.3

echo "[Installer] Configuring and making, this will take a while..."
sudo ./configure --with-optimizations --with-lto
sudo make -j 3

echo "[Installer] Installing Python 3.7..."
sudo make altinstall

echo "[Installer] Cleaning up..."
cd ..
cd ..
rm -rf tempPython

echo "[Installer] Installing pipenv..."
python3.7 -m pip install pipenv

echo "[Installer] Setting up pipenv..."
pipenv --python 3.7

# Include the cleanup below, if necessary

# echo "[Installer] Removing dependencies..."
# sudo apt-get remove --purge -y build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev libffi-dev uuid-dev
# sudo apt-get autoremove -y
# sudo apt-get clean
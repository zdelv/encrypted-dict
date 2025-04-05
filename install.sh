#!/bin/bash

while [[ $# -gt 0 ]]; do
  case $1 in
    --git)
      SSH_CONFIG=$2
      shift
      shift
      ;;
    --install-dir)
      INSTALL_DIR=$2
      shift
      shift
      ;;
    *)
      echo "Unknown argument"
      exit 1
      ;;
  esac
end

if [ -z ${INSTALL_DIR+x} ]; then
  INSTALL_DIR=/usr/local/encrypted_dict
fi

if [ -z ${SSH_CONFIG+x} ]; then
  git clone https://github.com/zdelv/encrypted_dict $INSTALL_DIR
else
  git clone git@${SSH_CONFIG}:zdelv/encrypted_dict $INSTALL_DIR
fi

cd $INSTALL_DIR
python3 -m venv .venv
pip install .
echo "Installed to /usr/local/encrypted_dict."
echo "Added symlink to encdb to /usr/local/bin/"
echo ""
echo "Run encdb to access the db"

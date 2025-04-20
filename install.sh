#!/bin/bash

while [[ $# -gt 0 ]]; do
  case $1 in
    --git)
      SSH_CONFIG="$2"
      shift
      shift
      ;;
    --install-dir)
      INSTALL_DIR="$2"
      shift
      shift
      ;;
    --uninstall)
      UNINSTALL=1
      shift
      ;;
    *)
      echo "Unknown argument $1"
      exit 1
      ;;
  esac
done

if [ -n "$UNINSTALL" ]; then
  DIR=$(dirname $(dirname $(dirname $(realpath $(which encdb)))))
  read -p "Uninstall encrypted-dict (located at $DIR)? [y/N]: " USER_INPUT
  if [ -n "$USER_INPUT" ] && [[ $USER_INPUT == [Yy] ]]; then
    rm ~/.local/bin/encdb
    rm -rf $DIR
    exit 1
  else
    echo "Exiting without uninstalling"
    exit 1
  fi
fi

if [ -z ${INSTALL_DIR+x} ]; then
  INSTALL_DIR=/usr/local/encrypted_dict
fi

if [ -z ${SSH_CONFIG+x} ]; then
  git clone https://github.com/zdelv/encrypted-dict $INSTALL_DIR
else
  git clone git@${SSH_CONFIG}:zdelv/encrypted-dict $INSTALL_DIR
fi

if [[ $? -ne 0 ]]; then
  echo "Failed to pull repo"
  exit 1
fi

cd $INSTALL_DIR
python3 -m venv .venv
.venv/bin/pip install .
ln -s $(realpath .venv/bin/encdb) ~/.local/bin/encdb
echo "Installed to ${INSTALL_DIR}"
echo "Added symlink to encdb to ~/.local/bin/encdb"
echo ""
echo "Run encdb to access the db"

#!/bin/bash
set -e

echo "Installing camilladsp-autoswitch..."

pip install .

install -m 644 systemd/camilladsp-autoswitch.service /etc/systemd/system/

systemctl daemon-reload

echo "Installation complete."

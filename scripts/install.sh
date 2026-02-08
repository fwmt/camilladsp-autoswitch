#!/bin/bash
set -e

echo "Installing camilladsp-control..."

pip install .

install -m 644 systemd/camilladsp-control.service /etc/systemd/system/

systemctl daemon-reload

echo "Installation complete."

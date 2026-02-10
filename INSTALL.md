# Installation Guide — camilladsp-autoswitch

## Requirements

- Linux
- Python >= 3.10
- CamillaDSP installed
- systemd (recommended)

## Install

```bash
pip install camilladsp-autoswitch
```

## Directory Layout

```
/etc/camilladsp-autoswitch/
├── mapping.yml
└── profiles/
    ├── music.yml
    ├── cinema.yml
    └── cinema.night.yml
```

## Register Profiles

```bash
cdspctl profile-add music music.yml
cdspctl profile-add cinema cinema.yml
cdspctl profile-add cinema cinema_night.yml --variant night
```

## systemd Example

```ini
[Unit]
Description=CamillaDSP Autoswitch
After=camilladsp.service

[Service]
ExecStart=/usr/bin/python -m camilladsp_autoswitch.autoswitch
Restart=always

[Install]
WantedBy=multi-user.target
```

## Verify

```bash
cdspctl status
```

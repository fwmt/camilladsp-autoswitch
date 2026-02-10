# camilladsp-autoswitch

Automatic, safe, and predictable profile switching for **CamillaDSP**.

`camilladsp-autoswitch` is a lightweight event-driven controller that automatically switches CamillaDSP DSP profiles based on media activity (e.g. Kodi), while still providing full manual control, strict validation, and production-safe behavior.

It does **not** replace CamillaDSP or CamillaGUI.
It **complements** them.

## Features

- Automatic switching between music and cinema DSP profiles
- Manual override modes (auto / manual)
- Declarative `mapping.yml`
- Safe experimental YAML testing
- Real CamillaDSP binary validation
- Event-driven architecture
- Clean CLI (`cdspctl`)
- Full automated test coverage

## Quick Start

```bash
pip install camilladsp-autoswitch
export CDSP_CONFIG_DIR=/etc/camilladsp-autoswitch
export CDSP_STATE_DIR=/run/cdsp
cdspctl mapping init
cdspctl mapping validate
```

## CLI Overview

```bash
cdspctl status
cdspctl auto
cdspctl manual
cdspctl profile music
cdspctl variant night
cdspctl experimental on test.yml
cdspctl experimental off
```

## Media Mapping

```bash
cdspctl mapping init
cdspctl mapping show
cdspctl mapping validate
cdspctl mapping test on
cdspctl mapping test off
```

## License

MIT

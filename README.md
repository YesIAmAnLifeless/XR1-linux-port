# XR1-linux-port

Unofficial Linux wrapper for the Section XR1 mouse configuration software.
It runs the Windows app under Wine and uses a small Python HID proxy so the
app can talk to the mouse.

Not affiliated with Section. Tested only with a Section XR1 (USB ID 30fa:1440).

## How it works

- `xr1proxy.py` creates a virtual HID device (via `/dev/uhid`) that Wine can see,
  and forwards the app's feature reports to the real mouse. It logs every report to
  `/tmp/xr1_log.txt`.
- `xr1-wine` copies the app into a private Wine prefix
  (`~/.local/share/xr1-wine`), starts the proxy, and launches the app.
- `fixperm.sh` makes the virtual device readable by your user.

## Install (Arch Linux)

The Section software is not included. Download the installer `Section_XR1.exe`
from Section, put it next to the PKGBUILD, and build:

    makepkg -si

The PKGBUILD checks the installer against this SHA-256, so use the same file:

    5899be89ab039963e69b20f77b5ceabb5568146819ceedd16bf87521c823bdae

The installer is unpacked at build time with `innoextract`; nothing from it is
stored in this repository.

## Use

Run `xr1-wine` or start "Section XR1 Mouse Software" from your menu. A polkit
prompt starts the proxy service. Stop it afterwards with:

    sudo systemctl stop xr1-proxy

## Warnings

- The proxy runs as a **root** service and creates a **world-writable** virtual
  HID device. Any local user could write to it while it is running.
- The app writes settings to the mouse's onboard memory. While developing this, a
  profile write once reset the lighting to the default effect. If your mouse
  misbehaves, reset it with Section's official Windows software.
- Do not use the app's firmware update function through this wrapper.

## License

The code in this repository is MIT licensed (see `LICENSE`). The Section XR1
software is not included and remains the property of its owner.

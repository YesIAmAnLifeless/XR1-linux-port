# XR1-linux-port

An unofficial Linux wrapper for the **Section XR1** mouse configuration software. It runs the official Windows application under Wine, paired with a lightweight Python HID proxy to bridge communication between the application and the physical mouse.

> **Disclaimer:** This project is not affiliated with, endorsed by, or connected to Section. Tested exclusively with the Section XR1 (`USB ID 30fa:1440`).

---

## Architecture & How It Works

- **`xr1proxy.py`** — Creates a virtual HID device via `/dev/uhid`, exposed to Wine. It captures and forwards the application's feature reports directly to the real mouse and logs all communication to `/tmp/xr1_log.txt`.
- **`xr1-wine`** — Manages an isolated Wine prefix located at `~/.local/share/xr1-wine`, automatically starts the proxy service, and launches the configuration utility.
- **`fixperm.sh`** — Adjusts permissions to ensure the virtual HID device is accessible to your local user.

---

## Installation

Choose the installation method that matches your Linux distribution.

### 🐧 Arch Linux

#### Option A: Install the prebuilt package

```bash
sudo pacman -U xr1-wine-1.0.1-1-any.pkg.tar.zst
```

#### Option B: Build from the PKGBUILD

1. Download the official Windows installer (`Section_XR1.exe`) from Section and place it alongside the `PKGBUILD` file.
2. Build and install the package:

   ```bash
   makepkg -si
   ```

The `PKGBUILD` verifies the installer against the following SHA-256 checksum:

```text
5899be89ab039963e69b20f77b5ceabb5568146819ceedd16bf87521c823bdae
```

### 🐧 Debian / Ubuntu

Install the prebuilt `.deb` package:

```bash
sudo apt install ./xr1-wine-1.0.1-1.deb
```

---

## Usage

1. Launch the application by running `xr1-wine` in your terminal, or open **Section XR1 Mouse Software** from your desktop environment's application menu.
2. When prompted, authorize the startup of the background proxy service through Polkit.
3. Configure your mouse using the official application.

### Stopping the Proxy Service

When you have finished configuring your mouse, you can stop the proxy service manually if needed:

```bash
sudo systemctl stop xr1-proxy
```

---

## Warnings & Precautions

### Security Considerations

The proxy service runs with root privileges and creates a world-writable virtual HID device (`/dev/uhid`). While the service is running, any local user on the system may be able to write to this device.

**Use this wrapper only if you understand and accept the associated security risks.** Consider restricting access to the virtual HID device rather than making it world-writable.

### Onboard Memory

The software writes configurations directly to the mouse's onboard memory. Writing profiles may occasionally reset lighting effects to their default settings.

If your mouse behaves unexpectedly, dual boot your mouse or leave it unplugged to reset it

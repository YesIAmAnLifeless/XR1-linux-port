#!/usr/bin/env python3
# XR1 proxy: makes a fake HID device (only the vendor part) so Wine will show it
# to the mouse app. Forwards app commands to the real mouse and logs every byte.
# Run:  sudo python3 xr1proxy.py
import os, sys, glob, fcntl, select, struct, time

VENDOR_RD = bytes.fromhex(
    "0600ff0901a1018506150026ff00092f950275088102c0"
    "0601ff0901a1018507150026ff00092095077508b102c0")
VID, PID = 0x30FA, 0x1440
LOG = "/tmp/xr1_log.txt"
EV = 4376  # size of struct uhid_event


def ioc(nr, size):
    # HIDIOCGFEATURE (nr 7) / HIDIOCSFEATURE (nr 6)
    return 0xC0000000 | (size << 16) | (0x48 << 8) | nr


def find_real():
    for d in sorted(glob.glob("/sys/class/hidraw/hidraw*")):
        try:
            if "/usb" not in os.path.realpath(d):
                continue  # skip virtual devices
            rd = open(d + "/device/report_descriptor", "rb").read()
            if VENDOR_RD[23:] in rd:
                return "/dev/" + os.path.basename(d)
        except Exception:
            pass
    return None


def log(tag, data):
    line = "%s %s %s" % (time.strftime("%H:%M:%S"), tag, bytes(data).hex(" "))
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")


def pad(b):
    return b.ljust(EV, b"\0")


def main():
    if os.geteuid() != 0:
        sys.exit("run with sudo")
    path = find_real()
    if not path:
        sys.exit("real mouse not found")
    real = os.open(path, os.O_RDWR)
    print("real mouse:", path)
    u = os.open("/dev/uhid", os.O_RDWR)
    create = struct.pack("<I128s64s64sHHIIII", 11, b"Section XR1", b"", b"",
                         len(VENDOR_RD), 3, VID, PID, 0x0100, 0) + VENDOR_RD
    os.write(u, pad(create))
    print("fake device up. In other terminal: chmod 666 /dev/hidraw*, then start app. Ctrl+C stops.")
    print("log file:", LOG)
    try:
        while True:
            r, _, _ = select.select([u, real], [], [])
            if u in r:
                ev = os.read(u, EV)
                t = struct.unpack_from("<I", ev)[0]
                if t == 9:  # GET_REPORT
                    rid, rnum, rtype = struct.unpack_from("<IBB", ev, 4)
                    size = 8 if rnum == 7 else 64
                    buf = bytearray(size)
                    buf[0] = rnum
                    err = 0
                    try:
                        n = fcntl.ioctl(real, ioc(0x07, size), buf)
                        data = bytes(buf[:n]) if n > 0 else bytes(buf)
                    except OSError as e:
                        err = e.errno or 5
                        data = b""
                    log("GET" if not err else "GET!%d" % err, data)
                    os.write(u, pad(struct.pack("<IIHH", 10, rid, err, len(data)) + data))
                elif t == 13:  # SET_REPORT
                    rid, rnum, rtype, size = struct.unpack_from("<IBBH", ev, 4)
                    data = ev[12:12 + size]
                    if not data or data[0] != rnum:
                        data = bytes([rnum]) + data
                    err = 0
                    try:
                        fcntl.ioctl(real, ioc(0x06, len(data)), bytearray(data))
                    except OSError as e:
                        err = e.errno or 5
                    log("SET" if not err else "SET!%d" % err, data)
                    os.write(u, pad(struct.pack("<IIH", 14, rid, err)))
            if real in r:
                try:
                    d = os.read(real, 64)
                except OSError:
                    print("real mouse gone")
                    break
                if d and d[0] == 6:
                    d = d[:3].ljust(3, b"\0")  # fake descriptor: ID + 2 bytes
                    os.write(u, pad(struct.pack("<IH", 12, len(d)) + d))
                    log("IN ", d)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            os.write(u, pad(struct.pack("<I", 1)))
        except OSError:
            pass
        os.close(u)
        os.close(real)


main()

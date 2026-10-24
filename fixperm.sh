#!/bin/sh
for i in 1 2 3 4 5 6 7 8 9 10; do
  for d in /sys/devices/virtual/misc/uhid/*/hidraw/hidraw*; do
    [ -e "$d" ] && chmod 666 "/dev/${d##*/}" && exit 0
  done
  sleep 0.5
done

#!/usr/bin/env python
import os
import fcntl
import sys
import enum
import time

# https://github.com/torvalds/linux/blob/b65054597872ce3aefbc6a666385eabdf9e288da/include/uapi/linux/cdrom.h#L126-L127
CDROM_DRIVE_STATUS = 0x5326  # Get tray position, etc.
CDROM_DISC_STATUS = 0x5327  # Get disc type, etc.


class CDS(enum.Enum):
    # https://github.com/torvalds/linux/blob/b65054597872ce3aefbc6a666385eabdf9e288da/include/uapi/linux/cdrom.h#L398-L403
    # Drive status possibilities returned by CDROM_DRIVE_STATUS ioctl
    NO_INFO = 0
    NO_DISC = 1
    TRAY_OPEN = 2
    DRIVE_NOT_READY = 3
    DISC_OK = 4

    # Return values for the CDROM_DISC_STATUS ioctl
    # Can also return NO_[INFO|DISC], from above
    AUDIO = 100
    DATA_1 = 101
    DATA_2 = 102
    XA_2_1 = 103
    XA_2_2 = 104
    MIXED = 105


def drive_open(drive):
    cmd = "eject {}".format(drive)
    # print(cmd)
    os.system(cmd)


def get_status(drive, drive_status=True):
    call = CDROM_DRIVE_STATUS if drive_status else CDROM_DISC_STATUS
    # https://askubuntu.com/a/1022721
    fd = os.open(drive, os.O_RDONLY | os.O_NONBLOCK)
    res = fcntl.ioctl(fd, call)
    os.close(fd)
    return CDS(res)


CANDIDATES = [
    "/dev/sr0",
    "/dev/dvd",
    "/dev/cdrom",
]


def guess_drive_path():
    for dev in CANDIDATES:
        if os.path.exists(dev):
            return os.path.realpath(dev)


def demand_disc(drive):
    """
    Block while there is no disk in drive.
    Eject drive if no disk.
    """
    while True:
        time.sleep(0.1)
        ds = get_status(drive)
        # print(ds.name)
        if ds == CDS.NO_INFO:
            raise NotImplementedError("Drive does not implement the CDROM_DRIVE_STATUS ioctl call")
        elif ds == CDS.DISC_OK:
            return get_status(drive, False)
        elif ds == CDS.NO_DISC:
            drive_open(drive)
            time.sleep(1)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        drive = guess_drive_path()
    else:
        drive = sys.argv[1]
    exit(demand_disc(drive).value)

# Python API for Bluefruit LE Sniffer 

This repository contains the Python API for Nordic's BLE Sniffer, and easy to use API wrapper.
Supports **live capture** on Windows, Linux, and OSX.

It has been tested on the following platforms using Python 2.7:

- OSX 10.10
- Windows 10 x64
- Ubuntu 16.10

## Hardware

* Seeed Tiny BLE            **≈ $14**
* Bluefruit LE Sniffer      **≈ $30**
* RedBear BLE Nano Kit      **≈ $33**
* Other nRF51 Dev Kits

# Sniffer Python Wrapper

Running sniffer.py in this folder on the Bluefruit LE Friend Sniffer Edition board will cause the device to scan for Bluetooth LE devices in range, and log any data from the selected device to a libpcap file (in `logs/capture.pcap`) that can be opened in Wireshark.

The current example does not enable live streaming of data directly into Wireshark via named pipes since this would require a pre-compiled utility for each platform, but it should be possible to implement this on your platform if required.


## Using sniffer.py

To use sniffer.py, simply specify the serial port where the sniffer can be found (ex. `COM14` on Windows, `/dev/tty.usbmodem1412311` on OS X, `/dev/ttyACM0` or Linux, etc.):

```
python sniffer.py /dev/tty.usbmodem1412311
```

**Note:** You may need to run python with `sudo` on Linux.

This will create a new log file and start scanning for BLE devices, which should result in the following menu:

```
$ python sniffer.py /dev/tty.usbmodem1412311
Logging data to logs/capture.pcap
Connecting to sniffer on /dev/tty.usbmodem1412311
Scanning for BLE devices (5s) ...
Found 2 BLE devices:

  [1] "" (14:99:E2:05:29:CF, RSSI = -85)
  [2] "" (E7:0C:E1:BE:87:66, RSSI = -49)

Select a device to sniff, or '0' to scan again
> 
```

Simply select the device you wish to sniff, and it will start logging traffic from the specified device.

Type **CTRL+C** to stop sniffing and quit the application, closing the libpcap log file.

**NOTE:** You may need to remove the sniffer and re-insert it before starting a new session if you see any unusual error messages running sniffer.py.

## Requirements

This Python script will require that both Python 2.7 and **pySerial** are installed on your system.
For Windows live capture support, you need to install **PyWin32**.

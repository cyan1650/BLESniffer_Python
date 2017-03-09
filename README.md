# Python API for nRF BLE Sniffer

This repository contains the Python API for Nordic's BLE Sniffer, and easy to use sniffer tool.

## Features

* **Live capture** on Windows, Linux, and OSX.
* Auto-start Wireshark in live mode
* Supports **Wireshark 2.x** using Lua dissector
* Python 3 support (not stable yet)

It has been tested on the following platforms using Python 2.7:

- Windows 10 x64
- Ubuntu 16.10
- OSX 10.10

## Hardware support

* Seeed Tiny BLE            **≈ $14**
* Bluefruit LE Sniffer      **≈ $30**
* RedBear BLE Nano Kit      **≈ $33**
* Other nRF51 Dev Kits

## Using sniffer.py

Running sniffer.py in this folder will cause the device to scan for Bluetooth LE devices in range, and log any data from the selected device to a libpcap file (in `logs/capture.pcap`) that can be opened in Wireshark.

Please specify the serial port where the sniffer can be found (ex. `COM14` on Windows, `/dev/tty.usbmodem1412311` on OSX, `/dev/ttyACM0` on Linux):

```
python sniffer.py /dev/ttyACM0
```

You can also start Wireshark in **live capture mode**:

```
python ./sniffer.py --pipe /dev/ttyACM0
```

This will create a log file and start scanning for BLE devices, which should result in the following menu:

```
$ python sniffer.py /dev/ttyACM0
Logging data to logs/capture.pcap
Connecting to sniffer on /dev/ttyACM0
Scanning for BLE devices (5s) ...
Found 2 BLE devices:

  [1] "" (14:99:E2:05:29:CF, RSSI = -85)
  [2] "My device" (E7:0C:E1:BE:87:66, RSSI = -49)

Select a device to sniff, or '0' to scan again
> 
```

Simply select the device you wish to sniff, and it will start logging traffic from the specified device.

Type **CTRL+C** to stop sniffing and quit the application, closing the libpcap log file.

## Requirements

This Python script will require that both Python 2.7 and **pySerial** are installed on your system.
For Windows live capture support, you need to install **PyWin32**.

## Known issues and limitations

* The sniffer board may need to be re-inserted before starting a new session.
* You may need to run python with `sudo` on Linux.
* On Windows, if you have both python2 and python3 installed, you may need to run with `py -2 sniffer.py ...` command.
* The list of known issues is [here](https://github.com/vshymanskyy/BLESniffer_Python/issues)

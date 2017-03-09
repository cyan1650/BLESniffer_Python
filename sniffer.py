#!/usr/bin/env python

__author__    = "ktown"
__copyright__ = "Copyright Adafruit Industries 2014 (adafruit.com)"
__license__   = "MIT"
__version__   = "0.1.0"

import os
import sys
import time
import argparse
import subprocess

from SnifferAPI import Sniffer
from SnifferAPI import CaptureFiles
from SnifferAPI.Devices import Device
from SnifferAPI.Devices import DeviceList
from SnifferAPI.PcapPipe import PcapPipe

mySniffer = None
"""@type: SnifferAPI.Sniffer.Sniffer"""

myPipe = None
"""@type: PcapPipe.PcapPipe"""

def setup(serport, delay=1):
    """
    Tries to connect to and initialize the sniffer using the specific serial port
    @param serport: The name of the serial port to connect to ("COM14", "/dev/tty.usbmodem1412311", etc.)
    @type serport: str
    @param delay: Time to wait for the UART connection to be established (in seconds)
    @param delay: int
    """
    global mySniffer

    # Initialize the device on the specified serial port
    print("Connecting to sniffer on " + serport)
    mySniffer = Sniffer.Sniffer(serport)
    # Start the sniffer
    mySniffer.start()
    # Wait a bit for the connection to initialise
    time.sleep(delay)


def scanForDevices(scantime=5):
    """
    @param scantime: The time (in seconds) to scan for BLE devices in range
    @type scantime: float
    @return: A DeviceList of any devices found during the scanning process
    @rtype: DeviceList
    """
    if args.verbose:
        print("Starting BLE device scan ({0} seconds)".format(str(scantime)))

    mySniffer.scan()
    time.sleep(scantime)
    devs = mySniffer.getDevices()
    return devs


def selectDevice(devlist):
    """
    Attempts to select a specific Device from the supplied DeviceList
    @param devlist: The full DeviceList that will be used to select a target Device from
    @type devlist: DeviceList
    @return: A Device object if a selection was made, otherwise None
    @rtype: Device
    """
    count = 0

    if len(devlist):
        print("Found {0} BLE devices:\n".format(str(len(devlist))))
        # Display a list of devices, sorting them by index number
        for d in devlist.asList():
            """@type : Device"""
            count += 1
            print("  [{0}] {1} ({2}:{3}:{4}:{5}:{6}:{7}, RSSI = {8})".format(count, d.name,
                                                                             "%02X" % d.address[0],
                                                                             "%02X" % d.address[1],
                                                                             "%02X" % d.address[2],
                                                                             "%02X" % d.address[3],
                                                                             "%02X" % d.address[4],
                                                                             "%02X" % d.address[5],
                                                                             d.RSSI))
        try:
            i = int(input("\nSelect a device to sniff, or '0' to scan again\n> "))
        except KeyboardInterrupt:
            raise KeyboardInterrupt
            return None
        except:
            return None

        # Select a device or scan again, depending on the input
        if (i > 0) and (i <= count):
            # Select the indicated device
            return devlist.find(i - 1)
        else:
            # This will start a new scan
            return None

def loop():
    """Main loop printing some useful statistics"""
    nLoops = 0
    nPackets = 0
    connected = False

    while True:
        time.sleep(0.1)

        packets   = mySniffer.getPackets()
        nLoops   += 1
        nPackets += len(packets)

        if args.verbose:
            for packet in packets:
                if packet.blePacket is not None:
                    # Display the raw BLE packet payload
                    # Note: 'BlePacket' is nested inside the higher level 'Packet' wrapper class
                    print(str(packet.blePacket.payload))
                else:
                    print(str(packet))
        else:
            '''
            for packet in packets:
                if packet.valid:
                    sys.stdout.write('.')
                else:
                    sys.stdout.write('x')
            sys.stdout.write('\n')
            '''
            if connected != mySniffer.inConnection or nLoops % 20 == 0:
                connected = mySniffer.inConnection
                sys.stdout.write("\rconnected: {}, packets: {}, missed: {}".format(mySniffer.inConnection, nPackets, mySniffer.missedPackets))
                sys.stdout.flush()


def findWireshark():
    if sys.platform == 'win32':
        programs = [ "Wireshark.exe", "WiresharkPortable.exe" ]
    else:
        programs = [ "wireshark" ]

    pathenv = os.environ["PATH"]

    if 'PROGRAMFILES' in os.environ:
        pathenv += os.pathsep + os.path.join(os.environ['PROGRAMFILES'], 'Wireshark')

    if 'PROGRAMFILES(X86)' in os.environ:
        pathenv += os.pathsep + os.path.join(os.environ['PROGRAMFILES(X86)'], 'Wireshark')

    pathenv += os.pathsep + os.path.join(os.path.expanduser('~'), 'Downloads', 'WiresharkPortable')

    #print("Looking for WS: " + pathenv)

    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    for path in pathenv.split(os.pathsep):
        path = path.strip('"')
        for program in programs:
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return programs[0]

def setupPipe():
    """setup pipe"""
    # Create a named pipe for Wireshark capture
    myPipe = PcapPipe('ble.pipe')

    ws_app = findWireshark()
    ws_script = 'lua_script:nordic_ble.lua'
    ws_filter = '!(btle.data_header.length==0)'
    ws_cmd = '%s -X %s -Y "%s" -i "%s" -k' % (ws_app, ws_script, ws_filter, myPipe.getPipeName())

    print("Run: " + ws_cmd)

    try:
        proc = subprocess.Popen(ws_cmd, shell = True)
    except:
        pass

    print("Waiting for Wireshark...")
    myPipe.open()
    mySniffer.subscribe("NEW_BLE_PACKET", myPipe.newBlePacket)


if __name__ == '__main__':
    """Main program execution point"""

    # Instantiate the command line argument parser
    argparser = argparse.ArgumentParser(description="Interacts with the Bluefruit LE Friend Sniffer firmware")

    # Add the individual arguments
    # Mandatory arguments:
    argparser.add_argument("serialport",
                           help="serial port location ('COM14', '/dev/tty.usbserial-DN009WNO', etc.)")

    # Optional arguments:
    argparser.add_argument("-p", "--pipe",
                           dest="pipe",
                           action="store_true",
                           default=False,
                           help="Pipe packets to wireshark")

    argparser.add_argument("-l", "--logfile",
                           dest="logfile",
                           default=CaptureFiles.captureFilePath,
                           help="log packets to file, default: " + CaptureFiles.captureFilePath)

    argparser.add_argument("-t", "--target",
                           dest="target",
                           help="target device address")

    argparser.add_argument("-r", "--random_txaddr",
                           dest="txaddr",
                           action="store_true",
                           default=False,
                           help="Target device is using random address")

    argparser.add_argument("-v", "--verbose",
                           dest="verbose",
                           action="store_true",
                           default=False,
                           help="verbose mode (all serial traffic is displayed)")

    # Parser the arguments passed in from the command-line
    args = argparser.parse_args()

    # Display the libpcap logfile location
    print("Capturing data to " + args.logfile)
    CaptureFiles.captureFilePath = args.logfile

    # Try to open the serial port
    try:
        setup(args.serialport)
    except OSError:
        # pySerial returns an OSError if an invalid port is supplied
        print("Unable to open serial port '" + args.serialport + "'")
        sys.exit(-1)
    except KeyboardInterrupt:
        sys.exit(-1)

    # Display some information about the sniffer
    print("Software Version: " + str(mySniffer.swversion))
    print("Firmware Version: " + str(mySniffer.fwversion))

    if mySniffer.fwversion == 0:
        print("Sniffer board is not responding. Please re-plug the board.")
        sys.exit(-1)
    elif mySniffer.fwversion != 1111:
        print("Sniffer board FW version is invalid.")

    # Scan for devices in range until the user makes a selection
    try:
        d = None
        """@type: Device"""
        if args.target:
            print("Specified target device " + args.target)
            _mac = map(lambda x: int(x, 16) , args.target.split(':'))
            if len(_mac) != 6:
                raise ValueError("Invalid device address")
            # -72 seems reasonable for a target device right next to the sniffer
            d = Device(_mac, name="NoDeviceName", RSSI=-72, txAdd=args.txaddr)

        # loop will be skipped if a target device is specified on commandline
        while d is None:
            print("Scanning for BLE devices (5s) ...")
            devlist = scanForDevices()
            if len(devlist):
                # Select a device
                d = selectDevice(devlist)

        # Start sniffing the selected device
        print("Attempting to follow device {0}:{1}:{2}:{3}:{4}:{5}".format("%02X" % d.address[0],
                                                                           "%02X" % d.address[1],
                                                                           "%02X" % d.address[2],
                                                                           "%02X" % d.address[3],
                                                                           "%02X" % d.address[4],
                                                                           "%02X" % d.address[5]))
        # TODO: Make sure we actually followed the selected device (i.e. it's still available, etc.)
        if d is not None:
            if args.pipe:
                setupPipe()

            mySniffer.follow(d)

        else:
            print("ERROR: Could not find the selected device")

        loop()

        # Close gracefully
        mySniffer.doExit()
        if myPipe is not None:
            myPipe.close()
        sys.exit()

    except (KeyboardInterrupt, ValueError, IndexError) as e:
        # Close gracefully on CTRL+C
        if 'KeyboardInterrupt' not in str(type(e)):
            print("Caught exception:" + str(e))
        mySniffer.doExit()
        if myPipe is not None:
            myPipe.close()
        sys.exit(-1)

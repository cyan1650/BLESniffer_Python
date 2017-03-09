import logging
import os
import sys
import time

__author__    = "Volodymyr Shymanskyy"
__license__   = "MIT"
__version__   = "0.1.0"

class PipeUnix():
    def __init__(self, pipeName):
        from SnifferAPI import Logger

        self._pipeName = os.path.join(Logger.logFilePath, pipeName)

        if os.path.exists(self._pipeName):
            os.remove(self._pipeName)

        try:
            os.mkfifo(self._pipeName)
        except OSError:
            logging.warn("fifo already exists?")
            raise SystemExit(1)

    def getPipeName(self):
        return self._pipeName

    def open(self):
        import fcntl

        self._pipe = open(self._pipeName, 'wb')

    def close(self):
        self._pipe.close()
        self._pipe = None

    def write(self, data):
        if not self._pipe: return
        try:
            self._pipe.write(data)
            self._pipe.flush()
        except IOError:
            exc_type, exc_value, exc_tb = sys.exc_info()
            logging.error('Got exception trying to write to pipe: %s', exc_value)
            self.close()

class PipeWin32():
    def __init__(self, pipeName):
        self._pipeName = r"\\.\pipe\%s" % pipeName
        
    def getPipeName(self):
        return self._pipeName
    
    def open(self):
        import win32pipe

        self._pipe = win32pipe.CreateNamedPipe(
            self._pipeName,
            win32pipe.PIPE_ACCESS_OUTBOUND,
            win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_WAIT,
            1, 65536, 65536,
            300,
            None)
            
        if not self._pipe:
            raise SystemExit(1)

        win32pipe.ConnectNamedPipe(self._pipe, None)

    def close(self):
        win32pipe.DisconnectNamedPipe(self._pipe)
        self._pipe.Close()
        self._pipe = None

    def write(self, data):
        if not self._pipe: return
        try:
            import win32file
            win32file.WriteFile(self._pipe, data)
        except IOError:
            exc_type, exc_value, exc_tb = sys.exc_info()
            logging.error('Got exception trying to write to pipe: %s', exc_value)
            self.close()


class PcapPipe(object):
    def __init__(self, pipeName):
        if (sys.platform.startswith('linux') or sys.platform == 'darwin'):
            self._pipe = PipeUnix(pipeName)
        else:
            self._pipe = PipeWin32(pipeName)
            
    def open(self):
        self._pipe.open()
        self.write(self.makeGlobalHeader())

    def write(self, message):
        if not self._pipe: return
        try:
            self._pipe.write(''.join(map(chr, message)))
        except IOError:
            exc_type, exc_value, exc_tb = sys.exc_info()
            logging.error('Got exception trying to write to pipe: %s', exc_value)
            self.close()

    def getPipeName(self):
        return self._pipe.getPipeName()

    def close(self):
        logging.debug("closing pipe")
        if not self._pipe: return
        self._pipe.close()
        self._pipe = None

    def newBlePacket(self, notification):
        packet      = notification.msg["packet"]
        packetList  = packet.getList()
        snifferList = self.makePacketHeader(len(packetList) + 1) + [packet.boardId] + packetList
        self.write(snifferList)

    def makeGlobalHeader(self):
        LINKTYPE_BLUETOOTH_LE_LL    = 251
        LINKTYPE_NORDIC_BLE         = 157

        MAGIC_NUMBER                = 0xa1b2c3d4
        VERSION_MAJOR               = 2
        VERSION_MINOR               = 4
        THISZONE                    = 0
        SIGFIGS                     = 0
        SNAPLEN                     = 0xFFFF
        NETWORK                     = LINKTYPE_NORDIC_BLE

        headerString = [
                            ((MAGIC_NUMBER  >>  0) & 0xFF),
                            ((MAGIC_NUMBER  >>  8) & 0xFF),
                            ((MAGIC_NUMBER  >> 16) & 0xFF),
                            ((MAGIC_NUMBER  >> 24) & 0xFF),
                            ((VERSION_MAJOR >>  0) & 0xFF),
                            ((VERSION_MAJOR >>  8) & 0xFF),
                            ((VERSION_MINOR >>  0) & 0xFF),
                            ((VERSION_MINOR >>  8) & 0xFF),
                            ((THISZONE      >>  0) & 0xFF),
                            ((THISZONE      >>  8) & 0xFF),
                            ((THISZONE      >> 16) & 0xFF),
                            ((THISZONE      >> 24) & 0xFF),
                            ((SIGFIGS       >>  0) & 0xFF),
                            ((SIGFIGS       >>  8) & 0xFF),
                            ((SIGFIGS       >> 16) & 0xFF),
                            ((SIGFIGS       >> 24) & 0xFF),
                            ((SNAPLEN       >>  0) & 0xFF),
                            ((SNAPLEN       >>  8) & 0xFF),
                            ((SNAPLEN       >> 16) & 0xFF),
                            ((SNAPLEN       >> 24) & 0xFF),
                            ((NETWORK       >>  0) & 0xFF),
                            ((NETWORK       >>  8) & 0xFF),
                            ((NETWORK       >> 16) & 0xFF),
                            ((NETWORK       >> 24) & 0xFF)
                        ]

        return headerString

    def makePacketHeader(self, length):

        if(os.name == 'posix'):
            timeNow = time.time()
        else:
            timeNow = time.clock()

        TS_SEC      = int(timeNow)
        TS_USEC     = int((timeNow-TS_SEC)*1000000)
        INCL_LENGTH = length
        ORIG_LENGTH = length

        headerString = [
                            ((TS_SEC        >>  0) & 0xFF),
                            ((TS_SEC        >>  8) & 0xFF),
                            ((TS_SEC        >> 16) & 0xFF),
                            ((TS_SEC        >> 24) & 0xFF),
                            ((TS_USEC       >>  0) & 0xFF),
                            ((TS_USEC       >>  8) & 0xFF),
                            ((TS_USEC       >> 16) & 0xFF),
                            ((TS_USEC       >> 24) & 0xFF),
                            ((INCL_LENGTH   >>  0) & 0xFF),
                            ((INCL_LENGTH   >>  8) & 0xFF),
                            ((INCL_LENGTH   >> 16) & 0xFF),
                            ((INCL_LENGTH   >> 24) & 0xFF),
                            ((ORIG_LENGTH   >>  0) & 0xFF),
                            ((ORIG_LENGTH   >>  8) & 0xFF),
                            ((ORIG_LENGTH   >> 16) & 0xFF),
                            ((ORIG_LENGTH   >> 24) & 0xFF)
                        ]
        return headerString

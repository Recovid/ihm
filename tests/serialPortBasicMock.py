import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from monitor.communication import *
from threading import Thread
import time

class SendFileContent(Thread):
    def __init__(self, fileToSend, pipeToRightDataIn):
        Thread.__init__(self)
        self.fileToSend = fileToSend
        self.pipeToRightDataIn = pipeToRightDataIn

    def run(self):
        self.running=True
        prevTimestamp = 0
        with open(self.fileToSend, "r") as f:
            for line in f:
                print (line)
                msg = parse_msg(line)
                if isinstance(msg, DataMsg):
                    timestamp = msg.timestamp_ms
                    if prevTimestamp < timestamp:
                        time.sleep((timestamp - prevTimestamp)/1000)
                    prevTimestamp = timestamp
                self.pipeToRightDataIn.write(line)
                self.pipeToRightDataIn.flush()
        self.running=False

    def stop(self):
        self.running=False

with open("out", "r") as fOut:
    with open("in", "w") as fIn:
        sendingThread = SendFileContent(sys.argv[1], fIn)
        sendingThread.start()
        for line in fOut:
            print("RECV : ", line)
            msg = parse_msg(line)
            if isinstance(msg, SetMsg):
                resp = SetMsg(msg)
                fIn.write(serialize_msg(resp))
                fIn.flush()
                print("SEND : ", serialize_msg(resp))
        sendingThread.stop()

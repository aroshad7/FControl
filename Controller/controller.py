import threading
from barcode import *
from datetime import datetime
import pdf
import telnetlib
import json
import time

myHOST = "127.0.0.1"
myPORT = "5555"

availablePeople = {}
database = {}

timeThreshold = 300


def load_database():
    with open("database.json", 'r') as f:
        data = f.read()

    return json.loads(data)


class TelnetClient:
    def __init__(self, host, port):
        self.HOST = host.encode('utf-8')
        self.PORT = port.encode('utf-8')
        self.client = []

    def connect(self):
        try:
            self.client = telnetlib.Telnet(self.HOST, self.PORT, 5)
            return 1
        except Exception as e:
            print ("Client Opening Error ", e)
            return 0

    def sendData(self, message):
        try:
            self.client.write((message + "\n").encode('utf-8'))
            print ("data sent")
        except Exception as e:
            print ("client Writing ", e)

    def close(self):
        try:
            self.client.close()
        except Exception as e:
            print ("client closing ", e)


client = TelnetClient(myHOST, myPORT)
while not client.connect():
    time.sleep(1)
    print("Server connection failed! Retrying...")


class Thread(threading.Thread):
    def __init__(self, thread_id, name):
        threading.Thread.__init__(self)
        self.threadID = thread_id
        self.name = name

    def run(self):
        handle_barcode_scanner(on_input)


def on_input(scanned_word):
    print(scanned_word)
    if scanned_word in database:
        if scanned_word in availablePeople:
            currentTime = datetime.now()
            oldTime = datetime.strptime(availablePeople[scanned_word], "%Y-%m-%d %H:%M:%S.%f")
            if (currentTime - oldTime).total_seconds() > timeThreshold:
                # -1 the number in GUI
                print(database[scanned_word] + " is leaving!")
                client.sendData("1," + str(len(availablePeople)))
                availablePeople.pop(scanned_word)
            else:
                # send attention to GUI
                client.sendData("attention," + database[scanned_word])
                print(database[scanned_word] + ", are you already leaving or is this a mistake?")
        else:
            availablePeople[scanned_word] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            client.sendData("1," + str(len(availablePeople)))
            print("Welcome " + database[scanned_word] + "!")


load_database()

barcodeScannerThread = Thread(1, "barcodeThread")
barcodeScannerThread.start()

pdf.print_attendance_sheet(availablePeople, database)


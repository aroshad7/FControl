import threading
from barcode import *
from datetime import datetime
from pdf import print_attendance_sheet
import telnetlib
import json
from time import sleep
import RPi.GPIO as GPIO

myHOST = "192.168.43.150"
myPORT = "5555"

availablePeople = {}
leftPeople = {}
database = {}

timeThreshold = 300


def load_database():
    with open("database.json", 'r') as f:
        data = f.read()

    return json.loads(data)
database = load_database()
sleep(1)

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
            print("Client Opening Error ", e)
            return 0

    def sendData(self, message):
        try:
            self.client.write((message + "\n").encode('utf-8'))
            print("data sent")
        except Exception as e:
            print("client Writing ", e)

    def close(self):
        try:
            self.client.close()
        except Exception as e:
            print("client closing ", e)


client = TelnetClient(myHOST, myPORT)
while not client.connect():
    sleep(1)
    print("Server connection failed! Retrying...")


class Thread(threading.Thread):
    def __init__(self, thread_id, name):
        threading.Thread.__init__(self)
        self.threadID = thread_id
        self.name = name

    def run(self):
        handle_barcode_scanner(on_input)
        print("barcode thread exiting...")


def on_input(scanned_word):
    global availablePeople, leftPeople
    print("sc: " + scanned_word)
    if scanned_word in database:
        if scanned_word in availablePeople:
            print (availablePeople)
            currentTime = datetime.now()
            oldTime = datetime.strptime(availablePeople[scanned_word], "%Y-%m-%d %H:%M:%S.%f")
            if (currentTime - oldTime).total_seconds() > timeThreshold:
                # -1 the number in GUI
                print(database[scanned_word] + " is leaving!")
                availablePeople.pop(scanned_word)
                leftPeople[scanned_word] = currentTime.strftime("%Y-%m-%d %H:%M:%S.%f")
                client.sendData("1," + str(len(availablePeople)))
            else:
                # send attention to GUI
                client.sendData("attention," + database[scanned_word])
                print(database[scanned_word] + ", are you already leaving or is this a mistake?")
                while True:
                    if not GPIO.input(27):
                        client.sendData("action,2")
                        availablePeople.pop(scanned_word)
                        leftPeople[scanned_word] = currentTime.strftime("%Y-%m-%d %H:%M:%S.%f")
                        client.sendData("1," + str(len(availablePeople)))
                        print(database[scanned_word] + " is leaving!")
                        # yes
                        break
                    if not GPIO.input(22):
                        client.sendData("action,1")
                        # no
                        break
        else:
            print(leftPeople)
            if scanned_word in leftPeople:
                currentTime = datetime.now()
                oldTime = datetime.strptime(leftPeople[scanned_word], "%Y-%m-%d %H:%M:%S.%f")
                if (currentTime - oldTime).total_seconds() > timeThreshold:
                    # -1 the number in GUI
                    print(database[scanned_word] + " is arriving!")
                    leftPeople.pop(scanned_word)
                    availablePeople[scanned_word] = currentTime.strftime("%Y-%m-%d %H:%M:%S.%f")
                    client.sendData("1," + str(len(availablePeople)))
                else:
                    # send attention to GUI
                    client.sendData("attention," + database[scanned_word])
                    print(database[scanned_word] + ", are you already arriving back or is this a mistake?")
                    while True:
                        if not GPIO.input(27):
                            client.sendData("action,2")
                            leftPeople.pop(scanned_word)
                            availablePeople[scanned_word] = currentTime.strftime("%Y-%m-%d %H:%M:%S.%f")
                            client.sendData("1," + str(len(availablePeople)))
                            print(database[scanned_word] + " is arriving!")
                            # yes
                            break
                        if not GPIO.input(22):
                            client.sendData("action,1")
                            # no
                            break
            else:
                availablePeople[scanned_word] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                client.sendData("1," + str(len(availablePeople)))
                print("Welcome " + database[scanned_word] + "!")
        
        


barcodeScannerThread = Thread(1, "barcodeThread")
barcodeScannerThread.start()

GPIO.setmode(GPIO.BCM)  # set up BCM GPIO numbering
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # set GPIO25 as input (button)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # set GPIO25 as input (button)
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # set GPIO25 as input (button)
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # set GPIO25 as input (button)

printStatus = True
try:
    while True:  # this will carry on until you hit CTRL+C
        if not GPIO.input(17):  # if port 25 == 1
            if printStatus:
                print_attendance_sheet(availablePeople, database)
                client.sendData("print")
                # client.sendData("action,4")
                printStatus = False
                sleep(0.5)
            else:
                client.sendData("action,3")
                sleep(0.5)
                printStatus = True
            print("1")
        elif not GPIO.input(10):
            # code for power down
            print("4")

        sleep(0.1)  # wait 0.1 seconds

finally:  # this block will run no matter how the try block exits
    GPIO.cleanup()  # clean up after yourself

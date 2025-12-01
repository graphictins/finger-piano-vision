

import serial
import time

def sendOutput(pin=1, value=0.0, com='COM17', verbose=False) :

    arduino = serial.Serial(com, 9600, timeout=10)

    data = f"pin({pin})value({value})\n"

    if verbose : print(f"attemp to write {data.encode()}")

    arduino.write(data.encode())

    if verbose : print("attemp to close")

    arduino.close()

def sendSingle(pin=1, value=0.0, com='COM17') :

    arduino = serial.Serial(com, 9600, timeout=10)

    data = f"{value}\n"

    arduino.write(data.encode())

    arduino.close()


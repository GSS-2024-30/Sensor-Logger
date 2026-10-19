import json
import random
import threading
import time
from datetime import datetime
import os

running = threading.Event()
saved = 0
readings = []

class Sensor():
    def __init__(self,name,unit):
        self.name = name
        self.unit = unit


    def reading(self):
        return random.randint(10,100)

class TemperatureSensor(Sensor):
    def __init__(self,name):
        super().__init__(name,"C")


class BrakePressure(Sensor):
    def __init__(self,name):
        super().__init__(name,"P")

class VoltageSensor(Sensor):
    def __init__(self,name):
        super().__init__(name,"V")


def save_to_csv(datas, remainder,filename):
    exist = os.path.isfile(filename)
    with open(filename, "a") as file:
        if not exist:
            file.write("Date,Sensor,Value,Unit\n")

        for data in datas:
            file.write(f"{data[0]},{data[1]},{data[2]},{data[3]}\n")



def read_sensor(settings):
    global saved
    counter = 0
    n = settings["batch_size"]

    while True:

        if running.is_set():
            counter += 1
            temp, brake, battery = TemperatureSensor("Motor Temp"), BrakePressure("Brake Pressure"), VoltageSensor("Battery Voltage")
            temp_reading = temp.reading()
            brake_reading = brake.reading()
            battery_reading = battery.reading()
            print(f"{temp.name}: {temp_reading} {temp.unit} | {brake.name}: {brake_reading} {brake.unit} | {battery.name}: {battery_reading} {battery.unit} | Rounds: {counter}")
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            readings.append([now, temp.name, temp_reading, temp.unit])
            readings.append([now, brake.name, brake_reading, brake.unit])
            readings.append([now, battery.name, battery_reading, battery.unit])
            result = len(readings) % n
            if counter % n ==0:
                save_to_csv(readings[saved:],result,"final_readings.csv")
                saved = len(readings)

        time.sleep(settings["interval_seconds"])


def build_summary(readings):
    grouped = {}
    for reading in readings:
        name = reading[1]
        if not(name in grouped):
            grouped[name] = []
        grouped[name].append(reading[2])
    return grouped

def save_summary(grouped,filename):
    summary = {}
    for name in grouped:
        max_value = max(grouped[name])
        min_value = min(grouped[name])
        average_value = sum(grouped[name]) / len(grouped[name])
        count = len(grouped[name])
        summary[name] = {"max":max_value,"min": min_value,"average": average_value,"count": count}
    with open(filename, "w") as file:
        json.dump(summary, file, indent = 2)

def program_settings():
    try:
        with open("logger_config.json") as file:
            settings = json.load(file)
    except FileNotFoundError:
        settings = {"batch_size": 10,"interval_seconds": 1}

    return settings

settings = program_settings()
t = threading.Thread(target=read_sensor, args=(settings,), daemon=True)
t.start()



while True:
    user_input = input("Please enter s  for start, p for pause, and q for quit")
    user_input = user_input.upper()
    if user_input == "S":
        running.set()
    elif user_input == "P":
        running.clear()
    elif user_input == "Q":
        running.clear()
        time.sleep(settings["interval_seconds"])
        save_to_csv(readings[saved:],settings,"final_readings.csv")
        save_summary(build_summary(readings), "summary.json")
        break
# Zoned Heater Control

import paho.mqtt.client as mqtt
import json
import time
import random

MIN_TEMP = 8   # degrees celcius
MAX_TEMP = 30  # degrees celcius
MAX_VPOS = 255 # valve pos 8 bit precision
MAX_BATT = 100 # battery level

class Heater:
    def __init__(self):
        self.identifier = id(self)
        self.temp_cur = 0.0
        self.temp_des = 0.0
        self.valve_pos = 0
        self.battery_level = 0
        self.random()

    def random(self):
        self.valve_pos = random.randint(0, MAX_VPOS) 
        self.temp_cur = random.uniform(MIN_TEMP, MAX_TEMP)
        self.temp_des = random.uniform(MIN_TEMP, MAX_TEMP)
        self.battery_level = random.randint(0, MAX_BATT)

    def __repr__(self):
        return json.dumps({
            "id":self.identifier,
            "valve":self.valve_pos,
            "temp_cur":self.temp_cur,
            "temp_des":self.temp_des,
            "battery":self.battery_level
            })

    def __str__(self):
        return "{:x} {} {} {:.1f} {:.1f}".format(self.identifier,
                self.battery_level, self.valve_pos, self.temp_cur,
                self.temp_des)


def message(client, heaters, msg):
    """
    Handles incomming requests

    @param client, the active mqtt client
    @param heaters, the state of the heaters
    @param msg, the incomming message
    """
    print msg.topic + " " + str(msg.payload)

def add(heaters):
    h = Heater()
    heaters[h.identifier] = h

def rm(heaters):
    if len(heaters) == 0:
        return

    k = random.choice(heaters.keys())
    del heaters[k]

def update(heaters):
    if len(heaters) == 0:
        return

    n = random.randint(1, len(heaters))
    for i in range(n):
        k = random.choice(heaters.keys())
        heaters[k].random()

if __name__ == "__main__":
    heaters = {}

    client = mqtt.Client("emulator", True, heaters)
    client.on_message = message
    client.connect("127.0.0.1", 1883, 60)
    client.loop_start()

    add(heaters)
    while True:
        r = random.random()

        # Remove heater
        if r < 0.01:
            rm(heaters) 
        # Add heater
        elif r < 0.04 and len(heaters) > 0:
            add(heaters)
        # Update vars of a heater
        elif r < 0.2 and len(heaters) > 0:
            update(heaters)

        print "heaters: {}".format(len(heaters))
        for h in heaters.values():
            print "  " + str(h)
        print ""
        time.sleep(random.randint(1, 20))


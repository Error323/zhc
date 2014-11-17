# Zoned Heater Control

import paho.mqtt.client as mqtt
import json
import time
import random

# The zhc protocol version
ZHC_VERSION = 1

class Heater:
    MIN_TEMP = 8   # degrees celcius
    MAX_TEMP = 30  # degrees celcius
    MAX_VPOS = 255 # valve pos 8 bit precision
    MAX_BATT = 100 # battery level
    index    = 0   # static index

    def __init__(self):
        self.identifier = Heater.index
        self.temp_cur = 0.0
        self.temp_des = 0.0
        self.valve_pos = 0
        self.battery_level = 0
        self.random()
        Heater.index += 1

    def random(self):
        self.valve_pos = random.randint(0, Heater.MAX_VPOS) 
        self.temp_cur = round(random.uniform(Heater.MIN_TEMP, Heater.MAX_TEMP), 1)
        self.battery_level = random.randint(0, Heater.MAX_BATT)

    def encode(self):
        return { "id":self.identifier, "valve":self.valve_pos,
                "temp_cur":self.temp_cur, "temp_des":self.temp_des,
                "battery":self.battery_level }

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
    if "zhc/set" in msg.topic:
        data = json.loads(msg.payload)
        for i,t in data.items():
           set_temp(client, heaters, int(i), t)
    else:
        print "Error: Invalid msg", msg


def set_temp(client, heaters, idx, temp):
    """
    Set desired temperature on a heater and publish the result

    @param client, the active mqtt client
    @param heaters, the state of the heaters
    @param idx, the heater index
    @param temp, the new temperature
    """
    if not heaters.has_key(idx):
        print "Error: Invalid heater id {}".format(idx)
        return
    heaters[idx].temp_des = round(temp, 1)
    client.publish("zhc/heater/{}".format(idx),
            payload=json.dumps(h.encode()), retain=True)


def add(client, heaters):
    """
    Add a heater and publish it

    @param client, the active mqtt client
    @param heaters, the state of the heaters
    """
    h = Heater()
    heaters[h.identifier] = h
    client.publish("zhc/heater/{}".format(h.identifier),
            payload=json.dumps(h.encode()), retain=True)


def rm(client, heaters):
    """
    Remove a heater and publish it

    @param client, the active mqtt client
    @param heaters, the state of the heaters
    """
    if len(heaters) == 0:
        return
    k = random.choice(heaters.keys())
    client.publish("zhc/heater/{}".format(h.identifier),
        payload=None, retain=True)
    del heaters[k]


def update(client, heaters):
    """
    Emulate random heater updates and publish result

    @param client, the active mqtt client
    @param heaters, the state of the heaters
    """
    if len(heaters) == 0:
        return
    n = random.randint(1, len(heaters))
    for i in range(n):
        h = random.choice(heaters.values())
        h.random()
        client.publish("zhc/heater/{}".format(h.identifier),
                payload=json.dumps(h.encode()), retain=True)


if __name__ == "__main__":
    heaters = {}

    client = mqtt.Client(client_id="emulator", clean_session=True,
        userdata=heaters, protocol=mqtt.MQTTv31)
    client.on_message = message
    client.connect("127.0.0.1", 1883, 60)
    client.loop_start()
    client.subscribe(("zhc/set", 2))

    client.publish("zhc/static",
            payload=json.dumps({"min_temp":Heater.MIN_TEMP,
                "max_temp":Heater.MAX_TEMP, "min_vpos":0,
                "max_vpos":Heater.MAX_VPOS, "min_batt":0,
                "max_batt":Heater.MAX_BATT}), retain=True, qos=2)

    add(client, heaters)
    while True:
        r = random.random()

        # Remove heater
        if r < 0.01:
            rm(client, heaters) 
        # Add heater
        elif r < 0.1:
            add(client, heaters)
        # Update vars of a heater
        elif r < 0.3:
            update(client, heaters)

        print "active heaters: {}".format(len(heaters))
        for h in heaters.values():
            print "  " + str(h)
        print ""
        time.sleep(random.randint(1, 20))


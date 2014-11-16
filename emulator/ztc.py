# Zoned Heater Control

import paho.mqtt.client as mqtt
import json
import time
import random

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
        self.temp_cur = random.uniform(Heater.MIN_TEMP, Heater.MAX_TEMP)
        self.temp_des = random.uniform(Heater.MIN_TEMP, Heater.MAX_TEMP)
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

def set_temp(heaters, idx, temp):
    if not heaters.has_key(idx):
        print "Error: Invalid heater id {}".format(idx)
        return

    heaters[idx].temp_des = temp

def add(heaters):
    h = Heater()
    heaters[h.identifier] = h

def rm(heaters):
    if len(heaters) == 0:
        return

    k = random.choice(heaters.keys())
    del heaters[k]

def pub_state(client, heaters):
    state = []
    for h in heaters.values():
        state.append(h.encode())
    client.publish("ztc/state", qos=2, payload=json.dumps(state), retain=True)

def update(client, heaters):
    if len(heaters) == 0:
        return

    n = random.randint(1, len(heaters))
    for i in range(n):
        k = random.choice(heaters.keys())
        heaters[k].random()
        client.publish("ztc/update", qos=0, payload=json.dumps(heaters[k].encode()))

if __name__ == "__main__":
    heaters = {}

    client = mqtt.Client(clean_session=True, userdata=heaters, protocol=mqtt.MQTTv31)
    client.subscribe([("ztc/set", 2)])
    client.on_message = message
    client.connect("127.0.0.1", 1883, 60)
    client.loop_start()

    add(heaters)
    pub_state(client, heaters)
    while True:
        r = random.random()

        # Remove heater
        if r < 0.01:
            rm(heaters) 
            pub_state(client, heaters)
        # Add heater
        elif r < 0.1:
            add(heaters)
            pub_state(client, heaters)
        # Update vars of a heater
        elif r < 0.2:
            update(client, heaters)

        print "active heaters: {}".format(len(heaters))
        for h in heaters.values():
            print "  " + str(h)
        print ""
        time.sleep(random.randint(1, 20))


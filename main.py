import paho.mqtt.subscribe as paho
import time, json

Connected = False

broker_addr = "mqtt.gen.polyb.io"
broker_port = 1883
broker_user = ""
broker_pass = ""
mqtt_topic = "/scoreboard/to/discsonline"
mauldasch_discid = "7c87ce9d59d5"
current_team = 1

def on_message_print(client, userdata, message):
    msg = str(message.payload.decode("utf-8"))
    msg = json.loads(msg)
    if (msg["discid"] == mauldasch_discid):
        if (msg["ownerteam"] != current_team):
            print("New Team!, " + str(msg["ownerteam"]))
            print(msg)
            current_team = msg["ownerteam"]
        # if (msg["ownerteam"] != current_team):
        #     current_team = msg["ownerteam"]
        #     print("New Team: " + current_team)

paho.callback(on_message_print, mqtt_topic, hostname=broker_addr, userdata={"message_count": 0})
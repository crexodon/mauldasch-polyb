import paho.mqtt.subscribe as paho
import time, json
import asyncio

import artnet

Connected = False

broker_addr = "mqtt.gen.polyb.io"
broker_port = 1883
broker_user = ""
broker_pass = ""
mqtt_topic = "/scoreboard/to/discsonline"
mauldasch_discid = "7c87ce9d59d5"
current_team = 1

# https://gen.polyb.io/posts/WHY2025/
# 1=pink
# 2=yellow
# 3=cyan
# 4=red

artctl: artnet.ArtNetController

async def main():
    global artctl
    artctl = artnet.ArtNetController("151.217.175.97", 2)

    await artctl.connect()
    # await artnet.set_color([0, 0, 0], 1)
    # await artnet.set_team(2)
    # asyncio.run(artnet.set_color([255, 0, 0]))

asyncio.run(main())

def on_message_print(client, userdata, message):
    global current_team

    msg = str(message.payload.decode("utf-8"))
    # print(msg)
    msg = json.loads(msg)
    if (msg["discid"] == mauldasch_discid):
        if (msg["ownerteam"] != current_team):
            print("New Team!, " + str(msg["ownerteam"]))
            print(msg)
            current_team = msg["ownerteam"]
            asyncio.run(artctl.set_team(current_team))
        # if (msg["ownerteam"] != current_team):
        #     current_team = msg["ownerteam"]
        #     print("New Team: " + current_team)

paho.callback(on_message_print, mqtt_topic, hostname=broker_addr, userdata={"message_count": 0})

# asyncio.run(artctl.loop())
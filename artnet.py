import asyncio
from pyartnet import ArtNetNode, Channel, impl_artnet
import colorsys
import time
from typing import List
import threading
import queue
import math



class ArtNetController:
    main_offset = 0
    rgb_offset = 1
    uv_offset = 6

    start_addresses = [193, 97, 33, 65, 1, 225]
    num_fixtures = len(start_addresses)

    animation_speed = 2     # s
    animation_time = 0.02   # s, time step

    # https://gen.polyb.io/posts/WHY2025/
    team_colors = [
        [200, 0, 100],  # pink
        [255, 100, 0],  # yellow
        [0, 127, 127],  # cyan
        [255, 0, 0]     # red
    ]

    universe: impl_artnet.ArtNetUniverse
    rgb_channels: List[Channel]
    main_channels: List[Channel]

    anim_queue = queue.Queue()
    running = True
    current_color = [0, 0, 0]
    current_anim = "idle"
    anim_thread: threading.Thread

    def generate_channels(self, universe: impl_artnet.ArtNetUniverse):
        main_channels: Channel = []
        rgb_channels: Channel = []
        for start in self.start_addresses:
            main_ch = universe.add_channel(start + self.main_offset, 1)
            main_ch.set_values([255])
            main_channels.append(main_ch)

            other_ch = universe.add_channel(start + self.rgb_offset + 3, 6)
            # main_ch.set_values([255])
            
            rgb_channels.append(universe.add_channel(start + self.rgb_offset, 3))
        
        return rgb_channels, main_channels     

    def __init__(self, ip: str, universe_num: int):
        self.ip = ip
        self.universe_num = universe_num

    async def connect(self):
        node = ArtNetNode(self.ip, 6454)

        self.universe = node.add_universe(self.universe_num)
        self.rgb_channels, self.main_channels = self.generate_channels(self.universe)

        self.anim_thread = threading.Thread(target=asyncio.run, args=(self.animation_loop(),), daemon=True)
        self.anim_thread.start()

        # self.universe.send_data()
    
    async def set_color(self, color: List[int], fade_time: int = 0.0):
        for ch in self.rgb_channels:
            ch.set_fade(color, fade_time * 1000)
        await self.rgb_channels[0]
        
    async def set_team(self, team_id: int):
        color = self.team_colors[team_id-1]
        self.anim_queue.put({"color": color, "anim": "idle"})
        # await self.set_color(color, 1)

    async def animation_loop(self):
        cur_step = 0
        while self.running:
            if not self.anim_queue.empty():
                event = self.anim_queue.get_nowait()

                if (event["color"] and event["anim"]):
                    self.current_color = event["color"]
                    self.current_anim = event["anim"]

            
            for i in range(self.num_fixtures):
                #cur_step = math.floor(time.time() % (self.animation_speed * 3)) // self.animation_speed     # idk either xD
                color = self.current_color if (cur_step == i) else [0, 0, 0]
                self.rgb_channels[i].set_fade(color, self.animation_speed * 1000)
                # print(cur_step)
            cur_step += 1
            if cur_step >= self.num_fixtures:
                cur_step = 0
            # print(cur_step)
            
            await asyncio.gather(*self.rgb_channels)    # waits for fade to finish

            # print(self.current_color)

            # time.sleep(self.animation_speed)
    
    

if __name__ == "__main__":
    async def main():
        artnet = ArtNetController("151.217.175.97", 2)

        await artnet.connect()
        await artnet.set_color([0, 0, 0], 1)
        await artnet.set_team(4)
        # asyncio.run(artnet.set_color([255, 0, 0]))
    
    asyncio.run(main())
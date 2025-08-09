import asyncio
from pyartnet import ArtNetNode, Channel, impl_artnet
import colorsys
import time
from typing import List


class ArtNetController:
    main_offset = 0
    rgb_offset = 1
    uv_offset = 6

    start_addresses = [193, 97, 33, 65, 1, 225]
    num_fixtures = len(start_addresses)

    # https://gen.polyb.io/posts/WHY2025/
    # 1=pink
    # 2=yellow
    # 3=cyan
    # 4=red
    team_colors = [
        [255, 0, 127],
        [255, 100, 0],
        [0, 200, 200],
        [255, 0, 0]
    ]

    universe: impl_artnet.ArtNetUniverse
    rgb_channels: Channel

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
        self.rgb_channels, _ = self.generate_channels(self.universe)

        # self.universe.send_data()
    
    async def set_color(self, color: List[int], fade_time: int = 0.0):
        for ch in self.rgb_channels:
            ch.set_fade(color, fade_time * 1000)
        await self.rgb_channels[0]
        
    async def set_team(self, team_id: int):
        await self.set_color(self.team_colors[team_id-1], 1)
    
    

if __name__ == "__main__":
    async def main():
        artnet = ArtNetController("151.217.175.97", 2)

        await artnet.connect()
        await artnet.set_color([0, 0, 0], 1)
        await artnet.set_team(4)
        # asyncio.run(artnet.set_color([255, 0, 0]))
    
    asyncio.run(main())
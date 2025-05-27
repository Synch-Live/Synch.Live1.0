import asyncio
#import aiohttp
import logging
import pygame
import time
from typing import Optional

import logger

VOL_URL = "http://observer:8888/sync"
INTERVAL = 3


class AudioFeedback:

    instances = []

    def __init__(self, sound_file: str, channel_id: int,
                 default_start_volume: float = 0):
        """
        Initialize tracker for a single sound stream and begin looping
        the sound

        Params
        ------
        sound_file
            filename for the mp3 containing the sound
        channel_id
            channel number to play sound on
        default_start_volume
            volume to start looping the sound at, between 0 and 1
        """

        self.sound = pygame.mixer.Sound(mp3)
        self.channel = pygame.mixer.Channel(channel_id)

        self.channel.play(self.sound, loops=-1)  # loop indefinitely
        self.current_volume = default_start_volume 
        self.channel.set_volume(self.current_volume)
        AudioFeedback.instances.append(self)

        logging.info(f"Initialised AudioFeedback channel {channel_id}: {mp3}")
        logging.info(f"  with volume {default_start_volume}")


    def set_volume(self, volume: float):
        """
        Set the volume for this audio stream.

        Params
        ------
        volume
            float between 0.0 and 1.0
        """
        volume = max(0.0, min(1.0, volume))  # clamp volume
        self.current_volume = volume
        self.channel.set_volume(volume)


    def get_volume(self) -> float:
        """
        Get the current volume of this audio stream.

        :return: float volume level
        """
        return self.current_volume


    @classmethod
    def get_all_volumes(cls):
        """
        Get current volumes of all tracked streams.

        :return: list of floats
        """
        return [instance.get_volume() for instance in cls.instances]


    @classmethod
    def stop_all(cls):
        """
        Stop playback on all tracked streams.
        """
        for instance in cls.instances:
            instance.channel.stop()
        cls.instances.clear()




async def fetch_sync() -> Optional[float]:
    try:
        async with aiohttp.ClientSession() as sess:
            async with sess.get(PSI_URL) as resp:
                r = await resp.json()
                return r
    except:
        logging.info("Exception in fetching psi")
        return None



async def loop(period: float, val: float) -> None:
    """
    This function uses a generator defined below in the tick() function to call
    the fetch_sync function with the same period as what makes the lights blink,
    and updates the sound effects.
    """
    def tick():
        t = time.time()
        while True:
            t += period
            yield max(t - time.time(), 0)

    gen = tick()

    while val > 0:
        sync = await fetch_sync()
        logging.info(f"Sync: {sync}")

        if sync is None:
            logging.info("Sync param was not fetched: entering mock synchronous loop")
            return 0

        val = sync

        time.sleep(next(gen))
        logging.info(f'Tick')

        # adjust song
        

    if val == 1:
        logging.info("Emergence suceeded! Entering rainbow loop")
        return 1


# Code developed/used by HL
def getVolumeForPsi(psi, start):
	end = start + 0.1
	vrange = end - start
	val = (psi - start) / vrange
	return min(1, max(0, val))

def onValueChange(psi, trackers):
    vols = [ getVolumeForPsi(psi, 0.3)
           , getVolumeForPsi(psi, 0.5)
           , getVolumeForPsi(psi, 0.75)
           , getVolumeForPsi(psi, 0.9) ]

    if psi >= 1:
        vols[-1] = 1

    for i, tracker in enumerate(trackers[1:]):
        tracker.set_volume(vols[i])


if __name__ == "__main__":

    mp3s = ["base.mp3", "layer1.mp3", "layer2.mp3", "layer3.mp3", "layer4.mp3"]
    mp3s = [ f"../../media/music/{m}" for m in mp3s ]

    pygame.mixer.init()

    trackers = []
    for idx, mp3 in enumerate(mp3s):
        init_vol = 0
        if idx == 0:
            init_vol = 1

        tracker = AudioFeedback(mp3, channel_id = idx, default_start_volume = init_vol)
        trackers.append(tracker)

    # Example: dynamically update volumes
    try:
        psi = 0
        while True:
            # Example: cycle volumes for demo purposes
            onValueChange(psi, trackers)
            print("Current volumes:", AudioFeedback.get_all_volumes())
            time.sleep(1)
            psi = psi + 0.05
    except KeyboardInterrupt:
        AudioFeedback.stop_all()
        pygame.mixer.quit()


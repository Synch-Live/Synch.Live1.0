import asyncio
import aiohttp
import logging
import pygame
import time
from typing import List, Optional

import logger

# put a hostname of your machine with a dot, or use 
# the one below when connected to SL router
TEST_URL = "http://127.0.0.1:8888/"
PSI_URL  = "http://observer.synch.live:8888/sync"
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

        self.current_volume = default_start_volume 
        self.channel.set_volume(self.current_volume)
        AudioFeedback.instances.append(self)

        logging.info(f"Initialised AudioFeedback channel {channel_id}: {mp3}")
        logging.info(f"  with volume {default_start_volume}")


    def play(self):
        """
        Start playing the audio stream in infinite loop
        """
        self.channel.play(self.sound, loops=-1)


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
    def get_all_volumes(cls) -> List[float]:
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


async def fetch_sync_mock() -> Optional[float]:
    """
    Asynchronously fetch a value from HTTP endpoint without waiting, or return None.
    Note the HTTP endpoint must not have a "malformed" URL (localhost does not work)
    """
    try:
        async with aiohttp.ClientSession() as sess:
            async with sess.get(TEST_URL) as resp:
                r = await resp.text()
                return r
    except Exception as e:
        logging.info(f"Exception in fetching value from test URL: {e}")
        return None


async def fetch_sync() -> Optional[float]:
    """
    Asynchronously fetch a value from HTTP endpoint without waiting, or return None.
    Note the HTTP endpoint must not have a "malformed" URL (localhost does not work)
    """
    try:
        async with aiohttp.ClientSession() as sess:
            async with sess.get(PSI_URL) as resp:
                r = await resp.json()
                return r
    except Exception as e:
        logging.info(f"Exception in fetching psi: {e}")
        return None


async def loop(period: float, val: float, trackers: List[AudioFeedback]) -> None:
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
        # replace with fetch_sync_mock() to test
        sync = await fetch_sync_mock()

        if sync is None:
            logging.info("Sync param was not fetched: entering mock loop")
            # TODO mock winning the game with sound as with lights
            return 0

        val = 1 - float(sync)
        logging.info(f"1 - Sync: {val}")

        time.sleep(next(gen))
        logging.info(f'Tick')

        # adjust song based on Psi
        dynamic_volume(val, trackers)

    if val == 1:
        logging.info("Emergence suceeded! Entering rainbow loop")
        return 1



# Code developed/used by HL
def getVolumeForPsi(psi: float, start: float) -> float:
	end = start + 0.1
	vrange = end - start
	val = (psi - start) / vrange
	return min(1, max(0, val))

def onValueChange(psi: float, trackers: List[AudioFeedback]) -> None:
    vols = [ getVolumeForPsi(psi, 0.3)
           , getVolumeForPsi(psi, 0.5)
           , getVolumeForPsi(psi, 0.75)
           , getVolumeForPsi(psi, 0.9) ]

    if psi >= 1:
        vols[-1] = 1

    for i, tracker in enumerate(trackers[1:]):
        tracker.set_volume(vols[i])
        logging.info(f"Track {i+1} volume {tracker.get_volume()}")


def dynamic_volume(sync: float, trackers: List[AudioFeedback]):
    sync = max(0.0, min(1.0, sync))
    raw_vols = {
        "base": 1.0,
    }
    peaks = {
        "layer1": 0.3,
        "layer2": 0.5,
        "layer3": 0.75,
        "layer4": 0.9,
    }

    def volume_curve(sync, peak, width=0.2):
        distance = abs(sync - peak)
        if distance > width:
            return 0.0
        return max(0.0, 1 - (distance / width))

    for layer, peak in peaks.items():
        raw_vols[layer] = volume_curve(sync, peak)

    total = sum(raw_vols.values())
    vols  = [ vol / total for track, vol in raw_vols.items() ]

    for i, tracker in enumerate(trackers):
        tracker.set_volume(vols[i])
        logging.info(f"Track {i+1} volume {tracker.get_volume()}")


def example_inc(trackers: List[AudioFeedback]):
    """
    Example function which simulates a slowly increasing Psi
    """
    try:
        psi = 0
        while True:
            #onValueChange(psi, trackers)
            dynamic_volume(psi, trackers)
            time.sleep(2)
            psi = psi + 0.05
    except KeyboardInterrupt:
        AudioFeedback.stop_all()
        pygame.mixer.quit()


def example_dec(trackers: List[AudioFeedback]):
    """
    Example function which simulates a slowly decreasing Psi
    """
    try:
        psi = 1 
        while True:
            #onValueChange(psi, trackers)
            dynamic_volume(psi, trackers)
            time.sleep(2)
            psi = psi - 0.05
    except KeyboardInterrupt:
        AudioFeedback.stop_all()
        pygame.mixer.quit()


if __name__ == "__main__":

    mp3s = ["base.mp3", "layer1.mp3", "layer2.mp3", "layer3.mp3", "layer4.mp3"]
    mp3s = [ f"../../media/music/{m}" for m in mp3s ]

    pygame.mixer.init()
    logging.info("Initialised audio mixer")

    trackers = []
    for i, mp3 in enumerate(mp3s):
        init_vol = 0
        if i == 0:
            init_vol = 1

        tracker = AudioFeedback(mp3, channel_id = i, default_start_volume = init_vol)
        trackers.append(tracker)
    logging.info("Initialised audio tracks")

    for tracker in trackers:
        tracker.play()

    example_dec(trackers)

    #logging.info("Begin running loop that fetches Psi")
    #ret = asyncio.run(loop(INTERVAL, 0.1, trackers))
    


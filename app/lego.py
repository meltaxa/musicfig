#!/usr/bin/env python

from app import webhook
from mutagen.mp3 import MP3
import app.spotify as spotify
import app.tags as nfctags
import binascii
import logging
import os
import threading
import time
import random
import usb.core
import usb.util
import app.mp3player as mp3player
import glob

logger = logging.getLogger(__name__)

class Dimensions():

    def __init__(self):
        try:
           self.dev = self.init_usb()
        except Exception:
            return

    def init_usb(self):
        dev = usb.core.find(idVendor=0x0e6f, idProduct=0x0241)

        if dev is None:
            logger.error('Lego Dimensions pad not found')
            raise ValueError('Device not found')

        if dev.is_kernel_driver_active(0):
            dev.detach_kernel_driver(0)

        # Initialise portal
        dev.set_configuration()
        dev.write(1,[0x55, 0x0f, 0xb0, 0x01, 0x28, 0x63, 0x29, 0x20, 0x4c, 
                     0x45, 0x47, 0x4f, 0x20, 0x32, 0x30, 0x31, 0x34, 0xf7, 
                     0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
                     0x00, 0x00, 0x00, 0x00, 0x00])
        return dev

    def send_command(self, command):
        checksum = 0
        for word in command:
            checksum = checksum + word
            if checksum >= 256:
                checksum -= 256
            message = command+[checksum]

        while(len(message) < 32):
            message.append(0x00)

        try:
            self.dev.write(1, message)
        except Exception:
            pass

    def switch_pad(self, pad, colour):
        self.send_command([0x55, 0x06, 0xc0, 0x02, pad, colour[0], 
                          colour[1], colour[2],])
        return

    def fade_pad(self, pad, pulse_time, pulse_count, colour):
        self.send_command([0x55, 0x08, 0xc2, 0x0f, pad, pulse_time, 
                          pulse_count, colour[0], colour[1], colour[2],])
        return

    def flash_pad(self, pad, on_length, off_length, pulse_count, colour):
        self.send_command([0x55, 0x09, 0xc3, 0x03, pad, 
                          on_length, off_length, pulse_count, 
                          colour[0], colour[1], colour[1],])
        return

    def update_nfc(self):
        try:
            inwards_packet = self.dev.read(0x81, 32, timeout = 10)
            bytelist = list(inwards_packet)
            if not bytelist:
                return
            if bytelist[0] != 0x56:
                return
            pad_num = bytelist[2]
            uid_bytes = bytelist[6:13]
            identifier = binascii.hexlify(bytearray(uid_bytes)).decode("utf-8")
            identifier = identifier.replace('000000','')
            removed = bool(bytelist[5])
            if removed:
                response = 'removed:%s:%s' % (pad_num, identifier)
            else:
                response = 'added:%s:%s' % (pad_num, identifier)
            return response
        except Exception:
            return

class Base():
    def __init__(self):
        self.OFF   = [0,0,0]
        self.RED   = [255,0,0]
        self.GREEN = [0,255,0]
        self.BLUE  = [0,0,255]
        self.PINK = [255,192,203]
        self.ORANGE = [255,165,0]
        self.PURPLE = [255,0,255]
        self.LBLUE = [255,255,255]
        self.OLIVE = [128,128,0]
        self.COLOURS = ['self.RED', 'self.GREEN', 'self.BLUE', 'self.PINK', 
                        'self.ORANGE', 'self.PURPLE', 'self.LBLUE', 'self.OLIVE']
        self.base = self.startLego()

    def randomLightshow(self,duration = 60):
        logger.info("Lightshow started for %s seconds." % duration)
        self.lightshowThread = threading.currentThread()
        t = time.perf_counter()
        while getattr(self.lightshowThread, "do_run", True) and (time.perf_counter() - t) < duration:
            pad = random.randint(0,2)
            self.colour = random.randint(0,len(self.COLOURS)-1)
            self.base.switch_pad(pad,eval(self.COLOURS[self.colour]))
            time.sleep(round(random.uniform(0,0.5), 1))
        self.base.switch_pad(0,self.OFF)

    def startLightshow(self,duration_ms):
        if switch_lights:
            self.lightshowThread = threading.Thread(target=self.randomLightshow,
                args=([(duration_ms / 1000)]))
            self.lightshowThread.daemon = True
            self.lightshowThread.start()

    def initMp3(self):
        self.p = mp3player.Player()
        def monitor():
            global mp3state
            global mp3elapsed
            while True:
                state = self.p.event_queue.get(block=True, timeout=None)
                mp3state = str(state[0]).replace('PlayerState.','')
                mp3elapsed = state[1]
            logger.info('thread exited.')
        threading.Thread(target=monitor, name="monitor").daemon = True
        threading.Thread(target=monitor, name="monitor").start() 

    def startMp3(self, filename, is_playlist=False):
        global mp3_duration
        # load an mp3 file
        if not is_playlist:
            mp3file = os.path.dirname(os.path.abspath(__file__)) + '/../music/' + filename
        else:
            mp3file = filename
        logger.info(f"mp3file::{mp3file}")
        logger.info('Playing %s.' % filename)
        self.p.open(mp3file)
        self.p.play()

        audio = MP3(mp3file)
        mp3_duration = audio.info.length
        self.startLightshow(mp3_duration * 1000)
        ##time.sleep(mp3_duration)

    def stopMp3(self):
        global mp3state
        try:
            #self.p.stop()
            mp3state = 'STOPPED'
        except Exception:
            pass

    def pauseMp3(self):
        global mp3state
        if 'PLAYING' in mp3state:
            self.p.pause()
            logger.info('Track paused.')
            mp3state = 'PAUSED'
            return

    def playMp3(self, filename):
        global t
        global mp3state
        spotify.pause()
        if previous_tag == current_tag and 'PAUSED' in ("%s" % mp3state):
            # Resume
            logger.info("Resuming mp3 track.")
            self.p.play()
            remaining = mp3_duration - mp3elapsed
            if remaining >= 0.1:
                self.startLightshow(remaining * 1000)
                return
        # New play 
        self.stopMp3()
        self.startMp3(filename)
        mp3state = 'PLAYING'

    def playPlaylist(self, playlist_filename):
        global mp3state
        spotify.pause()
        self.stopMp3()
        mp3list = '/home/pi/Music/' + playlist_filename + '/*.mp3'
        logger.info(f"mp3list::{mp3list}")
        for mp3song in glob.glob(mp3list):
            logger.info("Playing..."+mp3song)
            self.startMp3(mp3song, True)
            mp3state = 'PLAYING'

    def startLego(self):
        global current_tag
        global previous_tag
        global mp3state
        global p
        global switch_lights
        current_tag = None
        previous_tag = None
        mp3state = None
        nfc = nfctags.Tags()
        nfc.load_tags()
        tags = nfc.tags
        self.base = Dimensions()
        logger.info("Lego Dimensions base activated.")
        self.initMp3()
        try:
            switch_lights = tags['lights']
        except Exception:
            switch_lights = True
        logger.info('Lightshow is %s' % switch_lights) #("disabled", "enabled")[switch_lights])
        if switch_lights:
            self.base.switch_pad(0,self.GREEN)
        else:
            self.base.switch_pad(0,self.OFF)
        while True:
            tag = self.base.update_nfc()
            if tag:
                status = tag.split(':')[0]
                pad = int(tag.split(':')[1])
                identifier = tag.split(':')[2]
                if status == 'removed':
                    if identifier == current_tag:
                        try:
                            self.lightshowThread.do_run = False
                            self.lightshowThread.join()
                        except Exception:
                            pass
                        self.pauseMp3()
                        if spotify.activated():
                            spotify.pause()
                if status == 'added':
                    if switch_lights:
                        self.base.switch_pad(pad = pad, colour = self.BLUE)

                    # Reload the tags config file
                    nfc.load_tags()
                    tags = nfc.tags

                    # Stop any current songs and light shows
                    try:
                        self.lightshowThread.do_run = False
                        self.lightshowThread.join()
                    except Exception:
                        pass

                    if (identifier in tags['identifier']):
                        if current_tag == None:
                            previous_tag = identifier
                        else:
                            previous_tag = current_tag
                        current_tag = identifier
                        # A tag has been matched
                        if ('playlist' in tags['identifier'][identifier]):
                            playlist = tags['identifier'][identifier]['playlist']
                            self.playPlaylist(playlist)
                        if ('mp3' in tags['identifier'][identifier]):
                            filename = tags['identifier'][identifier]['mp3']
                            self.playMp3(filename)
                        if ('slack' in tags['identifier'][identifier]):
                            webhook.Requests.post(tags['slack_hook'],{'text': tags['identifier'][identifier]['slack']})
                        if ('command' in tags['identifier'][identifier]):
                            command = tags['identifier'][identifier]['command']
                            logger.info('Running command %s' % command)
                            os.system(command)
                        if ('spotify' in tags['identifier'][identifier]) and spotify.activated():
                            if current_tag == previous_tag:
                                self.startLightshow(spotify.resume())
                                continue
                            try:
                                position_ms = int(tags['identifier'][identifier]['position_ms'])
                            except Exception:
                                position_ms = 0
                            self.stopMp3()
                            duration_ms = spotify.spotcast(tags['identifier'][identifier]['spotify'],
                                                           position_ms)
                            if duration_ms > 0:
                                self.startLightshow(duration_ms)
                            else:
                                self.base.flash_pad(pad = pad, on_length = 10, off_length = 10,
                                                    pulse_count = 6, colour = self.RED)
                        if ('spotify' in tags['identifier'][identifier]) and not spotify.activated():
                            current_tag = previous_tag
                    else:
                        # Unknown tag. Display UID.
                        logger.info('Discovered new tag: %s' % identifier)
                        self.base.switch_pad(pad, self.RED)

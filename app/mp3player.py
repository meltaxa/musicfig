#!/usr/bin/env python

import ctypes
from enum import Enum
import threading
import queue
from queue import Empty
import mpg123
import logging
import random

logger = logging.getLogger(__name__)

class mpg123_frameinfo(ctypes.Structure):
    _fields_ = [
        ('version',     ctypes.c_ubyte),
        ('layer',       ctypes.c_int),
        ('rate',        ctypes.c_long),
        ('mode',        ctypes.c_ubyte),
        ('mode_ext',    ctypes.c_int),
        ('framesize',   ctypes.c_int),
        ('flags',       ctypes.c_ubyte),
        ('emphasis',    ctypes.c_int),
        ('bitrate',     ctypes.c_int),
        ('abr_rate',    ctypes.c_int),
        ('vbr',         ctypes.c_ubyte)
    ]


class ExtMpg123(mpg123.Mpg123):
    SEEK_SET = 0
    SEEK_CURRENT = 1
    SEEK_END = 2

    def __init__(self, filename=None, library_path=None):
        super().__init__(filename, library_path)

    def open(self, filename):
        errcode = self._lib.mpg123_open(self.handle, filename.encode())
        if errcode != mpg123.OK:
            raise self.OpenFileException(self.plain_strerror(errcode))

    def timeframe(self, tsec):
        t = ctypes.c_double(tsec)
        errcode = self._lib.mpg123_timeframe(self.handle, t)
        if errcode >= mpg123.OK:
            return errcode
        else:
            raise self.LengthException(self.plain_strerror(errcode))

    def seek_frame(self, pos, whence=SEEK_SET):
        px = ctypes.c_long(pos)
        errcode = self._lib.mpg123_seek_frame(self.handle, px, whence)
        if errcode >= mpg123.OK:
            return errcode
        else:
            raise self.LengthException(self.plain_strerror(errcode))

    def tellframe(self):
        errcode = self._lib.mpg123_tellframe(self.handle)
        if errcode >= mpg123.OK:
            return errcode
        else:
            raise self.LengthException(self.plain_strerror(errcode))

    def info(self):
        px = mpg123_frameinfo()
        errcode = self._lib.mpg123_info(self.handle, ctypes.pointer(px))
        if errcode != mpg123.OK:
            raise self.ID3Exception(self.plain_strerror(errcode))
        return px

    _samples_per_frame = [
        # version 1, layers 1,2,3
        [384, 1152, 1152],
        # version 2, layers 1,2,3
        [384, 1152, 576],
        # version 2.5, layers 1,2,3
        [384, 1152, 576]
    ]

    def frame_seconds(self, frame):
        info = self.info()
        return ExtMpg123._samples_per_frame[info.version][info.layer - 1] * frame / info.rate

class ExtOut123(mpg123.Out123):
    def __init__(self, library_path=None):
        super().__init__(library_path)

    def pause(self):
        self._lib.out123_pause(self.handle)

    def resume(self):
        self._lib.out123_continue(self.handle)

    def stop(self):
        self._lib.out123_stop(self.handle)

class PlayerState(Enum):
    UNINITALISED = 0
    INITALISED = 1,  # Drivers loaded
    LOADED = 2,  # MP3 loaded of x seconds
    READY = 3,  # Ready to play a time x
    PLAYING = 4,  # Playing a file at time x
    PAUSED = 5,  # Paused at time x
    FINISHED = 6,  # Finished
    PLAYLIST = 7   #Playing a playlist


class Player:

    class Command(Enum):
        LOAD = 1,
        PLAY = 2,
        PAUSE = 3,
        PLAYLIST = 4,
        SEEK = 5

    class IllegalStateException(Exception):
        pass

    def __init__(self):
        self.mp3 = ExtMpg123()
        self.out = ExtOut123()

        self.command_queue = queue.Queue(maxsize=1)
        self.event_queue = queue.Queue()
        self.playlist_queue = queue.Queue()

        self._current_state = PlayerState.INITALISED
        self.event_queue.put((self._current_state, None))
        threading.Thread(target=self._run_player, daemon=True, name="Player").start()

    def _run_player(self):
        while True:
            command = self.command_queue.get(block=True, timeout=None)
            if command[0] == Player.Command.LOAD:
                if self._current_state in [PlayerState.PLAYING]:
                    self.out.pause()

                self.mp3.open(command[1])
                tf = self.mp3.frame_length()
                self.track_length = self.mp3.frame_seconds(tf)
                self.frames_per_second = tf // self.track_length
                self.update_per_frame_count = round(self.frames_per_second / 5)
                self.to_time = self.track_length
                self._set_state(PlayerState.LOADED, self.track_length)
                self._set_state(PlayerState.READY, 0)

            elif command[0] == Player.Command.PLAY:

                if command[1] is not None:
                    tf = self.mp3.timeframe(command[1])
                    self.mp3.seek_frame(tf)
                self.to_time = self.track_length if command[2] is None else command[2]

                if self._current_state in [PlayerState.READY, PlayerState.PLAYING]:
                    self._play()

                elif self._current_state in [PlayerState.PAUSED]:
                    self.out.resume()
                    self._play()

            elif command[0] == Player.Command.PAUSE:
                self.out.pause()
                current_frame = self.mp3.tellframe()
                current_time = self.mp3.frame_seconds(current_frame)
                self._set_state(PlayerState.PAUSED, current_time)

            elif command[0] == Player.Command.SEEK:
                if self._current_state in \
                            [PlayerState.READY, PlayerState.PLAYING, PlayerState.PAUSED, PlayerState.FINISHED]:

                    tf = self.mp3.timeframe(command[1])
                    self.mp3.seek_frame(tf)
                    if self._current_state == PlayerState.FINISHED:
                        self._set_state(PlayerState.PAUSED, command[1])
                    else:
                        self.event_queue.put((self._current_state, command[1]))

                if self._current_state in [PlayerState.PLAYING]:
                    self._play()
            elif command[0] == Player.Command.PLAYLIST:
                if self._current_state in [PlayerState.PLAYING]:
                    self.out.pause()

                for song in command[1]:
                    self.playlist_queue.put(song)

                self._set_state(PlayerState.PLAYLIST)
                self._play_playlist()
            else:
                # what happened?
                pass

    def _play_playlist(self):
        while True:
            try:
                song_mp3 = self.playlist_queue.get(block=False)
                self.mp3.open(song_mp3)
                tf = self.mp3.frame_length()
                self.track_length = self.mp3.frame_seconds(tf)
                self.frames_per_second = tf // self.track_length
                self.update_per_frame_count = round(self.frames_per_second / 5)
                self.to_time = self.track_length
                fc = self.mp3.tellframe()
                current_time = self.mp3.frame_seconds(fc)
                self._set_state(PlayerState.PLAYING, current_time)

                to_frame = self.mp3.timeframe(self.to_time) + 1

                for frame in self.mp3.iter_frames(self.out.start):
                    self.out.play(frame)

                    fc += 1
                    if fc > to_frame:
                        current_time = self.mp3.frame_seconds(self.mp3.tellframe())
                        self._set_state(PlayerState.PAUSED, current_time)
                        return

                    if fc % self.update_per_frame_count == 0:
                        current_time = self.mp3.frame_seconds(self.mp3.tellframe())
                        self.event_queue.put((PlayerState.PLAYING, current_time))

                    if not self.command_queue.empty():
                        return
            except Empty:
                break
        self._set_state(PlayerState.FINISHED)

    def _play(self):
        fc = self.mp3.tellframe()
        current_time = self.mp3.frame_seconds(fc)
        self._set_state(PlayerState.PLAYING, current_time)

        to_frame = self.mp3.timeframe(self.to_time) + 1

        for frame in self.mp3.iter_frames(self.out.start):
            self.out.play(frame)

            fc += 1
            if fc > to_frame:
                current_time = self.mp3.frame_seconds(self.mp3.tellframe())
                self._set_state(PlayerState.PAUSED, current_time)
                return

            if fc % self.update_per_frame_count == 0:
                current_time = self.mp3.frame_seconds(self.mp3.tellframe())
                self.event_queue.put((PlayerState.PLAYING, current_time))

            if not self.command_queue.empty():
                return
        self._set_state(PlayerState.FINISHED)

    def _set_state(self, state, param=None):
        self._current_state = state
        self.event_queue.put((state, param))

    def open(self, filename):
        self.command_queue.put((Player.Command.LOAD, filename))

    def pause(self):
        self.command_queue.put((Player.Command.PAUSE, None))

    def play(self, from_time=None, to_time=None):
        self.command_queue.put((Player.Command.PLAY, from_time, to_time))

    def seek(self, tsec):
        self.command_queue.put((Player.Command.SEEK, tsec))

    def playlist(self, filename_list):
        self.command_queue.put((Player.Command.PLAYLIST, filename_list))
# encoding: utf-8
from __future__ import absolute_import, unicode_literals

import logging
import time
import pykka

from mopidy.core import PlaybackController
from mopidy.core import CoreListener
from mopidy.models import Track
from mopidy.core import PlaybackState

logger = logging.getLogger(__name__)

from blink1.blink1 import blink1 # pip install blink1, from https://github.com/todbot/blink1/tree/master/python/pypi

class Blink1Frontend(pykka.ThreadingActor, CoreListener):
    def __init__(self, config, core):
        super(Blink1Frontend, self).__init__()
        self.core = core
        self.config = config['blink1']
        self.b1 = blink1()
        self.looping = False

    def on_start(self):
        logger.debug('extension startup')

    def on_stop(self):
        logger.debug('extension teardown')
        try:
            self.b1.close()
        except Exception as e:
            logger.exception(e)

    # interesting callbacks we may implement one day
    # mute_changed(boolean)
    # volume_changed(volume [0..100])

    def playback_state_changed(self, old_state, new_state):
        """ Called whenever playback state is changed.

            MAY be implemented by actor.

            Parameters: 
            old_state (string from mopidy.core.PlaybackState field) – the state before the change
            new_state (string from mopidy.core.PlaybackState field) – the state after the change


            class mopidy.core.PlaybackState
                STOPPED = 'stopped'
                PLAYING = 'playing'
                PAUSED = 'paused'

        """
        logger.debug('Playback_state_changed(old, new): (%r, %r)', old_state, new_state)
        self.looping = False # clear any prev state feedback (like blinks)

        if new_state == PlaybackState.STOPPED:
            self.b1.fade_to_color(100, 'navy')
            time.sleep(10)
        elif new_state == PlaybackState.PLAYING:
            self.b1.fade_to_color(1000, 'green')
        elif new_state == PlaybackState.PAUSED:
            self.looping = True
            while self.looping:
                self.b1.fade_to_color(1000, 'green')
                time.sleep(1)
                self.b1.fade_to_color(1000, 'light green')
                time.sleep(1)
    
    


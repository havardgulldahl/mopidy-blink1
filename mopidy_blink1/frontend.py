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

from blink1py import open_blink1 # pip install blink1py, https://github.com/TronPaul/blink1py

class Blink1Frontend(pykka.ThreadingActor, CoreListener):
    def __init__(self, config, core):
        super(Blink1Frontend, self).__init__()
        self.core = core
        self.config = config['blink1']
        self.b1 = open_blink1()
        self.looping = False

    def on_start(self):
        logger.debug('extension startup')
        #preprogram led
        self.b1.set_pattern(0, 0,   255, 255, 1000)
        self.b1.set_pattern(1, 0,   127, 255, 1000)

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
        self.stop()

        if new_state == PlaybackState.STOPPED:
            self.b1.fade_rgb(0,0,100, 1000)
        elif new_state == PlaybackState.PLAYING:
            self.b1.fade_rgb(127,255,0, 1000) # PaleGreen
        elif new_state == PlaybackState.PAUSED:
            self.play()
    
    


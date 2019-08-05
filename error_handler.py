from __future__ import absolute_import

from collections import deque
import os
import os.path
import pyautogui
from robot.api import logger as LOGGER

pyautogui.FAILSAFE = False

from .singleton import Singleton






class ErrorHandler(object):
    '''Slotbot error reporter'''

    __metaclass__ = Singleton

    HISTORY_SIZE = 50

    def __init__(self, game_id, game_name, screenshot_folder, area, debug):
        self.game_id = game_id
        self.game_name = game_name.replace(" ", "_")
        self.game_prefix = "{}_{}".format(game_id, self.game_name)
        self.screenshot_folder = screenshot_folder
        self.screenshot_counter = 1
        self.area = area
        self.clear_history()
        self.debug = debug
        self.info_message_counter = 1

    def _save_to_disk(self, img, name):
        try:
            os.remove(os.path.join(self.screenshot_folder, name))
        except OSError:
            pass
        i = img.convert('RGB')
        i.save(os.path.join(self.screenshot_folder, name), "JPEG", quality=10)

    def save_state(self, level="INFO"):
        '''Save screen and log everything about current game state to log
        Screenshots made with level "INFO" will not be saved in screenshot_folder until dump_screenshots is not called
        Screenshots with level "WARN" and "ERROR" appears in screenshot_folder immedeately
        '''

        screenshot_name = "{}-state-{}.png".format(self.game_prefix, self.screenshot_counter)
        self.screenshot_counter += 1

        screen_img = pyautogui.screenshot(region=self.area)

        if level == "INFO" and not self.debug:
            self.history.append((screen_img, screenshot_name))
        else:
            self._save_to_disk(screen_img, screenshot_name)

    def clear_history(self):
        self.history = deque(maxlen=ErrorHandler.HISTORY_SIZE)

    def dump_screenshots(self):
        LOGGER.info("Dumping screenshots to disk")
        for screen in self.history:
            self._save_to_disk(screen[0], screen[1])

        self.clear_history()

    def report_message(self, message, level, *images):
        #image is tuple(name, PIL image)
        msg = message
        for image in images:
            image_filename = "{}-{}-{}.png".format(self.game_prefix, image[0], self.info_message_counter)
            self._save_to_disk(image[1], image_filename)
            msg += '<br/>{}: <img src="{}"/>'.format(image[0], image_filename)

        self.info_message_counter += 1
        LOGGER.write(msg, level, html=True)

    def report_error(self, message, *images):
        return self.report_message(message, "ERROR", *images)

    def report_warning(self, message, *images):
        return self.report_message(message, "WARN", *images)

    def report_info(self, message, *images):
        return self.report_message(message, "INFO", *images)

    #debug
    save_pictures_counter = 1

    def save_pictures(self, images):
        for image in images:
            image[0].save(os.path.join(self.screenshot_folder, "%s-%s.png" % (ErrorHandler.save_pictures_counter, image[1])), "PNG")

        ErrorHandler.save_pictures_counter += 1


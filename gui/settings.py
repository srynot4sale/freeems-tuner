#   Copyright 2008 Aaron Barnes
#
#   This file is part of the FreeEMS project.
#
#   FreeEMS software is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   FreeEMS software is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with any FreeEMS software.  If not, see <http://www.gnu.org/licenses/>.
#
#   We ask that if you make any changes to this file you send them upstream to us at admin@diyefi.org

import logging
import libs.config as config

logger = logging.getLogger('gui.settings')

# Dictionary of settings (non-recursive)
_settings = {}

# Flag that is set when the settings dict is updated
# This triggers the settings to be written to disc
# during the next idle event
_save_settings = False


def set(setting, value):
    '''Update a UI setting value'''
    global _settings, _save_settings
    _settings[setting] = value
    _save_settings = True


def get(setting, default):
    '''Get a UI setting value'''
    global _settings, _save_settings
    
    try:
        return _settings[setting]
    except KeyError:
        return default


def loadSettings():
    '''Load gui settings'''
    global _settings, _save_settings

    _settings = config.getItems('UI_Settings')


def saveSettings():
    '''Save gui settings'''
    global _settings, _save_settings

    # If a setting save has not been triggered, dont
    # waste time
    if not _save_settings:
        return

    _save_settings = False

    config.set('UI_Settings', _settings)



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


import ConfigParser

import action


# Parser object
_parser = None

# Save settings trigger
_save_settings = False


def parser():
    '''
    Get config parser

    Defaults are stored in config.ini (in same directory as code)
    User overrided settings are found in data/my_config.ini
    '''
    global _parser
    if _parser == None:
        _parser = ConfigParser.RawConfigParser()
        _parser.read(['data/my_config.cached.ini', 'config.default.ini', 'data/my_config.ini'])

    return _parser


def save():
    '''
    Save settings to file if they have changed
    '''
    # If a setting save has not been triggered, dont
    # waste time
    global _save_settings
    if not _save_settings:
        return

    _save_settings = False

    # Write options to the users config file
    configfile = open('data/my_config.cached.ini', 'wb')

    parser().write(configfile)


def get(section, option, default = None):
    '''
    Get option from config file
    '''
    # Get defaults and user settings
    _parser = parser()

    if not _parser.has_section(section):
        return default

    if not _parser.has_option(section, option):
        return default
    
    return _parser.get(section, option)


def getBool(section, option, default = None):
    '''
    Get option but return as a boolean value
    '''
    _parser = parser()

    if not _parser.has_section(section):
        return default

    if not _parser.has_option(section, option):
        return default
    
    return _parser.getboolean(section, option)


def getItems(section):
    '''
    Get all options in a section as a dict
    '''
    _parser = parser()

    if not _parser.has_section(section):
        return {}

    items = _parser.items(section)
    dict = {}

    for (item, value) in items:
        dict[item] = value

    return dict


def set(section, option, value = None):
    '''
    Set options

    Called two ways, if option is a dict
    and value is not set, it loops through
    the dict. Otherwise just sets the option
    and value
    '''
    _parser = parser()

    if not _parser.has_section(section):
        _parser.add_section(section)

    if not isinstance(option, dict):
        option = {option: value}

    for key in option.keys():
        _parser.set(section, key, option[key])

    global _save_settings
    _save_settings = True


class actions():
    '''
    Modules' actions
    '''

    class save(action.action):
        '''
        Save config to file
        '''
        def run(self):
            save()

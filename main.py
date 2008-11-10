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


# FreeEMS-Tuner
__revision__ = '0.0.1-2008110600'
__name__ = 'FreeEMS-Tuner'
__title__ = '%s %s' % (__name__, __revision__)


# Load libraries
import libs.data, libs.config, libs.logger, protocols, gui, comms

# Begin setting up program
libs.data.createDirectory()

# Turn on logging
libs.logger.setup()

# Load default comms interface
comms.loadDefault()

# Load default hardware interface protocol
protocols.loadDefault()

# Setup GUI
gui.load()

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


import os, sys, tarfile
import json


def createDirectory():
    '''
    Create data directory if it does not exist
    '''
    # Create path
    path = getPath()

    # Check to see if it exists
    if os.path.exists(path) and os.path.isdir(path):
        return
        
    # Attempt to create
    os.mkdir(path)    


def getPath():
    '''
    Get path to data directory
    '''
    cwd = sys.path[0]
    if not len(cwd):
        cwd = os.getcwd()
        
    return cwd+'/data/'


def loadProtocolDataFile(filename):
    '''
    Loads a json data file from the protocols
    data directory and returns its contents as python
    '''
    protocol = 'protocols/IFreeEMS_Vanilla/0_0_1/'

    path = getPath()+protocol+filename+'.js'

    if not os.path.exists(path) or not os.path.isfile(path):
        return None

    file = open(path, 'r')
    data = file.read()

    # Load json
    parser = json.JsonReader()
    return parser.read(data)


def installProtocolDataFiles(archive_path):
    '''
    Unpacks a specially made tgz file into the protocol data directory
    '''
    if not tarfile.is_tarfile(archive_path):
        return False

    archive = tarfile.open(archive_path, 'r:gz') 

    # Check files will be extracted into the correct directory
    for path in archive.getnames():
        if not path.startswith('protocols/'):
            return False

    # Extract
    archive.extractall(getPath())

    return True

# Stratosphere Linux IPS. A machine-learning Intrusion Detection System
# Copyright (C) 2021 Sebastian Garcia

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
# Contact: eldraco@gmail.com, sebastian.garcia@agents.fel.cvut.cz, stratosphere@aic.fel.cvut.cz

import os
from watchdog.events import RegexMatchingEventHandler
import redis
from slips_files.core.database import __database__

class FileEventHandler(RegexMatchingEventHandler):
    """ Adds newly generated zeek log files in zeek_files/ dir to the database for processing """
    REGEX = [r".*\.log$"]

    def __init__(self, config):
        super().__init__()
        self.config = config
        # Start the DB
        __database__.start(self.config)

    def on_created(self, event):
        self.process(event)

    def on_moved(self, event):
        """ this will be triggered everytime zeek renames all log files"""
        # tell inputProcess to delete old files
        __database__.publish("remove_old_files",True)


    def process(self, event):
        filename, ext = os.path.splitext(event.src_path)
        __database__.add_zeek_file(filename)

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

import multiprocessing
import sys


# Output Process
class OutputProcess(multiprocessing.Process):
    """ A class process to output everything we need. Manages all the output """
    def __init__(self, inputqueue, verbose, debug, config):
        multiprocessing.Process.__init__(self)
        self.verbose = verbose
        self.debug = debug
        self.queue = inputqueue
        self.config = config
        # self.quiet manages if we should really print stuff or not
        self.quiet = False
        if self.verbose > 2:
            print('Verbosity: {}. Debugging: {}'.format(str(self.verbose), str(self.debug)))

    def process_line(self, line):
        """
        Extract the verbosity level, the sender and the message from the line.
        The line is separated by | and the fields are:
        1. The level. It means the importance/verbosity we should be. The lower the less important
            The level is a two digit number
            first digit: verbosity level
            second digit: debug level
            both levels range from 0 to 3

            verbosity:
                0 - don't print
                1 - basic operation/proof of work
                2 - log I/O operations and filenames
                3 - log database/profile/timewindow changes

            debug:
                0 - don't print
                1 - print exceptions
                2 - unsupported and unhandled types (cases that may cause errors)
                3 - red warnings that needs examination - developer warnings

            Messages should be about verbosity or debugging, but not both simultaneously
        2. The sender
        3. The message

        The level is always an integer from 0 to 10
        """
        try:
            try:
                level = line.split('|')[0]
                if int(level) < 0 or int(level) >= 100 or len(level) < 2:
                    level = '00'
            except TypeError:
                print('Error in the level sent to the Output Process')
            except KeyError:
                level = '00'
                print('The level passed to OutputProcess was wrongly formated.')
            except ValueError as inst:
                # We probably received some text instead of an int()
                print('Error receiving a text to output. Check that you are sending the format of the msg correctly: level|msg')
                print(inst)
                sys.exit(-1)
            try:
                sender = f"[{line.split('|')[1]}] "
            except KeyError:
                sender = ''
                print('The sender passed to OutputProcess was wrongly formated.')
                sys.exit(-1)
            try:
                # If there are more | inside the msg, we don't care, just print them
                msg = ''.join(line.split('|')[2:])
            except KeyError:
                msg = ''
                print('The message passed to OutputProcess was wrongly formated.')
                sys.exit(-1)
            return (level, sender, msg)
        except KeyboardInterrupt:
            return True
        except Exception as inst:
            print('\tProblem with process line in OutputProcess()')
            print(type(inst))
            print(inst.args)
            print(inst)
            sys.exit(1)

    def output_line(self, line):
        """ Get a line of text and output it correctly """
        (level, sender, msg) = self.process_line(line)
        verbose_level, debug_level = int(level[0]), int(level[1])
        # if verbosity level is 3 make it red
        if debug_level == 3 : msg = f'\033[1;31;40m{msg}\033[00m'
        # There should be a level 0 that we never print. So its >, and not >=
        if verbose_level > 0 and verbose_level <= 3 and verbose_level <= self.verbose:
            print(f'{sender} {msg}')
        elif debug_level > 0 and debug_level <= 3 and debug_level <= self.debug:
            # For now print DEBUG, then we can use colors or something
            print(f'{sender}{msg}')
        # This is to test if we are reading the flows completely

    def run(self):
        try:
            while True:
                line = self.queue.get()
                if line == 'quiet':
                    self.quiet = True
                elif 'stop_process' in line:
                    return True
                elif line != 'stop':
                    if not self.quiet:
                        self.output_line(line)
                else:
                    # Here we should still print the lines coming in the input for a while after receiving a 'stop'. We don't know how to do it.
                    print('Stopping the output thread')
                    return True
        except KeyboardInterrupt:
            return True
        except Exception as inst:
            print('\tProblem with OutputProcess()')
            print(type(inst))
            print(inst.args)
            print(inst)
            sys.exit(1)

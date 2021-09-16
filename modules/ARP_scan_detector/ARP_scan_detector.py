# Ths is a template module for you to copy and create your own slips module
# Instructions
# 1. Create a new folder on ./modules with the name of your template. Example:
#    mkdir modules/anomaly_detector
# 2. Copy this template file in that folder.
#    cp modules/template/template.py modules/anomaly_detector/anomaly_detector.py
# 3. Make it a module
#    touch modules/template/__init__.py
# 4. Change the name of the module, description and author in the variables
# 5. The file name of the python module (template.py) MUST be the same as the name of the folder (template)
# 6. The variable 'name' MUST have the public name of this module. This is used to ignore the module
# 7. The name of the class MUST be 'Module', do not change it.

# Must imports
from slips_files.common.abstracts import Module
import multiprocessing
from slips_files.core.database import __database__
import platform

# Your imports
import json

class Module(Module, multiprocessing.Process):
    # Name: short name of the module. Do not use spaces
    name = 'arp_scan_detector'
    description = 'Module to detect ARP scans.'
    authors = ['Alya']

    def __init__(self, outputqueue, config):
        multiprocessing.Process.__init__(self)
        # All the printing output should be sent to the outputqueue.
        # The outputqueue is connected to another process called OutputProcess
        self.outputqueue = outputqueue
        # In case you need to read the slips.conf configuration file for
        # your own configurations
        self.config = config
        # Start the DB
        __database__.start(self.config)
        # To which channels do you wnat to subscribe? When a message
        # arrives on the channel the module will wakeup
        # The options change, so the last list is on the
        # slips/core/database.py file. However common options are:
        # - new_ip
        # - tw_modified
        # - evidence_added
        # Remember to subscribe to this channel in database.py
        self.c1 = __database__.subscribe('new_flow')
        self.timeout = None

    def print(self, text, verbose=1, debug=0):
        """
        Function to use to print text using the outputqueue of slips.
        Slips then decides how, when and where to print this text by
        taking all the prcocesses into account

        Input
         verbose: is the minimum verbosity level required for this text to
         be printed
         debug: is the minimum debugging level required for this text to be
         printed
         text: text to print. Can include format like 'Test {}'.format('here')

        If not specified, the minimum verbosity level required is 1, and the
        minimum debugging level is 0
        """

        vd_text = str(int(verbose) * 10 + int(debug))
        self.outputqueue.put(vd_text + '|' + self.name + '|[' + self.name + '] ' + str(text))

    def run(self):
        # Main loop function
        while True:
            try:
                # Wait for a message from the channel that a TW was modified
                message = self.c1.get_message(timeout=self.timeout)
                #print('Message received from channel {} with data {}'.format(message['channel'], message['data']))
                if message['data'] == 'stop_process':
                    # Confirm that the module is done processing
                    __database__.publish('finished_modules', self.name)
                    return True
                elif message['channel'] == 'new_flow' and type(message['data'])==str:
                    # Get the profileid and twid
                    profileid = message['data'].split(':')[0]
                    twid = message['data'].split(':')[1]
                    data = message['data']
                    # Convert from json to dict
                    data = json.loads(data)
                    profileid = data['profileid']
                    twid = data['twid']
                    # Get flow as a json
                    flow = data['flow']
                    timestamp = data['stime']
                    # Convert flow to a dict
                    flow = json.loads(flow)
                    flow =  json.loads(flow[list(flow.keys())[0]])
                    protocol = flow['proto']
                    if 'arp' in protocol.lower():
                        pass

            except KeyboardInterrupt:
                # On KeyboardInterrupt, slips.py sends a stop_process msg to all modules, so continue to receive it
                continue
            # except Exception as inst:
            #     self.print('Problem on the run()', 0, 1)
            #     self.print(str(type(inst)), 0, 1)
            #     self.print(str(inst.args), 0, 1)
            #     self.print(str(inst), 0, 1)
            #     return True

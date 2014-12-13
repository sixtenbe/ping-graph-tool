#!/usr/bin/python
# -*- coding: UTF-8 -*-
from numpy import NaN
from os import system
import re
import subprocess
import sys
import traceback
from time import sleep, time

def excepthook(etype, value, tb):
    message = '\nUncaught exception:\n'
    message += ''.join(traceback.format_exception(etype, value, tb))
    with open('error.log', 'a') as log:
        log.write(message)
sys.excepthook = excepthook

#needs some kind of threading support I think

def get_ping_time(ping_string):
    """
    Retrieves the time for ping from the stdout string of ping.
    Will set the time to NaN if timeout occured.

    Keyword arguments:
    ping_string -- return from the ping program
    """
    regex = '[<>=]([\d]+)?ms'
    try:
        ping_time = int(re.search(regex, ping_string).groups()[0])
    except AttributeError:
        pattern = '(time(d|out)|unreachable|General failure)'
        flags = re.IGNORECASE
        if not re.search(pattern, ping_string, flags) == None:
            #ping timeout occured set return to Not a number
            ping_time = NaN
        else:
            raise Exception, "faulty ping string: {0!s}".format(ping_string)

    return ping_time, time()

class ping():

    def __init__(self, server, timeout):
        """
        Will ping the specified server using the given timeout

        Keyword arguments:
        server -- the server url to ping
        timeout -- the time to timeout in milliseconds (ms)
        """
        #convert timeout to int as float is not unexpected
        cmd = 'ping {0!s} -t -w {1:d}'.format(server, int(timeout))

        startupinfo = subprocess.STARTUPINFO()
        #startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.dwFlags |= subprocess._subprocess.STARTF_USESHOWWINDOW
        self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                    stdin=subprocess.PIPE, shell=False,
                                    startupinfo=startupinfo)
        self.server = server
        self.timeout = timeout

    def __exit__(self, type, value, traceback):
        #terminate the process
        self.proc.kill()

    def __enter__(self):
        i=0
        #dump the two first rows as they don't contain anything interesting
        output = self.proc.stdout.readline()
        output = self.proc.stdout.readline()

        while not output == '':
            output = self.proc.stdout.readline()
            #if output.find('statistics') > -1:
            if output.find('stat') > -1:
                #end of data stream
                break

            yield get_ping_time(output)
            i+=1

        if i == 0:
            raise Exception,"cmd failed to run properly: {0!s}".format(output)

class ping_native():
    def __init__(self, server, timeout):
        """
        Will ping the specified server using the given timeout

        Keyword arguments:
        server -- the server url to ping
        timeout -- the time to timeout in milliseconds (ms)
        """

        self.server = server
        self.timeout = timeout



# -*- coding: UTF-8 -*-

############################
# Setup script for current source control
############################

from distutils.core import setup
import matplotlib
import sys
import py2exe
from glob import glob

#append py2exe to the command line variable if needed
if sys.argv.count('py2exe') == 0:
    sys.argv.append('py2exe')

ver = '01.00'
relstate = 'Stable'
copyright = "Copyright Kyomujin, no rights reserved"



#Create a list of files to include
files = matplotlib.get_py2exe_datafiles()
#remove the fonts from matplotlib
#this fixes some problem with matplotlib not finding them
d = []
for i in range(len(files)):
    if files[i][0].find('fonts')>= 0:
        d.insert(0, i)
for i in d:
    files.pop(i)
del d
files.append(('Microsoft.VC90.CRT', glob(r'MSVC90\*.*')))


setup(windows = [{'script': 'ping_gui.pyw'}],
    options = {'py2exe': {
                        'optimize': 2,
                        'compressed': True,
                        'bundle_files': 1,
                        #'dist_dir': 'frozen',
                        'dist_dir': 'J:/python/#frozen',
                        'excludes' :['_ssl', '_hashlib', '_socket'
                                    'Tkconstants', 'Tkinter', 'tcl',
                                    '_gtkagg', '_tkagg',
                                    'pyreadline',
                                    'doctest', 'optparse',
                                    'pickle',
                                    'webbrowser', 'cookielib',
                                    'email', 'pydoc_topics',
                                    'BaseHTTPServer',
                                    'SocketServer', '_MozillaCookieJar'],
                        'dll_excludes' :['msvcr71.dll',
                                        'mswsock.dll', 'powrprof.dll',
                                        'w9xpopen.exe']
                        },
                'build': {'build_base': 'J:/python/build'}
                },
    name='Ping graphing program',
    version=str(ver),
    description='Plots the ping time to a server',
    author='Kyomujin',
    data_files = files)


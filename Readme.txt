The recommended way to use this is to have python installed and just run the file, but using freeze.py it can also be frozen to a .exe.

The major limitation of this program right now is that it only function on windows, as it uses popen to grab the output from ping.exe


Packages needed to run/freeze this:
    python 2.7 (2.6 should work just fine as well)
    numpy
    wxpython
    matplotlib
    unittest (for test.py, but I think this is inlcluded with all python releases)
    py2exe (needed to run freeze.py to create a windows .exe file)
    
For freezing you also need some .dll files:
    msvcp90.dll
    msvcm90.dll
    msvcr90.dll
    Microsoft.VC90.CRT.manifest
More information about these files should be possible to find on the website for py2exe:
http://www.py2exe.org/
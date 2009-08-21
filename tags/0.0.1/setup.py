#!/usr/bin/env python

from distutils.core import setup
import sys, os, os.path

version = "0.5.3"

### this manifest enables the standard Windows XP-looking theme
##manifest = """
##<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
##<assembly xmlns="urn:schemas-microsoft-com:asm.v1"
##manifestVersion="1.0">
##<assemblyIdentity
##    version="0.64.1.0"
##    processorArchitecture="x86"
##    name="Controls"
##    type="win32"
##/>
##<description>Picalo</description>
##<dependency>
##    <dependentAssembly>
##        <assemblyIdentity
##            type="win32"
##            name="Microsoft.Windows.Common-Controls"
##            version="6.0.0.0"
##            processorArchitecture="X86"
##            publicKeyToken="6595b64144ccf1df"
##            language="*"
##        />
##    </dependentAssembly>
##</dependency>
##</assembly>
##"""
##
# returns a list of all the files in a directory tree
def walk_dir(dirname):
    files = []
    ret = [ (dirname, files) ]
    for name in os.listdir(dirname):
        fullname = os.path.join(dirname, name)
        if os.path.isdir(fullname) and os.path.split(fullname)[1] != ".svn":
            ret.extend(walk_dir(fullname))
        else:
            if os.path.split(fullname)[1] != ".svn":
                files.append(fullname)
    return ret
  

# Generic options
options = {
    'name':             'Bezier Track Demo',
    'version':          "0.0.1",
    'description':      '',
    'long_description': '',
    'author':           'Timothy Baldock',
    'author_email':     'tb@entropy.me.uk',
    'url':              'http://entropy.me.uk/pytile',
    "zipfile":          "python\\library.zip",
##    "data_files":       ["licence.txt", "tc.config", "test.png"] + walk_dir("languages")
}

# windows specific
if len(sys.argv) >= 2 and sys.argv[1] == "py2exe":
    try:
        import py2exe
    except ImportError:
        print "Could not import py2exe. Aborting windows exe output"
        sys.exit(0)
    # windows-specific options
    options["windows"] = [
        {
        "script":"bezier.py",
        "windows":"bezier.py",
        },
    ]



# mac specific
##if len(sys.argv) >= 2 and sys.argv[1] == 'py2app':
##    try:
##        import py2app
##    except ImportError:
##        print 'Could not import py2app.   Mac bundle could not be built.'
##    sys.exit(0)
##    # mac-specific options
##    options['app'] = ['rur_start.py']
##    options['options'] = {
##    'py2app': {
##        'argv_emulation': True,
##        'iconfile': 'rur_images/icon_mac.icns',
##        'packages': [],
##        }
##    }


# run the setup
setup(**options)
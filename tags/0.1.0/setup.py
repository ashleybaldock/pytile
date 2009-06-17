#!/usr/bin/env python
# coding: UTF-8
#
# This file is part of the pyTile project
#
# http://entropy.me.uk/pytile
#
## Copyright © 2008-2009 Timothy Baldock. All Rights Reserved.
##
## Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
##
## 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
##
## 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
##
## 3. The name of the author may not be used to endorse or promote products derived from this software without specific prior written permission from the author.
##
## 4. Products derived from this software may not be called "pyTile" nor may "pyTile" appear in their names without specific prior written permission from the author.
##
## THIS SOFTWARE IS PROVIDED BY THE AUTHOR "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. 



from distutils.core import setup
import sys, os, os.path

version = "0.1"

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
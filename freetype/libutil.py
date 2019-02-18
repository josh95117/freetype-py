# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#  Utilities for freetype-py to discover a FreeType C library
#  Distributed under the terms of the new BSD license.
# -----------------------------------------------------------------------------

"""
Utilities for discovering a FreeType C library (.dll, .dylib, .so) for use with
freetype-py. Uses techniques based on ctypes.util.find_library(), but with a
more generous regex-based search so as to locate variants such as
"freetype6.dll", "libfreetype.6.dylib", etc. which the standard
ctypes.util.find_library fails to match under some platforms.
"""

import os
import re
import sys

if os.name == "nt":
    def find_ftlibrary(freetypepydir):
        """
        Imlpementation for Windows. Searches custom/local dir, then all
        directories in $PATH for DLL.
        """
        p = re.compile(r'(lib)?freetype.*\.dll', flags=re.I)

        searchdirs = [freetypepydir] + os.environ['PATH'].split(os.pathsep)

        for d in searchdirs:
            if os.path.isdir(d):  # checks existence + is directory
                for f in os.listdir(d):
                    fp = os.path.join(d, f)
                    if os.path.isfile(fp) and p.match(f):
                        return fp

elif os.name == "posix" and sys.platform == "darwin":
    from ctypes.macholib.dyld import (DEFAULT_FRAMEWORK_FALLBACK,
                                      DEFAULT_LIBRARY_FALLBACK)

    def find_ftlibrary(freetypepydir):
        """
        Implementation for Mac. The ctypes find_library implementation is
        somewhat complicated but it essentially searches a number of
        optionally-defined `_PATH` environment variables and predefined
        directories in a preferential order. Here, we mimic that, but
        start with our custom/local directory first (and also use a regex)
        to find a suitable .dylb.
        """
        # TODO: determine whether the FRAMEWORK paths should be included
        # in this search.
        p = re.compile(r'(lib)?freetype.*\.dylib', flags=re.I)
        searchdirs = [freetypepydir]
        for evn in ("DYLD_FRAMEWORK_PATH",
                    "DYLD_LIBRARY_PATH",
                    "DYLD_FALLBACK_FRAMEWORK_PATH",
                    "DYLD_FALLBACK_LIBRARY_PATH"):
            ev = os.environ.get(evn)

            if ev:
                searchdirs += [p for p in ev.split(os.pathsep) if p]

        searchdirs += DEFAULT_FRAMEWORK_FALLBACK + DEFAULT_LIBRARY_FALLBACK

        for d in searchdirs:
            if os.path.isdir(d):  # checks existence + is directory
                for f in os.listdir(d):
                    fp = os.path.join(d, f)
                    if os.path.isfile(fp) and p.match(f):
                        return fp

else:
    # TODO: adapt ctypes logic for other platforms where ctypes find_library
    # fails to locate filename variants.

    from ctypes.util import find_library

    def find_ftlibrary(freetypepydir):
        """
        Implementation for all other platforms. It first searches the
        freetypepydir with a generous search pattern. If a .so is not
        found, it falls back to the not-as-generous ctypes routine to
        search for a system-installed freetype.so.
        """
        p = re.compile(r'(lib)?freetype.*\.so.*', flags=re.I)

        for f in os.listdir(freetypepydir):
            fp = os.path.join(freetypepydir, f)
            if os.path.isfile(fp) and p.match(f):
                return fp

        return find_library('freetype')

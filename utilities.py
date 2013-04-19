from __future__ import print_function

import sys

def debug_print (*args, **kwargs):
    if "file" not in kwargs:
        kwargs["file"] = sys.stderr
    print("DEBUG:", *args, **kwargs)

def debug_silence (*args, **kwargs):
    pass


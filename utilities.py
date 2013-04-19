from __future__ import print_function

import sys

def debug (*args, **kwargs):
    if "file" not in kwargs:
        kwargs["file"] = sys.stderr
    print("DEBUG:", *args, **kwargs)


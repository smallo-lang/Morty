import sys
from pathlib import Path

import termcolor as tc


def err(msg):
    tc.cprint(f'Error: {msg.lower()}', 'red')
    sys.exit(1)


def source_file_extension_is_invalid(src):
    return Path(src).suffix != '.so'

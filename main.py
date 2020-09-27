import sys

import util
from Loader import Loader
from Preprocessor import Preprocessor

if __name__ == '__main__':
    if len(sys.argv) < 2:
        util.err('source file not specified')

    src = sys.argv[1]
    loader = Loader()
    loader.load(src)

    if loader.err:
        util.err(f'[loader] {loader.err}')

    pre = Preprocessor()
    pre.process(loader.code)

    if pre.err:
        util.err(f'[preprocessor] {pre.err}')

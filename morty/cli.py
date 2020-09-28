import click
import colorama

from . import util
from .Loader import Loader
from .Preprocessor import Preprocessor
from . import make

colorama.init()


@click.command(help='assemble SmallO assembly code.')
@click.argument('source')
@click.option('--target', default='out.rk', help='path to bytecode target')
def assemble(source, target):
    if util.source_file_extension_is_invalid(source):
        util.err("source file extension is invalid: '.so' expected")

    loader = Loader()
    loader.load(source)

    if loader.err:
        util.err(f'[loader] {loader.err}')

    pre = Preprocessor()
    pre.process(loader.code)

    if pre.err:
        util.err(f'[preprocessor] {pre.err}')

    make.write(
        code=make.code(
            mem=make.mem(*pre.memory),
            ins=pre.instructions
        ),
        path=target
    )


if __name__ == '__main__':
    assemble()

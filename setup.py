from setuptools import setup, find_packages

setup(
    name='morty-smallo-assembler',
    version='0.1.0',
    author='Viktor A. Rozenko Voitenko',
    author_email='sharp.vik@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click',
        'colorama',
        'termcolor',
    ],
    entry_points="""
        [console_scripts]
        morty=morty.cli:assemble
    """,
)

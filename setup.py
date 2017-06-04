from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='denonavr_serial',
    version='0.0.1',
    description='Library for controlling Denon AVR Receivers via a serial port',
	long_description=long_description,
    url='https://github.com/auchter/denonavr_serial',
    author='Michael Auchter',
    author_email='a@phire.org',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='denon stereo receiver avr serial rs232',
    packages=['denonavr_serial'],
    install_requires=[],
    entry_points={}
)

# setup.py

from setuptools import find_packages, setup

requirements = [line.strip() for line in open("requirements.txt")]

setup(
  name='energy_balance',
  version='0.1',
  packages=find_packages(),
  install_requires=requirements,
)
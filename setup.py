# setup.py

from setuptools import find_packages, setup

requirements = [line.strip() for line in open("requirements.txt")]

setup(
  name='energy_balance',
  version='0.2',
  packages=find_packages(),
  install_requires=requirements,
  package_data={"energy_balance": ["etc/config.ini"]},
)

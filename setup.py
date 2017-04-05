import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()
    
# Allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-rt-pdb',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description='',
    long_description=README,
    url='',
    author='',
    author_email='',
    classifiers=[],
    install_requires=['django-picklefield']
)

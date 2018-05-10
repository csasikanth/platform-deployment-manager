import uuid
from setuptools import setup,find_packages
import os
from pip.req import parse_requirements
import shutil
import sys

LIB_DIR_NAME = 'platform_deployment_manager' # name of the library 

#def parse_requirements(filename):
#    """ load requirements from a pip requirements file """
#    lineiter = (line.strip() for line in open(filename))
#    return [line for line in lineiter if line and not line.startswith("#")]

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

# To form directory structure of platfrom deployment manager.
# Make a copy from api/src/main/resources to platform_deployment_manager directory.
def get_packages():
    try:
        shutil.copytree('api/src/main/resources', LIB_DIR_NAME)
    except Exception, e:
        print "Destination folder exist. Proceeding setup with existing folder.."
        # sys.exit()
        pass
        
get_packages()

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
requirements_file = os.path.join(BASE_DIR + os.sep + LIB_DIR_NAME, 'requirements.txt')
requirements = parse_requirements(requirements_file, session=uuid.uuid1())
#requirements = parse_requirements(requirements_file)
print requirements
requirements_list = [ str(package.req) for package in requirements]

setup(
    name="platform_deployment_manager",
    version="1.0",
    author="Sasi Kanth",
    author_email="saschand@cisco.com",
    description=("The Deployment Manager is a service that manages package deployment and application creation for a single PNDA cluster."),
    license="MIT",
    install_requires=requirements_list,
    url="https://github.com/pndaproject/platform-deployment-manager",
    packages=[LIB_DIR_NAME],
    long_description=read('README.md'),
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7"
    ],
)



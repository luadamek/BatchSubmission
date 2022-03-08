from setuptools import setup

setup(
   name='batch_submission',
   version='0.1',
   description='A module to submit jobs to a batch system, and then to monitor them.',
   author='Lukas Adamek',
   author_email='lukas.adamek@mail.utoronto.ca',
   packages=['batch_submission'],
   install_requires=[htcondor],
)

from setuptools import setup
import os

with open(os.path.join(os.path.dirname(__file__), 'requirements.txt')) as f:
    required = f.read().splitlines()

setup(name='SqsToLambdaListener',
    version='0.1',
    description='Library class to pop messages off SQS and submit them to AWS lambda',
    url='https://github.com/CurryEleison/SqsToLambdaListener',
    author='Thomas Petersen',
    author_email='petersen@temp.dk',
    license='Apache',
    packages=['SqsToLambdaListener'],
    install_requires=required,
    zip_safe=False)

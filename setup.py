from setuptools import setup

setup(
    name='django-cal',
    version='0.1dev',
    author='Maik Hoepfel',
    packages=['django_cal',],
    license='BSD',
    long_description=open('README.md').read(),
    install_requires=[
        'python-dateutil < 2.0'  # dateutil (used by vobject) 2+ only works with Python 3
        'vobject',
    ],
)

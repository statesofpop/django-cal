from setuptools import setup

setup(
    name='django-cal',
    version='0.1dev',
    author='Maik Hoepfel',
    packages=['django_cal',],
    license='BSD',
    long_description=open('README.md').read(),
    install_requires=[
        'vobject',
    ],
)

from setuptools import setup

setup(
    name='django-cal',
    version='0.2',
    author='Maik Hoepfel',
    author_email = 'm@maikhoepfel.de',
    description = ('Django app to enable exporting of events to iCalendar files.'),
    packages=['django_cal',],
    keywords='Django iCalendar iCal ics vobject',
    url = 'http://github.com/statesofpop/django-cal',
    license='BSD',
    long_description=open('README.md').read(),
    install_requires=[
        'python-dateutil < 2.0',  # dateutil (used by vobject) 2+ only works with Python 3
        'vobject',
        'Django',
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        'License :: OSI Approved :: BSD License',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)

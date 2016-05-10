from setuptools import setup

setup(
    name='django-cal',
    version='0.2.3',
    author='Maik Hoepfel',
    author_email = 'm@maikhoepfel.de',
    description = ('Django app to enable exporting of events to iCalendar files.'),
    packages=['django_cal',],
    keywords='Django iCalendar iCal ics vobject',
    url = 'http://github.com/statesofpop/django-cal',
    license='BSD',
    install_requires=[
        'python-dateutil < 2.0',  # dateutil (used by vobject) 2+ only works with Python 3
        'vobject',
        'Django',
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        'License :: OSI Approved :: BSD License',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2 :: Only',
    ],
)

from setuptools import setup

setup(
    name='django-cal',
    version='0.3.0',
    author='Maik Hoepfel',
    author_email='m@maikhoepfel.de',
    description=(
        'Django app to enable exporting of events to iCalendar files.'
    ),
    packages=['django_cal', ],
    keywords='Django iCalendar iCal ics vobject',
    url='http://github.com/statesofpop/django-cal',
    license='BSD',
    install_requires=[
        'python-dateutil',
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
    ],
)

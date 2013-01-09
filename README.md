# django-cal #

Django app to enable exporting of events to iCalendar files. 
Imitates behavior of django.contrib.syndication and is based upon vobject
(<http://vobject.skyhouseconsulting.com/>).

Heavy inspiration came from Christian Joergensen
(<http://www.technobabble.dk/2008/mar/06/exposing-calendar-events-using-icalendar-django/>)
and Derek Willis (<http://blog.thescoop.org/archives/2007/07/31/django-ical-and-vobject/>).

## Installation ##

    pip install django-cal
    
## Documentation ##

### Overview ###

Please see Django's syndication feed framework documentation, django_cal imitates its
behavior: <http://docs.djangoproject.com/en/1.2/ref/contrib/syndication/>.


### Defining event properties ###

The following parameters work analagous to how they're implemented in 
django.contrib.syndication. That means, the framework checks in the following
order: `self.$param(obj)`, `self.$param()`, `self.$param`; `obj` being the object 
returned by `self.get_object`.
    
    items           Returns the list of events.
                    Must be set.
    filename        Filename of the file returned in the view.
                    Optional, defaults to 'events.ics'.
    cal_name        Name of the calendar.
                    Optional, defaults to None.
    cal_desc        Description of the calendar. 
                    Optional, defaults to None.

    item_summary    The "title" of the item.
                    Optional, defaults to unicode representation of item.

    item_end        Duration or end time of item.
    item_duration   Optional, defaults to None. Must not define both.
    
    item_rruleset   Optional, defaults to None.
                    Should return dateutil.rruleset instance
                    for recurrent events.

    item_url        Optional, default calls item.get_absolute_url()
                    Should return a URL with the fully-qualified domain and
                    protocol (e.g. 'http://www.example.com/blog/') or an
                    absolute path (e.g. '/events/'). If only a path is
                    present, the 'django.contrib.sites' app will be used
                    to insert the domain of the current site.
                    Note: To find the current site, 'django.contrib.sites'
                          must be in your settings.INSTALLED_APPS (it is
                          there by default)

    item_uid        All correspond to their vEvent equivalents.
    item_start      All optional, all default to None.
    item_description
    item_categories
    item_comment
    item_location
    item_last_modified
    item_created

### Duration of events ###

django-cal imitates vobject behavior regarding start and end of events. In short:
Use Date objects for all-day events, DateTime for more granular control.
Define either duration or end time, never both.

### Complex behavior ###

`self.get_object` can be overriden to allow for more complex events, as is possible for
[syndication feeds](https://docs.djangoproject.com/en/1.2/ref/contrib/syndication/#a-complex-example).


    
## Dependencies ##

  * [vObject](http://vobject.skyhouseconsulting.com/)
  * [dateutil](http://labix.org/python-dateutil/)
  * [Django](http://djangoproject.com/)

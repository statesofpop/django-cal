""" Django app to enable exporting of events to iCalendar files.
    Imitates behavior of django.contrib.syndication.

    Heavy inspiration came from Christian Joergensen
        http://www.technobabble.dk/2008/mar/06/exposing-calendar-events-using-icalendar-django/
    and Derek Willis
        http://blog.thescoop.org/archives/2007/07/31/django-ical-and-vobject/ .
"""

import vobject

from django.http import HttpResponse, Http404
from django.utils.encoding import force_unicode

# Mapping of iCalendar event attributes to prettier names.
EVENT_ITEMS = (
    ('uid', 'item_uid'),
    ('dtstart', 'item_start'),
    ('dtend', 'item_end'),
    ('duration', 'item_duration'),
    ('summary', 'item_summary'),
    ('location', 'item_location'),
    ('url', 'item_url'),
    ('comment', 'item_comment'),
    ('last_modified', 'item_last_modified'),
    ('created', 'item_created'),
)

class Events(object):
    def __call__(self, request, *args, **kwargs):
        """ Makes Events callable for easy use in your urls.py """
        try:
            obj = self.get_object(request, *args, **kwargs)
        except ObjectDoesNotExist:
            raise Http404('Events object does not exist.')
        ical = self.get_ical(obj, request)
        response = HttpResponse(ical.serialize(), mimetype='text/calendar')
        filename = self.__get_dynamic_attr('filename', obj)
        # following added for IE, see
        # http://blog.thescoop.org/archives/2007/07/31/django-ical-and-vobject/
        response['Filename'] = filename 
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response


    def __get_dynamic_attr(self, attname, obj, default=None):
        """ Returns first defined occurence of the following: 
                self.$attname(obj)
                self.$attname()
                self.$attname
                default
            Taken from django.contrib.syndication.views.Feed
        """
        try:
            attr = getattr(self, attname)
        except AttributeError:
            return default
        if callable(attr):
            # Check func_code.co_argcount rather than try/excepting the
            # function and catching the TypeError, because something inside
            # the function may raise the TypeError. This technique is more
            # accurate.
            if hasattr(attr, 'func_code'):
                argcount = attr.func_code.co_argcount
            else:
                argcount = attr.__call__.func_code.co_argcount
            if argcount == 2: # one argument is 'self'
                return attr(obj)
            else:
                return attr()
        return attr

    def get_ical(self, obj, request):
        """ Returns a populated iCalendar instance. """
        cal = vobject.iCalendar()
        items = self.__get_dynamic_attr("items", obj)
        cal_name = self.__get_dynamic_attr("cal_name", obj)
        cal_desc = self.__get_dynamic_attr("cal_desc", obj)
        # Add calendar name and description if set 
        if cal_name:
            cal.add('x-wr-calname')
            cal.x_wr_calname.value = cal_name
        if cal_desc:
            cal.add('x-wr-caldesc')
            cal.x_wr_caldesc.value = cal_desc

        for item in items:
            event = cal.add('vevent')
            for vkey, key in EVENT_ITEMS:
                value = self.__get_dynamic_attr(key, item)
                if value:
                    event.add(vkey).value = value
        return cal

    # ONLY DEFAULT PARAMETERS FOLLOW #

    def get_object(self, request, *args, **kwargs):
        return None
    
    def item_summary(self, item):
        return force_unicode(item)

    def filename(self, item):
        return u"events.ics"

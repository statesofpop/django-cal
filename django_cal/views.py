from __future__ import unicode_literals, absolute_import

import vobject
from django.db.models import ObjectDoesNotExist
from django.http import HttpResponse, Http404
from django.conf import settings
from django.utils import six

from django.contrib.syndication.views import add_domain
import django


if add_domain.__code__.co_argcount < 3:
    # Django <= 1.2
    # Source: Django 1.4 django.contrib.syndication.views
    from django.utils.encoding import iri_to_uri

    def add_domain(domain, url, secure=False):
        protocol = 'https' if secure else 'http'
        if url.startswith('//'):
            # Support network-path reference (see #16753)
            # RSS requires a protocol
            url = '{}:{}'.format(protocol, url)
        elif (
            not url.startswith('http://')
            or url.startswith('https://')
            or url.startswith('mailto:')
        ):
            # 'url' must already be ASCII and URL-quoted, so no need
            # for encoding conversions here.
            url = iri_to_uri('{}://{}{}'.format(protocol, domain, url))
        return url

if 'django.contrib.sites' in settings.INSTALLED_APPS:
    if django.VERSION >= (1, 7):
        from django.contrib.sites.shortcuts import get_current_site
    elif django.VERSION >= (1, 3):
        # Django >= 1.3
        from django.contrib.sites.models import get_current_site
    else:
        # Django <= 1.2
        # Source: Django 1.4 django.contrib.sites.models
        from django.contrib.sites.models import Site, RequestSite

        def get_current_site(request):
            """
            Checks if contrib.sites is installed and returns either the current
            ``Site`` object or a ``RequestSite`` object based on the request.
            """
            if Site._meta.installed:
                current_site = Site.objects.get_current()
            else:
                current_site = RequestSite(request)
            return current_site
else:
    get_current_site = None


# Mapping of iCalendar event attributes to prettier names.
# Last boolean indicates whether self.__get_dynamic_attr(key, item) should
# return an iterable of return values (i.e., whether the key supports multiple
# content lines).
EVENT_ITEMS = (
    ('uid', 'item_uid', False),
    ('dtstart', 'item_start', False),
    ('dtend', 'item_end', False),
    ('duration', 'item_duration', False),
    ('summary', 'item_summary', False),
    ('description', 'item_description', False),
    ('location', 'item_location', False),
    ('url', 'item_url', False),
    ('comment', 'item_comment', False),
    ('status', 'item_status', False),
    ('attendee', 'item_attendee', True),
    ('organizer', 'item_organizer', False),
    ('last-modified', 'item_last_modified', False),
    ('created', 'item_created', False),
    ('categories', 'item_categories', False),
    ('rruleset', 'item_rruleset', False),
)


class Events(object):
    def __call__(self, request, *args, **kwargs):
        """ Makes Events callable for easy use in your urls.py """
        try:
            obj = self.get_object(request, *args, **kwargs)
        except ObjectDoesNotExist:
            raise Http404('Events object does not exist.')
        ical = self.get_ical(obj, request)
        response = HttpResponse(
            ical.serialize(),
            content_type='text/calendar;charset={}'.format(
                settings.DEFAULT_CHARSET
            ))
        filename = self.__get_dynamic_attr('filename', obj)
        # following added for IE, see
        # http://blog.thescoop.org/archives/2007/07/31/django-ical-and-vobject/
        response['Filename'] = filename
        response['Content-Disposition'] = 'attachment; filename={}'.format(
            filename
        )
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
            # Check co_argcount rather than try/excepting the function and
            # catching the TypeError, because something inside the function
            # may raise the TypeError. This technique is more accurate.
            try:
                code = six.get_function_code(attr)
            except AttributeError:
                code = six.get_function_code(attr.__call__)
            if code.co_argcount == 2:       # one argument is 'self'
                return attr(obj)
            else:
                return attr()
        return attr

    def get_ical(self, obj, request):
        """ Returns a populated iCalendar instance. """
        def add_content_line(event, vkey, ret_value):
            """
            Adds content line(s) as specified by vkey and ret_value to the
            event.
            ret_value is either a plain value, or a 2-tuple of 1) a value and
            2) a dictionary of parameters.
            """
            # Optionally unpack parameter tuple.
            if isinstance(ret_value, tuple):
                (value, params) = ret_value
            else:
                value = ret_value
                params = None

            content_line = None
            # Set content line value.
            if value:
                if vkey == 'rruleset':
                    event.rruleset = value
                else:
                    if vkey == 'url' and current_site:
                        value = add_domain(
                            current_site.domain,
                            value,
                            request.is_secure(),
                        )
                    content_line = event.add(vkey)
                    content_line.value = value
            # Set content line parameters.
            if params and content_line:
                for p in params:
                    parameter = params[p]
                    content_line.params[p] = [parameter]
            return

        cal = vobject.iCalendar()
        cal.add('method').value = 'PUBLISH'  # IE/Outlook needs this
        items = self.__get_dynamic_attr("items", obj)
        cal_name = self.__get_dynamic_attr("cal_name", obj)
        cal_desc = self.__get_dynamic_attr("cal_desc", obj)
        # Add calendar name and description if set
        if cal_name:
            cal.add('x-wr-calname').value = cal_name
        if cal_desc:
            cal.add('x-wr-caldesc').value = cal_desc

        if get_current_site:
            current_site = get_current_site(request)
        else:
            current_site = None

        for item in items:
            event = cal.add('vevent')
            for vkey, key, multiple in EVENT_ITEMS:
                value_or_list = self.__get_dynamic_attr(key, item)
                if multiple:
                    for ret_value in value_or_list:
                        add_content_line(event, vkey, ret_value)
                else:
                    ret_value = value_or_list
                    add_content_line(event, vkey, ret_value)
        return cal

    # ONLY DEFAULT PARAMETERS FOLLOW #

    def get_object(self, request, *args, **kwargs):
        return None

    def item_summary(self, item):
        return item

    def item_url(self, item):
        return getattr(item, 'get_absolute_url', lambda: None)()

    def filename(self, item):
        return "events.ics"

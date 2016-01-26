import vobject
from django.db.models import ObjectDoesNotExist
from django.http import HttpResponse, Http404
from django.utils.encoding import force_unicode
from django.conf import settings

from django.contrib.syndication.views import add_domain
import django


if add_domain.func_code.co_argcount < 3:
    # Django <= 1.2
    # Source: Django 1.4 django.contrib.syndication.views
    from django.utils.encoding import iri_to_uri

    def add_domain(domain, url, secure=False):
        protocol = 'https' if secure else 'http'
        if url.startswith('//'):
            # Support network-path reference (see #16753) - RSS requires a protocol
            url = '%s:%s' % (protocol, url)
        elif not (url.startswith('http://')
                or url.startswith('https://')
                or url.startswith('mailto:')):
            # 'url' must already be ASCII and URL-quoted, so no need for encoding
            # conversions here.
            url = iri_to_uri(u'%s://%s%s' % (protocol, domain, url))
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
EVENT_ITEMS = (
    ('uid', 'item_uid'),
    ('dtstart', 'item_start'),
    ('dtend', 'item_end'),
    ('duration', 'item_duration'),
    ('summary', 'item_summary'),
    ('description', 'item_description'),
    ('location', 'item_location'),
    ('url', 'item_url'),
    ('comment', 'item_comment'),
    ('last-modified', 'item_last_modified'),
    ('created', 'item_created'),
    ('categories', 'item_categories'),
    ('rruleset', 'item_rruleset')
)

class Events(object):
    def __call__(self, request, *args, **kwargs):
        """ Makes Events callable for easy use in your urls.py """
        try:
            obj = self.get_object(request, *args, **kwargs)
        except ObjectDoesNotExist:
            raise Http404('Events object does not exist.')
        ical = self.get_ical(obj, request)
        response = HttpResponse(ical.serialize(),
            content_type='text/calendar;charset=' + settings.DEFAULT_CHARSET)
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
            for vkey, key in EVENT_ITEMS:
                value = self.__get_dynamic_attr(key, item)
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
                        event.add(vkey).value = value
        return cal

    # ONLY DEFAULT PARAMETERS FOLLOW #

    def get_object(self, request, *args, **kwargs):
        return None

    def item_summary(self, item):
        return force_unicode(item)

    def item_url(self, item):
        return getattr(item, 'get_absolute_url', lambda: None)()

    def filename(self, item):
        return u"events.ics"

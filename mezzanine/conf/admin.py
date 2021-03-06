from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.messages import info
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_text

from mezzanine.conf.models import Setting
from mezzanine.conf.forms import SettingsForm
from mezzanine.utils.cache import (cache_delete, cache_installed,
                                   cache_key_prefix)
from mezzanine.utils.urls import admin_url


class SettingsAdmin(admin.ModelAdmin):
    """
    Admin class for settings model. Redirect add/change views to the list
    view where a single form is rendered for editing all settings.
    """

    class Media:
        js = (
            'modeltranslation/js/force_jquery.js',
            '//ajax.googleapis.com/ajax/libs/jqueryui'
                    '/1.8.2/jquery-ui.min.js',
            'mezzanine/js/admin/tabbed_translatable_settings.js',
        )
        css = {
            'all': (
                'mezzanine/css/admin/tabbed_translation_fields.css',
                'mezzanine/css/admin/settings.css',
            ),
        }

    def changelist_redirect(self):
        changelist_url = admin_url(Setting, "changelist")
        return HttpResponseRedirect(changelist_url)

    def add_view(self, *args, **kwargs):
        return self.changelist_redirect()

    def change_view(self, *args, **kwargs):
        return self.changelist_redirect()

    def changelist_view(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}
        settings_form = SettingsForm(request.POST or None)
        if settings_form.is_valid():
            settings_form.save()
            info(request, _("Settings were successfully updated."))
            if cache_installed():
                cache_key = (cache_key_prefix(request, ignore_device=True) +
                             "context-settings")
                cache_delete(cache_key)
            return self.changelist_redirect()
        extra_context["settings_form"] = settings_form
        extra_context["title"] = u"%s %s" % (
            _("Change"), force_text(Setting._meta.verbose_name_plural))
        return super(SettingsAdmin, self).changelist_view(request,
                                                            extra_context)


admin.site.register(Setting, SettingsAdmin)

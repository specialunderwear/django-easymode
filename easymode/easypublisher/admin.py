import functools

from django import template
from django.conf import settings
from django.conf.urls.defaults import patterns, url
from django.shortcuts import get_object_or_404, render_to_response
from django.utils.translation import ugettext as _
from django.utils.translation import get_language
from django.forms.formsets import all_valid
from django.db import transaction
from django.http import HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin import helpers
from django.core.urlresolvers import reverse
from django.utils.html import mark_safe
from django.utils.encoding import force_unicode
from django.utils.dateformat import format

from reversion.admin import VersionAdmin
from reversion.revisions import Version, Revision
import reversion

from easymode.easypublisher.models import EasyPublisherMetaData
from easymode.tree.admin.relation import ForeignKeyAwareModelAdmin, InvisibleModelAdmin

class EasyPublisher(VersionAdmin):
    """docstring for EasyPublisher"""
    
    object_history_template = "easymode/easypublisher/object_history.html"
    revision_form_template = "easymode/easypublisher/publish_form.html"
    change_form_template = 'easymode/easypublisher/change_form.html'
    
    def get_urls(self):
        """The urls for the publisher"""
        urls = super(EasyPublisher, self).get_urls()
        admin_site = self.admin_site
        opts = self.model._meta
        info = opts.app_label, opts.module_name,
        
        easy_publisher_urls = patterns("",
            url(r"^([^/]+)/drafts/$", admin_site.admin_view(self.drafts_view), name='%s_%s_draftlist' % info),
            url(r"^([^/]+)/drafts/([^/]+)/", admin_site.admin_view(self.publish_view), name='%s_%s_draft' % info),
            url(r"^(.+)/current/$", admin_site.admin_view(self.change_view), {'extra_context':{'current':True}}, name='%s_%s_current' % info)
        )

        return easy_publisher_urls + urls
            
    def drafts_view(self, request, object_id, extra_context=None):
        """Renders the drafts view, listing all drafts"""
        opts = self.model._meta
        action_list = [{"revision": version.revision,
                        "url": reverse("admin:%s_%s_draft" % (opts.app_label, opts.module_name), args=(version.object_id, version.id))}
                       for version in self.get_draft_versions(object_id).select_related("revision__user")]
        context = {
            "action_list": action_list, 
            "title": _("Ongepubliceerde items"), 
            'draft_view':True, 
            'has_draft':self.has_draft(object_id)
        }
        context.update(extra_context or {})
        return super(EasyPublisher, self).history_view(request, object_id, context)
    
    def history_view(self, request, object_id, extra_context=None):
        """Renders the history view, shows the drafts button, but hides the history button"""
        defaults = {
            'has_draft': self.has_draft(object_id)
        }
        defaults.update(extra_context or {})
        return super(EasyPublisher, self).history_view(request, object_id, defaults)
    
    def change_view(self, request, object_id, extra_context=None):
        """Renders the normal editing view, which does not display a draft"""

        latest_draft = self.get_latest_draft(object_id)
        has_publish_perm = request.user.has_perm("easypublisher.can_approve_for_publication")
        context = extra_context or {}

        if latest_draft:
            context['has_draft'] = latest_draft.pk
            
            if not context.get('current', False):
            
                if not has_publish_perm:                
                    return HttpResponseRedirect('drafts/%s/' % latest_draft.pk)
        
        return super(EasyPublisher, self).change_view(request, object_id, context)
        
    @transaction.commit_on_success
    @reversion.revision.create_on_success
    def publish_view(self, request, object_id, version_id, extra_context=None):
        """
        Displays a draft.
        If you have publishing right, the save button will publish the draft.
        If you don't it will just create another draft.
        """
        
        obj = get_object_or_404(self.model, pk=object_id)
        version = get_object_or_404(Version, pk=version_id, object_id=force_unicode(obj.pk))
        
        if not version.revision.easypublishermetadata_set.filter(language=request.LANGUAGE_CODE):
            request.user.message_set.create(message=_("There is no draft available for language %s") % request.LANGUAGE_CODE)
            return HttpResponseRedirect('../../current')
        
        # Generate the context.
        context = {
            "title": _("Publish %(name)s") % {"name": self.model._meta.verbose_name},
            "publish":True,
            'has_draft':True,
            'link_current':True,
            'extra':0
        }
        context.update(extra_context or {})
        return self.render_revision_form(request, obj, version, context, revert=True)
            
    def save_model(self, request, obj, form, change):
        """
        Saves the model if you have publishing right, but only makes
        a draft in reversion if you don't
        """
        
        if request.user.has_perm("easypublisher.can_approve_for_publication"):
            obj.save()
        else:
            reversion.revision.add_meta(EasyPublisherMetaData, status='draft', language=request.LANGUAGE_CODE)
            reversion.revision.comment = "Draft"
            reversion.revision.post_save_receiver(obj, 0)            

    def save_formset(self, request, form, formset, change):
        """
        Saves the formset if you have publishing right, but only makes
        a draft in reversion if you don't
        """

        if request.user.has_perm("easypublisher.can_approve_for_publication"):
            formset.save()
        else:
            reversion.revision.add_meta(EasyPublisherMetaData, status='draft', language=request.LANGUAGE_CODE)
            instances = formset.save(commit=False)
            for instance in instances:
                reversion.revision.post_save_receiver(instance, 0)
            
    def has_draft(self, object_id):
        """Find out if there is a draft version of this model"""
        return len(self.get_draft_revisions(object_id))
    
    def get_draft_revisions(self, object_id):
        """
        retrieve all revision marked as draft that belong to object_id.
        """
        content_type = ContentType.objects.get_for_model(self.model)
        return Revision.objects.filter(
            version__object_id=object_id, 
            version__content_type=content_type,
            easypublishermetadata__status='draft',
            easypublishermetadata__language=get_language()
        ).select_related().distinct()
    
    def get_draft_versions(self, object_id):
        """
        Retrieve all drafts that belong to this item
        """
        content_type = ContentType.objects.get_for_model(self.model)
        versions = Version.objects.filter(
            revision__easypublishermetadata__status='draft',
            revision__easypublishermetadata__language=get_language(),
            object_id=object_id,
            content_type=content_type
        ).distinct()
        
        return versions
        
    def get_latest_draft_revision(self, object_id):
        """
        Retrieve latest draft revision that belongs to object_id.
        """
        revisions = self.get_draft_revisions(object_id)
        num_revisions = len(revisions)
        if num_revisions:
            return revisions[num_revisions-1]
        
        return None
    
    def get_latest_draft(self, object_id):
        """
        Retrieves the latest draft that belongs to object_id.
        """
        latest_revision = self.get_latest_draft_revision(object_id)
        content_type = ContentType.objects.get_for_model(self.model)
        if latest_revision:
            latest_drafts = latest_revision.version_set.filter(content_type=content_type).distinct()
            if len(latest_drafts):
                return latest_drafts[0]
            
        return None
    
    def update_draft(self, version, request):
        """Update the status of the draft belonging to this version"""
        for metadata in version.revision.easypublishermetadata_set.all():
            if request.user.has_perm("easypublisher.can_approve_for_publication"):                
                metadata.status = 'published'
            else:
                metadata.status = 'updated'
            metadata.save()
        
    
    ##     ##    ###    ##     ## 
    ##     ##   ## ##    ##   ##  
    ##     ##  ##   ##    ## ##   
    ######### ##     ##    ###    
    ##     ## #########   ## ##   
    ##     ## ##     ##  ##   ##  
    ##     ## ##     ## ##     ## 
    # this is copy pasted because reversion does not let us do anything with the 
    # messages that go after the you know what.
    # please remove this if nolonger needed
    def render_revision_form(self, request, obj, version, context, revert=False, recover=False):
        """Renders the object revision form."""
        model = self.model
        opts = model._meta
        object_id = obj.pk
        # Generate the model form.
        ModelForm = self.get_form(request, obj)
        formsets = []
        if request.method == "POST":
            # This section is copied directly from the model admin change view
            # method.  Maybe one day there will be a hook for doing this better.
            form = ModelForm(request.POST, request.FILES, instance=obj, initial=self.get_revision_form_data(request, obj, version))
            if form.is_valid():
                form_validated = True
                new_object = self.save_form(request, form, change=True)
            else:
                form_validated = False
                new_object = obj
            prefixes = {}
            for FormSet in self.get_formsets(request, new_object):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                if prefixes[prefix] != 1:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])
                formset = FormSet(request.POST, request.FILES,
                                  instance=new_object, prefix=prefix)
                formsets.append(formset)
            if all_valid(formsets) and form_validated:
                self.save_model(request, new_object, form, change=True)
                form.save_m2m()
                for formset in formsets:
                    self.save_formset(request, form, formset, change=True)
                # _ _ _ ____ ___ ____ _  _    ____ _  _ ___ 
                # | | | |__|  |  |    |__|    |  | |  |  |  
                # |_|_| |  |  |  |___ |  |    |__| |__|  |
                # this is not copy pasted:
                self.update_draft(version, request)
                # end of not copy pasted code
                
                change_message = _(u"Publisher message %(datetime)s") % {"datetime": format(version.revision.date_created, _(settings.DATETIME_FORMAT))}
                self.log_change(request, new_object, change_message)
                self.message_user(request, _(u'%(model)s "%(name)s" publisher message.') % {"model": opts.verbose_name, "name": unicode(obj)})
                # Redirect to the model change form.
                if revert:
                    return HttpResponseRedirect("../../")
                elif recover:
                    return HttpResponseRedirect("../../%s/" % object_id)
                else:
                    assert False
        else:
            # This is a mutated version of the code in the standard model admin
            # change_view.  Once again, a hook for this kind of functionality
            # would be nice.  Unfortunately, it results in doubling the number
            # of queries required to construct the formets.
            form = ModelForm(instance=obj, initial=self.get_revision_form_data(request, obj, version))
            prefixes = {}
            revision_versions = version.revision.version_set.all()
            for FormSet in self.get_formsets(request, obj):
                # This code is standard for creating the formset.
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                if prefixes[prefix] != 1:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])
                formset = FormSet(instance=obj, prefix=prefix)
                # Now we hack it to push in the data from the revision!
                try:
                    fk_name = FormSet.fk.name
                except AttributeError:
                    # This is a GenericInlineFormset, or similar.
                    fk_name = FormSet.ct_fk_field.name
                related_versions = dict([(related_version.object_id, related_version)
                                         for related_version in revision_versions
                                         if ContentType.objects.get_for_id(related_version.content_type_id).model_class() == FormSet.model
                                         and unicode(related_version.field_dict[fk_name]) == unicode(object_id)])
                pk_name = FormSet.model._meta.pk.name
                initial = formset.initial or []
                for initial_row in initial:
                    pk = unicode(initial_row[pk_name])
                    if pk in related_versions:
                        initial_row.update(related_versions[pk].field_dict)
                        del related_versions[pk]
                    else:
                        initial_row["DELETE"] = True
                initial.extend([related_version.field_dict
                                for related_version in related_versions.values()])
                # Reconstruct the forms with the new revision data.
                formset._total_form_count = len(initial)
                formset.initial = initial
                formset._construct_forms()
                # Add this hacked formset to the form.
                formsets.append(formset)
        # Generate admin form helper.
        adminForm = helpers.AdminForm(form, self.get_fieldsets(request, obj), self.prepopulated_fields)
        media = self.media + adminForm.media
        # Generate formset helpers.
        inline_admin_formsets = []
        for inline, formset in zip(self.inline_instances, formsets):
            fieldsets = list(inline.get_fieldsets(request, obj))
            inline_admin_formset = helpers.InlineAdminFormSet(inline, formset, fieldsets)
            inline_admin_formsets.append(inline_admin_formset)
            media = media + inline_admin_formset.media
        # Generate the context.
        context.update({"adminform": adminForm,
                        "object_id": object_id,
                        "original": obj,
                        "is_popup": False,
                        "media": mark_safe(media),
                        "inline_admin_formsets": inline_admin_formsets,
                        "errors": helpers.AdminErrorList(form, formsets),
                        "root_path": self.admin_site.root_path,
                        "app_label": opts.app_label,
                        "add": False,
                        "change": True,
                        "has_add_permission": self.has_add_permission(request),
                        "has_change_permission": self.has_change_permission(request, obj),
                        "has_delete_permission": self.has_delete_permission(request, obj),
                        "has_file_field": True,
                        "has_absolute_url": False,
                        "ordered_objects": opts.get_ordered_objects(),
                        "form_url": mark_safe(request.path),
                        "opts": opts,
                        "content_type_id": ContentType.objects.get_for_model(self.model).id,
                        "save_as": False,
                        "save_on_top": self.save_on_top,})
        # Render the form.
        if revert:
            form_template = self.revision_form_template
        elif recover:
            form_template = self.recover_form_template
        else:
            assert False
        return render_to_response(form_template, context, template.RequestContext(request))


def _add_foreign_key_aware_model_admin_behaviour(method):
    """
    Is used to add some stuff of ForeignKeyAwareModelAdmin to
    EasyPublisher views.
    """
    @functools.wraps(method)
    def altered_view(self, request, object_id, extra_context=None):
        inline_links = {}
        inline_links['extra_forms'] = self.extra_forms(object_id)

        # retrieve link to parent for breadcrumb path
        inline_links.update(self._get_parent_link(object_id))
        if extra_context:
            inline_links.update(extra_context)
        
        return method(self, request, object_id, inline_links)
    
    return altered_view

class EasyPublisherFKAModelAdmin(EasyPublisher, ForeignKeyAwareModelAdmin):
    """fixes the collision between EasyPublisher, ForeignKeyAwareModelAdmin"""

    change_form_template = 'easymode/easypublisher/change_form_with_related_links.html'
    revision_form_template = 'easymode/easypublisher/publish_form_with_related_links.html'
    def get_model_perms(self, request):
        perms = super(EasyPublisherFKAModelAdmin, self).get_model_perms(request)
        perms['invisible_in_admin'] = self.invisible_in_admin
        return perms
    
    def publish_view(self, request, object_id, version_id, extra_context=None):
        inline_links = {}
        inline_links['extra_forms'] = self.extra_forms(object_id)

        # retrieve link to parent for breadcrumb path
        inline_links.update(self._get_parent_link(object_id))
        if extra_context:
            inline_links.update(extra_context)
            
        return EasyPublisher.publish_view(self, request, object_id, version_id, inline_links)
        
    change_view = _add_foreign_key_aware_model_admin_behaviour(EasyPublisher.change_view)
    drafts_view = _add_foreign_key_aware_model_admin_behaviour(EasyPublisher.drafts_view)
    history_view = _add_foreign_key_aware_model_admin_behaviour(EasyPublisher.history_view)

def _add_invisible_model_admin_behaviour(method):
    """
    Is used to add some stuff of InvisibleModelAdmin to
    EasyPublisher views.
    """
    @functools.wraps(method)
    def altered_view(self, request, object_id, extra_context=None):
        # retrieve link to parent for breadcrumb path
        defaults = self._get_parent_link(object_id)

        if extra_context:
            defaults.update(extra_context)
    
        return method(self, request, object_id, extra_context)
    
    return altered_view

class EasyPublisherInvisibleModelAdmin(EasyPublisher, InvisibleModelAdmin):
    """fixes the collision between EasyPublisher and InvisibleModelAdmin"""
        
    def get_model_perms(self, request):
        perms = super(EasyPublisherInvisibleModelAdmin, self).get_model_perms(request)
        perms['invisible_in_admin'] = self.invisible_in_admin
        return perms
    
    def publish_view(self, request, object_id, version_id, extra_context=None):
        """docstring for publish_view"""
        defaults = self._get_parent_link(object_id)

        if extra_context:
            defaults.update(extra_context)
            
        return EasyPublisher.publish_view(self, request, object_id, version_id, defaults)      
         
    change_view = _add_invisible_model_admin_behaviour(EasyPublisher.change_view)
    drafts_view = _add_invisible_model_admin_behaviour(EasyPublisher.drafts_view)
    history_view = _add_invisible_model_admin_behaviour(EasyPublisher.history_view)

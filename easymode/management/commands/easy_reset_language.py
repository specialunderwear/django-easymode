from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import get_models, get_app, get_model
from django.utils.encoding import force_unicode
from django.utils import translation

from easymode import i18n

class Command(BaseCommand):
    help = """
        easy_reset_language <target locale> <app>
        
        will clear all fields for the locale in question so the values will be read from
        the locale again.
        
        example:
        ./manage.py easy_reset_language en myapp.mymodel
        
        This will clear myapp.mymodel in the en locale so all values
        will be fetched by gettext instead of being overridden.
    """
    
    def handle(self, locale, app=None, **options):
        """ command execution """
        translation.activate(settings.LANGUAGE_CODE)
        if app:
            unpack = app.split('.')

            if len(unpack) == 2:
                models = [get_model(unpack[0], unpack[1])]
            elif len(unpack) == 1:
                models = get_models(get_app(unpack[0]))
        else:
            models = get_models()
            
        for model in models:
            if hasattr(model, 'localized_fields'):
                i18n.unregister(model)
                model_full_name = '%s.%s' % (model._meta.app_label, model._meta.module_name)
                update_instances = set()
                messages = []
                
                for instance in model.objects.all():
                    for field in model.localized_fields:
                        local_field_name = "%s_%s" % (field, locale)
                        
                        if  hasattr(instance, local_field_name):
                                local_field_value = getattr(instance, local_field_name)
                                if local_field_value not in (None, u''):
                                    setattr(instance, local_field_name, None)
                                
                                    update_instances.add(instance)
                                    messages.append(u"%s %s %s : %s will become reset to None" % (model_full_name, instance, local_field_name, force_unicode(local_field_value)))

                if len(update_instances):
                    if self.ask_for_confirmation(messages, u'%s.%s' % (model._meta.app_label, model._meta.module_name)):
                        for update_instance in update_instances:
                            print u"resetting %s" % update_instance
                            update_instance.save()
                
                
    def ask_for_confirmation(self, messages, model_full_name):
        print u'\nSummary for "%s":' % model_full_name
        for message in messages:
            print '   %s' % message
        while True:
            prompt = u'\nAre you sure that you want to reset %s: (y/n) [n]: ' % model_full_name
            answer = raw_input(prompt).strip()
            if answer == '':
                return False
            elif answer not in ('y', 'n', 'yes', 'no'):
                print u'Please answer yes or no'
            elif answer == 'y' or answer == 'yes':
                return True
            else:
                return False
            

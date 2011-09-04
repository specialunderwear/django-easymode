"""
    easy_copy_language <source locale> <target locale> <app>
    
    will copy all internationalised fields from source to target for the app in question.
    
    example:
    
    ./manage.py easy_copy_language en de myapp.mymodel
    
    will copy the en fields into the de locale for myapp.mymodel
"""
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import get_models, get_app, get_model
from django.utils import translation
from django.utils.encoding import force_unicode

from easymode.utils.languagecode import get_real_fieldname


class Command(BaseCommand):
    help = __doc__
    
    def handle(self, source, target, app=None, **options):
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

                model_full_name = '%s.%s' % (model._meta.app_label, model._meta.module_name)
                update_instances = set()
                messages = []
                
                for instance in model.objects.all():
                    for field in model.localized_fields:
                        source_field = get_real_fieldname(field, source)
                        target_field = get_real_fieldname(field, target)
                        
                        if  hasattr(instance, source_field) and hasattr(instance, target_field):
                            source_field_value = getattr(instance, source_field)
                            target_field_value = getattr(instance, target_field)

                            if target_field_value in (None, u'')\
                                and source_field_value not in (None, u''):
                                setattr(instance, target_field, force_unicode(source_field_value))
                                update_instances.add(instance)
                                messages.append(u"%s %s %s will become %s" % (model_full_name, instance, target_field, force_unicode(source_field_value)))

                if len(update_instances):
                    if self.ask_for_confirmation(messages, u'%s.%s' % (model._meta.app_label, model._meta.module_name)):
                        for update_instance in update_instances:
                            print u"saving %s" % update_instance
                            update_instance.save()
                
                
    def ask_for_confirmation(self, messages, model_full_name):
        print u'\nData to update "%s":' % model_full_name
        for message in messages:
            print u'   %s' % message
        while True:
            prompt = u'\nAre you sure that you want to update %s: (y/n) [n]: ' % model_full_name
            answer = raw_input(prompt).strip()
            if answer == '':
                return False
            elif answer not in ('y', 'n', 'yes', 'no'):
                print u'Please answer yes or no'
            elif answer == 'y' or answer == 'yes':
                return True
            else:
                return False
            
    

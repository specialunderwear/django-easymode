from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import get_models, get_app, get_model
from django.utils import translation

from easymode.i18n.gettext import MakeModelMessages

class Command(BaseCommand):
    help = """
        easy_locale <targetdir> <applabel>
        
        Will create a folder locale in targetdir with locales parsed
        from the models in applabel.
        
        example:
        ./manage.py easy_locale myapp myapp
        
        will create myapp/locale/ with po files in it.
    """
    
    def handle(self, targetdir, app=None, **options):
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
        
        messagemaker = MakeModelMessages(targetdir)
        
        for model in models:
            if hasattr(model, 'localized_fields'):
                for instance in model.objects.all():
                    messagemaker(instance)
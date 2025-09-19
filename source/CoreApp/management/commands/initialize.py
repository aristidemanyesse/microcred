from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        try:
            from MainApp.initialize import initialize
            initialize()
            
            from AuthentificationApp.initialize import initialize
            initialize()
            
            from FinanceApp.initialize import initialize
            initialize()
    
            self.stdout.write(self.style.SUCCESS('Base de données initialisée avec succes !'))
            
        except Exception as e:
            
            self.stdout.write(self.style.SUCCESS('Base de données initialisée avec succes !'))
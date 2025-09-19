from functools import wraps
from django.db import transaction
import re, random, string


######################################################################################################
######## UTILS FUNCTIONS

def form_to_model(modelform, suffix = 'Form'):
    if suffix and modelform.endswith(suffix):
        return modelform[:-len(suffix)]
    return modelform



class GenerateTools:
    
    @staticmethod
    def increment_code(current_code):
        letters = current_code[:3] if current_code != "" else "AAA"
        numbers = int(current_code[3:]) if current_code != "" else int("0000")

        # Incrémenter les chiffres
        if numbers < 9999:
            numbers += 1
        else:
            # Réinitialiser les chiffres et incrémenter les lettres
            numbers = 1
            letters = GenerateTools.increment_letters(letters)

        return f"{letters}{numbers:04d}"


    @staticmethod
    def increment_letters(letters):
        # Convertir en index (base 26)
        alphabet = string.ascii_uppercase
        indices = [alphabet.index(c) for c in letters]

        # Incrémenter comme un compteur en base 26
        for i in reversed(range(3)):
            if indices[i] < 25:
                indices[i] += 1
                break
            else:
                indices[i] = 0
        else:
            raise ValueError("Limite atteinte (ZZZ9999)")

        return ''.join(alphabet[i] for i in indices)
    
    
    @staticmethod
    def password():
        return str(random.randint(10000000, 99999999))
    
    @staticmethod
    def otp():
        return random.randint(1000, 9999)
    
    
    @staticmethod
    def clientId(agence):
        from MainApp.models import Client
        with transaction.atomic():
            item = Client.objects.filter().order_by("created_at").last()
            new_id = GenerateTools.increment_code(item.numero.split("-")[-1] if item else "")
            return f"{agence.code}-{new_id}"
        
    @staticmethod
    def epargneId(agence):
        from FinanceApp.models import CompteEpargne
        with transaction.atomic():
            item = CompteEpargne.objects.filter().order_by("created_at").last()
            new_id = GenerateTools.increment_code(item.numero.split("-")[-1] if item else "")
            return f"EPG-{agence.code}-{new_id}"
        
    @staticmethod
    def pretId(agence):
        from FinanceApp.models import Pret
        with transaction.atomic():
            item = Pret.objects.filter().order_by("created_at").last()
            new_id = GenerateTools.increment_code(item.numero.split("-")[-1] if item else "")
            return f"PRT-{agence.code}-{new_id}"
            
        
    @staticmethod
    def transactionId(agence):
        from FinanceApp.models import Transaction
        with transaction.atomic():
            item = Transaction.objects.filter().order_by("created_at").last()
            new_id = GenerateTools.increment_code(item.numero.split("-")[-1] if item else "")
            return f"TRS-{agence.code}-{new_id}"
            
 

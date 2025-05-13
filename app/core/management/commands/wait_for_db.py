"""
Comando de DJango para aguardar pela base de dados
"""
import time
from psycopg2 import OperationalError as Psycopg2OpError
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand
class Command(BaseCommand):
    """Comando Django para aguardar pela base de dados"""

    def handle(self, *args, **options):
        """Ponto de entrada para o comando"""
        self.stdout.write('Aguardando a base de dados...')
        db_up = False

        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except (Psycopg2OpError, OperationalError):
                self.stdout.write('Base de dados indisponível, aguardando 1 segundo...')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Base de dados disponível!'))

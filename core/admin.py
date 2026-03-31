from django.contrib import admin
from .models import Propriedade, Maquina  # Importe seus modelos aqui

# Registra os modelos para aparecerem no painel
admin.site.register(Propriedade)
admin.site.register(Maquina)
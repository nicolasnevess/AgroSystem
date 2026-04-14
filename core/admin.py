from django.contrib import admin
from .models import Propriedade, Maquina, TarefaMaquina, Animal  # Importar modelos

# Registra os modelos para aparecerem no painel
admin.site.register(Propriedade)
admin.site.register(Maquina)
admin.site.register(TarefaMaquina)
admin.site.register(Animal)

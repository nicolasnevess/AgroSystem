from django.db import models
from django.contrib.auth.models import User

# PROPRIEDADE
class Propriedade(models.Model):
    SOLO_CHOICES = [
        ('arenoso', 'Arenoso'),
        ('argiloso', 'Argiloso'),
        ('misto', 'Misto'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='propriedades')
    nome_fazenda = models.CharField(max_length=100)
    area_total = models.DecimalField(max_digits=10, decimal_places=2)
    tipo_solo = models.CharField(max_length=20, choices=SOLO_CHOICES)
    cidade = models.CharField(max_length=100)
    uf = models.CharField(max_length=2)
    
    def __str__(self):
        return self.nome_fazenda

# MÁQUINAS 
class Maquina(models.Model):
    TIPO_CHOICES = [
        ('trator', 'Trator'),
        ('colheitadeira', 'Colheitadeira'),
        ('pulverizador', 'Pulverizador'),
        ('plantadeira', 'Plantadeira'),
        ('outro', 'Outro')
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    propriedade = models.ForeignKey(Propriedade, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    modelo = models.CharField(max_length=100)
    identificacao = models.CharField(max_length=50)
    horimetro = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.nome} ({self.identificacao})"

# TAREFAS / OBSERVAÇÕES DA MÁQUINA
class TarefaMaquina(models.Model):
    # Relaciona a tarefa a uma máquina específica
    maquina = models.ForeignKey(Maquina, on_delete=models.CASCADE, related_name='tarefas')
    descricao = models.CharField(max_length=255)
    concluida = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.descricao} - {self.maquina.nome}"
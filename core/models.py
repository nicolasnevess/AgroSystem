from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# --- PROPRIEDADE ---
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

# --- MÁQUINAS ---
class Maquina(models.Model):
    TIPO_CHOICES = [
        ('trator', 'Trator'),
        ('colheitadeira', 'Colheitadeira'),
        ('pulverizador', 'Pulverizador'),
        ('plantadeira', 'Plantadeira'),
        ('outro', 'Outro')
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    propriedade = models.ForeignKey(Propriedade, on_delete=models.CASCADE, related_name='maquinas')
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    modelo = models.CharField(max_length=100)
    identificacao = models.CharField(max_length=50)
    horimetro = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.nome} ({self.identificacao})"

# --- TAREFAS DA MÁQUINA ---
class TarefaMaquina(models.Model):
    maquina = models.ForeignKey(Maquina, on_delete=models.CASCADE, related_name='tarefas')
    descricao = models.CharField(max_length=255)
    concluida = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.descricao} - {self.maquina.nome}"

# --- NOVO: PLANTAÇÕES ---
class Plantacao(models.Model):
    STATUS_CHOICES = [
        ('plantado', 'Recém Plantado'),
        ('germinacao', 'Em Germinação'),
        ('desenvolvimento', 'Desenvolvimento Vegetativo'),
        ('colheita', 'Pronto para Colheita'),
        ('finalizado', 'Finalizado'),
    ]

    propriedade = models.ForeignKey(Propriedade, on_delete=models.CASCADE, related_name='plantacoes')
    nome_planta = models.CharField(max_length=100) # Ex: Soja Talhão A
    tipo_planta = models.CharField(max_length=50) # Ex: Oleaginosa
    area_plantada = models.DecimalField(max_digits=10, decimal_places=2)
    data_plantio = models.DateField()
    previsao_colheita = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='plantado')

    @property
    def esta_atrasada(self):
        """Retorna True se a data atual passou da previsão e não foi finalizado"""
        return self.status != 'finalizado' and self.previsao_colheita < timezone.now().date()

    def __str__(self):
        return f"{self.nome_planta} - {self.propriedade.nome_fazenda}"

# --- NOVO: ANIMAIS (Para o seu próximo passo) ---
class Animal(models.Model):
    propriedade = models.ForeignKey(Propriedade, on_delete=models.CASCADE, related_name='animais')
    especie = models.CharField(max_length=50) # Ex: Bovino, Suíno
    quantidade = models.IntegerField()
    finalidade = models.CharField(max_length=50) # Ex: Corte, Leite

    def __str__(self):
        return f"{self.especie} - {self.propriedade.nome_fazenda}"
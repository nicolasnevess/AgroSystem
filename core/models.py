from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# --- CLASSE MÃE (PILAR: HERANÇA) ---
# Esta classe não vira uma tabela, ela serve de molde para as outras.
class AtivoFazenda(models.Model):
    data_criacao = models.DateTimeField(auto_now_add=True)
    # Aqui poderíamos colocar 'propriedade', mas para não quebrar seu código
    # vamos deixar apenas a data de criação como base comum.

    class Meta:
        abstract = True

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
class Maquina(AtivoFazenda): # Herda de AtivoFazenda
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
class TarefaMaquina(AtivoFazenda):
    maquina = models.ForeignKey(Maquina, on_delete=models.CASCADE, related_name='tarefas')
    descricao = models.CharField(max_length=255)
    concluida = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.descricao} - {self.maquina.nome}"

# --- PLANTAÇÕES ---
class Plantacao(AtivoFazenda): # Herda de AtivoFazenda
    STATUS_CHOICES = [
        ('plantado', 'Recém Plantado'),
        ('germinacao', 'Em Germinação'),
        ('desenvolvimento', 'Desenvolvimento Vegetativo'),
        ('colheita', 'Pronto para Colheita'),
        ('finalizado', 'Finalizado'),
    ]

    propriedade = models.ForeignKey(Propriedade, on_delete=models.CASCADE, related_name='plantacoes')
    nome_planta = models.CharField(max_length=100) 
    tipo_planta = models.CharField(max_length=50) 
    area_plantada = models.DecimalField(max_digits=10, decimal_places=2)
    data_plantio = models.DateField()
    previsao_colheita = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='plantado')

    # PILAR: ENCAPSULAMENTO
    @property
    def esta_atrasada(self):
        return self.status != 'finalizado' and self.previsao_colheita < timezone.now().date()

    def __str__(self):
        return f"{self.nome_planta} - {self.propriedade.nome_fazenda}"

# --- ANIMAIS ---
class Animal(AtivoFazenda): # Herda de AtivoFazenda
    ESPECIE_CHOICES = [
        ('bovino', 'Bovino'),
        ('suino', 'Suíno'),
        ('ovino', 'Ovino'),
        ('equino', 'Equino'),
    ]
    
    SEXO_CHOICES = [
        ('M', 'Macho'),
        ('F', 'Fêmea'),
    ]

    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('tratamento', 'Em Tratamento'),
        ('vendido', 'Vendido'),
    ]

    propriedade = models.ForeignKey(Propriedade, on_delete=models.CASCADE, related_name='animais')
    identificacao = models.CharField(max_length=50)
    nome_animal = models.CharField(max_length=100, blank=True, null=True)
    especie = models.CharField(max_length=20, choices=ESPECIE_CHOICES)
    raca = models.CharField(max_length=50)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    #data_nascimento = models.DateField(blank=True, null=True)
    peso = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ativo')
    #sanitario = models.TextField(blank=True, null=True)
    foto = models.ImageField(upload_to='animais/', blank=True, null=True)

    # PILAR: POLIMORFISMO (Sobrescrita de método)
    def save(self, *args, **kwargs):
        if self.identificacao:
            self.identificacao = self.identificacao.upper().strip()
        if self.nome_animal:
            self.nome_animal = self.nome_animal.strip().capitalize()
        if self.raca:
            self.raca = self.raca.strip().capitalize()
        super(Animal, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.identificacao} - {self.nome_animal if self.nome_animal else self.especie}"
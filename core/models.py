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

# --- ANIMAIS ---
class Animal(models.Model):
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
    identificacao = models.CharField(max_length=50) # Brinco/ID
    nome_animal = models.CharField(max_length=100, blank=True, null=True)
    especie = models.CharField(max_length=20, choices=ESPECIE_CHOICES)
    raca = models.CharField(max_length=50)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    data_nascimento = models.DateField(blank=True, null=True)
    peso = models.DecimalField(max_digits=10, decimal_places=2, help_text="Peso em kg")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ativo')
    sanitario = models.TextField(blank=True, null=True, help_text="Histórico de vacinas/medicamentos")
    foto = models.ImageField(upload_to='animais/', blank=True, null=True)

    def save(self, *args, **kwargs):
        # Identificação sempre em MAIÚSCULO e sem espaços sobrando
        if self.identificacao:
            self.identificacao = self.identificacao.upper().strip()
        
        # Nome e Raça com a Primeira Letra Maiúscula (Capitalize)
        if self.nome_animal:
            self.nome_animal = self.nome_animal.strip().capitalize()
        
        if self.raca:
            self.raca = self.raca.strip().capitalize()
            
        # Sanitário também formatado para manter o padrão
        if self.sanitario:
            self.sanitario = self.sanitario.strip().capitalize()

        # Chama o método save original para gravar no banco
        super(Animal, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.identificacao} - {self.nome_animal if self.nome_animal else self.especie}"
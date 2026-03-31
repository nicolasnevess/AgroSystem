from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import CadastroForm
from .models import Propriedade, Maquina

# --- AUTENTICAÇÃO ---

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Usuário ou senha inválidos.")
    else: 
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def cadastro_view(request):
    if request.method == 'POST':
        form = CadastroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Cadastro realizado com sucesso!")
            return redirect('login')
    else:
        form = CadastroForm()
    return render(request, 'cadastro.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')


# --- DASHBOARD E GERENCIAMENTO (PROTEGIDOS) ---

@login_required
def dashboard_view(request):
    # Busca todas as fazendas do usuário logado
    fazendas = Propriedade.objects.filter(usuario=request.user)
    tem_propriedade = fazendas.exists()
    
    # Se houver fazendas, pegamos a primeira como padrão
    fazenda_ativa = fazendas.first()
    
    # VALIDAÇÃO DAS MÁQUINAS
    minhas_maquinas = Maquina.objects.filter(usuario=request.user)
    tem_maquinas = minhas_maquinas.exists()

    # Variáveis de controle para o Dashboard mostrar ou esconder cards
    # Por enquanto deixamos False para você ver o quadro de "Próximos Passos"
    tem_plantacoes = False

    context = {
        'tem_propriedade': tem_propriedade,
        'fazendas': fazendas,
        'fazenda_ativa': fazenda_ativa,
        'tem_maquinas': tem_maquinas, # Necessário para o seu HTML novo
        'maquinas': minhas_maquinas,
        'tem_plantacoes': tem_plantacoes, # Necessário para o seu HTML novo
    }
    return render(request, 'dashboard.html', context)

@login_required
def maquinas_view(request):
    # Busca todas as máquinas do usuário logado
    minhas_maquinas = Maquina.objects.filter(usuario=request.user).order_by('-id')
    tem_maquinas = minhas_maquinas.exists()
    
    return render(request, 'maquinas.html', {
        'maquinas': minhas_maquinas,
        'tem_maquinas': tem_maquinas
    })

@login_required
def config_propriedade_view(request):
    if request.method == 'POST':
        Propriedade.objects.create(
            usuario=request.user,
            nome_fazenda=request.POST.get('nome_fazenda'),
            area_total=request.POST.get('area_total'),
            tipo_solo=request.POST.get('tipo_solo'),
            cidade=request.POST.get('cidade'),
            uf=request.POST.get('uf')
        )
        return redirect('dashboard')
    return render(request, 'config_propriedade.html')

@login_required
def config_areas_view(request):
    return render(request, 'config_areas.html')

@login_required
def plantacoes_view(request):
    return render(request, 'plantacoes.html')

@login_required
def animais_view(request):
    return render(request, 'animais.html')

@login_required
def config_animais_view(request):
    return render(request, 'config_animais.html')

@login_required
def config_maquinas_view(request):
    if request.method == 'POST':
        # Buscamos a propriedade correta pelo ID vindo do select
        propriedade_id = request.POST.get('propriedade')
        propriedade_obj = Propriedade.objects.get(id=propriedade_id)

        # Criamos a máquina usando exatamente os campos do SEU MODEL
        Maquina.objects.create(
            usuario=request.user,
            propriedade=propriedade_obj,
            nome=request.POST.get('nome'),
            tipo=request.POST.get('tipo'),
            modelo=request.POST.get('modelo'),
            identificacao=request.POST.get('identificacao'),
            horimetro=request.POST.get('horimetro')
        )
        return redirect('maquinas')

    # Carrega as fazendas do usuário para o select do formulário
    fazendas = Propriedade.objects.filter(usuario=request.user)
    return render(request, 'config_maquinas.html', {'fazendas': fazendas})
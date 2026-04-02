from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import CadastroForm
from .models import Propriedade, Maquina, TarefaMaquina

# Para as tarefas funcionarem via JavaScript (AJAX)
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

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


# --- DASHBOARD E GERENCIAMENTO ---

@login_required
def dashboard_view(request):
    fazendas = Propriedade.objects.filter(usuario=request.user)
    tem_propriedade = fazendas.exists()
    fazenda_ativa = fazendas.first()
    
    minhas_maquinas = Maquina.objects.filter(usuario=request.user)
    tem_maquinas = minhas_maquinas.exists()
    tem_plantacoes = False

    context = {
        'tem_propriedade': tem_propriedade,
        'fazendas': fazendas,
        'fazenda_ativa': fazenda_ativa,
        'tem_maquinas': tem_maquinas,
        'maquinas': minhas_maquinas,
        'tem_plantacoes': tem_plantacoes,
    }
    return render(request, 'dashboard.html', context)

@login_required
def maquinas_view(request):
    fazendas = Propriedade.objects.filter(usuario=request.user)
    tem_fazenda = fazendas.exists()

    if tem_fazenda:
        # prefetch_related evita múltiplas consultas ao banco para carregar as tarefas
        minhas_maquinas = Maquina.objects.filter(usuario=request.user).prefetch_related('tarefas').order_by('-id')
    else:
        minhas_maquinas = Maquina.objects.none()

    return render(request, 'maquinas.html', {
        'maquinas': minhas_maquinas,
        'tem_maquinas': minhas_maquinas.exists(),
        'tem_fazenda': tem_fazenda,
    })

# --- CONFIGURAÇÕES E CADASTROS ---

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
    """View para cadastrar áreas (talhões)"""
    return render(request, 'config_areas.html')

@login_required
def plantacoes_view(request):
    tem_fazenda = Propriedade.objects.filter(usuario=request.user).exists()
    fazendas = Propriedade.objects.filter(usuario=request.user)
    return render(request, 'plantacoes.html', {'tem_fazenda': tem_fazenda, 'fazendas': fazendas})

@login_required
def animais_view(request):
    tem_fazenda = Propriedade.objects.filter(usuario=request.user).exists()
    return render(request, 'animais.html', {'tem_fazenda': tem_fazenda})

@login_required
def config_animais_view(request):
    """View para cadastrar animais"""
    return render(request, 'config_animais.html')

@login_required
def config_maquinas_view(request):
    if request.method == 'POST':
        propriedade_id = request.POST.get('propriedade')
        propriedade_obj = Propriedade.objects.get(id=propriedade_id)
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
    fazendas = Propriedade.objects.filter(usuario=request.user)
    return render(request, 'config_maquinas.html', {'fazendas': fazendas})


# --- LÓGICA DE TAREFAS (AJAX) ---

@csrf_exempt
@login_required
def adicionar_tarefa(request, maquina_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            descricao = data.get('descricao', '').strip()
            
            if descricao:
                # Transforma a primeira letra em Maiúscula
                descricao = descricao[0].upper() + descricao[1:]
                
                maquina = get_object_or_404(Maquina, id=maquina_id, usuario=request.user)
                tarefa = TarefaMaquina.objects.create(maquina=maquina, descricao=descricao)
                
                return JsonResponse({
                    'id': tarefa.id,
                    'descricao': tarefa.descricao,
                    'concluida': tarefa.concluida
                })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Dados inválidos'}, status=400)

@csrf_exempt
@login_required
def alternar_tarefa(request, tarefa_id):
    if request.method == 'POST':
        # Busca garantindo que a tarefa pertence a uma máquina do usuário logado
        tarefa = get_object_or_404(TarefaMaquina, id=tarefa_id, maquina__usuario=request.user)
        tarefa.concluida = not tarefa.concluida
        tarefa.save()
        return JsonResponse({'status': 'sucesso', 'concluida': tarefa.concluida})
    return JsonResponse({'error': 'Método inválido'}, status=400)

@csrf_exempt
@login_required
def deletar_tarefa(request, tarefa_id):
    if request.method == 'POST':
        # Busca garantindo que a tarefa pertence a uma máquina do usuário logado
        tarefa = get_object_or_404(TarefaMaquina, id=tarefa_id, maquina__usuario=request.user)
        tarefa.delete()
        return JsonResponse({'status': 'sucesso'})
    return JsonResponse({'status': 'erro'}, status=400)
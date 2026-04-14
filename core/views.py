from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import CadastroForm
from .models import Propriedade, Maquina, TarefaMaquina, Plantacao, Animal
from django.utils import timezone
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

# --- DASHBOARD ---

@login_required
def dashboard_view(request):
    fazendas = Propriedade.objects.filter(usuario=request.user)
    tem_propriedade = fazendas.exists()
    
    # 1. Tenta pegar o ID da URL
    fazenda_id = request.GET.get('fazenda_id')
    
    if fazenda_id:
        # Se veio na URL, salva na sessão (memória do navegador)
        request.session['fazenda_ativa_id'] = fazenda_id
    else:
        # Se não veio na URL, tenta recuperar da sessão
        fazenda_id = request.session.get('fazenda_ativa_id')
    
    # 2. Define a fazenda ativa
    if fazenda_id and tem_propriedade:
        fazenda_ativa = Propriedade.objects.filter(id=fazenda_id, usuario=request.user).first()
        # Se por acaso o ID da sessão for de uma fazenda deletada, volta pra primeira
        if not fazenda_ativa:
            fazenda_ativa = fazendas.first()
    else:
        fazenda_ativa = fazendas.first()

    minhas_maquinas = Maquina.objects.none()
    minhas_plantacoes = Plantacao.objects.none()
    alertas_atraso = []

    if fazenda_ativa:
        minhas_maquinas = Maquina.objects.filter(propriedade=fazenda_ativa)
        minhas_plantacoes = Plantacao.objects.filter(propriedade=fazenda_ativa)
        
        # 3. Lógica de Alertas: Não finalizadas e com data menor que hoje
        alertas_atraso = minhas_plantacoes.exclude(status='finalizado').filter(
            previsao_colheita__lt=timezone.now().date()
        )

    context = {
        'tem_propriedade': tem_propriedade,
        'fazendas': fazendas,
        'fazenda_ativa': fazenda_ativa,
        'tem_maquinas': minhas_maquinas.exists(),
        'maquinas': minhas_maquinas,
        'tem_plantacoes': minhas_plantacoes.exists(),
        'plantacoes': minhas_plantacoes,
        'plantacoes_atrasadas': alertas_atraso, # Nome batendo com o que colocamos no HTML
    }
    return render(request, 'dashboard.html', context)


# --- PROPRIEDADE ---

@login_required
def editar_propriedade(request, propriedade_id):
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, usuario=request.user)
    
    if request.method == 'POST':
        propriedade.nome_fazenda = request.POST.get('nome_fazenda')
        propriedade.area_total = request.POST.get('area_total')
        propriedade.tipo_solo = request.POST.get('tipo_solo')
        propriedade.cidade = request.POST.get('cidade')
        propriedade.uf = request.POST.get('uf')
        propriedade.save()
        messages.success(request, 'Propriedade atualizada com sucesso!')
        return redirect('dashboard')
    
    return render(request, 'editar_propriedade.html', {'propriedade': propriedade})

@login_required
def deletar_propriedade(request, propriedade_id):
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, usuario=request.user)
    
    # Impedir de deletar se for a única fazenda
    # if Propriedade.objects.filter(usuario=request.user).count() <= 1:
    #     messages.error(request, "Você precisa de pelo menos uma fazenda cadastrada.")
    #     return redirect('dashboard')

    propriedade.delete()
    messages.success(request, "Propriedade removida com sucesso!")
    
    # Se deletar a fazenda que estava ativa, limpa a sessão
    if str(propriedade_id) == str(request.session.get('fazenda_ativa_id')):
        request.session['fazenda_ativa_id'] = None
        
    return redirect('dashboard')


# --- PLANTAÇÕES ---

@login_required
def plantacoes_view(request):
    fazendas = Propriedade.objects.filter(usuario=request.user)
    
    # Tenta URL, depois Sessão
    fazenda_id = request.GET.get('fazenda_id') or request.session.get('fazenda_ativa_id')
    
    if fazenda_id:
        fazenda_ativa = Propriedade.objects.filter(id=fazenda_id, usuario=request.user).first()
    else:
        fazenda_ativa = fazendas.first()

    if request.method == 'POST':
        id_fazenda_destinataria = request.POST.get('fazenda')
        fazenda_obj = get_object_or_404(Propriedade, id=id_fazenda_destinataria, usuario=request.user)
        
        # Salva na sessão que essa é a fazenda ativa agora
        request.session['fazenda_ativa_id'] = id_fazenda_destinataria

        nome_cru = request.POST.get('nome_planta', '')
        nome_formatado = nome_cru.strip().capitalize()

        Plantacao.objects.create(
            propriedade=fazenda_obj,
            nome_planta=nome_formatado,
            tipo_planta=request.POST.get('tipo_planta'),
            area_plantada=request.POST.get('area_plantada'),
            data_plantio=request.POST.get('data_plantio'),
            previsao_colheita=request.POST.get('previsao_colheita'),
            status=request.POST.get('status', 'plantado')
        )
        return redirect('plantacoes') # O ID agora será pego da sessão automaticamente

    plantacoes = Plantacao.objects.filter(propriedade=fazenda_ativa)

    return render(request, 'plantacoes.html', {
        'fazendas': fazendas,
        'fazenda_ativa': fazenda_ativa,
        'plantacoes': plantacoes,
        'tem_fazenda': fazendas.exists()
    })

@login_required
def concluir_plantacao(request, plantacao_id):
    plantacao = get_object_or_404(Plantacao, id=plantacao_id, propriedade__usuario=request.user)
    plantacao.status = 'finalizado'
    plantacao.save()
    return redirect(f'/plantacoes/?fazenda_id={plantacao.propriedade.id}')

@login_required
def deletar_plantacao(request, plantacao_id):
    plantacao = get_object_or_404(Plantacao, id=plantacao_id, propriedade__usuario=request.user)
    f_id = plantacao.propriedade.id
    plantacao.delete()
    return redirect(f'/plantacoes/?fazenda_id={f_id}')

# --- MÁQUINAS ---

@login_required
def maquinas_view(request):
    fazendas = Propriedade.objects.filter(usuario=request.user)
    tem_fazenda = fazendas.exists()
    
    # Tenta pegar da URL, se não tiver, pega da Sessão
    fazenda_id = request.GET.get('fazenda_id') or request.session.get('fazenda_ativa_id')
    
    if tem_fazenda:
        if fazenda_id:
            fazenda_ativa = fazendas.filter(id=fazenda_id).first()
            # Se o ID for inválido, pega a primeira
            if not fazenda_ativa:
                fazenda_ativa = fazendas.first()
        else:
            fazenda_ativa = fazendas.first()
        
        # Salva a fazenda atual na sessão para as outras páginas lembrarem
        request.session['fazenda_ativa_id'] = fazenda_ativa.id
        
        minhas_maquinas = Maquina.objects.filter(propriedade=fazenda_ativa).prefetch_related('tarefas').order_by('-id')
    else:
        fazenda_ativa = None
        minhas_maquinas = Maquina.objects.none()

    return render(request, 'maquinas.html', {
        'maquinas': minhas_maquinas,
        'tem_maquinas': minhas_maquinas.exists(),
        'tem_fazenda': tem_fazenda,
        'fazendas': fazendas,
        'fazenda_ativa': fazenda_ativa
    })

# --- CONFIGURAÇÕES (NOMES SINCRONIZADOS COM URLS.PY) ---

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
def config_maquinas_view(request):
    fazendas = Propriedade.objects.filter(usuario=request.user)
    if request.method == 'POST':
        propriedade_id = request.POST.get('propriedade')
        propriedade_obj = get_object_or_404(Propriedade, id=propriedade_id, usuario=request.user)
        Maquina.objects.create(
            usuario=request.user,
            propriedade=propriedade_obj,
            nome=request.POST.get('nome'),
            tipo=request.POST.get('tipo'),
            modelo=request.POST.get('modelo'),
            identificacao=request.POST.get('identificacao'),
            horimetro=request.POST.get('horimetro')
        )
        return redirect(f'/maquinas/?fazenda_id={propriedade_obj.id}')
    return render(request, 'config_maquinas.html', {'fazendas': fazendas})

@login_required
def config_areas_view(request):
    fazendas = Propriedade.objects.filter(usuario=request.user)
    return render(request, 'config_areas.html', {'fazendas': fazendas})

@login_required
def config_animais_view(request):
    fazendas = Propriedade.objects.filter(usuario=request.user)
    return render(request, 'config_animais.html', {'fazendas': fazendas})

@login_required
def animais_view(request):
    fazendas = Propriedade.objects.filter(usuario=request.user)
    
    # 1. Prioridade total para o que vem na URL (?fazenda_id=X)
    fazenda_id = request.GET.get('fazenda_id')
    
    if fazenda_id:
        # Se veio na URL, atualizamos a sessão IMEDIATAMENTE
        request.session['fazenda_ativa_id'] = fazenda_id
    else:
        # Se não veio na URL, tentamos pegar o que estava na sessão
        fazenda_id = request.session.get('fazenda_ativa_id')

    # 2. Busca a fazenda no banco
    fazenda_ativa = None
    if fazendas.exists():
        if fazenda_id:
            fazenda_ativa = fazendas.filter(id=fazenda_id).first()
        
        # Se o ID da sessão/URL for inválido ou nulo, pega a primeira disponível
        if not fazenda_ativa:
            fazenda_ativa = fazendas.first()
            request.session['fazenda_ativa_id'] = fazenda_ativa.id

    # 3. Lógica do POST (Salvar Animal) - Mantida igual
    if request.method == 'POST' and fazenda_ativa:
        Animal.objects.create(
            propriedade=fazenda_ativa,
            identificacao=request.POST.get('identificacao'),
            nome_animal=request.POST.get('nome_animal'),
            especie=request.POST.get('especie'),
            raca=request.POST.get('raca'),
            sexo=request.POST.get('sexo'),
            data_nascimento=request.POST.get('data_nascimento') or None,
            peso=request.POST.get('peso') or 0,
            status=request.POST.get('status', 'ativo'),
            sanitario=request.POST.get('sanitario'),
            foto=request.FILES.get('foto')
        )
        messages.success(request, "Animal cadastrado com sucesso!")
        return redirect(f'/animais/?fazenda_id={fazenda_ativa.id}')

    animais = Animal.objects.filter(propriedade=fazenda_ativa) if fazenda_ativa else []

    return render(request, 'animais.html', {
        'tem_fazenda': fazendas.exists(),
        'fazendas': fazendas,
        'fazenda_ativa': fazenda_ativa,
        'animais': animais 
    })
    
@login_required
def deletar_animal(request, animal_id):
    animal = get_object_or_404(Animal, id=animal_id, propriedade__usuario=request.user)
    animal.delete()
    messages.success(request, "Animal removido do rebanho.")
    return redirect('animais')

@login_required
def editar_animal(request, animal_id):
    # Garante que o animal existe e pertence ao usuário logado
    animal = get_object_or_404(Animal, id=animal_id, propriedade__usuario=request.user)
    
    if request.method == 'POST':
        animal.identificacao = request.POST.get('identificacao')
        animal.nome_animal = request.POST.get('nome_animal')
        animal.especie = request.POST.get('especie')
        animal.raca = request.POST.get('raca')
        animal.sexo = request.POST.get('sexo')
        animal.peso = request.POST.get('peso') or 0  # Evita erro se o peso vier vazio
        animal.status = request.POST.get('status')
        animal.sanitario = request.POST.get('sanitario')
        
        # Se enviou uma foto nova, troca. Se não, mantém a antiga.
        if request.FILES.get('foto'):
            animal.foto = request.FILES.get('foto')
            
        animal.save()
        messages.success(request, f"O animal {animal.identificacao} foi atualizado com sucesso!")
        return redirect('animais')

    # Se alguém tentar acessar a URL via GET (direto no navegador), 
    # apenas mandamos de volta para a lista, já que o edit é por Modal.
    return redirect('animais')

# --- AJAX TAREFAS ---

@csrf_exempt
@login_required
def adicionar_tarefa(request, maquina_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            descricao = data.get('descricao', '').strip()
            if descricao:
                descricao = descricao[0].upper() + descricao[1:]
                maquina = get_object_or_404(Maquina, id=maquina_id, usuario=request.user)
                tarefa = TarefaMaquina.objects.create(maquina=maquina, descricao=descricao)
                return JsonResponse({'id': tarefa.id, 'descricao': tarefa.descricao, 'concluida': tarefa.concluida})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Dados inválidos'}, status=400)

@csrf_exempt
@login_required
def alternar_tarefa(request, tarefa_id):
    if request.method == 'POST':
        tarefa = get_object_or_404(TarefaMaquina, id=tarefa_id, maquina__usuario=request.user)
        tarefa.concluida = not tarefa.concluida
        tarefa.save()
        return JsonResponse({'status': 'sucesso', 'concluida': tarefa.concluida})
    return JsonResponse({'error': 'Método inválido'}, status=400)

@csrf_exempt
@login_required
def deletar_tarefa(request, tarefa_id):
    if request.method == 'POST':
        tarefa = get_object_or_404(TarefaMaquina, id=tarefa_id, maquina__usuario=request.user)
        tarefa.delete()
        return JsonResponse({'status': 'sucesso'})
    return JsonResponse({'status': 'erro'}, status=400)
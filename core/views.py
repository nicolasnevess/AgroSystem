from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import CadastroForm
from .models import Propriedade, Maquina, TarefaMaquina, Plantacao, Animal
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# --- 1. AUTENTICAÇÃO ---

def login_view(request):
    form = AuthenticationForm() # Inicializa vazio para o GET
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST) # Pega os dados do POST
        if form.is_valid():
            login(request, form.get_user())
            return redirect('dashboard')
        else:
            # Se o form não for válido, ele já contém os erros.
            messages.error(request, "Usuário ou senha inválidos.")
            
    # Aqui passa o form que pode estar vazio (GET) ou com erros (POST)
    return render(request, 'login.html', {'form': form})

def cadastro_view(request):
    form = CadastroForm()
    if request.method == 'POST':
        form = CadastroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Cadastro realizado com sucesso!")
            return redirect('login')
        else:
            messages.error(request, "Erro ao realizar cadastro. Verifique os campos.")
            
    return render(request, 'cadastro.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')


# --- 2. DASHBOARD ---

@login_required
def dashboard_view(request):
    fazendas = Propriedade.objects.filter(usuario=request.user)
    fazenda_id = request.GET.get('fazenda_id') or request.session.get('fazenda_ativa_id')
    fazenda_ativa = fazendas.filter(id=fazenda_id).first() or fazendas.first()
    
    context = {'tem_propriedade': fazendas.exists(), 'fazendas': fazendas, 'fazenda_ativa': fazenda_ativa}

    if fazenda_ativa:
        request.session['fazenda_ativa_id'] = fazenda_ativa.id
        plantacoes = fazenda_ativa.plantacoes.all()
        
        # --- LÓGICA DE DIAS RESTANTES ---
        hoje = timezone.now().date()
        lista_colheita = []

        for p in plantacoes:
            # Só calcula para plantações que não foram finalizadas
            if p.status != 'finalizado':
                dias_restantes = (p.previsao_colheita - hoje).days
                lista_colheita.append({
                    'nome': p.nome_planta,
                    'dias': dias_restantes,
                    'data': p.previsao_colheita
                })

        context.update({
            'maquinas': fazenda_ativa.maquinas.all(),
            'plantacoes': plantacoes,
            'lista_colheita': lista_colheita, # Envia a nova lista com os cálculos
            'animais': fazenda_ativa.animais.all(),
        })
        
    return render(request, 'dashboard.html', context)


# --- 3. PLANTAÇÕES ---

@login_required
def plantacoes_view(request):
    fazendas = Propriedade.objects.filter(usuario=request.user)
    
    # Busca a fazenda ativa
    fazenda_id = request.GET.get('fazenda_id') or request.session.get('fazenda_ativa_id')
    fazenda_ativa = fazendas.filter(id=fazenda_id).first() or fazendas.first()

    if request.method == 'POST' and fazenda_ativa:
        # Criando a plantação
        Plantacao.objects.create(
            propriedade=fazenda_ativa,
            nome_planta=request.POST.get('nome_planta'),
            tipo_planta=request.POST.get('tipo_planta'),
            area_plantada=request.POST.get('area_plantada'),
            data_plantio=request.POST.get('data_plantio'),
            previsao_colheita=request.POST.get('previsao_colheita'),
            status=request.POST.get('status', 'plantado')
        )
        # Redireciona mantendo a mesma fazenda na tela
        return redirect(f'/plantacoes/?fazenda_id={fazenda_ativa.id}')

    # IMPORTANTE: Nomes sincronizados com seu HTML
    context = {
        'fazendas': fazendas,
        'fazenda_ativa': fazenda_ativa,
        'tem_fazenda': fazendas.exists(), # O HTML usa tem_fazenda
        'plantacoes': fazenda_ativa.plantacoes.all() if fazenda_ativa else [] # plural
    }
    
    return render(request, 'plantacoes.html', context)

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


# --- 4. MÁQUINAS ---

@login_required
def maquinas_view(request):
    fazendas = Propriedade.objects.filter(usuario=request.user)
    fazenda_id = request.GET.get('fazenda_id') or request.session.get('fazenda_ativa_id')
    
    # Busca a fazenda ativa
    fazenda_ativa = fazendas.filter(id=fazenda_id).first() or fazendas.first()
    
    # Se houver fazenda, pega o QuerySet. Se não, pega um QuerySet vazio do modelo Maquina
    if fazenda_ativa:
        maquinas_queryset = fazenda_ativa.maquinas.all()
    else:
        maquinas_queryset = Maquina.objects.none() # QuerySet vazio

    return render(request, 'maquinas.html', {
        'fazendas': fazendas,
        'fazenda_ativa': fazenda_ativa,
        'maquinas': maquinas_queryset,         
        'tem_fazenda': fazendas.exists(),  
        'tem_maquinas': maquinas_queryset.exists() # Agora funciona sempre!
    })

@login_required
def config_maquinas_view(request):
    fazendas = Propriedade.objects.filter(usuario=request.user)
    if request.method == 'POST':
        prop_id = request.POST.get('propriedade')
        prop_obj = get_object_or_404(Propriedade, id=prop_id, usuario=request.user)
        Maquina.objects.create(
            usuario=request.user, propriedade=prop_obj,
            nome=request.POST.get('nome'), tipo=request.POST.get('tipo'),
            modelo=request.POST.get('modelo'), identificacao=request.POST.get('identificacao'),
            horimetro=request.POST.get('horimetro') or 0
        )
        return redirect(f'/maquinas/?fazenda_id={prop_obj.id}')
    return render(request, 'config_maquinas.html', {'fazendas': fazendas})

@login_required
def editar_maquina(request, maquina_id):
    maquina = get_object_or_404(Maquina, id=maquina_id, usuario=request.user)
    if request.method == 'POST':
        maquina.nome = request.POST.get('nome')
        maquina.tipo = request.POST.get('tipo')
        maquina.modelo = request.POST.get('modelo')
        maquina.identificacao = request.POST.get('identificacao')
        maquina.horimetro = request.POST.get('horimetro') or 0
        maquina.save()
        return redirect(f'/maquinas/?fazenda_id={maquina.propriedade.id}')
    return render(request, 'editar_maquina.html', {'maquina': maquina})

@login_required
def deletar_maquina(request, maquina_id):
    maquina = get_object_or_404(Maquina, id=maquina_id, usuario=request.user)
    f_id = maquina.propriedade.id
    maquina.delete()
    return redirect(f'/maquinas/?fazenda_id={f_id}')


# --- 5. ANIMAIS ---

@login_required
def animais_view(request):
    fazendas = Propriedade.objects.filter(usuario=request.user)
    fazenda_id = request.GET.get('fazenda_id') or request.session.get('fazenda_ativa_id')
    fazenda_ativa = fazendas.filter(id=fazenda_id).first() or fazendas.first()

    if request.method == 'POST' and fazenda_ativa:
        # Criando o animal e recebendo a FOTO via request.FILES
        Animal.objects.create(
            propriedade=fazenda_ativa,
            identificacao=request.POST.get('identificacao'),
            nome_animal=request.POST.get('nome_animal'),
            especie=request.POST.get('especie'),
            raca=request.POST.get('raca'),
            sexo=request.POST.get('sexo'),
            peso=request.POST.get('peso') or 0,
            status=request.POST.get('status', 'ativo'),
            foto=request.FILES.get('foto') # Captura a imagem
        )
        messages.success(request, "Animal cadastrado com sucesso!")
        return redirect(f'/animais/?fazenda_id={fazenda_ativa.id}')

    context = {
        'fazendas': fazendas,
        'fazenda_ativa': fazenda_ativa,
        'tem_fazenda': fazendas.exists(),
        'animais': fazenda_ativa.animais.all() if fazenda_ativa else []
    }
    return render(request, 'animais.html', context)

@login_required
def config_animais_view(request):
    fazendas = Propriedade.objects.filter(usuario=request.user)
    if request.method == 'POST':
        prop_id = request.POST.get('propriedade')
        fazenda = get_object_or_404(Propriedade, id=prop_id, usuario=request.user)
        Animal.objects.create(
            propriedade=fazenda,
            identificacao=request.POST.get('identificacao'),
            nome_animal=request.POST.get('nome_animal'),
            especie=request.POST.get('especie'),
            raca=request.POST.get('raca'),
            sexo=request.POST.get('sexo'),
            peso=request.POST.get('peso') or 0,
            foto=request.FILES.get('foto')
        )
        return redirect(f'/animais/?fazenda_id={fazenda.id}')
    return render(request, 'config_animais.html', {'fazendas': fazendas})

@login_required
def editar_animal(request, animal_id):
    animal = get_object_or_404(Animal, id=animal_id, propriedade__usuario=request.user)
    
    if request.method == 'POST':
        animal.identificacao = request.POST.get('identificacao')
        animal.nome_animal = request.POST.get('nome_animal')
        animal.raca = request.POST.get('raca')
        animal.sexo = request.POST.get('sexo')
        animal.peso = request.POST.get('peso') or 0
        animal.status = request.POST.get('status')
        
        especie_vinda = request.POST.get('especie')
        if especie_vinda:
            animal.especie = especie_vinda

        # Lógica para atualizar a foto apenas se uma nova for enviada
        nova_foto = request.FILES.get('foto')
        if nova_foto:
            animal.foto = nova_foto
            
        animal.save()
        messages.success(request, "Dados atualizados!")
        return redirect(f'/animais/?fazenda_id={animal.propriedade.id}')
    
    return redirect('animais')

@login_required
def deletar_animal(request, animal_id):
    animal = get_object_or_404(Animal, id=animal_id, propriedade__usuario=request.user)
    f_id = animal.propriedade.id
    animal.delete()
    return redirect(f'/animais/?fazenda_id={f_id}')


# --- 6. PROPRIEDADE ---

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
def editar_propriedade(request, propriedade_id):
    prop = get_object_or_404(Propriedade, id=propriedade_id, usuario=request.user)
    if request.method == 'POST':
        prop.nome_fazenda = request.POST.get('nome_fazenda')
        prop.area_total = request.POST.get('area_total')
        prop.tipo_solo = request.POST.get('tipo_solo')
        prop.cidade = request.POST.get('cidade')
        prop.uf = request.POST.get('uf')
        prop.save()
        return redirect('dashboard')
    return render(request, 'editar_propriedade.html', {'propriedade': prop})

@login_required
def deletar_propriedade(request, propriedade_id):
    prop = get_object_or_404(Propriedade, id=propriedade_id, usuario=request.user)
    prop.delete()
    return redirect('dashboard')

@login_required
def config_areas_view(request):
    fazendas = Propriedade.objects.filter(usuario=request.user)
    return render(request, 'config_areas.html', {'fazendas': fazendas})


# --- 7. TAREFAS (AJAX) ---

@csrf_exempt
@login_required
def adicionar_tarefa(request, maquina_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        maquina = get_object_or_404(Maquina, id=maquina_id, usuario=request.user)
        
        tarefa = TarefaMaquina.objects.create(
            maquina=maquina, 
            descricao=data.get('descricao')
        )
        
        # Converte o horário do banco para o horário local
        data_local = timezone.localtime(tarefa.data_criacao)
        
        return JsonResponse({
            'id': tarefa.id, 
            'descricao': tarefa.descricao, 
            'concluida': tarefa.concluida,
            # Agora usa a data_local que tem o fuso horário corrigido
            'data_criacao': data_local.strftime('%d/%m/%Y %H:%M') 
        })
    return JsonResponse({'error': 'Erro'}, status=400)

@csrf_exempt
@login_required
def alternar_tarefa(request, tarefa_id):
    if request.method == 'POST':
        tarefa = get_object_or_404(TarefaMaquina, id=tarefa_id, maquina__usuario=request.user)
        tarefa.concluida = not tarefa.concluida
        tarefa.save()
        return JsonResponse({'status': 'sucesso', 'concluida': tarefa.concluida})
    return JsonResponse({'error': 'Erro'}, status=400)

@csrf_exempt
@login_required
def deletar_tarefa(request, tarefa_id):
    if request.method == 'POST':
        tarefa = get_object_or_404(TarefaMaquina, id=tarefa_id, maquina__usuario=request.user)
        tarefa.delete()
        return JsonResponse({'status': 'sucesso'})
    return JsonResponse({'status': 'erro'}, status=400)


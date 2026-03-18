from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import CadastroForm

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

#def esqueceu_senha_view(request):
   # return render(request, 'esqueceu_senha.html')


#def esqueceu_senha_confirm_view(request):
    #return render(request, 'esqueceu_senha_confirm.html')

@login_required
def dashboard_view(request):
    return render(request, 'dashboard.html')

@login_required
def maquinas_view(request):
    return render(request, 'maquinas.html')

@login_required
def config_propriedade_view(request):
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
    return render(request, 'config_maquinas.html')
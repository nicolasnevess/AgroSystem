from django.shortcuts import render

def login_view(request):
    return render(request, 'login.html')

def cadastro_view(request):
    return render(request, 'cadastro.html')

def esqueceu_senha_view(request):
    return render(request, 'esqueceu_senha.html')

def esqueceu_senha_confirm_view(request):
    return render(request, 'esqueceu_senha_confirm.html')

def dashboard_view(request):
    return render(request, 'dashboard.html')
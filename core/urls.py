from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('cadastro/', views.cadastro_view, name='cadastro'),
    path('recuperar-senha/', views.esqueceu_senha_view, name='password_reset'),
    path('nova-senha/', views.esqueceu_senha_confirm_view, name='password_reset_confirm'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('maquinas/', views.maquinas_view, name='maquinas'),
    path('configurar-propriedade/', views.config_propriedade_view, name='config_propriedade'),
]
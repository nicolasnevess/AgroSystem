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
    path('cadastrar-area/', views.config_areas_view, name='config_areas'),
    path('plantacoes/', views.plantacoes_view, name='plantacoes'),
    path('animais/', views.animais_view, name='animais'),
    path('cadastrar-animal/', views.config_animais_view, name='config_animais'),
    path('cadastrar-maquina/', views.config_maquinas_view, name='config_maquinas'),
]
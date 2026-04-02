from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Autenticação principal
    path('', views.login_view, name='login'),
    path('cadastro/', views.cadastro_view, name='cadastro'),
    path('logout/', views.logout_view, name='logout'),

    # Recuperação de senha
    path('recuperar-senha/',
        auth_views.PasswordResetView.as_view(
            template_name='password_reset.html',
            email_template_name='password_reset_email.html',
            subject_template_name='password_reset_subject.txt'
        ),
        name='password_reset'),

    path('recuperar-senha/sucesso/',
        auth_views.PasswordResetDoneView.as_view(template_name='password_reset_sent.html'),
        name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),
        name='password_reset_confirm'),

    path('reset/concluido/', 
        auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_done.html'), 
        name='password_reset_complete'),
    
    # Tarefas
    path('maquina/<int:maquina_id>/adicionar_tarefa/', views.adicionar_tarefa, name='adicionar_tarefa'),
    path('tarefa/<int:tarefa_id>/alternar/', views.alternar_tarefa, name='alternar_tarefa'),
    path('tarefa/<int:tarefa_id>/deletar/', views.deletar_tarefa, name='deletar_tarefa'),

    # Dashboard e Gerenciamento
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('maquinas/', views.maquinas_view, name='maquinas'),
    path('configurar-propriedade/', views.config_propriedade_view, name='config_propriedade'),
    path('cadastrar-area/', views.config_areas_view, name='config_areas'),
    path('plantacoes/', views.plantacoes_view, name='plantacoes'),
    path('animais/', views.animais_view, name='animais'),
    path('cadastrar-animal/', views.config_animais_view, name='config_animais'),
    path('cadastrar-maquina/', views.config_maquinas_view, name='config_maquinas'),
]
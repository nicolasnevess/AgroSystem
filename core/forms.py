from django import forms
from django.contrib.auth.models import User

class CadastroForm(forms.ModelForm):
    nome_completo = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Nome completo'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Usuário'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Senha'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password'] # Removi nome_completo daqui porque ele não existe no modelo User original, nós salvamos ele no first_name abaixo

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"]) # Criptografar senha
        nome_formatado = self.cleaned_data["nome_completo"].strip().title() # Salva o nome completo no campo first_name do Django
        user.first_name = nome_formatado
        if commit:
            user.save()
        return user
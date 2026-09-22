from django import forms

from .models import Empresa, User, Cliente


class EmpresaForm(forms.ModelForm):

    class Meta:
        model = Empresa
        fields = [
            "nome",
            "cnpj",
            "razao_social",
            "email",
            "resumo_loja",
            "telefonedecontato",
            "descricao",
            "logo",
            "color",
            "color_fonte",
            "logo_navegador",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.instance.pk and not self.initial.get("nome"):
            self.initial["nome"] = "DDI IFMG"

        self.fields["descricao"].label = "Descrição:"
        self.fields["descricao"].help_text = (
            "Use este campo para registrar informações institucionais da DDI IFMG."
        )

        self.fields["logo"].label = "Logo da barra de menu:"
        self.fields["logo"].help_text = (
            "Logo que estará presente na barra de menu."
        )

        self.fields["color"].label = "Cor da barra de menu:"
        self.fields["color_fonte"].label = (
            "Cor da letra da barra de menu:"
        )

        self.fields["logo_navegador"].label = (
            "Logo da aba do navegador."
        )

        self.fields["resumo_loja"].label = (
            "Resumo institucional"
        )

        self.fields["resumo_loja"].help_text = (
            "Informações gerais da instituição."
        )

        self.fields["telefonedecontato"].label = (
            "Telefone de Contato"
        )

        self.fields["telefonedecontato"].help_text = (
            "Telefone institucional."
        )


class UserForm(forms.ModelForm):

    password = forms.CharField(
        label="Senha:",
        widget=forms.PasswordInput,
        required=True
    )

    class Meta:
        model = User
        fields = [
            "nome",
            "email",
            "descricao",
            "password",
            "if_funcionario",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["nome"].label = "Nome:"
        self.fields["nome"].help_text = (
            "Nome completo do usuário."
        )

        self.fields["email"].label = "E-mail:"
        self.fields["email"].help_text = (
            "O e-mail será utilizado para acessar o sistema."
        )

        self.fields["descricao"].label = "Observações:"

        self.fields["if_funcionario"].label = (
            "Funcionário:"
        )

        self.fields["if_funcionario"].help_text = (
            "Define se o usuário será tratado como funcionário."
        )

    def save(self, commit=True):
        user = super().save(commit=False)

        user.set_password(
            self.cleaned_data["password"]
        )

        if commit:
            user.save()

        return user


class UserEditForm(forms.ModelForm):

    class Meta:
        model = User
        fields = [
            "nome",
            "email",
            "descricao",
            "if_funcionario",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["nome"].label = "Nome:"
        self.fields["nome"].help_text = (
            "Nome completo do usuário."
        )

        self.fields["email"].label = "E-mail:"
        self.fields["email"].help_text = (
            "O e-mail será utilizado para acessar o sistema."
        )

        self.fields["descricao"].label = "Observações:"

        self.fields["if_funcionario"].label = (
            "Funcionário:"
        )

        self.fields["if_funcionario"].help_text = (
            "Define se o usuário será tratado como funcionário."
        )


class UserFormAdmin(forms.ModelForm):

    password = forms.CharField(
        label="Senha:",
        widget=forms.PasswordInput,
        required=True
    )

    class Meta:
        model = User
        fields = [
            "nome",
            "email",
            "descricao",
            "password",
            "if_funcionario",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["nome"].label = "Nome:"

        self.fields["email"].label = "E-mail:"
        self.fields["email"].help_text = (
            "O e-mail será utilizado para acessar o sistema."
        )

        self.fields["descricao"].label = "Observações:"

        self.fields["if_funcionario"].label = (
            "Funcionário:"
        )

        self.fields["if_funcionario"].help_text = (
            "Define se o usuário será tratado como funcionário."
        )

    def save(self, commit=True):
        user = super().save(commit=False)

        user.set_password(
            self.cleaned_data["password"]
        )

        if commit:
            user.save()

        return user


class ClienteForm(forms.ModelForm):

    class Meta:
        model = Cliente
        fields = [
            "nome",
            "observacoes",
        ]

    def __init__(self, *args, **kwargs):
        kwargs.pop("user", None)

        super().__init__(*args, **kwargs)

        self.fields["nome"].label = "Nome:"
        self.fields["observacoes"].label = "Observações:"
        self.fields["observacoes"].help_text = (
            "Use este campo para registrar informações adicionais."
        )


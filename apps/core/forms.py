from django import forms

from .models import (
    Categoria,
    Destino,
    Estoque,
    Fornecedor,
    Produto,
)


class EmpresaScopedModelForm(forms.ModelForm):
    """
    Formulário base compatível com o modelo atual.
    A empresa pode ser definida pela view quando necessário.
    """

    class Meta:
        abstract = True


class CategoriaForm(EmpresaScopedModelForm):
    class Meta:
        model = Categoria
        fields = [
            "nome",
            "descricao",
            "ativo",
        ]


class EstoqueForm(EmpresaScopedModelForm):
    class Meta:
        model = Estoque
        fields = [
            "empresa",
            "nome",
            "localizacao",
            "descricao",
            "ativo",
        ]


class DestinoForm(EmpresaScopedModelForm):
    class Meta:
        model = Destino
        fields = [
            "empresa",
            "nome",
            "descricao",
            "responsavel",
            "ativo",
        ]


class FornecedorForm(EmpresaScopedModelForm):
    """
    Mantido apenas para compatibilidade com as telas antigas.
    Fornecedor não participa mais do cadastro/operação de Produto.
    """

    class Meta:
        model = Fornecedor
        fields = [
            "empresa",
            "nome",
            "documento",
            "telefone",
            "email",
            "endereco",
            "cidade",
            "estado",
            "observacao",
            "ativo",
        ]


class ProdutoForm(EmpresaScopedModelForm):
    class Meta:
        model = Produto
        fields = [
            "empresa",
            "categoria",
            "nome",
            "codigo",
            "tipo_produto",
            "marca",
            "modelo",
            "material",
            "cor",
            "dimensoes",
            "condicao",
            "descricao",
            "documento_origem",
            "observacao",
            "estoque_minimo",
            "ativo",
        ]


class EntradaEstoqueForm(forms.Form):
    produto = forms.ModelChoiceField(
        queryset=Produto.objects.all(),
        label="Produto",
    )

    estoque = forms.ModelChoiceField(
        queryset=Estoque.objects.all(),
        label="Estoque",
    )

    quantidade = forms.IntegerField(
        min_value=1,
        label="Quantidade",
    )

    documento = forms.CharField(
        required=False,
        label="Documento",
    )

    observacao = forms.CharField(
        required=False,
        widget=forms.Textarea,
        label="Observação",
    )


class SaidaEstoqueForm(forms.Form):
    produto = forms.ModelChoiceField(
        queryset=Produto.objects.all(),
        label="Produto",
    )

    estoque = forms.ModelChoiceField(
        queryset=Estoque.objects.all(),
        label="Estoque",
    )

    destino = forms.ModelChoiceField(
        queryset=Destino.objects.all(),
        required=False,
        label="Destinatário",
    )

    quantidade = forms.IntegerField(
        min_value=1,
        label="Quantidade",
    )

    documento = forms.CharField(
        required=False,
        label="Documento",
    )

    observacao = forms.CharField(
        required=False,
        widget=forms.Textarea,
        label="Observação",
    )


class MovimentacaoFiltroForm(forms.Form):
    produto = forms.ModelChoiceField(
        queryset=Produto.objects.all(),
        required=False,
        label="Produto",
    )

    estoque = forms.ModelChoiceField(
        queryset=Estoque.objects.all(),
        required=False,
        label="Estoque",
    )

    tipo = forms.ChoiceField(
        choices=[
            ("", "Todos"),
            ("E", "Entrada"),
            ("S", "Saída"),
        ],
        required=False,
        label="Tipo",
    )

    data_inicio = forms.DateField(
        required=False,
        label="Data inicial",
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    data_fim = forms.DateField(
        required=False,
        label="Data final",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
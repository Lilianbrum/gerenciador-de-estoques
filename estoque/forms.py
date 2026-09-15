from django import forms

from .models import Produto, Destino, Categoria


class EntradaEstoqueForm(forms.Form):

    produto = forms.ModelChoiceField(
        queryset=Produto.objects.filter(ativo=True),
        label="Produto"
    )

    quantidade = forms.IntegerField(
        label="Quantidade",
        min_value=1
    )

    observacao = forms.CharField(
        label="Observação",
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 3
            }
        )
    )


class SaidaEstoqueForm(forms.Form):

    produto = forms.ModelChoiceField(
        queryset=Produto.objects.filter(ativo=True),
        label="Produto"
    )

    quantidade = forms.IntegerField(
        label="Quantidade",
        min_value=1
    )

    destino = forms.ModelChoiceField(
        queryset=Destino.objects.filter(ativo=True),
        label="Destino"
    )

    observacao = forms.CharField(
        label="Observação",
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 3
            }
        )
    )


class ProdutoForm(forms.ModelForm):

    class Meta:
        model = Produto

        fields = [
            "nome",
            "descricao",
            "codigo",
            "tipo_produto",
            "condicao",
            "documento_origem",
            "categoria",
            "unidade",
            "estoque_minimo",
            "ativo",
        ]

        labels = {
            "nome": "Nome do produto",
            "descricao": "Descrição / Observações",
            "codigo": "Código",
            "tipo_produto": "Tipo do produto",
            "condicao": "Condição",
            "documento_origem": "Documento de origem",
            "categoria": "Categoria",
            "unidade": "Unidade",
            "estoque_minimo": "Estoque mínimo",
            "ativo": "Produto ativo",
        }

        widgets = {
            "nome": forms.TextInput(
                attrs={
                    "placeholder": "Nome completo do produto"
                }
            ),

            "descricao": forms.Textarea(
                attrs={
                    "rows": 6,
                    "placeholder": (
                        "Informe características, especificações "
                        "ou outras observações do produto."
                    )
                }
            ),

            "codigo": forms.TextInput(
                attrs={
                    "placeholder": "Código do produto, se houver"
                }
            ),

            "tipo_produto": forms.TextInput(
                attrs={
                    "placeholder": (
                        "Ex.: Smartphone, cadeira, balança, "
                        "veículo, ferramenta..."
                    )
                }
            ),

            "condicao": forms.TextInput(
                attrs={
                    "placeholder": (
                        "Ex.: Novo, usado, lacrado..."
                    )
                }
            ),

            "documento_origem": forms.TextInput(
                attrs={
                    "placeholder": "Ex.: DOC-38"
                }
            ),

            "categoria": forms.Select(),

            "unidade": forms.TextInput(
                attrs={
                    "placeholder": "Ex.: UN, CX, KG, LT..."
                }
            ),

            "estoque_minimo": forms.NumberInput(
                attrs={
                    "min": 0
                }
            ),
        }

    def clean_codigo(self):
        codigo = self.cleaned_data.get("codigo", "").strip()

        if not codigo:
            return ""

        consulta = Produto.objects.filter(codigo__iexact=codigo)

        # Ao editar, não considerar o próprio produto como duplicado.
        if self.instance and self.instance.pk:
            consulta = consulta.exclude(pk=self.instance.pk)

        if consulta.exists():
            raise forms.ValidationError(
                "Já existe um produto cadastrado com este código. "
                "Se for o mesmo produto, utilize a Entrada de Estoque "
                "para adicionar a quantidade."
            )

        return codigo


class CategoriaForm(forms.ModelForm):

    class Meta:
        model = Categoria

        fields = [
            "nome",
            "descricao",
        ]

        labels = {
            "nome": "Nome da categoria",
            "descricao": "Descrição",
        }

        widgets = {
            "nome": forms.TextInput(
                attrs={
                    "placeholder": "Nome da categoria"
                }
            ),

            "descricao": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": (
                        "Descrição da categoria, se necessário."
                    )
                }
            ),
        }


class DestinoForm(forms.ModelForm):

    class Meta:
        model = Destino

        fields = [
            "nome",
            "tipo",
            "descricao",
            "ativo",
        ]

        labels = {
            "nome": "Nome do destino",
            "tipo": "Tipo",
            "descricao": "Descrição / Observações",
            "ativo": "Destino ativo",
        }

        widgets = {
            "nome": forms.TextInput(
                attrs={
                    "placeholder": (
                        "Ex.: Secretaria Municipal, Filial A, "
                        "Escola Municipal..."
                    )
                }
            ),

            "tipo": forms.TextInput(
                attrs={
                    "placeholder": (
                        "Ex.: Órgão público, filial, escola, "
                        "cliente, setor..."
                    )
                }
            ),

            "descricao": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": (
                        "Informações adicionais sobre este destino."
                    )
                }
            ),
        }
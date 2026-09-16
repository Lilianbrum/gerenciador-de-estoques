from django import forms

from .models import (
    Produto,
    Destino,
    Categoria,
    ConfiguracaoEstoque,
)


class EntradaEstoqueForm(forms.Form):

    produto = forms.ModelChoiceField(
        queryset=Produto.objects.filter(ativo=True),
        label="Produto"
    )

    descricao = forms.CharField(
        label="Descrição do item",
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": (
                    "Descrição específica deste item ou configuração."
                )
            }
        )
    )

    marca = forms.CharField(
        label="Marca",
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": (
                    "Ex.: Apple, Samsung, Tramontina..."
                )
            }
        )
    )

    modelo = forms.CharField(
        label="Modelo",
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": (
                    "Ex.: A2602, Galaxy A15, modelo 120..."
                )
            }
        )
    )

    material = forms.CharField(
        label="Material",
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": (
                    "Ex.: aço inox, madeira, plástico..."
                )
            }
        )
    )

    cor = forms.CharField(
        label="Cor",
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": (
                    "Ex.: prata, preto, branco, marrom..."
                )
            }
        )
    )

    dimensoes = forms.CharField(
        label="Dimensões / tamanho",
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": (
                    "Ex.: 20 cm, 1,20 m x 0,60 m, tamanho M..."
                )
            }
        )
    )

    capacidade = forms.CharField(
        label="Capacidade",
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": (
                    "Ex.: 64 GB, 128 GB, 256 GB, 1 TB, 20 L..."
                )
            }
        )
    )

    memoria_ram = forms.CharField(
        label="RAM",
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": (
                    "Ex.: 4 GB, 8 GB, 16 GB..."
                )
            }
        )
    )

    condicao = forms.CharField(
        label="Condição",
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": (
                    "Ex.: Novo, Usado, Lacrado..."
                )
            }
        )
    )

    origem = forms.CharField(
        label="Origem",
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": (
                    "Ex.: China, Índia, Brasil, Não indicado..."
                )
            }
        )
    )

    documento_origem = forms.CharField(
        label="Documento de origem",
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Ex.: DOC-38"
            }
        )
    )

    quantidade = forms.IntegerField(
        label="Quantidade",
        min_value=1,
        widget=forms.NumberInput(
            attrs={
                "min": 1
            }
        )
    )

    observacao = forms.CharField(
        label="Observação",
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": (
                    "Observações sobre esta entrada."
                )
            }
        )
    )


class SaidaEstoqueForm(forms.Form):

    produto = forms.ModelChoiceField(
        queryset=Produto.objects.filter(ativo=True),
        label="Produto"
    )

    configuracao = forms.ModelChoiceField(
        queryset=ConfiguracaoEstoque.objects.filter(
            ativo=True
        ).select_related(
            "produto"
        ),
        label="Configuração",
        empty_label="Selecione a configuração"
    )

    quantidade = forms.IntegerField(
        label="Quantidade",
        min_value=1,
        widget=forms.NumberInput(
            attrs={
                "min": 1
            }
        )
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

    def clean(self):

        cleaned_data = super().clean()

        produto = cleaned_data.get(
            "produto"
        )

        configuracao = cleaned_data.get(
            "configuracao"
        )

        if (
            produto is not None
            and configuracao is not None
            and configuracao.produto_id != produto.id
        ):
            self.add_error(
                "configuracao",
                "A configuração selecionada não pertence "
                "ao produto escolhido."
            )

        return cleaned_data


class ProdutoForm(forms.ModelForm):

    class Meta:
        model = Produto

        fields = [
            "nome",
            "codigo",
            "tipo_produto",
            "categoria",
            "unidade",
            "estoque_minimo",
            "ativo",
        ]

        labels = {
            "nome": "Nome do produto",
            "codigo": "Código",
            "tipo_produto": "Tipo do produto",
            "categoria": "Categoria",
            "unidade": "Unidade",
            "estoque_minimo": "Estoque mínimo",
            "ativo": "Produto ativo",
        }

        widgets = {
            "nome": forms.TextInput(
                attrs={
                    "placeholder": (
                        "Nome base do produto"
                    )
                }
            ),

            "codigo": forms.TextInput(
                attrs={
                    "placeholder": (
                        "Código do produto, se houver"
                    )
                }
            ),

            "tipo_produto": forms.TextInput(
                attrs={
                    "placeholder": (
                        "Ex.: Smartphone, tablet, cadeira, "
                        "balança, veículo, ferramenta, talher..."
                    )
                }
            ),

            "categoria": forms.Select(),

            "unidade": forms.TextInput(
                attrs={
                    "placeholder": (
                        "Ex.: UN, CX, KG, LT..."
                    )
                }
            ),

            "estoque_minimo": forms.NumberInput(
                attrs={
                    "min": 0
                }
            ),
        }

    def clean_codigo(self):

        codigo = self.cleaned_data.get(
            "codigo",
            ""
        ).strip()

        if not codigo:
            return ""

        consulta = Produto.objects.filter(
            codigo__iexact=codigo
        )

        if self.instance and self.instance.pk:

            consulta = consulta.exclude(
                pk=self.instance.pk
            )

        if consulta.exists():

            raise forms.ValidationError(
                "Já existe um produto cadastrado com este código. "
                "Se for o mesmo produto com outra configuração, "
                "utilize a Entrada de Estoque para adicionar "
                "a nova configuração."
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
                    "placeholder": (
                        "Nome da categoria"
                    )
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
from rest_framework import serializers

from core.models import (
    Categoria,
    Destino,
    Estoque,
    Movimentacao,
    Produto,
    SaldoEstoque,
)


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = [
            "id",
            "nome",
            "descricao",
            "ativo",
            "criado_em",
            "atualizado_em",
        ]


class EstoqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estoque
        fields = [
            "id",
            "empresa",
            "nome",
            "localizacao",
            "descricao",
            "ativo",
            "criado_em",
            "atualizado_em",
        ]


class DestinoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destino
        fields = [
            "id",
            "empresa",
            "nome",
            "descricao",
            "responsavel",
            "ativo",
            "criado_em",
            "atualizado_em",
        ]


class SaldoEstoqueSerializer(serializers.ModelSerializer):
    estoque_nome = serializers.CharField(
        source="estoque.nome",
        read_only=True,
    )
    estoque_localizacao = serializers.CharField(
        source="estoque.localizacao",
        read_only=True,
    )

    class Meta:
        model = SaldoEstoque
        fields = [
            "id",
            "produto",
            "estoque",
            "estoque_nome",
            "estoque_localizacao",
            "quantidade",
            "atualizado_em",
        ]


class ProdutoSerializer(serializers.ModelSerializer):
    categoria_nome = serializers.CharField(
        source="categoria.nome",
        read_only=True,
    )
    estoque_total = serializers.IntegerField(
        read_only=True,
    )
    estoque_baixo = serializers.BooleanField(
        read_only=True,
    )
    saldos = SaldoEstoqueSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Produto
        fields = [
            "id",
            "empresa",
            "categoria",
            "categoria_nome",
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
            "estoque_total",
            "estoque_baixo",
            "saldos",
            "criado_em",
            "atualizado_em",
        ]


class MovimentacaoSerializer(serializers.ModelSerializer):
    produto_nome = serializers.CharField(
        source="produto.nome",
        read_only=True,
    )
    estoque_nome = serializers.CharField(
        source="estoque.nome",
        read_only=True,
    )
    destino_nome = serializers.CharField(
        source="destino.nome",
        read_only=True,
    )
    usuario_nome = serializers.CharField(
        source="usuario.nome",
        read_only=True,
    )
    tipo_display = serializers.CharField(
        source="get_tipo_display",
        read_only=True,
    )

    class Meta:
        model = Movimentacao
        fields = [
            "id",
            "empresa",
            "produto",
            "produto_nome",
            "estoque",
            "estoque_nome",
            "destino",
            "destino_nome",
            "tipo",
            "tipo_display",
            "quantidade",
            "documento",
            "observacao",
            "usuario",
            "usuario_nome",
            "criado_em",
        ]
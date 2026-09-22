from django.contrib import admin

from .models import (
    Categoria,
    Destino,
    Estoque,
    Fornecedor,
    Movimentacao,
    Produto,
    SaldoEstoque,
)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "ativo",
        "criado_em",
    )
    list_filter = (
        "ativo",
    )
    search_fields = (
        "nome",
        "descricao",
    )


@admin.register(Estoque)
class EstoqueAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "empresa",
        "localizacao",
        "ativo",
    )
    list_filter = (
        "empresa",
        "ativo",
    )
    search_fields = (
        "nome",
        "localizacao",
    )


@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "empresa",
        "documento",
        "telefone",
        "ativo",
    )
    list_filter = (
        "empresa",
        "ativo",
    )
    search_fields = (
        "nome",
        "documento",
        "email",
    )


@admin.register(Destino)
class DestinoAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "empresa",
        "responsavel",
        "ativo",
    )
    list_filter = (
        "empresa",
        "ativo",
    )
    search_fields = (
        "nome",
        "responsavel",
    )


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "codigo",
        "categoria",
        "empresa",
        "condicao",
        "ativo",
    )
    list_filter = (
        "empresa",
        "categoria",
        "condicao",
        "ativo",
    )
    search_fields = (
        "nome",
        "codigo",
        "marca",
        "modelo",
        "tipo_produto",
        "documento_origem",
    )


@admin.register(SaldoEstoque)
class SaldoEstoqueAdmin(admin.ModelAdmin):
    list_display = (
        "produto",
        "estoque",
        "quantidade",
        "atualizado_em",
    )
    list_filter = (
        "estoque",
    )
    search_fields = (
        "produto__nome",
        "produto__codigo",
        "estoque__nome",
    )


@admin.register(Movimentacao)
class MovimentacaoAdmin(admin.ModelAdmin):
    list_display = (
        "criado_em",
        "tipo",
        "produto",
        "estoque",
        "quantidade",
        "destino",
        "usuario",
    )
    list_filter = (
        "tipo",
        "estoque",
        "destino",
        "criado_em",
    )
    search_fields = (
        "produto__nome",
        "produto__codigo",
        "documento",
        "observacao",
        "usuario__nome",
    )
    date_hierarchy = "criado_em"
    ordering = (
        "-criado_em",
        "-id",
    )
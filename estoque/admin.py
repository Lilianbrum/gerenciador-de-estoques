from django.contrib import admin
from .models import Categoria, Produto, Destino, Movimentacao


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "descricao",
    )

    search_fields = (
        "nome",
    )


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "codigo",
        "categoria",
        "tipo_produto",
        "condicao",
        "estoque_atual",
        "estoque_minimo",
        "ativo",
    )

    search_fields = (
        "nome",
        "codigo",
        "tipo_produto",
        "documento_origem",
    )

    list_filter = (
        "categoria",
        "tipo_produto",
        "condicao",
        "ativo",
    )

    list_display_links = (
        "nome",
    )

    ordering = (
        "nome",
    )


@admin.register(Destino)
class DestinoAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "tipo",
        "ativo",
    )

    search_fields = (
        "nome",
        "tipo",
    )

    list_filter = (
        "tipo",
        "ativo",
    )


@admin.register(Movimentacao)
class MovimentacaoAdmin(admin.ModelAdmin):
    list_display = (
        "produto",
        "tipo",
        "quantidade",
        "destino",
        "usuario",
        "criado_em",
    )

    search_fields = (
        "produto__nome",
        "destino__nome",
        "observacao",
    )

    list_filter = (
        "tipo",
        "destino",
        "criado_em",
    )
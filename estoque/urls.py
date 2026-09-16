from django.urls import path

from . import views


urlpatterns = [

    path(
        "",
        views.dashboard,
        name="dashboard",
    ),

    path(
        "produtos/",
        views.produtos,
        name="produtos",
    ),

    path(
        "entrada/",
        views.entrada_estoque,
        name="entrada_estoque",
    ),

    path(
        "saida/",
        views.saida_estoque,
        name="saida_estoque",
    ),

    path(
        "produto/novo/",
        views.novo_produto,
        name="novo_produto",
    ),

    path(
        "produto/<int:produto_id>/editar/",
        views.editar_produto,
        name="editar_produto",
    ),

    path(
        "categorias/",
        views.categorias,
        name="categorias",
    ),

    path(
        "historico/",
        views.historico_movimentacoes,
        name="historico_movimentacoes",
    ),

    path(
        "historico/<int:movimentacao_id>/excluir/",
        views.excluir_movimentacao,
        name="excluir_movimentacao",
    ),

    path(
        "destinos/",
        views.destinos,
        name="destinos",
    ),

    path(
        "destino/<int:destino_id>/editar/",
        views.editar_destino,
        name="editar_destino",
    ),

    path(
        "destino/<int:destino_id>/alternar/",
        views.alternar_destino,
        name="alternar_destino",
    ),

    path(
        "distribuicoes/",
        views.distribuicoes,
        name="distribuicoes",
    ),
]
from django.urls import include, path

from . import ajax

from .views import (
    DashboardView,
    EstoqueCreateView,
    EstoqueListView,
    EstoqueUpdateView,
    CategoriaCreateView,
    CategoriaListView,
    CategoriaUpdateView,
    FornecedorCreateView,
    FornecedorListView,
    FornecedorUpdateView,
    DestinoCreateView,
    DestinoListView,
    DestinoUpdateView,
    ProdutoCreateView,
    ProdutoListView,
    ProdutoDetailView,
    ProdutoUpdateView,
    EntradaEstoqueView,
    SaidaEstoqueView,
    MovimentacaoListView,
    EstoqueAtualView,
    RelatoriosView,
)


app_name = "core"


urlpatterns = [
    # Dashboard
    path("dashboard/", DashboardView.as_view(), name="dashboard"),

    # Produtos
    path("produtos/", ProdutoListView.as_view(), name="produto_list"),
    path("produtos/novo/", ProdutoCreateView.as_view(), name="produto_create"),
    path("produtos/<int:pk>/", ProdutoDetailView.as_view(), name="produto_detail"),
    path("produtos/<int:pk>/editar/", ProdutoUpdateView.as_view(), name="produto_update"),

    # Categorias
    path("categorias/", CategoriaListView.as_view(), name="categoria_list"),
    path("categorias/nova/", CategoriaCreateView.as_view(), name="categoria_create"),
    path("categorias/<int:pk>/editar/", CategoriaUpdateView.as_view(), name="categoria_update"),

    # Estoques
    path("estoques/", EstoqueListView.as_view(), name="estoque_list"),
    path("estoques/novo/", EstoqueCreateView.as_view(), name="estoque_create"),
    path("estoques/<int:pk>/editar/", EstoqueUpdateView.as_view(), name="estoque_update"),
    path("estoque/atual/", EstoqueAtualView.as_view(), name="estoque_atual"),

    # Fornecedores
    path("fornecedores/", FornecedorListView.as_view(), name="fornecedor_list"),
    path("fornecedores/novo/", FornecedorCreateView.as_view(), name="fornecedor_create"),
    path("fornecedores/<int:pk>/editar/", FornecedorUpdateView.as_view(), name="fornecedor_update"),

    # Destinos
    path("destinos/", DestinoListView.as_view(), name="destino_list"),
    path("destinos/novo/", DestinoCreateView.as_view(), name="destino_create"),
    path("destinos/<int:pk>/editar/", DestinoUpdateView.as_view(), name="destino_update"),

    # Movimentação de estoque
    path("estoque/entrada/", EntradaEstoqueView.as_view(), name="entrada"),
    path("estoque/saida/", SaidaEstoqueView.as_view(), name="saida"),
    path("movimentacoes/", MovimentacaoListView.as_view(), name="movimentacao_list"),

    # Relatórios
    path("relatorios/", RelatoriosView.as_view(), name="relatorios"),

    # AJAX existente
    path("ajax/fornecedores/", ajax.fornecedor_por_empresa, name="ajax_fornecedores"),
    path("ajax/marcas/", ajax.marca_por_empresa, name="ajax_marcas"),
    path("ajax/tipos-produto/", ajax.tipo_por_empresa, name="ajax_tipos_produtos"),
    path("ajax/produtos/", ajax.produto_por_empresa, name="ajax_produtos"),
    path("ajax/categorias/", ajax.categoria_por_empresa, name="ajax_categorias"),
    path("ajax/estoques/", ajax.estoque_por_empresa, name="ajax_estoques"),
    path("ajax/destinos/", ajax.destino_por_empresa, name="ajax_destinos"),

    # API REST
    path("api/", include("core.api.urls")),
]
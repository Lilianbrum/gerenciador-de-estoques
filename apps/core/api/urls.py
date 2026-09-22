from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoriaViewSet,
    DestinoViewSet,
    EstoqueViewSet,
    MovimentacaoViewSet,
    ProdutoViewSet,
    SaldoEstoqueViewSet,
    dashboard_api,
)


router = DefaultRouter()

router.register(
    r"categorias",
    CategoriaViewSet,
    basename="categoria",
)

router.register(
    r"estoques",
    EstoqueViewSet,
    basename="estoque",
)

router.register(
    r"destinos",
    DestinoViewSet,
    basename="destino",
)

router.register(
    r"produtos",
    ProdutoViewSet,
    basename="produto",
)

router.register(
    r"saldos",
    SaldoEstoqueViewSet,
    basename="saldo",
)

router.register(
    r"movimentacoes",
    MovimentacaoViewSet,
    basename="movimentacao",
)


urlpatterns = [
    path(
        "dashboard/",
        dashboard_api,
        name="dashboard-api",
    ),
    path(
        "",
        include(router.urls),
    ),
]
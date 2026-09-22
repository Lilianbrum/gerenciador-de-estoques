from django.urls import path

from .views import (
    HomePageView,
    ToggleThemeView,
    UserCreateView,
    UserCreateViewAdmin,
    UserDeactivateView,
    UserDetailView,
    UserListView,
    UserUpdateView,
)


urlpatterns = [

    # Página inicial
    path(
        "home/",
        HomePageView.as_view(),
        name="home",
    ),

    # Usuários
    path(
        "cadastrar_usuario/",
        UserCreateView.as_view(),
        name="cadastrar_usuario",
    ),

    path(
        "cadastrar_usuario_admin/",
        UserCreateViewAdmin.as_view(),
        name="cadastrar_usuario_admin",
    ),

    path(
        "lista_usuarios/",
        UserListView.as_view(),
        name="lista_usuarios",
    ),

    path(
        "editar_usuario/<int:pk>/",
        UserUpdateView.as_view(),
        name="editar_usuario",
    ),

    path(
        "inativar_usuario/<int:pk>/",
        UserDeactivateView.as_view(),
        name="inativar_usuario",
    ),

    path(
        "detalhe_colaborador/<int:pk>/",
        UserDetailView.as_view(),
        name="detalhe_colaborador",
    ),

    # Tema
    path(
        "toggle_theme/",
        ToggleThemeView.as_view(),
        name="toggle_theme",
    ),
]
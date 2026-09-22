from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.generic import TemplateView


urlpatterns = [

    # Administração
    path(
        "admin/",
        admin.site.urls,
    ),

    # Usuários
    path(
        "users/",
        include("users.urls"),
    ),

    # Sistema de estoque
    path(
        "core/",
        include("core.urls"),
    ),

    # Página inicial pública
    path(
        "",
        TemplateView.as_view(
            template_name="base/inicio.html"
        ),
        name="inicio",
    ),

    # Informações do sistema
    path(
        "infosistema/",
        TemplateView.as_view(
            template_name="base/infosistema.html"
        ),
        name="infosistema",
    ),

    # Login
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="users/users/login.html"
        ),
        name="login",
    ),

    # Logout
    path(
        "logout/",
        auth_views.LogoutView.as_view(
            next_page="login"
        ),
        name="logout",
    ),
]


if settings.DEBUG:

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )

    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT,
    )
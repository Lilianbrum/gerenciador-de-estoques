from datetime import date

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView

from .forms import UserEditForm, UserForm, UserFormAdmin
from .models import User


def base(request):
    """
    Contexto global utilizado pelos templates.
    """

    context = {
        "now": timezone.now().time(),
    }

    area_url = request.META.get("PATH_INFO", "")

    if request.user.is_authenticated and "/admin/" not in area_url:

        objuser = request.user

        if objuser.nome:
            partes_nome = objuser.nome.strip().split()

            if len(partes_nome) == 1:
                nome_formatado = partes_nome[0]
            else:
                nome_formatado = (
                    f"{partes_nome[0]} {partes_nome[-1]}"
                )
        else:
            nome_formatado = "Usuário"

        context.update(
            {
                "objuser": objuser,
                "nome_e_sobrenome": nome_formatado,
            }
        )

    return context


class HomePageView(
    LoginRequiredMixin,
    TemplateView,
):
    template_name = "users/users/home.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["objuser"] = self.request.user
        context["data_atual"] = date.today()

        return context


class UserCreateView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    CreateView,
):
    model = User
    form_class = UserForm
    template_name = "users/users/cadastrar_usuario.html"

    def get_success_url(self):
        return reverse_lazy("lista_usuarios")

    def test_func(self):
        return (
            self.request.user.is_superuser
            or self.request.user.is_staff
        )

    def handle_no_permission(self):

        if self.request.user.is_authenticated:
            return redirect("home")

        return super().handle_no_permission()


class UserCreateViewAdmin(
    LoginRequiredMixin,
    UserPassesTestMixin,
    CreateView,
):
    model = User
    form_class = UserFormAdmin
    template_name = "users/users/cadastrar_usuario.html"
    success_url = reverse_lazy("lista_usuarios")

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):

        if self.request.user.is_authenticated:
            return redirect("home")

        return super().handle_no_permission()


class UserListView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    ListView,
):
    model = User
    template_name = "users/users/lista_usuarios.html"
    context_object_name = "usuarios"

    def get_queryset(self):

        consulta = self.request.GET.get("q")

        queryset = User.objects.all().order_by(
            "nome",
            "email",
        )

        if consulta:
            queryset = queryset.filter(
                nome__icontains=consulta
            ) | queryset.filter(
                email__icontains=consulta
            )

        return queryset

    def test_func(self):

        return (
            self.request.user.is_superuser
            or self.request.user.is_staff
        )

    def handle_no_permission(self):

        if self.request.user.is_authenticated:
            return redirect("home")

        return super().handle_no_permission()


class UserUpdateView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    UpdateView,
):
    model = User
    form_class = UserEditForm
    template_name = "users/users/editar_usuario.html"

    def get_success_url(self):
        return reverse_lazy(
            "detalhe_colaborador",
            kwargs={
                "pk": self.object.pk
            },
        )

    def test_func(self):

        usuario = self.get_object()

        return (
            self.request.user.is_superuser
            or self.request.user.is_staff
            or self.request.user == usuario
        )

    def handle_no_permission(self):

        if self.request.user.is_authenticated:
            return redirect("home")

        return super().handle_no_permission()


class UserDeactivateView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    View,
):
    def test_func(self):

        usuario = get_object_or_404(
            User,
            pk=self.kwargs["pk"],
        )

        return (
            self.request.user.is_superuser
            or self.request.user.is_staff
            or self.request.user == usuario
        )

    def handle_no_permission(self):

        if self.request.user.is_authenticated:
            return redirect("home")

        return super().handle_no_permission()

    def post(self, request, *args, **kwargs):

        usuario = get_object_or_404(
            User,
            pk=kwargs["pk"],
        )

        usuario.is_active = False
        usuario.data_desativacao = timezone.now()
        usuario.save(
            update_fields=[
                "is_active",
                "data_desativacao",
            ]
        )

        messages.success(
            request,
            f"O usuário {usuario.nome} foi "
            "inativado com sucesso.",
        )

        return redirect("lista_usuarios")


class UserDetailView(
    LoginRequiredMixin,
    DetailView,
):
    model = User
    template_name = "users/users/detalhe.html"
    context_object_name = "objuser"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["objuser"] = self.get_object()

        return context


class ToggleThemeView(
    LoginRequiredMixin,
    View,
):
    def post(self, request, *args, **kwargs):

        usuario = request.user

        if usuario.theme == "dark":
            usuario.theme = "light"
        else:
            usuario.theme = "dark"

        usuario.save(
            update_fields=["theme"]
        )

        if request.headers.get(
            "X-Requested-With"
        ) == "XMLHttpRequest":

            return JsonResponse(
                {
                    "success": True,
                    "new_theme": usuario.theme,
                }
            )

        return redirect(
            request.META.get(
                "HTTP_REFERER",
                "home",
            )
        )
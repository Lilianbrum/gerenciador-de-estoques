from django.contrib import admin

from .models import Cliente, Empresa, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    list_display = (
        "nome",
        "email",
        "if_funcionario",
        "is_active",
        "is_staff",
        "is_superuser",
    )

    list_filter = (
        "if_funcionario",
        "is_active",
        "is_staff",
        "is_superuser",
    )

    search_fields = (
        "nome",
        "email",
    )


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):

    list_display = (
        "nome",
        "cnpj",
        "razao_social",
        "email",
    )

    search_fields = (
        "nome",
        "cnpj",
        "razao_social",
        "email",
    )


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):

    list_display = (
        "nome",
        "is_active",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "nome",
        "observacoes",
    )


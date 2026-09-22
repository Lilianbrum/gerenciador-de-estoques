from django.db import models
from django.db.models import Q
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from colorfield.fields import ColorField
from ckeditor_uploader.fields import RichTextUploadingField


class UserManager(BaseUserManager):

    def get_or_create(self, defaults=None, **kwargs):
        try:
            user = self.get(**kwargs)

            if user.excluido or not user.is_active:
                user.excluido = False
                user.is_active = True
                user.save()

            return user, False

        except self.model.DoesNotExist:
            if defaults:
                kwargs.update(defaults)

            return self._create_user(**kwargs), True

    def _create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(
                "Usuário deve possuir um endereço de e-mail."
            )

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        return self._create_user(
            email,
            password,
            **extra_fields
        )

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("excluido", False)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(
                "Superuser must have is_staff=True."
            )

        if extra_fields.get("is_superuser") is not True:
            raise ValueError(
                "Superuser must have is_superuser=True."
            )

        return self._create_user(
            email,
            password,
            **extra_fields
        )

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .exclude(is_active=False)
            .exclude(excluido=True)
        )

    def todos_usuarios(self):
        return super().get_queryset()


class BaseModel(models.Model):
    data_criacao = models.DateTimeField(
        auto_now_add=True
    )

    data_atualizacao = models.DateTimeField(
        auto_now=True
    )

    is_active = models.BooleanField(
        default=True
    )

    data_desativacao = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        abstract = True


class Empresa(BaseModel):
    """
    Mantida para compatibilidade com estruturas herdadas
    do projeto original.

    Não possui vínculo com o usuário.
    """

    nome = models.CharField(
        max_length=255
    )

    cnpj = models.CharField(
        "CNPJ",
        max_length=18,
        blank=True,
        null=True
    )

    razao_social = models.CharField(
        "Razão Social",
        max_length=255,
        blank=True,
        null=True
    )

    email = models.EmailField(
        "Endereço de E-mail",
        max_length=255,
        unique=True,
        null=True,
        blank=True
    )

    descricao = RichTextUploadingField(
        "Observação",
        blank=True,
        null=True
    )

    logo = models.ImageField(
        "Logo",
        upload_to="logo/",
        blank=True,
        null=True
    )

    color = ColorField(
        format="hexa",
        default="#000000"
    )

    color_fonte = ColorField(
        format="hexa",
        blank=True,
        null=True
    )

    logo_navegador = models.ImageField(
        "Logo do navegador",
        upload_to="logonavegador/",
        blank=True,
        null=True
    )

    agenda = models.BooleanField(
        "Liberar funcionalidade de agenda",
        default=False
    )

    lista_produto = models.BooleanField(
        "Liberar funcionalidade de lista de produto",
        default=False
    )

    telefonedecontato = models.CharField(
        "Número de telefone",
        max_length=18,
        blank=True,
        null=True
    )

    resumo_loja = models.TextField(
        "Resumo",
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Instituição"
        verbose_name_plural = "Instituições"

    def __str__(self):
        return self.nome


THEME_CHOICES = [
    ("dark", "Dark"),
    ("light", "Light"),
    ("auto", "Auto"),
]


class User(AbstractBaseUser, PermissionsMixin):

    nome = models.CharField(
        "Nome",
        max_length=255
    )

    email = models.EmailField(
        "E-mail",
        max_length=255,
        unique=True
    )

    descricao = RichTextUploadingField(
        "Observações",
        null=True,
        blank=True
    )

    theme = models.CharField(
        "Tema",
        max_length=5,
        default="dark",
        choices=THEME_CHOICES
    )

    if_funcionario = models.BooleanField(
        "Funcionário",
        default=True
    )

    is_active = models.BooleanField(
        "Ativo",
        default=True
    )

    is_staff = models.BooleanField(
        "Acesso administrativo",
        default=False
    )

    is_admin = models.BooleanField(
        "Administrador",
        default=False
    )

    excluido = models.BooleanField(
        default=False
    )

    data_criacao = models.DateTimeField(
        auto_now_add=True
    )

    data_desativacao = models.DateTimeField(
        null=True,
        blank=True
    )

    objects = UserManager()

    # O e-mail será o login.
    USERNAME_FIELD = "email"

    # Não existem outros campos obrigatórios para criação.
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):

        if not self.pk and self.email:

            usuarios_qs = (
                User.objects
                .todos_usuarios()
                .filter(
                    Q(excluido=True) | Q(is_active=False),
                    email=self.email
                )
            )

            if usuarios_qs.exists():

                usuario_existente = usuarios_qs.first()

                usuario_existente.is_active = True
                usuario_existente.excluido = False

                usuario_existente.save()

                return usuario_existente

        return super().save(*args, **kwargs)

    def get_short_name(self):
        return self.nome

    def __str__(self):
        return self.nome


class ProfileManager(BaseUserManager):

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .exclude(
                user__is_active=False
            )
            .exclude(
                user__excluido=True
            )
        )

    def todos_usuarios(self):
        return super().get_queryset()

    def usuarios_inativos(self):
        return (
            super()
            .get_queryset()
            .filter(
                user__is_active=False
            )
        )

    def usuarios_ativos(self):
        return (
            super()
            .get_queryset()
            .filter(
                user__is_active=True
            )
        )


class Cliente(BaseModel):

    nome = models.CharField(
        max_length=255
    )

    observacoes = RichTextUploadingField(
        "Observação",
        blank=True,
        null=True
    )

    def __str__(self):
        return self.nome
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Categoria(models.Model):
    nome = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Classe"
    )
    descricao = models.TextField(
        blank=True,
        verbose_name="Descrição"
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )

    class Meta:
        ordering = ["nome"]
        verbose_name = "Classe"
        verbose_name_plural = "Classes"

    def __str__(self):
        return self.nome


class Estoque(models.Model):
    empresa = models.ForeignKey(
        "users.Empresa",
        on_delete=models.CASCADE,
        related_name="estoques",
        verbose_name="Instituição"
    )
    nome = models.CharField(
        max_length=150,
        verbose_name="Nome"
    )
    localizacao = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Localização"
    )
    descricao = models.TextField(
        blank=True,
        verbose_name="Descrição"
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )

    class Meta:
        ordering = ["nome"]
        verbose_name = "Estoque"
        verbose_name_plural = "Estoques"
        constraints = [
            models.UniqueConstraint(
                fields=["empresa", "nome"],
                name="estoque_empresa_nome_unico"
            )
        ]

    def __str__(self):
        if self.localizacao:
            return f"{self.nome} - {self.localizacao}"
        return self.nome


class Fornecedor(models.Model):
    """
    Mantido temporariamente no banco por compatibilidade com
    versões anteriores do sistema. Não participa mais do
    cadastro/operação dos produtos.
    """
    empresa = models.ForeignKey(
        "users.Empresa",
        on_delete=models.CASCADE,
        related_name="fornecedores",
        verbose_name="Instituição"
    )
    nome = models.CharField(
        max_length=200,
        verbose_name="Nome"
    )
    documento = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="CPF/CNPJ"
    )
    telefone = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Telefone"
    )
    email = models.EmailField(
        blank=True,
        verbose_name="E-mail"
    )
    endereco = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Endereço"
    )
    cidade = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Cidade"
    )
    estado = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Estado"
    )
    observacao = models.TextField(
        blank=True,
        verbose_name="Observação"
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )

    class Meta:
        ordering = ["nome"]
        verbose_name = "Fornecedor"
        verbose_name_plural = "Fornecedores"

    def __str__(self):
        return self.nome


class Destino(models.Model):
    """
    Representa o destinatário/setor/unidade que recebe
    materiais nas saídas de estoque.
    """
    empresa = models.ForeignKey(
        "users.Empresa",
        on_delete=models.CASCADE,
        related_name="destinos",
        verbose_name="Instituição"
    )
    nome = models.CharField(
        max_length=200,
        verbose_name="Destinatário"
    )
    descricao = models.TextField(
        blank=True,
        verbose_name="Descrição"
    )
    responsavel = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Responsável"
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )

    class Meta:
        ordering = ["nome"]
        verbose_name = "Destinatário"
        verbose_name_plural = "Destinatários"

    def __str__(self):
        return self.nome


class Produto(models.Model):
    empresa = models.ForeignKey(
        "users.Empresa",
        on_delete=models.CASCADE,
        related_name="produtos",
        verbose_name="Instituição"
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name="produtos",
        verbose_name="Classe"
    )

    nome = models.CharField(
        max_length=255,
        verbose_name="Nome"
    )
    codigo = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Código"
    )
    tipo_produto = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Tipo de produto",
        help_text=(
            "Ex.: smartphone, veículo, material de escritório, "
            "equipamento etc."
        )
    )
    marca = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Marca"
    )
    modelo = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Modelo"
    )
    material = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Material"
    )
    cor = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Cor"
    )
    dimensoes = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Dimensões"
    )
    condicao = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Condição",
        help_text=(
            "Ex.: novo, usado, lacrado, seminovo etc."
        )
    )
    descricao = models.TextField(
        blank=True,
        verbose_name="Descrição"
    )
    documento_origem = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Documento de origem"
    )
    observacao = models.TextField(
        blank=True,
        verbose_name="Observação"
    )
    estoque_minimo = models.PositiveIntegerField(
        default=0,
        verbose_name="Estoque mínimo"
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )

    class Meta:
        ordering = ["nome"]
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        constraints = [
            models.UniqueConstraint(
                fields=["empresa", "codigo"],
                condition=~models.Q(codigo=""),
                name="produto_empresa_codigo_unico"
            )
        ]

    def __str__(self):
        if self.codigo:
            return f"{self.nome} ({self.codigo})"
        return self.nome

    @property
    def estoque_total(self):
        return sum(
            saldo.quantidade
            for saldo in self.saldos.select_related("estoque").all()
        )

    @property
    def estoque_baixo(self):
        return (
            self.estoque_minimo > 0
            and self.estoque_total <= self.estoque_minimo
        )


class SaldoEstoque(models.Model):
    produto = models.ForeignKey(
        Produto,
        on_delete=models.CASCADE,
        related_name="saldos",
        verbose_name="Produto"
    )
    estoque = models.ForeignKey(
        Estoque,
        on_delete=models.CASCADE,
        related_name="saldos",
        verbose_name="Estoque"
    )
    quantidade = models.PositiveIntegerField(
        default=0,
        verbose_name="Quantidade"
    )
    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )

    class Meta:
        ordering = ["produto__nome", "estoque__nome"]
        verbose_name = "Saldo de estoque"
        verbose_name_plural = "Saldos de estoque"
        constraints = [
            models.UniqueConstraint(
                fields=["produto", "estoque"],
                name="saldo_produto_estoque_unico"
            )
        ]

    def __str__(self):
        return (
            f"{self.produto} - "
            f"{self.estoque}: "
            f"{self.quantidade}"
        )


class Movimentacao(models.Model):

    class Tipo(models.TextChoices):
        ENTRADA = "E", "Entrada"
        SAIDA = "S", "Saída"

    empresa = models.ForeignKey(
        "users.Empresa",
        on_delete=models.CASCADE,
        related_name="movimentacoes",
        verbose_name="Instituição"
    )
    produto = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT,
        related_name="movimentacoes",
        verbose_name="Produto"
    )
    estoque = models.ForeignKey(
        Estoque,
        on_delete=models.PROTECT,
        related_name="movimentacoes",
        verbose_name="Estoque"
    )
    destino = models.ForeignKey(
        Destino,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movimentacoes",
        verbose_name="Destinatário"
    )
    tipo = models.CharField(
        max_length=1,
        choices=Tipo.choices,
        verbose_name="Tipo"
    )
    quantidade = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Quantidade"
    )
    documento = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Documento"
    )
    observacao = models.TextField(
        blank=True,
        verbose_name="Observação"
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movimentacoes_estoque",
        verbose_name="Usuário"
    )
    criado_em = models.DateTimeField(
        default=timezone.now,
        verbose_name="Data da movimentação"
    )

    class Meta:
        ordering = ["-criado_em", "-id"]
        verbose_name = "Movimentação"
        verbose_name_plural = "Movimentações"

    def __str__(self):
        return (
            f"{self.get_tipo_display()} - "
            f"{self.produto} - "
            f"{self.quantidade}"
        )
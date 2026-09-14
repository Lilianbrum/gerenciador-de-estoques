from django.db import models


class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Produto(models.Model):
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)

    codigo = models.CharField(
        max_length=100,
        blank=True
    )

    tipo_produto = models.CharField(
        max_length=100,
        blank=True
    )

    condicao = models.CharField(
        max_length=20,
        blank=True
    )

    documento_origem = models.CharField(
        max_length=100,
        blank=True
    )

    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name="produtos"
    )

    unidade = models.CharField(
        max_length=20,
        default="UN"
    )

    estoque_atual = models.PositiveIntegerField(
        default=0
    )

    estoque_minimo = models.PositiveIntegerField(
        default=0
    )

    ativo = models.BooleanField(
        default=True
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    atualizado_em = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Destino(models.Model):
    nome = models.CharField(
        max_length=200,
        unique=True
    )

    tipo = models.CharField(
        max_length=100,
        blank=True
    )

    descricao = models.TextField(
        blank=True
    )

    ativo = models.BooleanField(
        default=True
    )

    class Meta:
        verbose_name = "Destino"
        verbose_name_plural = "Destinos"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Movimentacao(models.Model):
    produto = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT,
        related_name="movimentacoes"
    )

    destino = models.ForeignKey(
        Destino,
        on_delete=models.PROTECT,
        related_name="movimentacoes",
        null=True,
        blank=True
    )

    tipo = models.CharField(
        max_length=1
    )

    quantidade = models.PositiveIntegerField()

    observacao = models.TextField(
        blank=True
    )

    usuario = models.ForeignKey(
        "auth.User",
        on_delete=models.PROTECT
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = "Movimentação"
        verbose_name_plural = "Movimentações"
        ordering = ["-criado_em"]

    def __str__(self):
        return (
            f"{self.produto} - "
            f"{self.tipo} - "
            f"{self.quantidade}"
        )


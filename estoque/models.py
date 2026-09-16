from django.db import models


class Categoria(models.Model):
    nome = models.CharField(
        max_length=100,
        unique=True
    )

    descricao = models.TextField(
        blank=True
    )

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Produto(models.Model):
    nome = models.CharField(
        max_length=200
    )

    # Mantido temporariamente para preservar os dados atuais.
    # Será reorganizado na próxima etapa.
    descricao = models.TextField(
        blank=True
    )

    codigo = models.CharField(
        max_length=100,
        blank=True
    )

    tipo_produto = models.CharField(
        max_length=100,
        blank=True
    )

    # Mantido temporariamente para migração dos dados existentes.
    condicao = models.CharField(
        max_length=20,
        blank=True
    )

    # Mantido temporariamente para migração dos dados existentes.
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

    # Mantido temporariamente como estoque total do produto.
    # Posteriormente será alimentado pelas configurações.
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


class ConfiguracaoEstoque(models.Model):
    """
    Representa uma configuração específica de um produto
    dentro do estoque.

    Um mesmo produto pode possuir várias configurações.

    Exemplo:

    Produto:
        Samsung Galaxy Tab A9

    Configurações:
        64 GB / 4 GB RAM / Novo
        128 GB / 8 GB RAM / Novo
        128 GB / 8 GB RAM / Usado
    """

    produto = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT,
        related_name="configuracoes"
    )

    descricao = models.TextField(
        blank=True
    )

    capacidade = models.CharField(
        max_length=100,
        blank=True
    )

    memoria_ram = models.CharField(
        max_length=100,
        blank=True
    )

    condicao = models.CharField(
        max_length=20,
        blank=True
    )

    origem = models.CharField(
        max_length=100,
        blank=True
    )

    documento_origem = models.CharField(
        max_length=100,
        blank=True
    )

    quantidade = models.PositiveIntegerField(
        default=0
    )

    observacao = models.TextField(
        blank=True
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
        verbose_name = "Configuração de estoque"
        verbose_name_plural = "Configurações de estoque"
        ordering = [
            "produto__nome",
            "capacidade",
            "memoria_ram",
            "condicao",
        ]

    def __str__(self):
        partes = [self.produto.nome]

        if self.capacidade:
            partes.append(self.capacidade)

        if self.memoria_ram:
            partes.append(self.memoria_ram)

        if self.condicao:
            partes.append(self.condicao)

        return " - ".join(partes)


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

    # A configuração será utilizada nas novas movimentações.
    # O campo começa opcional para permitir a migração segura
    # das movimentações que já existem no sistema.
    configuracao = models.ForeignKey(
        ConfiguracaoEstoque,
        on_delete=models.PROTECT,
        related_name="movimentacoes",
        null=True,
        blank=True
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
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


class ConfiguracaoEstoque(models.Model):
    """
    Características específicas de uma determinada configuração
    de um produto.

    Os campos são opcionais para permitir que o sistema trabalhe
    com eletrônicos, móveis, talheres, equipamentos e outros tipos
    de materiais.

    Exemplos:

    iPad:
        Marca: Apple
        Modelo: A2602
        Capacidade: 64 GB
        RAM: 4 GB
        Condição: Novo

    Mesa:
        Marca: -
        Modelo: -
        Material: Madeira
        Cor: Marrom
        Dimensões: 1,20 m x 0,60 m
        Condição: Usado

    Talher:
        Material: Aço inox
        Cor: Prata
        Dimensões: 20 cm
        Condição: Novo
    """

    produto = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT,
        related_name="configuracoes"
    )

    descricao = models.TextField(
        blank=True
    )

    marca = models.CharField(
        max_length=100,
        blank=True
    )

    modelo = models.CharField(
        max_length=150,
        blank=True
    )

    material = models.CharField(
        max_length=150,
        blank=True
    )

    cor = models.CharField(
        max_length=100,
        blank=True
    )

    dimensoes = models.CharField(
        max_length=200,
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
            "marca",
            "modelo",
            "capacidade",
            "memoria_ram",
            "condicao",
        ]

    def __str__(self):
        partes = [self.produto.nome]

        if self.marca:
            partes.append(self.marca)

        if self.modelo:
            partes.append(self.modelo)

        if self.capacidade:
            partes.append(self.capacidade)

        if self.memoria_ram:
            partes.append(self.memoria_ram)

        if self.material:
            partes.append(self.material)

        if self.cor:
            partes.append(self.cor)

        if self.dimensoes:
            partes.append(self.dimensoes)

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
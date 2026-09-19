from django.core.exceptions import ValidationError
from django.db import transaction

from .models import (
    Produto,
    ConfiguracaoEstoque,
    Movimentacao,
)


@transaction.atomic
def registrar_entrada(
    produto,
    quantidade,
    usuario,
    descricao="",
    marca="",
    modelo="",
    material="",
    cor="",
    dimensoes="",
    capacidade="",
    memoria_ram="",
    condicao="",
    origem="",
    documento_origem="",
    ativo=True,
    observacao="",
):
    if quantidade <= 0:
        raise ValidationError(
            "A quantidade deve ser maior que zero."
        )

    produto = (
        Produto.objects
        .select_for_update()
        .get(pk=produto.pk)
    )

    configuracao, criada = (
        ConfiguracaoEstoque.objects.get_or_create(
            produto=produto,
            descricao=descricao,
            marca=marca,
            modelo=modelo,
            material=material,
            cor=cor,
            dimensoes=dimensoes,
            capacidade=capacidade,
            memoria_ram=memoria_ram,
            condicao=condicao,
            origem=origem,
            documento_origem=documento_origem,
            defaults={
                "quantidade": 0,
                "observacao": observacao,
                "ativo": ativo,
            },
        )
    )

    configuracao.quantidade += quantidade

    if observacao:
        configuracao.observacao = observacao

    configuracao.ativo = ativo

    configuracao.save()

    produto.estoque_atual += quantidade

    produto.save(
        update_fields=[
            "estoque_atual",
            "atualizado_em",
        ]
    )

    movimentacao = Movimentacao.objects.create(
        produto=produto,
        configuracao=configuracao,
        tipo="E",
        quantidade=quantidade,
        usuario=usuario,
        observacao=observacao,
    )

    return movimentacao, criada


@transaction.atomic
def registrar_saida(
    produto,
    quantidade,
    usuario,
    destino,
    configuracao=None,
    observacao="",
):
    if quantidade <= 0:
        raise ValidationError(
            "A quantidade deve ser maior que zero."
        )

    produto = (
        Produto.objects
        .select_for_update()
        .get(pk=produto.pk)
    )

    if configuracao is None:
        raise ValidationError(
            "É necessário informar a configuração do produto."
        )

    if configuracao.produto_id != produto.id:
        raise ValidationError(
            "A configuração selecionada não pertence ao produto."
        )

    configuracao = (
        ConfiguracaoEstoque.objects
        .select_for_update()
        .get(pk=configuracao.pk)
    )

    if not configuracao.ativo:
        raise ValidationError(
            "A configuração selecionada está inativa."
        )

    if quantidade > configuracao.quantidade:
        raise ValidationError(
            "A quantidade solicitada é maior que o estoque "
            "disponível para esta configuração."
        )

    if quantidade > produto.estoque_atual:
        raise ValidationError(
            "A quantidade solicitada é maior que o estoque "
            "total disponível do produto."
        )

    configuracao.quantidade -= quantidade

    configuracao.save(
        update_fields=[
            "quantidade",
            "atualizado_em",
        ]
    )

    produto.estoque_atual -= quantidade

    produto.save(
        update_fields=[
            "estoque_atual",
            "atualizado_em",
        ]
    )

    movimentacao = Movimentacao.objects.create(
        produto=produto,
        configuracao=configuracao,
        destino=destino,
        tipo="S",
        quantidade=quantidade,
        usuario=usuario,
        observacao=observacao,
    )

    return movimentacao


@transaction.atomic
def ajustar_estoque(
    configuracao,
    nova_quantidade,
    usuario,
    observacao="",
):
    """
    Ajusta diretamente a quantidade de uma configuração,
    atualiza o estoque total do produto e registra uma
    movimentação do tipo A (ajuste).
    """

    if nova_quantidade < 0:
        raise ValidationError(
            "A nova quantidade não pode ser negativa."
        )

    configuracao = (
        ConfiguracaoEstoque.objects
        .select_for_update()
        .select_related("produto")
        .get(pk=configuracao.pk)
    )

    produto = (
        Produto.objects
        .select_for_update()
        .get(pk=configuracao.produto_id)
    )

    quantidade_anterior = configuracao.quantidade

    if nova_quantidade == quantidade_anterior:
        raise ValidationError(
            "A nova quantidade é igual à quantidade atual. "
            "Nenhum ajuste é necessário."
        )

    diferenca = (
        nova_quantidade - quantidade_anterior
    )

    novo_estoque_produto = (
        produto.estoque_atual + diferenca
    )

    if novo_estoque_produto < 0:
        raise ValidationError(
            "O ajuste desta configuração faria o estoque "
            "total do produto ficar negativo."
        )

    configuracao.quantidade = nova_quantidade

    configuracao.save(
        update_fields=[
            "quantidade",
            "atualizado_em",
        ]
    )

    produto.estoque_atual = novo_estoque_produto

    produto.save(
        update_fields=[
            "estoque_atual",
            "atualizado_em",
        ]
    )

    observacao_final = (
        f"Ajuste de estoque: "
        f"{quantidade_anterior} -> {nova_quantidade}."
    )

    if observacao:
        observacao_final += (
            f" Motivo: {observacao.strip()}"
        )

    movimentacao = Movimentacao.objects.create(
        produto=produto,
        configuracao=configuracao,
        tipo="A",
        quantidade=abs(diferenca),
        usuario=usuario,
        observacao=observacao_final,
    )

    return movimentacao


@transaction.atomic
def reverter_movimentacao(
    movimentacao_id,
    usuario,
):
    movimentacao = (
        Movimentacao.objects
        .select_for_update()
        .select_related(
            "produto",
            "configuracao",
            "destino",
        )
        .get(pk=movimentacao_id)
    )

    produto = (
        Produto.objects
        .select_for_update()
        .get(pk=movimentacao.produto_id)
    )

    configuracao = None

    if movimentacao.configuracao_id:
        configuracao = (
            ConfiguracaoEstoque.objects
            .select_for_update()
            .get(
                pk=movimentacao.configuracao_id
            )
        )

    quantidade = movimentacao.quantidade

    if quantidade <= 0:
        raise ValidationError(
            "A movimentação possui uma quantidade inválida."
        )

    if movimentacao.tipo == "E":

        if produto.estoque_atual < quantidade:
            raise ValidationError(
                "Não é possível excluir esta entrada porque "
                "o estoque atual do produto é menor que a "
                "quantidade da movimentação."
            )

        if configuracao is not None:

            if configuracao.quantidade < quantidade:
                raise ValidationError(
                    "Não é possível excluir esta entrada porque "
                    "a quantidade atual da configuração é menor "
                    "que a quantidade registrada na entrada."
                )

            configuracao.quantidade -= quantidade

            configuracao.save(
                update_fields=[
                    "quantidade",
                    "atualizado_em",
                ]
            )

        produto.estoque_atual -= quantidade

        produto.save(
            update_fields=[
                "estoque_atual",
                "atualizado_em",
            ]
        )

    elif movimentacao.tipo == "S":

        produto.estoque_atual += quantidade

        produto.save(
            update_fields=[
                "estoque_atual",
                "atualizado_em",
            ]
        )

        if configuracao is not None:

            configuracao.quantidade += quantidade
            configuracao.ativo = True

            configuracao.save(
                update_fields=[
                    "quantidade",
                    "ativo",
                    "atualizado_em",
                ]
            )

    elif movimentacao.tipo == "A":

        raise ValidationError(
            "Movimentações de ajuste ainda não podem ser "
            "excluídas por esta rotina."
        )

    else:

        raise ValidationError(
            "Tipo de movimentação desconhecido."
        )

    movimentacao.delete()

    return True
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
    observacao="",
):
    """
    Registra uma entrada de estoque.

    A entrada atualiza:
        1. ConfiguracaoEstoque
        2. Produto.estoque_atual
        3. Movimentacao

    Tudo ocorre dentro de uma única transação.

    A configuração é identificada pela combinação das
    características informadas. Isso permite que o sistema
    diferencie, por exemplo:

        Mesa - Madeira - Marrom - 1,20 m x 0,60 m

    de:

        Mesa - Madeira - Branca - 1,80 m x 0,80 m

    e também:

        iPad - Apple - A2602 - 64 GB - 4 GB RAM
    """

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
                "ativo": True,
            },
        )
    )

    configuracao.quantidade += quantidade

    if observacao:
        configuracao.observacao = observacao

    configuracao.ativo = True

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
    """
    Registra uma saída de estoque.

    Para novas saídas, a configuração é obrigatória.

    A saída atualiza:
        1. ConfiguracaoEstoque
        2. Produto.estoque_atual
        3. Movimentacao
    """

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

    if configuracao.quantidade == 0:
        configuracao.ativo = True

    configuracao.save(
        update_fields=[
            "quantidade",
            "ativo",
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
def reverter_movimentacao(
    movimentacao_id,
    usuario,
):
    """
    Reverte uma movimentação existente e depois a exclui.

    Entrada:
        devolve o estoque ao estado anterior.

    Saída:
        devolve os itens ao estoque.

    A operação é atômica para evitar que o histórico
    seja apagado sem a reversão correspondente.
    """

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

    # ========================================================
    # REVERSÃO DE ENTRADA
    # ========================================================

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

    # ========================================================
    # REVERSÃO DE SAÍDA
    # ========================================================

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

    # ========================================================
    # AJUSTE
    # ========================================================

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
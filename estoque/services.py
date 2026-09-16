from django.db import transaction
from django.core.exceptions import ValidationError

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
    capacidade="",
    memoria_ram="",
    condicao="",
    origem="",
    documento_origem="",
    observacao="",
):
    if quantidade <= 0:
        raise ValidationError(
            "A quantidade deve ser maior que zero."
        )

    configuracao, criada = (
        ConfiguracaoEstoque.objects.get_or_create(
            produto=produto,
            descricao=descricao,
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

    return movimentacao


@transaction.atomic
def registrar_saida(
    produto,
    quantidade,
    usuario,
    destino,
    observacao="",
):
    if quantidade <= 0:
        raise ValidationError(
            "A quantidade deve ser maior que zero."
        )

    if quantidade > produto.estoque_atual:
        raise ValidationError(
            "Estoque insuficiente."
        )

    produto.estoque_atual -= quantidade

    produto.save(
        update_fields=[
            "estoque_atual",
            "atualizado_em",
        ]
    )

    return Movimentacao.objects.create(
        produto=produto,
        tipo="S",
        quantidade=quantidade,
        destino=destino,
        usuario=usuario,
        observacao=observacao,
    )
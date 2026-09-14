from django.db import transaction
from django.core.exceptions import ValidationError

from .models import Produto, Movimentacao


@transaction.atomic
def registrar_entrada(
    produto,
    quantidade,
    usuario,
    observacao=""
):
    if quantidade <= 0:
        raise ValidationError(
            "A quantidade deve ser maior que zero."
        )

    produto.estoque_atual += quantidade

    produto.save(
        update_fields=["estoque_atual"]
    )

    return Movimentacao.objects.create(
        produto=produto,
        tipo=Movimentacao.Tipo.ENTRADA,
        quantidade=quantidade,
        usuario=usuario,
        observacao=observacao,
    )


@transaction.atomic
def registrar_saida(
    produto,
    quantidade,
    usuario,
    destino,
    observacao=""
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
        update_fields=["estoque_atual"]
    )

    return Movimentacao.objects.create(
        produto=produto,
        tipo=Movimentacao.Tipo.SAIDA,
        quantidade=quantidade,
        destino=destino,
        usuario=usuario,
        observacao=observacao,
    )
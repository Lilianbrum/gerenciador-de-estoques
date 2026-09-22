from django.db import transaction
from django.db.models import Sum
from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from core.models import (
    Categoria,
    Destino,
    Estoque,
    Movimentacao,
    Produto,
    SaldoEstoque,
)

from .serializers import (
    CategoriaSerializer,
    DestinoSerializer,
    EstoqueSerializer,
    MovimentacaoSerializer,
    ProdutoSerializer,
    SaldoEstoqueSerializer,
)


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all().order_by("nome")
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticated]


class EstoqueViewSet(viewsets.ModelViewSet):
    queryset = Estoque.objects.all().order_by("nome")
    serializer_class = EstoqueSerializer
    permission_classes = [IsAuthenticated]


class DestinoViewSet(viewsets.ModelViewSet):
    queryset = Destino.objects.all().order_by("nome")
    serializer_class = DestinoSerializer
    permission_classes = [IsAuthenticated]


class ProdutoViewSet(viewsets.ModelViewSet):
    queryset = (
        Produto.objects
        .select_related("categoria")
        .prefetch_related("saldos__estoque")
        .all()
        .order_by("nome")
    )
    serializer_class = ProdutoSerializer

    # Mantido público durante a integração com o frontend React.
    permission_classes = []


class SaldoEstoqueViewSet(viewsets.ModelViewSet):
    queryset = (
        SaldoEstoque.objects
        .select_related("produto", "estoque")
        .all()
        .order_by("produto__nome", "estoque__nome")
    )
    serializer_class = SaldoEstoqueSerializer
    permission_classes = [IsAuthenticated]


    permission_classes = []
    queryset = (
        Movimentacao.objects
        .select_related("produto", "estoque", "destino", "usuario")
        .all()
        .order_by("-criado_em", "-id")
    )
    serializer_class = MovimentacaoSerializer
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        dados = serializer.validated_data

        produto = dados["produto"]
        estoque = dados["estoque"]
        tipo = dados["tipo"]
        quantidade = dados["quantidade"]

        if produto.empresa_id != estoque.empresa_id:
            raise ValidationError({
                "estoque": (
                    "O estoque selecionado pertence a uma instituição "
                    "diferente da instituição do produto."
                )
            })

        destino = dados.get("destino")

        if destino and destino.empresa_id != produto.empresa_id:
            raise ValidationError({
                "destino": (
                    "O destinatário selecionado pertence a uma instituição "
                    "diferente da instituição do produto."
                )
            })

        saldo, _ = (
            SaldoEstoque.objects
            .select_for_update()
            .get_or_create(
                produto=produto,
                estoque=estoque,
                defaults={"quantidade": 0},
            )
        )

        if tipo == Movimentacao.Tipo.ENTRADA:
            saldo.quantidade += quantidade

        elif tipo == Movimentacao.Tipo.SAIDA:
            if saldo.quantidade < quantidade:
                raise ValidationError({
                    "quantidade": (
                        f"Estoque insuficiente. "
                        f"Saldo disponível: {saldo.quantidade}."
                    )
                })

            saldo.quantidade -= quantidade

        else:
            raise ValidationError({
                "tipo": "Tipo de movimentação inválido."
            })

        saldo.save(
            update_fields=[
                "quantidade",
                "atualizado_em",
            ]
        )

        movimentacao = serializer.save(
            empresa=produto.empresa,
            usuario=request.user,
        )

        resposta = self.get_serializer(movimentacao)

        return Response(
            resposta.data,
            status=status.HTTP_201_CREATED,
        )


@api_view(["GET"])
@permission_classes([])
def dashboard_api(request):
    """
    Dados públicos de leitura usados pelo Dashboard React
    durante a integração do frontend.
    """

    distribuicao = []

    estoques = (
        Estoque.objects
        .filter(ativo=True)
        .order_by("nome")
    )

    for estoque in estoques:
        quantidade = (
            SaldoEstoque.objects
            .filter(estoque=estoque)
            .aggregate(total=Sum("quantidade"))
            ["total"]
            or 0
        )

        distribuicao.append({
            "id": estoque.id,
            "nome": estoque.nome,
            "localizacao": estoque.localizacao,
            "quantidade": quantidade,
        })

    return Response({
        "classes": Categoria.objects.filter(ativo=True).count(),
        "produtos": Produto.objects.filter(ativo=True).count(),
        "unidades": Estoque.objects.filter(ativo=True).count(),
        "setores": Destino.objects.filter(ativo=True).count(),
        "estoque_total": (
            SaldoEstoque.objects.aggregate(
                total=Sum("quantidade")
            )["total"]
            or 0
        ),
        "distribuicao_por_unidade": distribuicao,
    })

class MovimentacaoViewSet(viewsets.ModelViewSet):
    queryset = (Movimentacao.objects.select_related("produto", "estoque", "destino", "usuario").all().order_by("-criado_em", "-id"))
    serializer_class = MovimentacaoSerializer
    permission_classes = []

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dados = serializer.validated_data
        produto = dados["produto"]
        estoque = dados["estoque"]
        tipo = dados["tipo"]
        quantidade = dados["quantidade"]

        if produto.empresa_id != estoque.empresa_id:
            raise ValidationError({"estoque": "O estoque selecionado pertence a uma instituição diferente da instituição do produto."})

        destino = dados.get("destino")
        if destino and destino.empresa_id != produto.empresa_id:
            raise ValidationError({"destino": "O destinatário selecionado pertence a uma instituição diferente da instituição do produto."})

        saldo, _ = SaldoEstoque.objects.select_for_update().get_or_create(produto=produto, estoque=estoque, defaults={"quantidade": 0})

        if tipo == Movimentacao.Tipo.ENTRADA:
            saldo.quantidade += quantidade
        elif tipo == Movimentacao.Tipo.SAIDA:
            if saldo.quantidade < quantidade:
                raise ValidationError({"quantidade": f"Estoque insuficiente. Saldo disponível: {saldo.quantidade}."})
            saldo.quantidade -= quantidade
        else:
            raise ValidationError({"tipo": "Tipo de movimentação inválido."})

        saldo.save(update_fields=["quantidade", "atualizado_em"])
        movimentacao = serializer.save(empresa=produto.empresa, usuario=request.user if request.user.is_authenticated else None)
        resposta = self.get_serializer(movimentacao)
        return Response(resposta.data, status=status.HTTP_201_CREATED)

from django.http import JsonResponse

from .models import (
    Categoria,
    Destino,
    Estoque,
    Fornecedor,
    Produto,
)


def _empresa_do_usuario(request):
    """
    Retorna a empresa/instituição vinculada ao usuário.
    Se o usuário não possuir empresa, retorna None.
    """
    return getattr(request.user, "empresa", None)


def _resultado(queryset, campo_id="id", campo_nome="nome"):
    return [
        {
            "id": item.get(campo_id),
            "text": item.get(campo_nome),
        }
        for item in queryset
    ]


def fornecedor_por_empresa(request):
    empresa = _empresa_do_usuario(request)
    busca = request.GET.get("term", "").strip()

    queryset = Fornecedor.objects.filter(ativo=True)

    if empresa is not None and hasattr(Fornecedor, "empresa"):
        queryset = queryset.filter(empresa=empresa)

    if busca:
        queryset = queryset.filter(nome__icontains=busca)

    queryset = queryset.order_by("nome")[:50]

    return JsonResponse(
        {
            "results": _resultado(
                queryset.values("id", "nome")
            )
        }
    )


def marca_por_empresa(request):
    """
    Retorna marcas disponíveis.

    Nesta adaptação, marca é tratada como campo de texto do produto,
    e não como uma tabela comercial separada.
    """
    empresa = _empresa_do_usuario(request)
    busca = request.GET.get("term", "").strip()

    queryset = Produto.objects.filter(
        ativo=True
    )

    if empresa is not None and hasattr(Produto, "empresa"):
        queryset = queryset.filter(empresa=empresa)

    if busca:
        queryset = queryset.filter(
            marca__icontains=busca
        )

    valores = (
        queryset
        .exclude(marca__isnull=True)
        .exclude(marca="")
        .values_list("marca", flat=True)
        .distinct()
        .order_by("marca")[:50]
    )

    return JsonResponse(
        {
            "results": [
                {
                    "id": marca,
                    "text": marca,
                }
                for marca in valores
            ]
        }
    )


def tipo_por_empresa(request):
    """
    Retorna tipos de produto cadastrados.
    O tipo de produto é texto livre no cadastro do produto.
    """
    empresa = _empresa_do_usuario(request)
    busca = request.GET.get("term", "").strip()

    queryset = Produto.objects.filter(
        ativo=True
    )

    if empresa is not None and hasattr(Produto, "empresa"):
        queryset = queryset.filter(empresa=empresa)

    if busca:
        queryset = queryset.filter(
            tipo_produto__icontains=busca
        )

    valores = (
        queryset
        .exclude(tipo_produto__isnull=True)
        .exclude(tipo_produto="")
        .values_list("tipo_produto", flat=True)
        .distinct()
        .order_by("tipo_produto")[:50]
    )

    return JsonResponse(
        {
            "results": [
                {
                    "id": tipo,
                    "text": tipo,
                }
                for tipo in valores
            ]
        }
    )


def produto_por_empresa(request):
    empresa = _empresa_do_usuario(request)
    busca = request.GET.get("term", "").strip()

    queryset = Produto.objects.filter(
        ativo=True
    )

    if empresa is not None and hasattr(Produto, "empresa"):
        queryset = queryset.filter(empresa=empresa)

    if busca:
        from django.db.models import Q

        queryset = queryset.filter(
            Q(nome__icontains=busca)
            | Q(codigo__icontains=busca)
            | Q(marca__icontains=busca)
            | Q(modelo__icontains=busca)
        )

    queryset = queryset.order_by("nome")[:50]

    return JsonResponse(
        {
            "results": [
                {
                    "id": produto.id,
                    "text": str(produto),
                }
                for produto in queryset
            ]
        }
    )


def categoria_por_empresa(request):
    empresa = _empresa_do_usuario(request)
    busca = request.GET.get("term", "").strip()

    queryset = Categoria.objects.filter(
        ativo=True
    )

    if empresa is not None and hasattr(Categoria, "empresa"):
        queryset = queryset.filter(empresa=empresa)

    if busca:
        queryset = queryset.filter(
            nome__icontains=busca
        )

    queryset = queryset.order_by("nome")[:50]

    return JsonResponse(
        {
            "results": _resultado(
                queryset.values("id", "nome")
            )
        }
    )


def estoque_por_empresa(request):
    empresa = _empresa_do_usuario(request)
    busca = request.GET.get("term", "").strip()

    queryset = Estoque.objects.filter(
        ativo=True
    )

    if empresa is not None and hasattr(Estoque, "empresa"):
        queryset = queryset.filter(empresa=empresa)

    if busca:
        queryset = queryset.filter(
            nome__icontains=busca
        )

    queryset = queryset.order_by("nome")[:50]

    return JsonResponse(
        {
            "results": _resultado(
                queryset.values("id", "nome")
            )
        }
    )


def destino_por_empresa(request):
    empresa = _empresa_do_usuario(request)
    busca = request.GET.get("term", "").strip()

    queryset = Destino.objects.filter(
        ativo=True
    )

    if empresa is not None and hasattr(Destino, "empresa"):
        queryset = queryset.filter(empresa=empresa)

    if busca:
        queryset = queryset.filter(
            nome__icontains=busca
        )

    queryset = queryset.order_by("nome")[:50]

    return JsonResponse(
        {
            "results": _resultado(
                queryset.values("id", "nome")
            )
        }
    )
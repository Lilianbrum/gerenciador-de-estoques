from datetime import datetime, timedelta
from collections import defaultdict

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone

from .forms import (
    EntradaEstoqueForm,
    SaidaEstoqueForm,
    ProdutoForm,
    CategoriaForm,
    DestinoForm,
)

from .models import (
    Produto,
    Categoria,
    Destino,
    Movimentacao,
)


# ============================================================
# DASHBOARD
# ============================================================

@login_required
def dashboard(request):

    produtos_ativos_qs = Produto.objects.filter(
        ativo=True
    )

    total_produtos = produtos_ativos_qs.count()

    quantidade_total = (
        produtos_ativos_qs.aggregate(
            total=models.Sum("estoque_atual")
        )["total"]
        or 0
    )

    produtos_estoque_baixo = produtos_ativos_qs.filter(
        estoque_atual__lte=models.F("estoque_minimo")
    ).count()

    total_itens_distribuidos = (
        Movimentacao.objects
        .filter(tipo="S")
        .aggregate(
            total=models.Sum("quantidade")
        )["total"]
        or 0
    )

    ultimas_movimentacoes = (
        Movimentacao.objects
        .select_related(
            "produto",
            "destino",
            "usuario"
        )
        .order_by("-criado_em")[:10]
    )

    hoje = timezone.localdate()

    meses = []

    for i in range(5, -1, -1):

        primeiro_dia = (
            hoje.replace(day=1)
            - timedelta(days=31 * i)
        ).replace(day=1)

        if primeiro_dia.month == 12:
            proximo_mes = primeiro_dia.replace(
                year=primeiro_dia.year + 1,
                month=1,
                day=1
            )
        else:
            proximo_mes = primeiro_dia.replace(
                month=primeiro_dia.month + 1,
                day=1
            )

        ultimo_dia = proximo_mes - timedelta(days=1)

        entradas = (
            Movimentacao.objects
            .filter(
                tipo="E",
                criado_em__date__gte=primeiro_dia,
                criado_em__date__lte=ultimo_dia,
            )
            .aggregate(
                total=models.Sum("quantidade")
            )["total"]
            or 0
        )

        saidas = (
            Movimentacao.objects
            .filter(
                tipo="S",
                criado_em__date__gte=primeiro_dia,
                criado_em__date__lte=ultimo_dia,
            )
            .aggregate(
                total=models.Sum("quantidade")
            )["total"]
            or 0
        )

        meses.append({
            "label": primeiro_dia.strftime("%m/%Y"),
            "entradas": entradas,
            "saidas": saidas,
        })

    estoque_por_categoria = defaultdict(int)

    produtos_com_categoria = (
        Produto.objects
        .filter(ativo=True)
        .select_related("categoria")
    )

    for produto in produtos_com_categoria:

        estoque_por_categoria[
            produto.categoria.nome
        ] += produto.estoque_atual

    estoque_categoria_lista = [
        {
            "categoria": categoria,
            "quantidade": quantidade,
        }
        for categoria, quantidade
        in sorted(
            estoque_por_categoria.items()
        )
    ]

    produtos_maior_estoque = (
        Produto.objects
        .filter(ativo=True)
        .select_related("categoria")
        .order_by("-estoque_atual", "nome")[:10]
    )

    distribuicoes_por_destino = defaultdict(int)

    saidas_destinos = (
        Movimentacao.objects
        .filter(
            tipo="S",
            destino__isnull=False
        )
        .select_related("destino")
    )

    for movimentacao in saidas_destinos:

        distribuicoes_por_destino[
            movimentacao.destino.nome
        ] += movimentacao.quantidade

    distribuicoes_destino_lista = [
        {
            "destino": destino,
            "quantidade": quantidade,
        }
        for destino, quantidade
        in sorted(
            distribuicoes_por_destino.items(),
            key=lambda item: item[1],
            reverse=True
        )
    ]

    produtos_baixo_estoque = (
        Produto.objects
        .filter(
            ativo=True,
            estoque_atual__lte=models.F("estoque_minimo")
        )
        .select_related("categoria")
        .order_by(
            "estoque_atual",
            "nome"
        )[:10]
    )

    context = {
        "total_produtos": total_produtos,
        "quantidade_total": quantidade_total,
        "produtos_estoque_baixo": produtos_estoque_baixo,
        "total_itens_distribuidos": total_itens_distribuidos,
        "ultimas_movimentacoes": ultimas_movimentacoes,
        "meses": meses,
        "estoque_categoria_lista": estoque_categoria_lista,
        "produtos_maior_estoque": produtos_maior_estoque,
        "distribuicoes_destino_lista": distribuicoes_destino_lista,
        "produtos_baixo_estoque": produtos_baixo_estoque,
    }

    return render(
        request,
        "estoque/dashboard.html",
        context
    )


# ============================================================
# PRODUTOS
# ============================================================

@login_required
def produtos(request):

    produtos_qs = (
        Produto.objects
        .select_related("categoria")
        .all()
        .order_by("nome")
    )

    busca = request.GET.get(
        "q",
        ""
    ).strip()

    categoria_id = request.GET.get(
        "categoria",
        ""
    ).strip()

    tipo = request.GET.get(
        "tipo",
        ""
    ).strip()

    condicao = request.GET.get(
        "condicao",
        ""
    ).strip()

    if busca:

        produtos_qs = produtos_qs.filter(
            models.Q(nome__icontains=busca)
            |
            models.Q(codigo__icontains=busca)
            |
            models.Q(descricao__icontains=busca)
        )

    if categoria_id:

        produtos_qs = produtos_qs.filter(
            categoria_id=categoria_id
        )

    if tipo:

        produtos_qs = produtos_qs.filter(
            tipo_produto__iexact=tipo
        )

    if condicao:

        produtos_qs = produtos_qs.filter(
            condicao=condicao
        )

    quantidade_total = (
        produtos_qs.aggregate(
            total=models.Sum("estoque_atual")
        )["total"]
        or 0
    )

    produtos_estoque_baixo = produtos_qs.filter(
        estoque_atual__lte=models.F("estoque_minimo")
    ).count()

    produtos_ativos = produtos_qs.filter(
        ativo=True
    ).count()

    categorias_lista = (
        Categoria.objects
        .order_by("nome")
    )

    tipos_lista = (
        Produto.objects
        .exclude(tipo_produto="")
        .values_list(
            "tipo_produto",
            flat=True
        )
        .distinct()
        .order_by("tipo_produto")
    )

    # ========================================================
    # CONDIÇÕES
    # Não usamos Produto.Condicao para evitar dependência
    # de uma classe interna que pode não existir no modelo.
    # Os valores correspondem aos valores atualmente usados
    # pelo campo condicao.
    # ========================================================

    condicoes = [
        ("NOVO", "Novo"),
        ("USADO", "Usado"),
        ("LACRADO", "Lacrado"),
    ]

    context = {
        "produtos": produtos_qs,

        "categorias": categorias_lista,

        "tipos": tipos_lista,

        "condicoes": condicoes,

        "quantidade_total": quantidade_total,

        "produtos_estoque_baixo": produtos_estoque_baixo,

        "produtos_ativos": produtos_ativos,

        "q": busca,

        "categoria_selecionada": categoria_id,

        "tipo_selecionado": tipo,

        "condicao_selecionada": condicao,
    }

    return render(
        request,
        "estoque/produtos.html",
        context
    )


# ============================================================
# NOVO PRODUTO
# ============================================================

@login_required
def novo_produto(request):

    if request.method == "POST":

        form = ProdutoForm(
            request.POST
        )

        if form.is_valid():

            produto = form.save()

            messages.success(
                request,
                f'Produto "{produto.nome}" cadastrado com sucesso.'
            )

            return redirect("produtos")

    else:

        form = ProdutoForm()

    return render(
        request,
        "estoque/novo_produto.html",
        {
            "form": form
        }
    )


# ============================================================
# EDITAR PRODUTO
# ============================================================

@login_required
def editar_produto(
    request,
    produto_id
):

    produto = get_object_or_404(
        Produto,
        id=produto_id
    )

    if request.method == "POST":

        form = ProdutoForm(
            request.POST,
            instance=produto
        )

        if form.is_valid():

            produto = form.save()

            messages.success(
                request,
                f'Produto "{produto.nome}" atualizado com sucesso.'
            )

            return redirect("produtos")

    else:

        form = ProdutoForm(
            instance=produto
        )

    return render(
        request,
        "estoque/editar_produto.html",
        {
            "form": form,
            "produto": produto,
        }
    )


# ============================================================
# CATEGORIAS
# ============================================================

@login_required
def categorias(request):

    if request.method == "POST":

        form = CategoriaForm(
            request.POST
        )

        if form.is_valid():

            categoria = form.save()

            messages.success(
                request,
                f'Categoria "{categoria.nome}" criada com sucesso.'
            )

            return redirect("categorias")

    else:

        form = CategoriaForm()

    categorias_lista = (
        Categoria.objects
        .order_by("nome")
    )

    return render(
        request,
        "estoque/categorias.html",
        {
            "form": form,
            "categorias": categorias_lista,
        }
    )


# ============================================================
# ENTRADA DE ESTOQUE
# ============================================================

@login_required
def entrada_estoque(request):

    if request.method == "POST":

        form = EntradaEstoqueForm(
            request.POST
        )

        if form.is_valid():

            produto = form.cleaned_data[
                "produto"
            ]

            quantidade = form.cleaned_data[
                "quantidade"
            ]

            observacao = form.cleaned_data[
                "observacao"
            ]

            produto.estoque_atual += quantidade

            produto.save()

            Movimentacao.objects.create(
                produto=produto,
                tipo="E",
                quantidade=quantidade,
                observacao=observacao,
                usuario=request.user,
            )

            messages.success(
                request,
                f"Entrada de {quantidade} unidade(s) "
                f"de {produto.nome} registrada com sucesso."
            )

            return redirect(
                "entrada_estoque"
            )

    else:

        form = EntradaEstoqueForm()

    return render(
        request,
        "estoque/entrada.html",
        {
            "form": form
        }
    )


# ============================================================
# SAÍDA DE ESTOQUE
# ============================================================

@login_required
def saida_estoque(request):

    if request.method == "POST":

        form = SaidaEstoqueForm(
            request.POST
        )

        if form.is_valid():

            produto = form.cleaned_data[
                "produto"
            ]

            quantidade = form.cleaned_data[
                "quantidade"
            ]

            destino = form.cleaned_data[
                "destino"
            ]

            observacao = form.cleaned_data[
                "observacao"
            ]

            if quantidade > produto.estoque_atual:

                form.add_error(
                    "quantidade",
                    "A quantidade solicitada é maior "
                    "que o estoque disponível."
                )

            else:

                produto.estoque_atual -= quantidade

                produto.save()

                Movimentacao.objects.create(
                    produto=produto,
                    destino=destino,
                    tipo="S",
                    quantidade=quantidade,
                    observacao=observacao,
                    usuario=request.user,
                )

                messages.success(
                    request,
                    f"Saída de {quantidade} unidade(s) "
                    f"de {produto.nome} registrada "
                    f"para {destino.nome}."
                )

                return redirect(
                    "saida_estoque"
                )

    else:

        form = SaidaEstoqueForm()

    return render(
        request,
        "estoque/saida.html",
        {
            "form": form
        }
    )


# ============================================================
# HISTÓRICO
# ============================================================

@login_required
def historico_movimentacoes(request):

    movimentacoes = (
        Movimentacao.objects
        .select_related(
            "produto",
            "destino",
            "usuario"
        )
        .order_by("-criado_em")
    )

    tipo = request.GET.get(
        "tipo",
        ""
    ).strip()

    if tipo:

        movimentacoes = movimentacoes.filter(
            tipo=tipo
        )

    produto_id = request.GET.get(
        "produto",
        ""
    ).strip()

    if produto_id:

        movimentacoes = movimentacoes.filter(
            produto_id=produto_id
        )

    data_inicio = request.GET.get(
        "data_inicio",
        ""
    ).strip()

    if data_inicio:

        try:

            data_inicio_obj = datetime.strptime(
                data_inicio,
                "%Y-%m-%d"
            ).date()

            movimentacoes = movimentacoes.filter(
                criado_em__date__gte=data_inicio_obj
            )

        except ValueError:

            pass

    data_fim = request.GET.get(
        "data_fim",
        ""
    ).strip()

    if data_fim:

        try:

            data_fim_obj = datetime.strptime(
                data_fim,
                "%Y-%m-%d"
            ).date()

            movimentacoes = movimentacoes.filter(
                criado_em__date__lte=data_fim_obj
            )

        except ValueError:

            pass

    produtos_lista = (
        Produto.objects
        .order_by("nome")
    )

    context = {
        "movimentacoes": movimentacoes,

        "produtos": produtos_lista,

        "tipo_selecionado": tipo,

        "produto_selecionado": produto_id,

        "data_inicio": data_inicio,

        "data_fim": data_fim,
    }

    return render(
        request,
        "estoque/historico.html",
        context
    )


# ============================================================
# DESTINOS
# ============================================================

@login_required
def destinos(request):

    if request.method == "POST":

        form = DestinoForm(
            request.POST
        )

        if form.is_valid():

            destino = form.save()

            messages.success(
                request,
                f'Destino "{destino.nome}" criado com sucesso.'
            )

            return redirect("destinos")

    else:

        form = DestinoForm()

    destinos_lista = (
        Destino.objects
        .order_by("nome")
    )

    return render(
        request,
        "estoque/destinos.html",
        {
            "form": form,
            "destinos": destinos_lista,
        }
    )


# ============================================================
# EDITAR DESTINO
# ============================================================

@login_required
def editar_destino(
    request,
    destino_id
):

    destino = get_object_or_404(
        Destino,
        id=destino_id
    )

    if request.method == "POST":

        form = DestinoForm(
            request.POST,
            instance=destino
        )

        if form.is_valid():

            destino = form.save()

            messages.success(
                request,
                f'Destino "{destino.nome}" atualizado com sucesso.'
            )

            return redirect(
                "destinos"
            )

    else:

        form = DestinoForm(
            instance=destino
        )

    return render(
        request,
        "estoque/editar_destino.html",
        {
            "form": form,
            "destino": destino,
        }
    )


# ============================================================
# ATIVAR / DESATIVAR DESTINO
# ============================================================

@login_required
def alternar_destino(
    request,
    destino_id
):

    destino = get_object_or_404(
        Destino,
        id=destino_id
    )

    destino.ativo = not destino.ativo

    destino.save()

    if destino.ativo:

        messages.success(
            request,
            f'Destino "{destino.nome}" ativado.'
        )

    else:

        messages.warning(
            request,
            f'Destino "{destino.nome}" desativado.'
        )

    return redirect(
        "destinos"
    )


# ============================================================
# DISTRIBUIÇÕES
# ============================================================

@login_required
def distribuicoes(request):

    distribuicoes_qs = (
        Movimentacao.objects
        .filter(
            tipo="S"
        )
        .select_related(
            "produto",
            "destino",
            "usuario"
        )
        .order_by("-criado_em")
    )

    busca = request.GET.get(
        "q",
        ""
    ).strip()

    destino_id = request.GET.get(
        "destino",
        ""
    ).strip()

    produto_id = request.GET.get(
        "produto",
        ""
    ).strip()

    data_inicio = request.GET.get(
        "data_inicio",
        ""
    ).strip()

    data_fim = request.GET.get(
        "data_fim",
        ""
    ).strip()

    if busca:

        distribuicoes_qs = distribuicoes_qs.filter(
            models.Q(produto__nome__icontains=busca)
            |
            models.Q(produto__codigo__icontains=busca)
            |
            models.Q(destino__nome__icontains=busca)
            |
            models.Q(observacao__icontains=busca)
        )

    if destino_id:

        distribuicoes_qs = distribuicoes_qs.filter(
            destino_id=destino_id
        )

    if produto_id:

        distribuicoes_qs = distribuicoes_qs.filter(
            produto_id=produto_id
        )

    if data_inicio:

        try:

            data_inicio_obj = datetime.strptime(
                data_inicio,
                "%Y-%m-%d"
            ).date()

            distribuicoes_qs = distribuicoes_qs.filter(
                criado_em__date__gte=data_inicio_obj
            )

        except ValueError:

            pass

    if data_fim:

        try:

            data_fim_obj = datetime.strptime(
                data_fim,
                "%Y-%m-%d"
            ).date()

            distribuicoes_qs = distribuicoes_qs.filter(
                criado_em__date__lte=data_fim_obj
            )

        except ValueError:

            pass

    total_registros = distribuicoes_qs.count()

    total_itens = (
        distribuicoes_qs.aggregate(
            total=models.Sum("quantidade")
        )["total"]
        or 0
    )

    destinos_lista = (
        Destino.objects
        .filter(ativo=True)
        .order_by("nome")
    )

    produtos_lista = (
        Produto.objects
        .filter(ativo=True)
        .order_by("nome")
    )

    context = {
        "distribuicoes": distribuicoes_qs,

        "total_registros": total_registros,

        "total_itens": total_itens,

        "destinos": destinos_lista,

        "produtos": produtos_lista,

        "q": busca,

        "destino_selecionado": destino_id,

        "produto_selecionado": produto_id,

        "data_inicio": data_inicio,

        "data_fim": data_fim,
    }

    return render(
        request,
        "estoque/distribuicoes.html",
        context
    )

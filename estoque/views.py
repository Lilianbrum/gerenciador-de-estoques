from datetime import datetime, timedelta
from collections import defaultdict

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import models
from django.shortcuts import (
    redirect,
    render,
    get_object_or_404,
)
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
    ConfiguracaoEstoque,
)

from .services import (
    registrar_entrada,
    registrar_saida,
    reverter_movimentacao,
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
            "usuario",
            "configuracao",
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
        .order_by(
            "-estoque_atual",
            "nome"
        )[:10]
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

            try:

                movimentacao, criada = registrar_entrada(
                    produto=form.cleaned_data["produto"],
                    quantidade=form.cleaned_data["quantidade"],
                    usuario=request.user,
                    descricao=form.cleaned_data.get(
                        "descricao",
                        ""
                    ).strip(),
                    capacidade=form.cleaned_data.get(
                        "capacidade",
                        ""
                    ).strip(),
                    memoria_ram=form.cleaned_data.get(
                        "memoria_ram",
                        ""
                    ).strip(),
                    condicao=form.cleaned_data.get(
                        "condicao",
                        ""
                    ).strip(),
                    origem=form.cleaned_data.get(
                        "origem",
                        ""
                    ).strip(),
                    documento_origem=form.cleaned_data.get(
                        "documento_origem",
                        ""
                    ).strip(),
                    observacao=form.cleaned_data.get(
                        "observacao",
                        ""
                    ),
                )

                if criada:

                    mensagem = (
                        "Entrada registrada com sucesso. "
                        "Uma nova configuração de estoque "
                        "foi criada."
                    )

                else:

                    mensagem = (
                        "Entrada registrada com sucesso. "
                        "A configuração existente foi atualizada."
                    )

                messages.success(
                    request,
                    mensagem
                )

                return redirect(
                    "entrada_estoque"
                )

            except ValidationError as exc:

                form.add_error(
                    None,
                    exc.message
                    if hasattr(exc, "message")
                    else str(exc)
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

            try:

                registrar_saida(
                    produto=form.cleaned_data["produto"],
                    quantidade=form.cleaned_data["quantidade"],
                    usuario=request.user,
                    destino=form.cleaned_data["destino"],
                    configuracao=form.cleaned_data[
                        "configuracao"
                    ],
                    observacao=form.cleaned_data.get(
                        "observacao",
                        ""
                    ),
                )

                messages.success(
                    request,
                    "Saída de estoque registrada com sucesso."
                )

                return redirect(
                    "saida_estoque"
                )

            except ValidationError as exc:

                form.add_error(
                    None,
                    exc.message
                    if hasattr(exc, "message")
                    else str(exc)
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
            "usuario",
            "configuracao",
        )
        .order_by("-criado_em")
    )

    termo = request.GET.get(
        "q",
        ""
    ).strip()

    tipo = request.GET.get(
        "tipo",
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

    if termo:

        movimentacoes = movimentacoes.filter(
            models.Q(produto__nome__icontains=termo)
            |
            models.Q(produto__codigo__icontains=termo)
            |
            models.Q(destino__nome__icontains=termo)
            |
            models.Q(usuario__username__icontains=termo)
            |
            models.Q(observacao__icontains=termo)
            |
            models.Q(
                configuracao__capacidade__icontains=termo
            )
            |
            models.Q(
                configuracao__memoria_ram__icontains=termo
            )
            |
            models.Q(
                configuracao__condicao__icontains=termo
            )
        )

    if tipo:

        movimentacoes = movimentacoes.filter(
            tipo=tipo
        )

    if produto_id:

        movimentacoes = movimentacoes.filter(
            produto_id=produto_id
        )

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
        "termo": termo,
        "q": termo,
        "tipo": tipo,
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


@login_required
def excluir_movimentacao(
    request,
    movimentacao_id
):

    if request.method != "POST":

        messages.error(
            request,
            "A exclusão de movimentações deve ser realizada "
            "por uma solicitação POST."
        )

        return redirect(
            "historico_movimentacoes"
        )

    if not request.user.is_staff:

        messages.error(
            request,
            "Somente usuários autorizados podem excluir "
            "movimentações."
        )

        return redirect(
            "historico_movimentacoes"
        )

    movimentacao = get_object_or_404(
        Movimentacao,
        id=movimentacao_id
    )

    try:

        descricao = (
            f"{movimentacao.get_tipo_display() if hasattr(movimentacao, 'get_tipo_display') else movimentacao.tipo} "
            f"de {movimentacao.quantidade} unidade(s) "
            f"do produto {movimentacao.produto.nome}"
        )

        reverter_movimentacao(
            movimentacao_id=movimentacao_id,
            usuario=request.user,
        )

        messages.success(
            request,
            f"Movimentação removida e estoque revertido: "
            f"{descricao}."
        )

    except ValidationError as exc:

        mensagem = (
            exc.message
            if hasattr(exc, "message")
            else str(exc)
        )

        messages.error(
            request,
            mensagem
        )

    return redirect(
        "historico_movimentacoes"
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
            "usuario",
            "configuracao",
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
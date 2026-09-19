from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import models
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    AjusteEstoqueForm,
    CategoriaForm,
    DestinoForm,
    EntradaEstoqueForm,
    ProdutoForm,
    SaidaEstoqueForm,
)

from .models import (
    Categoria,
    ConfiguracaoEstoque,
    Destino,
    Movimentacao,
    Produto,
)

from .services import (
    ajustar_estoque as ajustar_estoque_service,
    registrar_entrada,
    registrar_saida,
    reverter_movimentacao,
)


@login_required
def dashboard(request):

    produtos = Produto.objects.all()

    total_produtos = produtos.count()

    produtos_ativos = produtos.filter(
        ativo=True
    ).count()

    produtos_inativos = produtos.filter(
        ativo=False
    ).count()

    quantidade_total = (
        produtos.aggregate(
            total=models.Sum("estoque_atual")
        )["total"]
        or 0
    )

    produtos_estoque_baixo = (
        produtos
        .filter(
            ativo=True,
            estoque_atual__lte=models.F("estoque_minimo"),
        )
        .select_related("categoria")
        .order_by(
            "estoque_atual",
            "nome",
        )
    )

    ultimas_movimentacoes = (
        Movimentacao.objects
        .select_related(
            "produto",
            "configuracao",
            "destino",
            "usuario",
        )
        .order_by("-criado_em")[:10]
    )

    hoje = datetime.now()

    nomes_meses = [
        "",
        "Jan",
        "Fev",
        "Mar",
        "Abr",
        "Mai",
        "Jun",
        "Jul",
        "Ago",
        "Set",
        "Out",
        "Nov",
        "Dez",
    ]

    meses = []

    for deslocamento in range(5, -1, -1):

        ano = hoje.year
        mes = hoje.month - deslocamento

        while mes <= 0:
            mes += 12
            ano -= 1

        primeiro_dia = datetime(
            ano,
            mes,
            1,
        )

        if mes == 12:
            proximo_mes = datetime(
                ano + 1,
                1,
                1,
            )
        else:
            proximo_mes = datetime(
                ano,
                mes + 1,
                1,
            )

        entradas = (
            Movimentacao.objects
            .filter(
                tipo="E",
                criado_em__gte=primeiro_dia,
                criado_em__lt=proximo_mes,
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
                criado_em__gte=primeiro_dia,
                criado_em__lt=proximo_mes,
            )
            .aggregate(
                total=models.Sum("quantidade")
            )["total"]
            or 0
        )

        meses.append(
            {
                "label": (
                    f"{nomes_meses[mes]}/{str(ano)[2:]}"
                ),
                "entradas": entradas,
                "saidas": saidas,
            }
        )

    estoque_categoria = (
        Categoria.objects
        .annotate(
            quantidade=models.Sum(
                "produtos__estoque_atual"
            )
        )
        .filter(
            quantidade__gt=0
        )
        .order_by(
            "-quantidade",
            "nome",
        )
    )

    estoque_categoria_lista = []

    for categoria in estoque_categoria:

        estoque_categoria_lista.append(
            {
                "categoria": categoria.nome,
                "quantidade": categoria.quantidade or 0,
            }
        )

    produtos_maior_estoque = (
        produtos
        .filter(
            ativo=True
        )
        .select_related(
            "categoria"
        )
        .order_by(
            "-estoque_atual",
            "nome",
        )[:10]
    )

    distribuicoes_destino = (
        Destino.objects
        .annotate(
            quantidade=models.Sum(
                "movimentacoes__quantidade",
                filter=models.Q(
                    movimentacoes__tipo="S"
                ),
            )
        )
        .filter(
            quantidade__gt=0
        )
        .order_by(
            "-quantidade",
            "nome",
        )
    )

    distribuicoes_destino_lista = []

    for destino in distribuicoes_destino:

        distribuicoes_destino_lista.append(
            {
                "destino": destino.nome,
                "quantidade": destino.quantidade or 0,
            }
        )

    contexto = {
        "total_produtos": total_produtos,
        "produtos_ativos": produtos_ativos,
        "produtos_inativos": produtos_inativos,
        "quantidade_total": quantidade_total,
        "produtos_estoque_baixo": produtos_estoque_baixo,
        "ultimas_movimentacoes": ultimas_movimentacoes,
        "meses": meses,
        "estoque_categoria_lista": estoque_categoria_lista,
        "produtos_maior_estoque": produtos_maior_estoque,
        "distribuicoes_destino_lista": (
            distribuicoes_destino_lista
        ),
    }

    return render(
        request,
        "estoque/dashboard.html",
        contexto,
    )


@login_required
def estoque(request):

    configuracoes = (
        ConfiguracaoEstoque.objects
        .select_related(
            "produto",
            "produto__categoria",
        )
        .annotate(
            total_entradas=models.Sum(
                "movimentacoes__quantidade",
                filter=models.Q(
                    movimentacoes__tipo="E"
                ),
            ),
            total_saidas=models.Sum(
                "movimentacoes__quantidade",
                filter=models.Q(
                    movimentacoes__tipo="S"
                ),
            ),
        )
        .order_by(
            "produto__nome",
            "marca",
            "modelo",
            "capacidade",
            "memoria_ram",
            "condicao",
        )
    )

    termo = request.GET.get(
        "q",
        "",
    ).strip()

    categoria_id = request.GET.get(
        "categoria",
        "",
    ).strip()

    condicao = request.GET.get(
        "condicao",
        "",
    ).strip()

    origem = request.GET.get(
        "origem",
        "",
    ).strip()

    documento = request.GET.get(
        "documento",
        "",
    ).strip()

    status = request.GET.get(
        "status",
        "",
    ).strip()

    if termo:

        configuracoes = configuracoes.filter(
            models.Q(produto__nome__icontains=termo)
            | models.Q(produto__codigo__icontains=termo)
            | models.Q(marca__icontains=termo)
            | models.Q(modelo__icontains=termo)
            | models.Q(capacidade__icontains=termo)
            | models.Q(memoria_ram__icontains=termo)
            | models.Q(material__icontains=termo)
            | models.Q(cor__icontains=termo)
            | models.Q(documento_origem__icontains=termo)
        )

    if categoria_id:

        configuracoes = configuracoes.filter(
            produto__categoria_id=categoria_id
        )

    if condicao:

        configuracoes = configuracoes.filter(
            condicao__iexact=condicao
        )

    if origem:

        configuracoes = configuracoes.filter(
            origem__iexact=origem
        )

    if documento:

        configuracoes = configuracoes.filter(
            documento_origem__icontains=documento
        )

    if status == "ativo":

        configuracoes = configuracoes.filter(
            ativo=True
        )

    elif status == "inativo":

        configuracoes = configuracoes.filter(
            ativo=False
        )

    categorias_lista = (
        Categoria.objects
        .order_by("nome")
    )

    condicoes_lista = (
        ConfiguracaoEstoque.objects
        .exclude(condicao="")
        .values_list(
            "condicao",
            flat=True,
        )
        .distinct()
        .order_by("condicao")
    )

    origens_lista = (
        ConfiguracaoEstoque.objects
        .exclude(origem="")
        .values_list(
            "origem",
            flat=True,
        )
        .distinct()
        .order_by("origem")
    )

    total_configuracoes = (
        configuracoes.count()
    )

    quantidade_em_estoque = (
        configuracoes.aggregate(
            total=models.Sum("quantidade")
        )["total"]
        or 0
    )

    configuracoes_com_estoque = (
        configuracoes
        .filter(
            quantidade__gt=0
        )
        .count()
    )

    configuracoes_sem_estoque = (
        configuracoes
        .filter(
            quantidade=0
        )
        .count()
    )

    contexto = {
        "configuracoes": configuracoes,
        "categorias": categorias_lista,
        "condicoes": condicoes_lista,
        "origens": origens_lista,

        "termo": termo,
        "categoria_selecionada": categoria_id,
        "condicao_selecionada": condicao,
        "origem_selecionada": origem,
        "documento_selecionado": documento,
        "status_selecionado": status,

        "total_configuracoes": total_configuracoes,
        "quantidade_em_estoque": quantidade_em_estoque,
        "configuracoes_com_estoque": configuracoes_com_estoque,
        "configuracoes_sem_estoque": configuracoes_sem_estoque,
    }

    return render(
        request,
        "estoque/estoque.html",
        contexto,
    )


@login_required
def detalhe_configuracao(request, configuracao_id):

    configuracao = get_object_or_404(
        ConfiguracaoEstoque.objects.select_related(
            "produto",
            "produto__categoria",
        ),
        pk=configuracao_id,
    )

    movimentacoes = (
        Movimentacao.objects
        .filter(
            configuracao=configuracao
        )
        .select_related(
            "produto",
            "destino",
            "usuario",
        )
        .order_by(
            "-criado_em"
        )
    )

    entradas = (
        movimentacoes
        .filter(tipo="E")
        .aggregate(
            total=models.Sum("quantidade")
        )["total"]
        or 0
    )

    saidas = (
        movimentacoes
        .filter(tipo="S")
        .aggregate(
            total=models.Sum("quantidade")
        )["total"]
        or 0
    )

    ajustes = (
        movimentacoes
        .filter(tipo="A")
        .aggregate(
            total=models.Sum("quantidade")
        )["total"]
        or 0
    )

    contexto = {
        "configuracao": configuracao,
        "movimentacoes": movimentacoes,
        "entradas": entradas,
        "saidas": saidas,
        "ajustes": ajustes,
        "saldo": configuracao.quantidade,
    }

    return render(
        request,
        "estoque/detalhe_configuracao.html",
        contexto,
    )


@login_required
def ajustar_estoque(request, configuracao_id):

    configuracao = get_object_or_404(
        ConfiguracaoEstoque.objects.select_related(
            "produto",
            "produto__categoria",
        ),
        pk=configuracao_id,
    )

    if request.method == "POST":

        form = AjusteEstoqueForm(
            request.POST
        )

        if form.is_valid():

            dados = form.cleaned_data

            try:

                movimentacao = ajustar_estoque_service(
                    configuracao=configuracao,
                    nova_quantidade=dados[
                        "nova_quantidade"
                    ],
                    usuario=request.user,
                    observacao=dados[
                        "observacao"
                    ],
                )

                messages.success(
                    request,
                    (
                        "Ajuste de estoque realizado com sucesso. "
                        "A alteração foi registrada no histórico."
                    ),
                )

                return redirect(
                    "detalhe_configuracao",
                    configuracao_id=movimentacao.configuracao_id,
                )

            except ValidationError as erro:

                mensagem = getattr(
                    erro,
                    "message",
                    None,
                )

                if mensagem is None:
                    mensagem = str(erro)

                form.add_error(
                    None,
                    mensagem,
                )

    else:

        form = AjusteEstoqueForm(
            initial={
                "nova_quantidade": configuracao.quantidade,
            }
        )

    return render(
        request,
        "estoque/ajustar_estoque.html",
        {
            "form": form,
            "configuracao": configuracao,
        },
    )


@login_required
def excluir_configuracao(request, configuracao_id):

    configuracao = get_object_or_404(
        ConfiguracaoEstoque.objects.select_related(
            "produto",
        ),
        pk=configuracao_id,
    )

    if request.method != "POST":

        messages.error(
            request,
            "Operação inválida.",
        )

        return redirect(
            "detalhe_configuracao",
            configuracao_id=configuracao.id,
        )

    if not request.user.is_staff:

        messages.error(
            request,
            "Somente usuários administradores podem excluir configurações de estoque.",
        )

        return redirect(
            "detalhe_configuracao",
            configuracao_id=configuracao.id,
        )

    if configuracao.quantidade > 0:

        messages.error(
            request,
            (
                "Não é possível excluir esta configuração enquanto "
                "houver estoque. Primeiro zere o estoque."
            ),
        )

        return redirect(
            "detalhe_configuracao",
            configuracao_id=configuracao.id,
        )

    if Movimentacao.objects.filter(
        configuracao=configuracao
    ).exists():

        messages.error(
            request,
            (
                "Não é possível excluir esta configuração porque "
                "ela possui movimentações no histórico."
            ),
        )

        return redirect(
            "detalhe_configuracao",
            configuracao_id=configuracao.id,
        )

    descricao_configuracao = str(
        configuracao
    )

    configuracao.delete()

    messages.success(
        request,
        (
            f'A configuração "{descricao_configuracao}" '
            "foi excluída com sucesso."
        ),
    )

    return redirect(
        "estoque"
    )


@login_required
def produtos(request):

    produtos_queryset = (
        Produto.objects
        .select_related("categoria")
        .order_by("nome")
    )

    termo = request.GET.get(
        "q",
        "",
    ).strip()

    categoria_id = request.GET.get(
        "categoria",
        "",
    ).strip()

    tipo = request.GET.get(
        "tipo",
        "",
    ).strip()

    status = request.GET.get(
        "status",
        "",
    ).strip()

    if termo:

        produtos_queryset = produtos_queryset.filter(
            models.Q(nome__icontains=termo)
            | models.Q(codigo__icontains=termo)
            | models.Q(tipo_produto__icontains=termo)
        )

    if categoria_id:

        produtos_queryset = produtos_queryset.filter(
            categoria_id=categoria_id
        )

    if tipo:

        produtos_queryset = produtos_queryset.filter(
            tipo_produto=tipo
        )

    if status == "ativo":

        produtos_queryset = produtos_queryset.filter(
            ativo=True
        )

    elif status == "inativo":

        produtos_queryset = produtos_queryset.filter(
            ativo=False
        )

    categorias_lista = (
        Categoria.objects
        .order_by("nome")
    )

    tipos_lista = (
        Produto.objects
        .exclude(tipo_produto="")
        .values_list(
            "tipo_produto",
            flat=True,
        )
        .distinct()
        .order_by("tipo_produto")
    )

    contexto = {
        "produtos": produtos_queryset,
        "categorias": categorias_lista,
        "tipos": tipos_lista,
        "termo": termo,
        "categoria_selecionada": categoria_id,
        "tipo_selecionado": tipo,
        "status_selecionado": status,
    }

    return render(
        request,
        "estoque/produtos.html",
        contexto,
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
                f'Produto "{produto.nome}" cadastrado com sucesso.',
            )

            return redirect(
                "produtos"
            )

    else:

        form = ProdutoForm()

    return render(
        request,
        "estoque/novo_produto.html",
        {
            "form": form,
        },
    )


@login_required
def editar_produto(
    request,
    produto_id,
):

    produto = get_object_or_404(
        Produto,
        pk=produto_id,
    )

    if request.method == "POST":

        form = ProdutoForm(
            request.POST,
            instance=produto,
        )

        if form.is_valid():

            produto = form.save()

            messages.success(
                request,
                f'Produto "{produto.nome}" atualizado com sucesso.',
            )

            return redirect(
                "produtos"
            )

    else:

        form = ProdutoForm(
            instance=produto,
        )

    return render(
        request,
        "estoque/editar_produto.html",
        {
            "form": form,
            "produto": produto,
        },
    )


@login_required
def descartar_produto(
    request,
    produto_id,
):

    produto = get_object_or_404(
        Produto,
        pk=produto_id,
    )

    if not request.user.is_staff:

        messages.error(
            request,
            "Somente usuários administradores podem descartar produtos.",
        )

        return redirect(
            "produtos"
        )

    if request.method != "POST":

        messages.error(
            request,
            "Operação inválida.",
        )

        return redirect(
            "produtos"
        )

    if produto.estoque_atual > 0:

        messages.error(
            request,
            (
                "Não é possível descartar este produto enquanto "
                "houver estoque. Primeiro realize a saída ou "
                "o ajuste necessário."
            ),
        )

        return redirect(
            "produtos"
        )

    produto.ativo = False

    produto.save(
        update_fields=[
            "ativo",
            "atualizado_em",
        ]
    )

    messages.success(
        request,
        f'Produto "{produto.nome}" foi descartado e ficou inativo.',
    )

    return redirect(
        "produtos"
    )


@login_required
def entrada_estoque(request):

    if request.method == "POST":

        form = EntradaEstoqueForm(
            request.POST
        )

        if form.is_valid():

            dados = form.cleaned_data

            try:

                movimentacao, criada = registrar_entrada(
                    produto=dados["produto"],
                    quantidade=dados["quantidade"],
                    usuario=request.user,
                    descricao=dados.get(
                        "descricao",
                        "",
                    ),
                    marca=dados.get(
                        "marca",
                        "",
                    ),
                    modelo=dados.get(
                        "modelo",
                        "",
                    ),
                    material=dados.get(
                        "material",
                        "",
                    ),
                    cor=dados.get(
                        "cor",
                        "",
                    ),
                    dimensoes=dados.get(
                        "dimensoes",
                        "",
                    ),
                    capacidade=dados.get(
                        "capacidade",
                        "",
                    ),
                    memoria_ram=dados.get(
                        "memoria_ram",
                        "",
                    ),
                    condicao=dados.get(
                        "condicao",
                        "",
                    ),
                    origem=dados.get(
                        "origem",
                        "",
                    ),
                    documento_origem=dados.get(
                        "documento_origem",
                        "",
                    ),
                    observacao=dados.get(
                        "observacao",
                        "",
                    ),
                )

                if criada:

                    mensagem = (
                        "Entrada registrada e nova configuração "
                        "de estoque criada com sucesso."
                    )

                else:

                    mensagem = (
                        "Entrada registrada e quantidade da "
                        "configuração atualizada com sucesso."
                    )

                messages.success(
                    request,
                    mensagem,
                )

                return redirect(
                    "entrada_estoque"
                )

            except ValidationError as erro:

                mensagem = getattr(
                    erro,
                    "message",
                    None,
                )

                if mensagem is None:
                    mensagem = str(erro)

                form.add_error(
                    None,
                    mensagem,
                )

    else:

        form = EntradaEstoqueForm()

    return render(
        request,
        "estoque/entrada.html",
        {
            "form": form,
        },
    )


@login_required
def saida_estoque(request):

    if request.method == "POST":

        form = SaidaEstoqueForm(
            request.POST
        )

        if form.is_valid():

            dados = form.cleaned_data

            try:

                registrar_saida(
                    produto=dados["produto"],
                    quantidade=dados["quantidade"],
                    usuario=request.user,
                    destino=dados["destino"],
                    configuracao=dados["configuracao"],
                    observacao=dados.get(
                        "observacao",
                        "",
                    ),
                )

                messages.success(
                    request,
                    "Saída de estoque registrada com sucesso.",
                )

                return redirect(
                    "saida_estoque"
                )

            except ValidationError as erro:

                mensagem = getattr(
                    erro,
                    "message",
                    None,
                )

                if mensagem is None:
                    mensagem = str(erro)

                form.add_error(
                    None,
                    mensagem,
                )

    else:

        form = SaidaEstoqueForm()

    return render(
        request,
        "estoque/saida.html",
        {
            "form": form,
        },
    )


@login_required
def categorias(request):

    categorias_queryset = (
        Categoria.objects
        .prefetch_related("produtos")
        .order_by("nome")
    )

    if request.method == "POST":

        form = CategoriaForm(
            request.POST
        )

        if form.is_valid():

            categoria = form.save()

            messages.success(
                request,
                f'Categoria "{categoria.nome}" cadastrada com sucesso.',
            )

            return redirect(
                "categorias"
            )

    else:

        form = CategoriaForm()

    return render(
        request,
        "estoque/categorias.html",
        {
            "categorias": categorias_queryset,
            "form": form,
        },
    )


@login_required
def excluir_categoria(
    request,
    categoria_id,
):

    categoria = get_object_or_404(
        Categoria,
        pk=categoria_id,
    )

    if request.method != "POST":

        messages.error(
            request,
            "Operação inválida.",
        )

        return redirect(
            "categorias"
        )

    if categoria.produtos.exists():

        messages.error(
            request,
            (
                f'A categoria "{categoria.nome}" não pode ser '
                "excluída porque possui produtos vinculados."
            ),
        )

        return redirect(
            "categorias"
        )

    nome_categoria = categoria.nome

    categoria.delete()

    messages.success(
        request,
        f'A categoria "{nome_categoria}" foi excluída com sucesso.',
    )

    return redirect(
        "categorias"
    )


@login_required
def historico_movimentacoes(request):

    movimentacoes = (
        Movimentacao.objects
        .select_related(
            "produto",
            "configuracao",
            "destino",
            "usuario",
        )
        .order_by("-criado_em")
    )

    produto_id = request.GET.get(
        "produto",
        "",
    ).strip()

    tipo = request.GET.get(
        "tipo",
        "",
    ).strip()

    data_inicio = request.GET.get(
        "data_inicio",
        "",
    ).strip()

    data_fim = request.GET.get(
        "data_fim",
        "",
    ).strip()

    if produto_id:

        movimentacoes = movimentacoes.filter(
            produto_id=produto_id
        )

    if tipo in [
        "E",
        "S",
        "A",
    ]:

        movimentacoes = movimentacoes.filter(
            tipo=tipo
        )

    if data_inicio:

        try:

            data_inicio_obj = datetime.strptime(
                data_inicio,
                "%Y-%m-%d",
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
                "%Y-%m-%d",
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

    contexto = {
        "movimentacoes": movimentacoes,
        "produtos": produtos_lista,
        "produto_selecionado": produto_id,
        "tipo_selecionado": tipo,
        "data_inicio": data_inicio,
        "data_fim": data_fim,
    }

    return render(
        request,
        "estoque/historico.html",
        contexto,
    )


@login_required
def excluir_movimentacao(
    request,
    movimentacao_id,
):

    movimentacao = get_object_or_404(
        Movimentacao,
        pk=movimentacao_id,
    )

    if request.method != "POST":

        messages.error(
            request,
            "Operação inválida.",
        )

        return redirect(
            "historico_movimentacoes"
        )

    try:

        reverter_movimentacao(
            movimentacao_id=movimentacao_id,
            usuario=request.user,
        )

        messages.success(
            request,
            "Movimentação excluída e estoque revertido com sucesso.",
        )

    except ValidationError as erro:

        mensagem = getattr(
            erro,
            "message",
            None,
        )

        if mensagem is None:
            mensagem = str(erro)

        messages.error(
            request,
            mensagem,
        )

    return redirect(
        "historico_movimentacoes"
    )


@login_required
def destinos(request):

    destinos_queryset = (
        Destino.objects
        .order_by("nome")
    )

    if request.method == "POST":

        form = DestinoForm(
            request.POST
        )

        if form.is_valid():

            destino = form.save()

            messages.success(
                request,
                f'Destino "{destino.nome}" cadastrado com sucesso.',
            )

            return redirect(
                "destinos"
            )

    else:

        form = DestinoForm()

    return render(
        request,
        "estoque/destinos.html",
        {
            "destinos": destinos_queryset,
            "form": form,
        },
    )


@login_required
def editar_destino(
    request,
    destino_id,
):

    destino = get_object_or_404(
        Destino,
        pk=destino_id,
    )

    if request.method == "POST":

        form = DestinoForm(
            request.POST,
            instance=destino,
        )

        if form.is_valid():

            destino = form.save()

            messages.success(
                request,
                f'Destino "{destino.nome}" atualizado com sucesso.',
            )

            return redirect(
                "destinos"
            )

    else:

        form = DestinoForm(
            instance=destino,
        )

    return render(
        request,
        "estoque/editar_destino.html",
        {
            "form": form,
            "destino": destino,
        },
    )


@login_required
def alternar_destino(
    request,
    destino_id,
):

    destino = get_object_or_404(
        Destino,
        pk=destino_id,
    )

    if request.method != "POST":

        messages.error(
            request,
            "Operação inválida.",
        )

        return redirect(
            "destinos"
        )

    destino.ativo = not destino.ativo

    destino.save(
        update_fields=[
            "ativo",
        ]
    )

    if destino.ativo:

        messages.success(
            request,
            f'Destino "{destino.nome}" foi ativado.',
        )

    else:

        messages.success(
            request,
            f'Destino "{destino.nome}" foi desativado.',
        )

    return redirect(
        "destinos"
    )


@login_required
def distribuicoes(request):

    movimentacoes = (
        Movimentacao.objects
        .filter(
            tipo="S",
            destino__isnull=False,
        )
        .select_related(
            "produto",
            "configuracao",
            "destino",
            "usuario",
        )
        .order_by("-criado_em")
    )

    destino_id = request.GET.get(
        "destino",
        "",
    ).strip()

    data_inicio = request.GET.get(
        "data_inicio",
        "",
    ).strip()

    data_fim = request.GET.get(
        "data_fim",
        "",
    ).strip()

    if destino_id:

        movimentacoes = movimentacoes.filter(
            destino_id=destino_id
        )

    if data_inicio:

        try:

            data_inicio_obj = datetime.strptime(
                data_inicio,
                "%Y-%m-%d",
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
                "%Y-%m-%d",
            ).date()

            movimentacoes = movimentacoes.filter(
                criado_em__date__lte=data_fim_obj
            )

        except ValueError:
            pass

    destinos_lista = (
        Destino.objects
        .order_by("nome")
    )

    contexto = {
        "movimentacoes": movimentacoes,
        "destinos": destinos_lista,
        "destino_selecionado": destino_id,
        "data_inicio": data_inicio,
        "data_fim": data_fim,
    }

    return render(
        request,
        "estoque/distribuicoes.html",
        contexto,
    )
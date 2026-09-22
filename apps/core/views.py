from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import F, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, TemplateView
from django.views.generic.edit import UpdateView

from .forms import (
    CategoriaForm,
    DestinoForm,
    EntradaEstoqueForm,
    EstoqueForm,
    FornecedorForm,
    MovimentacaoFiltroForm,
    ProdutoForm,
    SaidaEstoqueForm,
)
from .models import (
    Categoria,
    Destino,
    Estoque,
    Fornecedor,
    Movimentacao,
    Produto,
    SaldoEstoque,
)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "core/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        empresa = self.request.user.empresa

        produtos = Produto.objects.filter(
            empresa=empresa
        )

        movimentacoes = Movimentacao.objects.filter(
            empresa=empresa
        )

        saldos = SaldoEstoque.objects.filter(
            produto__empresa=empresa
        )

        context.update(
            {
                "total_produtos": produtos.filter(
                    ativo=True
                ).count(),

                "total_estoque": (
                    saldos.aggregate(
                        total=Sum("quantidade")
                    )["total"]
                    or 0
                ),

                "produtos_sem_estoque": produtos.filter(
                    ativo=True,
                    saldos__quantidade=0,
                ).distinct().count(),

                "entradas": movimentacoes.filter(
                    tipo=Movimentacao.Tipo.ENTRADA
                ).count(),

                "saidas": movimentacoes.filter(
                    tipo=Movimentacao.Tipo.SAIDA
                ).count(),

                "movimentacoes_recentes": movimentacoes.select_related(
                    "produto",
                    "estoque",
                    "destino",
                    "usuario",
                )[:10],

                "produtos_recentes": produtos.order_by(
                    "-criado_em"
                )[:10],

                "estoques": Estoque.objects.filter(
                    empresa=empresa,
                    ativo=True,
                ),
            }
        )

        return context


class EstoqueCreateView(LoginRequiredMixin, CreateView):
    model = Estoque
    form_class = EstoqueForm
    template_name = "core/estoque/form.html"
    success_url = reverse_lazy("lista_estoques")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.empresa = self.request.user.empresa

        messages.success(
            self.request,
            "Estoque cadastrado com sucesso.",
        )

        return super().form_valid(form)


class EstoqueListView(LoginRequiredMixin, ListView):
    model = Estoque
    template_name = "core/estoque/lista.html"
    context_object_name = "estoques"

    def get_queryset(self):
        return Estoque.objects.filter(
            empresa=self.request.user.empresa
        ).order_by("nome")


class EstoqueUpdateView(LoginRequiredMixin, UpdateView):
    model = Estoque
    form_class = EstoqueForm
    template_name = "core/estoque/form.html"
    success_url = reverse_lazy("lista_estoques")

    def get_queryset(self):
        return Estoque.objects.filter(
            empresa=self.request.user.empresa
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(
            self.request,
            "Estoque atualizado com sucesso.",
        )

        return super().form_valid(form)


class CategoriaCreateView(LoginRequiredMixin, CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = "core/categoria/form.html"
    success_url = reverse_lazy("lista_categorias")


class CategoriaListView(LoginRequiredMixin, ListView):
    model = Categoria
    template_name = "core/categoria/lista.html"
    context_object_name = "categorias"

    def get_queryset(self):
        return Categoria.objects.filter(
            ativo=True
        ).order_by("nome")


class CategoriaUpdateView(LoginRequiredMixin, UpdateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = "core/categoria/form.html"
    success_url = reverse_lazy("lista_categorias")


class FornecedorCreateView(LoginRequiredMixin, CreateView):
    model = Fornecedor
    form_class = FornecedorForm
    template_name = "core/fornecedor/form.html"
    success_url = reverse_lazy("lista_fornecedores")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.empresa = self.request.user.empresa

        messages.success(
            self.request,
            "Fornecedor cadastrado com sucesso.",
        )

        return super().form_valid(form)


class FornecedorListView(LoginRequiredMixin, ListView):
    model = Fornecedor
    template_name = "core/fornecedor/lista.html"
    context_object_name = "fornecedores"

    def get_queryset(self):
        return Fornecedor.objects.filter(
            empresa=self.request.user.empresa
        ).order_by("nome")


class FornecedorUpdateView(LoginRequiredMixin, UpdateView):
    model = Fornecedor
    form_class = FornecedorForm
    template_name = "core/fornecedor/form.html"
    success_url = reverse_lazy("lista_fornecedores")

    def get_queryset(self):
        return Fornecedor.objects.filter(
            empresa=self.request.user.empresa
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class DestinoCreateView(LoginRequiredMixin, CreateView):
    model = Destino
    form_class = DestinoForm
    template_name = "core/destino/form.html"
    success_url = reverse_lazy("lista_destinos")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.empresa = self.request.user.empresa

        messages.success(
            self.request,
            "Destino cadastrado com sucesso.",
        )

        return super().form_valid(form)


class DestinoListView(LoginRequiredMixin, ListView):
    model = Destino
    template_name = "core/destino/lista.html"
    context_object_name = "destinos"

    def get_queryset(self):
        return Destino.objects.filter(
            empresa=self.request.user.empresa
        ).order_by("nome")


class DestinoUpdateView(LoginRequiredMixin, UpdateView):
    model = Destino
    form_class = DestinoForm
    template_name = "core/destino/form.html"
    success_url = reverse_lazy("lista_destinos")

    def get_queryset(self):
        return Destino.objects.filter(
            empresa=self.request.user.empresa
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class ProdutoCreateView(LoginRequiredMixin, CreateView):
    model = Produto
    form_class = ProdutoForm
    template_name = "core/produto/form.html"
    success_url = reverse_lazy("lista_produtos")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.empresa = self.request.user.empresa

        messages.success(
            self.request,
            "Produto cadastrado com sucesso.",
        )

        return super().form_valid(form)


class ProdutoListView(LoginRequiredMixin, ListView):
    model = Produto
    template_name = "core/produto/lista.html"
    context_object_name = "produtos"

    def get_queryset(self):
        queryset = Produto.objects.filter(
            empresa=self.request.user.empresa
        ).select_related(
            "categoria",
            "fornecedor",
        )

        busca = self.request.GET.get("q", "").strip()

        if busca:
            queryset = queryset.filter(
                nome__icontains=busca
            ) | queryset.filter(
                codigo__icontains=busca
            ) | queryset.filter(
                tipo_produto__icontains=busca
            ) | queryset.filter(
                marca__icontains=busca
            )

        return queryset.distinct().order_by("nome")


class ProdutoDetailView(LoginRequiredMixin, DetailView):
    model = Produto
    template_name = "core/produto/detalhe.html"
    context_object_name = "produto"

    def get_queryset(self):
        return Produto.objects.filter(
            empresa=self.request.user.empresa
        ).select_related(
            "categoria",
            "fornecedor",
        ).prefetch_related(
            "saldos__estoque",
            "movimentacoes__estoque",
            "movimentacoes__destino",
        )


class ProdutoUpdateView(LoginRequiredMixin, UpdateView):
    model = Produto
    form_class = ProdutoForm
    template_name = "core/produto/form.html"
    success_url = reverse_lazy("lista_produtos")

    def get_queryset(self):
        return Produto.objects.filter(
            empresa=self.request.user.empresa
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(
            self.request,
            "Produto atualizado com sucesso.",
        )

        return super().form_valid(form)


class EntradaEstoqueView(LoginRequiredMixin, View):
    template_name = "core/movimentacao/entrada.html"

    def get(self, request):
        form = EntradaEstoqueForm(
            user=request.user
        )

        return render(
            request,
            self.template_name,
            {"form": form},
        )

    @transaction.atomic
    def post(self, request):
        form = EntradaEstoqueForm(
            request.POST,
            user=request.user,
        )

        if not form.is_valid():
            return render(
                request,
                self.template_name,
                {"form": form},
            )

        produto = form.cleaned_data["produto"]
        estoque = form.cleaned_data["estoque"]
        quantidade = form.cleaned_data["quantidade"]

        saldo, _ = SaldoEstoque.objects.get_or_create(
            produto=produto,
            estoque=estoque,
            defaults={"quantidade": 0},
        )

        saldo.quantidade = F("quantidade") + quantidade
        saldo.save(update_fields=["quantidade", "atualizado_em"])

        saldo.refresh_from_db()

        Movimentacao.objects.create(
            empresa=request.user.empresa,
            produto=produto,
            estoque=estoque,
            tipo=Movimentacao.Tipo.ENTRADA,
            quantidade=quantidade,
            documento=form.cleaned_data["documento"],
            observacao=form.cleaned_data["observacao"],
            usuario=request.user,
        )

        messages.success(
            request,
            "Entrada registrada com sucesso.",
        )

        return redirect("lista_produtos")


class SaidaEstoqueView(LoginRequiredMixin, View):
    template_name = "core/movimentacao/saida.html"

    def get(self, request):
        form = SaidaEstoqueForm(
            user=request.user
        )

        return render(
            request,
            self.template_name,
            {"form": form},
        )

    @transaction.atomic
    def post(self, request):
        form = SaidaEstoqueForm(
            request.POST,
            user=request.user,
        )

        if not form.is_valid():
            return render(
                request,
                self.template_name,
                {"form": form},
            )

        produto = form.cleaned_data["produto"]
        estoque = form.cleaned_data["estoque"]
        quantidade = form.cleaned_data["quantidade"]

        saldo = SaldoEstoque.objects.select_for_update().filter(
            produto=produto,
            estoque=estoque,
        ).first()

        if not saldo or saldo.quantidade < quantidade:
            form.add_error(
                "quantidade",
                "Quantidade insuficiente no estoque selecionado.",
            )

            return render(
                request,
                self.template_name,
                {"form": form},
            )

        saldo.quantidade = F("quantidade") - quantidade
        saldo.save(update_fields=["quantidade", "atualizado_em"])

        Movimentacao.objects.create(
            empresa=request.user.empresa,
            produto=produto,
            estoque=estoque,
            destino=form.cleaned_data["destino"],
            tipo=Movimentacao.Tipo.SAIDA,
            quantidade=quantidade,
            documento=form.cleaned_data["documento"],
            observacao=form.cleaned_data["observacao"],
            usuario=request.user,
        )

        messages.success(
            request,
            "Saída registrada com sucesso.",
        )

        return redirect("lista_produtos")


class MovimentacaoListView(LoginRequiredMixin, ListView):
    model = Movimentacao
    template_name = "core/movimentacao/lista.html"
    context_object_name = "movimentacoes"

    def get_queryset(self):
        queryset = Movimentacao.objects.filter(
            empresa=self.request.user.empresa
        ).select_related(
            "produto",
            "estoque",
            "destino",
            "usuario",
        )

        produto = self.request.GET.get("produto")
        estoque = self.request.GET.get("estoque")
        tipo = self.request.GET.get("tipo")
        data_inicio = self.request.GET.get("data_inicio")
        data_fim = self.request.GET.get("data_fim")

        if produto:
            queryset = queryset.filter(
                produto_id=produto
            )

        if estoque:
            queryset = queryset.filter(
                estoque_id=estoque
            )

        if tipo:
            queryset = queryset.filter(
                tipo=tipo
            )

        if data_inicio:
            queryset = queryset.filter(
                criado_em__date__gte=data_inicio
            )

        if data_fim:
            queryset = queryset.filter(
                criado_em__date__lte=data_fim
            )

        return queryset.order_by(
            "-criado_em",
            "-id",
        )


class EstoqueAtualView(LoginRequiredMixin, ListView):
    model = SaldoEstoque
    template_name = "core/estoque/saldos.html"
    context_object_name = "saldos"

    def get_queryset(self):
        return SaldoEstoque.objects.filter(
            produto__empresa=self.request.user.empresa
        ).select_related(
            "produto",
            "estoque",
        ).order_by(
            "produto__nome",
            "estoque__nome",
        )


class RelatoriosView(LoginRequiredMixin, TemplateView):
    template_name = "core/relatorios.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        empresa = self.request.user.empresa

        context["produtos"] = Produto.objects.filter(
            empresa=empresa
        ).count()

        context["estoques"] = Estoque.objects.filter(
            empresa=empresa
        ).count()

        context["movimentacoes"] = Movimentacao.objects.filter(
            empresa=empresa
        ).count()

        return context
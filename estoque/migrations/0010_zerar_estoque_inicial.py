from django.db import migrations


def zerar_estoque(apps, schema_editor):
    Produto = apps.get_model("estoque", "Produto")
    ConfiguracaoEstoque = apps.get_model(
        "estoque",
        "ConfiguracaoEstoque",
    )

    # Zera o estoque total dos produtos.
    Produto.objects.all().update(
        estoque_atual=0
    )

    # Zera as quantidades das configurações
    # específicas de estoque.
    ConfiguracaoEstoque.objects.all().update(
        quantidade=0
    )


def desfazer_zeragem(apps, schema_editor):
    # Não existe uma forma segura de recuperar os
    # valores anteriores sem apagar o histórico.
    #
    # Portanto, esta migração não restaura os valores
    # anteriores caso seja revertida.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("estoque", "0009_configuracaoestoque_movimentacao_configuracao"),
    ]

    operations = [
        migrations.RunPython(
            zerar_estoque,
            desfazer_zeragem,
        ),
    ]
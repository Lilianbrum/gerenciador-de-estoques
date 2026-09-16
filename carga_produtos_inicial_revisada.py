from django.db import transaction
from estoque.models import Categoria, Produto

# Carga inicial dos PRODUTOS-BASE identificados nos documentos enviados.
# Quantidades e configurações NÃO são importadas.
# As entradas de estoque serão registradas manualmente depois.
# IMEI não é cadastrado neste sistema.

PRODUTOS = [
    ('Smartphones', 'Smartphone', 'Xiaomi Mi 10'),
    ('Smartphones', 'Smartphone', 'Xiaomi Redmi 10'),
    ('Smartphones', 'Smartphone', 'Xiaomi Redmi Note 9S'),
    ('Smartphones', 'Smartphone', 'Xiaomi Redmi Note 11S'),
    ('Smartphones', 'Smartphone', 'Xiaomi Redmi Note 12S'),
    ('Smartphones', 'Smartphone', 'Xiaomi Redmi Note 12'),
    ('Smartphones', 'Smartphone', 'Xiaomi Redmi 12C'),
    ('Smartphones', 'Smartphone', 'Xiaomi Redmi A2'),
    ('Smartphones', 'Smartphone', 'Xiaomi Redmi A3'),
    ('Smartphones', 'Smartphone', 'Xiaomi Redmi 13C'),
    ('Smartphones', 'Smartphone', 'Xiaomi Redmi 14C'),
    ('Smartphones', 'Smartphone', 'Xiaomi Redmi 12'),
    ('Smartphones', 'Smartphone', 'Xiaomi Redmi Note 50'),
    ('Smartphones', 'Smartphone', 'Xiaomi Redmi — diversos'),
    ('Smartphones', 'Smartphone', 'Xiaomi Redmi Note 11S — modelo identificado no documento'),
    ('Smartphones', 'Smartphone', 'Xiaomi Poco X5'),
    ('Smartphones', 'Smartphone', 'Xiaomi Poco X5 Pro 5G'),
    ('Smartphones', 'Smartphone', 'Xiaomi Poco X6'),
    ('Smartphones', 'Smartphone', 'Xiaomi Poco X6 Pro'),
    ('Smartphones', 'Smartphone', 'Xiaomi Poco — diversos'),
    ('Smartphones', 'Smartphone', 'Xiaomi 12 Lite'),
    ('Smartphones', 'Smartphone', 'Motorola G73'),
    ('Smartphones', 'Smartphone', 'Infinix Smart 8'),
    ('Smartphones', 'Smartphone', 'Realme C53'),
    ('Smartphones', 'Smartphone', 'Realme C55'),
    ('Smartphones', 'Smartphone', 'Realme C67'),
    ('Smartphones', 'Smartphone', 'Realme Note 50'),
    ('Smartphones', 'Smartphone', 'Realme — diversos'),
    ('Smartphones', 'Smartphone', 'Honor Magic 6 Lite'),
    ('Smartphones', 'Smartphone', 'Samsung — modelo não identificado'),
    ('Smartphones', 'Smartphone', 'Apple iPhone 11'),
    ('Smartphones', 'Smartphone', 'Apple iPhone 15'),
    ('Smartphones', 'Smartphone', 'Apple iPhone 15 Pro Max'),
    ('Smartphones', 'Smartphone', 'Apple iPhone 17 Pro Max'),
    ('Smartphones', 'Smartphone', 'Apple — modelo não identificado'),
    ('Smartphones', 'Smartphone', 'Nokia — modelo não identificado'),
    ('Tablets', 'Tablet', 'Apple iPad — modelo A2602'),
    ('Tablets', 'Tablet', 'Apple iPad 10ª geração'),
    ('Tablets', 'Tablet', 'Xiaomi Redmi Pad SE'),
    ('Tablets', 'Tablet', 'Xiaomi Pad 5'),
    ('Tablets', 'Tablet', 'Samsung Galaxy Tab A7 Lite'),
    ('Armazenamento', 'Armazenamento', 'SSD Kingston 240GB'),
    ('Armazenamento', 'Armazenamento', 'SSD Samsung 980 Pro PCIe 4.0 NVMe M.2'),
    ('Armazenamento', 'Armazenamento', 'SSD SanDisk Extreme Plus'),
    ('Armazenamento', 'Armazenamento', 'HD externo Seagate'),
    ('Armazenamento', 'Armazenamento', 'Cartão de memória SanDisk'),
    ('Armazenamento', 'Armazenamento', 'Cartão de memória Samsung'),
    ('Armazenamento', 'Armazenamento', 'Pendrive (memória flash)'),
    ('Câmeras', 'Câmera', 'Câmera S/Fio P/Circ.Fech. China'),
    ('Câmeras', 'Câmera', 'Câmera S/Fio P/Circ.Fech. Video Baby Monitor VB603'),
    ('Câmeras', 'Câmera', 'Câmera S/Fio P/Circ.Fech. Panasonic'),
    ('Câmeras', 'Câmera', 'Câmera S/Fio P/Circ.Fech. Diversos'),
    ('Televisores', 'Televisor', 'Televisor a cores Audisat 32'),
    ('Acessórios', 'Acessório', 'Fonte de notebook Positivo / carregador de bateria universal portátil'),
    ('Acessórios', 'Acessório', 'Recarregador de bateria Apple'),
    ('Acessórios', 'Acessório', 'Carregador de celular portátil Kaidi'),
    ('Utensílios', 'Utensílio', 'Lata ou recipiente de alumínio tipo quentinha'),
    ('Utensílios', 'Utensílio', 'Talheres — conjunto de três peças'),
    ('Balanças', 'Balança', 'Balança digital Luizawn Styles 40 kg — modelo ZY-999'),
    ('Balanças', 'Balança', 'Balança digital Luizawn Styles 40 kg — modelo ZY-007'),
]

with transaction.atomic():
    criados = 0
    existentes = 0
    for nome_categoria, tipo_produto, nome_produto in PRODUTOS:
        categoria, _ = Categoria.objects.get_or_create(
            nome=nome_categoria,
            defaults={"descricao": "Categoria da carga inicial de produtos."},
        )
        produto, criado = Produto.objects.get_or_create(
            nome=nome_produto,
            defaults={
                "categoria": categoria,
                "tipo_produto": tipo_produto,
                "unidade": "UN",
                "estoque_atual": 0,
                "estoque_minimo": 0,
                "ativo": True,
            },
        )
        if criado:
            criados += 1
        else:
            existentes += 1

print(f"Carga concluída: {criados} produtos criados; {existentes} já existentes.")
print("Todos os produtos permanecem com estoque zero.")

# Gerenciador de Estoques

Aplicação web em desenvolvimento para gestão de estoque, construída com Django. Este repositório contém o código-fonte do projeto; a interface e os recursos podem estar em evolução.

## Preparação local

Requer Python compatível com as dependências listadas em `requirements.txt`.

```bash
python -m venv .venv
```

Ative o ambiente virtual e instale as dependências:

```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
```

Prepare o banco e inicie o servidor:

```bash
python manage.py migrate
python manage.py runserver
```

Acesse http://127.0.0.1:8000/.

## Stack

- Python
- Django
- SQLite para desenvolvimento local; a configuração também inclui dependências para PostgreSQL

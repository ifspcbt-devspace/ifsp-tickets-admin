# ===== Base =====
FROM python:3.12-slim

# Não gera arquivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Cria usuário não-root
RUN groupadd -r django && useradd -r -g django django

# Instala dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia dependências
COPY requirements.txt .

# Instala dependências
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código
COPY . .

# Coleta arquivos estáticos
RUN python manage.py collectstatic --noinput

# Ajusta permissões
RUN chown -R django:django /app

USER django

EXPOSE 8000

# Rodar servidor em produção
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]

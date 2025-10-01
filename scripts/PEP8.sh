#!/usr/bin/env bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

pacotes=("isort" "black" "flake8")
for pkg in "${pacotes[@]}"; do
    (pip freeze | grep -iq "$pkg") || {
        >&2 echo "$pkg nao esta instalado"
        exit 1
    }
done

echo "Rodando isort..."
isort "$PROJECT_ROOT"

echo "Rodando black..."
black --line-length 79 "$PROJECT_ROOT"

# opção --max-line-length=999 para evitar aviso de limite de 79 caracteres
echo "Rodando flake8..."
flake8 --max-line-length=999 "$PROJECT_ROOT"

echo "Concluído! Código formatado e verificado."


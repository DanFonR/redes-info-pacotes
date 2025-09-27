#!/usr/bin/env bash

if [ "$(whoami)" != "root" ]; then
    echo "Execute este script como superusuario"
    exit 1
fi

pacotes=("pyftpdlib" "scapy")
for pkg in "${pacotes[@]}"; do
    (pip freeze | grep -iq "$pkg") || {
        >&2 echo "$pkg nao esta instalado"
        exit 1
    }
done

python src/ip.py || exit 1

trap "kill -9 0" INT # Em caso de Ctrl+C, elimina todos os subprocessos

python src/main.py &

echo "Pressione Ctrl+C para terminar o programa"

wait

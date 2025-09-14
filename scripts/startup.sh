#!/bin/sh

if [[ $EUID -ne 0 ]]; then
    echo "Execute este script como superusuário"
    read -p "Pressione qualquer tecla para sair..." -n1 -s
    echo ""
    exit 1
fi

trap "kill -9 0" EXIT # termina quaisquer subprocessos ao sair do programa

cd ..

python -m http.server &
python -m pyftpdlib &
python src/redes.py &

echo "Pressione Ctrl+C para terminar o programa"

wait

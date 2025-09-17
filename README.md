# NetLogger - Captura de Pacotes de Rede

### Arthur Brito - 2312130001
### Dannyel F. Ribeiro - 2322130061
### Nálbert B. N. Bernardo - 2322130036
### Regimar D. Negreiros - 2322130016
### Samuel R. Aguiar - 2312130106
### Vitor Hugo C. Moura - 2312130182

## Sobre

Este projeto permite monitorar o tráfego de entrada e saída de um servidor.
Os dados sobre os pacotes são registrados em um arquivo CSV, que pode ser aberto no Excel ou outro visualizador de planilhas.

O script cria servidores **HTTP** e **FTP** para testes de captura de pacotes.

## Instalação

### Requisitos Python

* [Scapy](https://scapy.net/) – biblioteca para manipulação de pacotes de rede.
* [pyftpdlib](https://pyftpdlib.readthedocs.io/) – biblioteca para criação rápida de servidor FTP.

Instale as dependências com:

```bash
pip install -r requirements.txt
```

> ⚠️ Apesar de ser prática, a utilização de ambientes virtuais **não é recomendada** neste projeto, pois pode impactar a performance da captura de pacotes em tempo real.

### Windows

Para rodar no Windows, instale o [Npcap](https://npcap.com/) e marque as opções:
  - _Support raw 802.11 traffic (and monitor mode) for wireless adapters_; e
  - _Install Npcap in WinPcap API-compatible mode_.

O Npcap fornece a API necessária para captura de pacotes pelo Scapy. 
O modo de compatibilidade evita a necessidade de privilégios administrativos, 
e o suporte ao tráfego 802.11 habilita escuta de conexões _wireless_.

## Execução

No diretório raiz do projeto:

* **Windows:**

```bat
.\scripts\startup.bat
```

* **Linux/macOS:**

```bash
sudo -E ./scripts/startup.sh
```

Para testar em outras máquinas:

* **HTTP:** acesse `http://<IP_DO_HOST>:8000` no navegador.
* **FTP:** acesse `ftp://<IP_DO_HOST>:2121` no explorador de arquivos.

> ⚠️ No Linux, a captura de pacotes normalmente requer privilégios de administrador (`sudo`).

## Desinstalação

* Python:

```bash
pip uninstall -r requirements.txt
```

> ⚠️ Caso não utilize um ambiente virtual, este comando removerá pacotes do sistema. Reinstale-os posteriormente se necessário.

* **Windows:** desinstale o Npcap pelo painel de controle.

## Desenvolvimento

Instale as dependências de desenvolvimento:
```bash
pip install -r requirements-dev.txt
```

O projeto segue o **padrão de código PEP8**.
A verificação e formatação podem ser feitas usando os scripts incluídos:

* **Linux/macOS:** `./scripts/PEP8.sh`
* **Windows:** `.\scripts\PEP8.bat`

Esses scripts executam:

* `isort` → organiza os imports
* `black` → formata o código automaticamente
* `flake8` → verifica estilo e possíveis problemas

O código possui **testes unitários e de integração** utilizando `pytest`.
Os testes verificam:

* Captura de pacotes
* Geração correta do CSV
* Criação de logs
* Tratamento de exceções e interrupções manuais

> 💡 É recomendado rodar os scripts antes de commits para garantir consistência no estilo do código.

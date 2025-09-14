# Volume de Tráfego de Dados por IP

### Arthur Brito - 2312130001
### Dannyel F. Ribeiro - 2322130061
### Nálbert B. N. Bernardo - 2322130036
### Regimar D. Negreiros - 2322130016
### Samuel R. Aguiar - 2312130106
### Vitor Hugo C. Moura - 2312130182

## Sobre

Este repositório trata-se da exposição do tráfego de entrada e saída 
de um servidor. Os dados sobre os pacotes são escritos em um arquivo CSV, 
que é acessado pelo Excel para exibição.

O script cria um servidor HTTP e outro FTP para testes.

## Instalação

### Requisitos Python

- Scapy: biblioteca de manipulação de pacotes
- pyftpdlib: biblioteca e ferramenta de criação rápida de servidor FTP

Instale-os com `pip install -r requirements.txt` no diretório raiz.
  
Apesar de ser boa prática, o uso de um ambiente virtual nesse caso 
não é recomendado, pois é lento demais para a captura de pacotes 
no devido tempo.

### Windows

Para executar no Windows, instale o programa [Npcap](https://npcap.com/), 
e, durante a instalação, selecione as opções _Install Npcap in WinPcap_ 
_API-compatible mode_ e _Support raw 802.11 traffic (and monitor mode)_ 
_for wireless adapters_. Reinicie o computador se necessário.

Esse programa fornece a API de captura de pacotes necessária 
para o Scapy funcionar no Windows, e o modo de compatibilidade evita 
a necessidade de privilégios administrativos.

## Execução

No diretório raiz, execute `.\scripts\startup.bat` no Windows, 
ou `sudo -E ./scripts/startup.sh` no Linux.

Para testar, em outras máquinas:
  - HTTP: digite o IP do host seguido de `:8000` no navegador
  - FTP: digite o IP do host seguido de `:2121` no caminho no 
    explorador de arquivos

## Desinstalação

Execute o comando `pip uninstall -r requirements.txt` no diretório raiz 
(Aviso: caso não esteja em um ambiente virtual, esse comando removerá os 
pacotes do sistema inteiro. 
Caso haja necessidade, reinstale-os posteriormente), e, no Windows, desinstale 
o Npcap.

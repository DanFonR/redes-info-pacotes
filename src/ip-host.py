import socket

soc: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ip: str

try:
    soc.connect(("8.8.8.8", 80))
    ip = soc.getsockname()[0]
except:
    ip = "localhost"
finally:
    soc.close()

print(f"USE ESSE IP PARA ACESSAR OS SERVIDORES: {ip}\n")
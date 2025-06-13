import os
import datetime

# Configurações do MySQL
usuario = "root"
senha = "20112005"
banco = "reserva_laboratorio"

# Nome do arquivo de backup com data e hora
data_atual = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
nome_arquivo = f"backup_{banco}_{data_atual}.sql"

# Comando de backup
comando = f'mysqldump -u {usuario} -p{senha} {banco} > {nome_arquivo}'

# Executa o comando
os.system(comando)
print(f"Backup criado: {nome_arquivo}")

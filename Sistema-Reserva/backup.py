import os
import datetime

usuario = "root"
senha = "20112005"
banco = "reserva_laboratorio"

data_atual = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
nome_arquivo = f"backup_{banco}_{data_atual}.sql"

comando = f'mysqldump -u {usuario} -p{senha} {banco} > {nome_arquivo}'

os.system(comando)
print(f"Backup criado: {nome_arquivo}")

## Não coloquei a client_secret por motivos de segurança 
## 💡 Introdução
O presente projeto tem como objetivo o desenvolvimento de um sistema completo para controle de reservas de salas de laboratório, utilizando uma abordagem centrada na segurança, desempenho e integração entre aplicação web e banco de dados. Desde sua concepção, o sistema foi pensado para atender à realidade acadêmica e institucional, possibilitando que usuários (alunos, professores e administradores) possam reservar, editar ou visualizar agendamentos de forma prática e segura.

Para garantir um resultado profissional, o sistema foi desenvolvido utilizando Flask (Python) no backend, MySQL como banco de dados relacional, e diversas ferramentas auxiliares como bcrypt, FPDF, Google Drive API e recursos de segurança contra ataques como SQL Injection e XSS.

## 🔧 Modelagem e Criação do Banco de Dados 
Diagrama Entidade-Relacionamento
O modelo relacional foi cuidadosamente planejado com três entidades principais: usuarios, salas e reservas. A tabela reservas possui chaves estrangeiras apontando para as tabelas usuarios e salas, garantindo integridade referencial.

A entidade usuarios contempla os tipos: admin, professor e aluno, com permissões específicas.

salas registra o nome, capacidade e equipamentos.

reservas registra data, hora e status (pendente, aprovada ou rejeitada).

## Criação do Banco

CREATE DATABASE IF NOT EXISTS reserva_laboratorio;
USE reserva_laboratorio;

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    senha VARCHAR(255),
    tipo ENUM('admin', 'professor', 'aluno') DEFAULT 'aluno'
);

CREATE TABLE salas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome_sala VARCHAR(50),
    capacidade INT,
    equipamentos TEXT
);

CREATE TABLE reservas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT,
    id_sala INT,
    data_reserva DATE,
    hora_inicio TIME,
    hora_fim TIME,
    status ENUM('pendente', 'aprovada', 'rejeitada') DEFAULT 'pendente',
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id),
    FOREIGN KEY (id_sala) REFERENCES salas(id)
);
Controles de Acesso
Criamos um usuário específico do MySQL para a aplicação:


CREATE USER 'usuario_lab'@'localhost' IDENTIFIED BY 'senha123';
GRANT SELECT, INSERT, UPDATE, DELETE ON reserva_laboratorio.* TO 'usuario_lab'@'localhost';
FLUSH PRIVILEGES;
## 🧩 Escolha das Tecnologias 
Tecnologias Utilizadas
Tecnologia	Justificativa
Python/Flask	Microframework leve, perfeito para criação de APIs REST, rotas, sessões e integração com HTML (Jinja2).
MySQL	Banco de dados relacional robusto, com ótima compatibilidade com Flask, segurança, e estrutura sólida.
Bcrypt	Criptografia de senhas no backend com alto nível de segurança.
FPDF/ReportLab	Geração de relatórios em PDF para reservas individuais ou totais.
Google Drive API	Envio automático de backups para a nuvem com autenticação OAuth.
ODBC	Comunicação alternativa entre app e banco, para aprendizado de interoperabilidade.

## Justificativa da Escolha
Nossa escolha foi orientada pela facilidade de integração com o ecossistema Python, segurança no armazenamento e acesso, além da flexibilidade no controle de permissões. Utilizamos ODBC e conexão nativa como forma de testar desempenho e interoperabilidade entre camadas.

## 🔄 Backup e Recuperação 
Implementamos um sistema de backup automático com mysqldump, além de uma opção de upload para o Google Drive com autenticação via OAuth2. A estratégia envolve:

Criação de backups periódicos com mysqldump.

Upload automático via script Python (upload_drive.py).

Controle de versão e nomeação por timestamp.

Permissões limitadas no banco para segurança do dump.

## 🔗 Integração com Aplicações 
Foram utilizadas duas abordagens de comunicação com o banco:

Nativa (MySQL Connector): Alta performance, ideal para sistemas dedicados.

ODBC (via pyodbc): Flexibilidade, compatibilidade com diversas linguagens, ideal para ambientes multiplataforma.

Comparativo
Recurso	Nativo	ODBC
Velocidade	Alta	Boa
Portabilidade	Limitada	Alta
Complexidade	Menor	Moderada
Segurança	Alta	Depende da configuração

## 🚀 Desempenho e Otimizações (PDF 9)
Implementamos práticas para garantir escalabilidade e resposta rápida:

Pool de Conexões com MySQL.

Uso de índices nas chaves estrangeiras.

Views otimizadas para consultas específicas.

Separação de usuários por permissões.

Evitar SQL dinâmico não parametrizado.

## 🔐 Segurança em Banco e Aplicação (PDF 10)
Medidas Aplicadas
Criptografia de senhas com bcrypt

Prevenção de SQL Injection com cursor.execute() e parâmetros

Validação de permissões por sessão

Uso de usuários restritos no MySQL

Separação de rotas e funções por tipo de usuário

Não exposição de scripts sensíveis

Práticas Evitadas
Senhas em texto claro

SQL concatenado diretamente

Contas root no deploy

## ✅ Considerações Finais
O projeto foi desenvolvido com base em práticas reais de segurança, modelagem sólida e tecnologias modernas, proporcionando não apenas uma solução funcional, mas também educativa. Todas as etapas foram documentadas, discutidas e justificadas em grupo, respeitando as etapas propostas nas atividades do curso.

Este sistema está pronto para ser usado e expandido em outros contextos acadêmicos ou corporativos.

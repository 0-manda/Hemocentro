# Projeto HemoCamp

Projeto Integrador - Pontifícia Universidade Católica de Campinas (PUCC)

O HemoCamp é uma plataforma centralizada desenvolvida para conectar hemocentros a potenciais doadores, visando mitigar a crise de estoques de sangue no Brasil.

## O Problema e a Solução
O Brasil enfrenta recorrentemente notícias sobre a falta de doações e hospitais com estoques críticos. Identificamos uma lacuna na comunicação entre as instituições e a população.

Nossa solução é um site centralizado onde hemocentros podem divulgar suas necessidades de forma prática. O objetivo é tornar a informação acessível, eliminando a necessidade do doador verificar individualmente a carência de cada hemocentro (X ou Y), facilitando assim o ato de doar.

Como o projeto está em desenvolvimento e em estágio inicial, nosso foco é atender a Região Metropolitana de Campinas (RMC).

## Tecnologias Utilizadas
O projeto foi construído utilizando as seguintes linguagens e ferramentas:

Front-end: HTML, CSS, JavaScript

Back-end: Python (Flask)

Banco de Dados: MySQL

## Instalação e Configuração
Para rodar o projeto localmente, siga os passos abaixo.

Pré-requisitos
Python instalado.

Permissões de administrador na máquina (necessário para o funcionamento correto de algumas bibliotecas e variáveis de ambiente).

Dependências
O projeto utiliza bibliotecas nativas do Python (os, datetime, re, secrets, functools, pathlib) e bibliotecas externas que precisam ser instaladas.

Execute o comando abaixo no seu terminal para instalar as dependências externas:

pip install flask flask-cors python-dotenv PyJWT bcrypt sib-api-v3-sdk mysql-connector-python

## Estrutura e Módulos
Importante notar que diversas importações presentes no código referem-se a módulos de nossa autoria. Estes arquivos já estão inclusos na estrutura do projeto (localizados principalmente em /app/back), não sendo necessária nenhuma instalação extra para eles.
  

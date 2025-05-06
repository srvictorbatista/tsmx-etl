

# !TSMX-ETL Documentação

## Visão Geral

Este repositório contém o projeto **TSMX-ETL**, um pipeline de ETL (Extract, Transform, Load) desenvolvido para automatizar a importação, limpeza e carga de dados relacionados ao Oscar para um banco de dados PostgreSQL. O objetivo principal deste projeto é integrar dados provenientes de arquivos em formatos `.csv`, `.xls` e `.xlsx`, processá-los de forma eficiente, normalizar e garantir sua integridade antes de armazená-los em um banco de dados relacional.

Por padrão o pipeline utiliza o Python 3.10.11 como linguagem principal, com bibliotecas como `pandas` para processamento de dados e `psycopg2` para comunicação com o PostgreSQL. Executado dentro de um container Docker, facilitando a portabilidade e replicabilidade do ambiente.


### 💡 _Por que Python 3.10.11?_
Em alguns ambientes (especialmente Linux Debian). É comum que o gerenciador de pacotes "forçe" a instalação do python 3.9.x ou 3.11.x automaticamente. Mesmo que o usuário, deixe explícito que deseja uma determinada versão do interpretador. Neste caso 3.10.11... 
Para fins de demonstração de domínio, sobre o versionamento do ambiente. Configurei especificamente, a versão 3.10.11. Mas poderia ser qualquer outra específica, a critério do dev. analista, gestor, etc...
O que pode ser observado e personalizado a seu critério/gosto no trecho: 
```bash
RUN apt-get update && apt-get install -y llvm && \
    /root/.pyenv/bin/pyenv install 3.10.11 && \
    ...
```

_Contido no arquivo "docker/config_amb". Apresentado mais a diante, em **[Estrutura do Projeto](#estrutura-do-projeto).**_
<br>&nbsp;

## Requisitos

Antes de executar o projeto, certifique-se de ter os seguintes requisitos:

### Software
- Docker e Docker-compose (obrigatórios, para execução em containers)
- Pip gerenciador de pacotes (opcional)

### Bibliotecas Python
As bibliotecas serão baixadas e incorporadas automaticamente ao contêiner gerado, e estão listadas no arquivo `requirements.txt`. Para instalá-las no hospedeiro (caso deseje). Precisará possuir Pip, instalado e disponível no host, basta executar o comando:

```bash
pip install -r requirements.txt
```

## Como usar? 

### Containers Docker
Este projeto usa o Docker para executar o banco de dados PostgreSQL, suas dependências, libs e serviços relacionados. Para isso, você precisará de uma instalação do Docker e Docker Compose.
Uma vez executado. Ele reunirá as partes necessárias, montará e configurará um ambiente completo para execução deste projeto.

#### ``Em Windows:`` 
Basta executar o arquivo "BASHEXEC.CMD"
A seguir, todo o processo se dará automaticamente. Até surgir um terminal consideravelmente maior, com a logo da TSMX, informando os serviços ativos.
<br>&nbsp; 

#### ``Em demais plataformas.`` 
Basta executar dois comandos em seu terminal:
1º Gera ambiente docker a partir do "docker-compose.yml":
```bash
docker-compose up --build
```
Quando a montagem do ambiente já estiver concluída:
2º Abra o terminal do container resultante:
```bash
docker exec -it tsmx_etl bash
```
<br>

### Notas Adicionais
(*) **Gestor Web Gráfico (WEB-GUI)**: 

Como item complementar (opcional) é erguido automaticamente, um **servidor [WEB-GUI](http://localhost:5433/)** para gestão do banco de dados **Postgres** de forma gráfica. Igualmentre personalizado para a **TSMX**.

A interface mencionada acompanha um **lugin de auto-login** que pode ser configurado (opcionalmente) para realizar **login de forma automatica** ou realizar o preenchimento parcial das **credenciais de acesso**. 

**Senha padrão:** 
```
postgres
```

<br>&nbsp; <br>&nbsp;

### No terminal (BASH)
-----
Uma vez diante do terminal do container \tsmx_etl\ execute:
```bash
ETL
```
ou:
```bash
etl
```
igualmente aceito:
```bash
python etl.py
```

Em seguida lhe será pedido o nome e local, do arquivo de origem dos dados. Recomendo alojar seus arquivos na pasta "imports/" do projeto. O que corresponderá a "\imports\seu_arquivo.(CSV, XLS ou XLSX)" no terminal de importação.

<br> &nbsp; 

## Estrutura do Projeto

A estrutura do projeto a seguir:

```
.
├── backups/                  # Arquivos de backup e logs
├── docker/                   # Arquivos de configuração do Docker
│   └── config_amb            # Configurações do ambiente de execução
│   └── schema_db.txt         # Descreve a estrutura do banco de dados
│   └── brand                 # Imagem (png) a ser exibida na apresentação do terminal
├── imports/                  # Contém os arquivos de dados para importação
├── app/                      # Diretório de execução do processo ETL (abriga os scripts)
│   └── etl.py                # Script principal responsável pela manipulação dos dados
├── docker-compose.yml        # Arquivo de orquestração do Docker
├── requirements.txt          # Lista de bibliotecas do Python (consulta e instação opcional)
└── README.md                 # Este arquivo de documentação
```

- `etl.py`: O script principal que executa o processo ETL, incluindo leitura de arquivos, transformação dos dados e inserção no banco.
- `backups/`: Diretório onde os arquivos de dados importados e logs de erro são armazenados.
- `docker/`: Contém os arquivos de configuração do ambiente Docker para o interpretador python, banco de dados PostgreSQL e Adminer (interface de administração web).
- `imports/`: Local onde recomenda-se colocar os arquivos `.csv`, `.xls` ou `.xlsx` para serem importados.
- `docker-compose.yml`: Arquivo para orquestrar o container Docker (que abrigará o ambiente da aplicação).
- `requirements.txt`: Lista das bibliotecas Python usadas no projeto.

## Fluxo do Script

### 1. Recebimento e Validação do Arquivo

A função `receber_arquivo()` solicita ao usuário o caminho de um arquivo e valida:

- Se o caminho informado existe.
- Se a extensão do arquivo é suportada (`.csv`, `.xls`, `.xlsx`).

Após a validação, o arquivo é copiado para o diretório `backups/`.

### 2. Leitura dos Dados

A função `carregar_arquivo()` usa a biblioteca `pandas` para importar os dados do arquivo. Caso o arquivo seja um Excel, o script detecta automaticamente o motor apropriado (`openpyxl` ou `xlrd`).

### 3. Visualização Inicial

A função `visualizar_arquivo()` permite ao usuário visualizar as primeiras linhas do arquivo para conferência, facilitando a validação do conteúdo antes do processamento completo.


### 4. Normalização e limpeza dos Dados

#### Função `normalizar_dataframe`
Esta função tem como objetivo **normalizar, limpar e padronizar** um `DataFrame` do `pandas`.
A função `normalizar_dataframe()` realiza várias tarefas para garantir que os dados sejam consistentes e prontos para inserção no banco de dados:

```python
def normalizar_dataframe(df):
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
    for col in ['note', 'detail', 'nominees', 'name', 'movie', 'category', 'class']:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str).str.strip()
    df['winner'] = df['winner'].fillna(False)
    df['winner'] = df['winner'].apply(lambda x: str(x).strip().lower() in ['true', '1', 'yes'])
    obrigatorias = ["ceremony", "year", "class", "category", "movie", "winner"]
    for col in obrigatorias:
        if col not in df.columns:
            raise Exception(f"🛑 Coluna obrigatória ausente: {col}")
    return df
```
- Normaliza os nomes das colunas para o formato `snake_case`.
- Remove espaços em branco e valores nulos.
- Converte campos booleanos (como o campo `winner`) para `True` ou `False`.
- Valida a presença de colunas obrigatórias: 
  - `ceremony`
  - `year`
  - `class`
  - `category`
  - `movie`
  - `winner`
 
  
Tão curta, que há quem passe pelo código se perguntando **"_... mas onde está a limpeza e tratamento dos dados?_"** 
Por isso, não se engane: _Apesar de curta. esta função faz tantos tratamentos, que achei por bem. Dividir sua explicação em **4 sub-etapas**. As quais, veremos a seguir._
 <br>&nbsp;
****************************
### Sub-etapas da Função ```normalizar_dataframe```

#### 4.1. Normalização dos nomes das colunas

-   Remove espaços em branco no início e fim de cada nome de coluna (`strip()`).
    
-   Converte todas as letras para minúsculas (`lower()`).
    
-   Substitui espaços por underscores (`_`), garantindo nomes de colunas compatíveis com boas práticas de manipulação de dados.
    

#### 4.2. Limpeza de colunas específicas

```python
for col in ['note', 'detail', 'nominees', 'name', 'movie', 'category', 'class']:
    if col in df.columns:
        df[col] = df[col].fillna("").astype(str).str.strip()

```

-   Para colunas específicas (se existirem), substitui valores nulos por strings vazias.
    
-   Garante que os dados nessas colunas sejam do tipo string.
    
-   Remove espaços em branco nas extremidades dos textos. Algo similar ao ``trim()`` em outras linguagens.
    

#### 4.3. Padronização da coluna `winner`

```python
df['winner'] = df['winner'].fillna(False)
df['winner'] = df['winner'].apply(lambda x: str(x).strip().lower() in ['true', '1', 'yes'])

```

-   Preenche valores nulos da coluna `winner` com `False`.
    
-   Converte os valores da coluna para string, remove espaços e transforma em minúsculo.
    
-   Interpreta como `True` os valores que correspondem a `'true'`, `'1'` ou `'yes'`.
    
-   Todo o resto será interpretado como `False`.
    

#### 4.4. Validação de colunas obrigatórias

```python
obrigatorias = ["ceremony", "year", "class", "category", "movie", "winner"]
for col in obrigatorias:
    if col not in df.columns:
        raise Exception(f"🛑 Coluna obrigatória ausente: {col}")
```

-   Define uma lista de colunas obrigatórias.
    
-   Verifica se cada uma dessas colunas está presente no `DataFrame`.
    
-   Caso alguma coluna esteja ausente, lança uma exceção indicando qual coluna está faltando.
    

----------

#### Observações

-   Apesar de curta. Esta função é robusta contra ausência de colunas, mas exigente com relação às colunas obrigatórias. O que exigirá atenção extra, durante modificações futuras deste projeto. Dado seu poder de atuação neste projeto.
    
-   Ela assume que a coluna `winner` pode vir com diferentes formatos booleanos (`True`, `1`, `yes`, etc.) e trata isso de forma prática.
    
-   A limpeza de texto evita problemas comuns em análises de dados, como duplicações ou agrupamentos errados causados por espaços em branco ou variações de maiúsculas/minúsculas.

- Possui uma implementação extremamente curta, prática e (modéstia a parte), elegante. Diante de alternativas com a mesma finalidade.

- Resumidamente: É baixinha, mas invocada! **_Por tanto, não menospreze seu tamanho..._** 
Dedique a ela, o respeito e atenção que ela merece.

****************************
 <br>&nbsp;

### 5. Inserção no Banco de Dados

O script usa `psycopg2` para conectar ao banco de dados PostgreSQL. As etapas de inserção são:

- Dados de cada categoria (`tbl_oscar`, `tbl_class`, `tbl_category`, `tbl_movie`) são inseridos com validação de duplicação. O comando `ON CONFLICT DO NOTHING` é utilizado para evitar inserções duplicadas.
- Os dados normalizados dos indicados e vencedores (`tbl_nominees`) são inseridos após a validação.

### 6. Tratamento de Erros

Se ocorrerem erros durante o processamento de uma linha (como valores ausentes ou exceções de tipo), essas linhas são registradas e ignoradas. Os detalhes do erro são registrados em um arquivo `aliás_de_origem.log` dentro do diretório `backups/`, contendo:

- A linha do erro
- Os dados originais da linha
- O motivo do erro
- Onde "aliás_de_origem" é o nome do arquivo de origem dos dados, correspondente ao log.

Caso um arquivo de log seja gerado durante o processamento. A leitura dele será oferecida de forma interativa. Podendo ser posteriormente, reexibida em tela com o comando: 
```cat(backups/aliás_de_origem.log)``` . 


### 7. Resumo Final

Ao final do processo de importação, o script exibe um resumo com:

- O número total de registros importados com sucesso.
- O número de registros rejeitados.
- O caminho do arquivo de log gerado (se houver rejeições).
- Opção (S/N) para leitura imediata do log, por meio de cat() simples e diretamente no terminal.

## Estrutura do Banco de Dados

Conforme conteúdo SQL do arquivo "docker/schema_db.txt". O banco de dados utiliza as seguintes tabelas principais:

```sql
CREATE TABLE tbl_oscar (
    id SERIAL PRIMARY KEY,
    ceremony INTEGER UNIQUE NOT NULL,
    year INTEGER NOT NULL
);

CREATE TABLE tbl_class (
    id SERIAL PRIMARY KEY,
    description TEXT UNIQUE NOT NULL
);

CREATE TABLE tbl_category (
    id SERIAL PRIMARY KEY,
    description TEXT UNIQUE NOT NULL
);

CREATE TABLE tbl_movie (
    id SERIAL PRIMARY KEY,
    title TEXT UNIQUE NOT NULL
);

CREATE TABLE tbl_nominees (
    id SERIAL PRIMARY KEY,
    oscar_id INTEGER REFERENCES tbl_oscar(id),
    class_id INTEGER REFERENCES tbl_class(id),
    category_id INTEGER REFERENCES tbl_category(id),
    movie_id INTEGER REFERENCES tbl_movie(id),
    name TEXT,
    nominees TEXT,
    winner BOOLEAN,
    detail TEXT,
    note TEXT
);
```

### Descrição das Tabelas:

- `tbl_oscar`: Armazena informações sobre a cerimônia e o ano do Oscar.
- `tbl_class`: Armazena categorias de premiação, como "Atuação", "Produção", etc.
- `tbl_category`: Armazena descrições de subcategorias de prêmios, como "Melhor Ator", "Melhor Filme", etc.
- `tbl_movie`: Armazena informações sobre os filmes indicados.
- `tbl_nominees`: Armazena os indicados, com referências às outras tabelas, além de informações como o vencedor e detalhes adicionais.


## Execução do Script

Para executar o processo ETL, basta rodar o script `etl.py`. Conforme já informado em **[No terminal (BASH)](#No-terminal-bash)**

## Auditoria e Logs

Todos os arquivos processados são copiados para o diretório `backups/`. Caso ocorram erros durante o processamento, um log detalhado é gerado contendo:

- Motivo da falha
- Linha do erro
- Dados da linha


Este log pode ser consultado logo após o processamento ou posteriormente, acessando a pasta de backups.
veja detalhes sobre, em **[tratamento de erros](#6-tratamento-de-erros)**

## Extensão e Customização

O código foi desenvolvido de forma modular para facilitar a manutenção e extensões:

- É possível adicionar novas validações específicas para cada coluna.
- Novas tabelas e relações podem ser facilmente integradas ao sistema.
- O projeto pode ser adaptado para outros bancos de dados com mínimas modificações.

## Sobre !TSMX-ETL

**Autor:** Victor Batista  
**GitHub:** [https://github.com/srvictorbatista](https://github.com/srvictorbatista)  
**LinkedIn:** [https://linkedin.com/in/levymac](https://linkedin.com/in/levymac)  
**Contato no Telegram:** [@LevyMac](https://t.me/levymac)    

Profissional com experiência em engenharia de dados, desenvolvimento, infraestrutura e automações, com foco em soluções escaláveis e seguras. Este projeto foi desenvolvido a partir de uma interação com a TSMX (Provedor de Sistemas) para avaliar minhas habilidades de automação em processos de dados estruturados em bancos relacionais. O que espero, ter correspondido às expectativas.

## Repositório

**URL do repositório GitHub:**  
[https://github.com/srvictorbatista/tsmx-etl](https://github.com/srvictorbatista/tsmx-etl)

O repositório contém:

- O aplicação pipeline ETL.
- Servidor de banco de dados PostgresSQL
- Servidor web com [WEB-GUI](http://localhost:5433/) para gestão do banco de dados Postgres.
- O arquivo de documentação `README.md` (este aqui).
- Scripts auxiliares para configuração e montagem do ambiente de execução.
- A estrutura de diretórios, arquivos, logs e demais dados podem ser revisitados em: **[estrutura do projeto](#estrutura-do-projeto)**

**Uma vez atendendo aos requisitos deste projeto (Docker e Docker-compose). Este repositório deverá ser capaz de criar um ambiente completo e totalmente autônomo, para a execução do pipeline.**

## Objetivo do Projeto

O objetivo deste projeto é automatizar o processo de extração, transformação e carga (ETL) de dados, provenientes de arquivos `.csv`, `.xls` e `.xlsx`, para um banco de dados PostgreSQL relacional.
Veja mais detalhes na seção **[Sobre !TSMX-ETL](#sobre-tsmx-etl)**

## Público-Alvo

**Este projeto é destinado a:**

- Engenheiros de dados e cientistas de dados que lidam com dados tabulares recorrentes.
- Equipes de BI/DataOps que precisam garantir a rastreabilidade e a integridade da ingestão de dados.
- Desenvolvedores que trabalham com pipelines de dados automatizados em ambientes corporativos.
- Gestores de infraestrutura que lidam com a configurações de automação para  ambientes de desenvolvimento, seguros e modulares. 

## Tecnologias Amparadas

- **Python 3.10.+**
- **Pandas**
- **psycopg2**
- **PostgreSQL 13+**
- **openpyxl** / **xlrd** 
- **Apache:** 
- **TZ-Data**
- **PHP** / **Plugin-Adminer**

## Licença

Este projeto está licenciado sob a Licença MIT, no estado em que se encontra. Sem limitações de uso ou distribuição.

### Dúvidas? [Faça contato com o autor, aqui](#sobre-tsmx-etl)

<br>&nbsp; <br>&nbsp; <br>&nbsp; <br>&nbsp; <br>&nbsp;

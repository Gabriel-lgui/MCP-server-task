# MCP Server - Usuários com Busca Semântica

Servidor MCP (Model Context Protocol) que permite a um agente de IA criar usuários, armazená-los com busca vetorial e realizar buscas semânticas sobre os dados.

## Arquitetura

```
server.py         -> Expõe as tools MCP
database.py       -> Persistência relacional (SQLite ou PostgreSQL)
embeddings.py     -> Geração de embeddings com sentence-transformers
vector_store.py   -> Índice FAISS para busca semântica
models.py         -> Modelos Pydantic (validação e serialização)
tests.py          -> Testes automatizados dos módulos principais
pytest.ini        -> Configuração do pytest com modo assíncrono
faiss_index/      -> Índice FAISS persistido em disco
```

**Por que FAISS + SQL?**
O banco SQL armazena os dados relacionais dos usuários. O FAISS armazena os vetores e realiza as buscas semânticas com alta performance. Os dois são ligados pelo campo `embedding_id` na tabela de usuários.

## Requisitos

- Python 3.11+
- Node.js 18+ (para o MCP Inspector)

Opcional:
- PostgreSQL (a instalação já é feita com SQLite, mas também suporta PostgreSQL)

## Instalação

Baixe o .zip dos arquivos acima e no terminal git-bash:
```bash
cd <Local da pasta>
```

Ou clone o repositório:
```bash
git clone <url-do-repositorio>
cd mcp-server-task
```

Crie e ative o ambiente virtual:
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

Instale as dependências:
```bash
pip install mcp fastmcp sqlalchemy aiosqlite asyncpg python-dotenv \
            faiss-cpu sentence-transformers \
            pytest pytest-asyncio
```

## Configuração

Crie um arquivo `.env` na raiz do projeto:

```env
# SQLite (padrão, não requer instalação)
DATABASE_URL=sqlite+aiosqlite:///./users.db

# PostgreSQL (descomentar para usar)
# DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname
```

## Como rodar

**Subir o servidor com o MCP Inspector:**
```bash
npx @modelcontextprotocol/inspector python server.py
```
O programa deve direcionar automaticamente para o navegador,
mas caso não aconteça, acesse `http://localhost:6274`.

**Rodar os testes:**
```bash
pytest tests.py -v
```

## Ferramentas MCP

# `create_user`:
Cria um novo usuário, gera embedding da descrição e armazena no FAISS.

**Resposta:**
```json
{ "id": 1 }
```

# `search_users`:
Busca usuários com descrições similares à query.

**Resposta:**
```json
[
  {
    "id": 1,
    "name": "Ana Lima",
    "email": "ana@email.com",
    "description": "Engenheira de software especializada em IA e machine learning",
    "score": 1.13
  }
]
```

# `get_user`:
Busca um usuário pelo ID.

**Resposta (sucesso):**
```json
{ "id": 1, "name": "Ana Lima", "email": "ana@email.com", "description": "..." }
```
**Resposta (não encontrado):**
```json
{ "error": "Usuário id=<id> não encontrado." }
```

# `list_users`:
Lista todos os usuários cadastrados. Não requer parâmetros.

**Resposta:**
```json
[
  { "id": 1, "name": "Ana Lima", "email": "ana@email.com", "description": "..." },
  { "id": 2, "name": "Carlos Melo", "email": "carlos@email.com", "description": "..." }
]
```

## Exemplos de uso

### 1. Criar usuários

Cadastre 3 usuários com descrições distintas:

**Request:**
```json
{ "name": "Ana Lima", "email": "ana@email.com", "description": "Engenheira de software especializada em IA e machine learning" }
```
**Retorna:**
```json
{ "id": 1 }
```

**Request:**
```json
{ "name": "Carlos Melo", "email": "carlos@email.com", "description": "Designer UX focado em acessibilidade e interfaces inclusivas" }
```
**Retorna:**
```json
{ "id": 2 }
```

**Request:**
```json
{ "name": "Beatriz Costa", "email": "bia@email.com", "description": "Cientista de dados com foco em NLP e processamento de linguagem" }
```
**Retorna:**
```json
{ "id": 3 }
```

### 2. Listar todos os usuários

**Request:** nenhum parâmetro necessário.

**Retorna:**
```json
[
  { "id": 1, "name": "Ana Lima", "email": "ana@email.com", "description": "Engenheira de software especializada em IA e machine learning" },
  { "id": 2, "name": "Carlos Melo", "email": "carlos@email.com", "description": "Designer UX focado em acessibilidade e interfaces inclusivas" },
  { "id": 3, "name": "Beatriz Costa", "email": "bia@email.com", "description": "Cientista de dados com foco em NLP e processamento de linguagem" }
]
```


### 3. Busca semântica

Busca por usuários relacionados a inteligência artificial — mesmo sem usar as palavras exatas das descrições:

**Request:**
```json
{ "query": "profissional de inteligência artificial", "top_k": 2 }
```

**Retorna:**
```json
[
  {
    "id": 1,
    "name": "Ana Lima",
    "email": "ana@email.com",
    "description": "Engenheira de software especializada em IA e machine learning",
    "score": 1.1383811235427856
  },
  {
    "id": 2,
    "name": "Carlos Melo",
    "email": "carlos@email.com",
    "description": "Designer UX focado em acessibilidade e interfaces inclusivas",
    "score": 1.2554905414581299
  }
]
```

O campo `score` representa a distância euclidiana no espaço vetorial, quanto menor, mais similar. Ana aparece em primeiro por ter a descrição semanticamente mais próxima da query.


### 4. Buscar usuário por ID

**Request:**
```json
{ "user_id": 1 }
```

**Retorna:**
```json
{ "id": 1, "name": "Ana Lima", "email": "ana@email.com", "description": "Engenheira de software especializada em IA e machine learning" }
```


### 5. Buscar usuário inexistente

**Request:**
```json
{ "user_id": 999 }
```

**Retorna:**
```json
{ "error": "Usuário id=999 não encontrado." }
```
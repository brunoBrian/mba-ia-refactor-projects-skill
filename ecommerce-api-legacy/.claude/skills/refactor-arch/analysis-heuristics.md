# Heurísticas de Análise de Projeto

## 1. Detecção de Linguagem

| Indicador | Linguagem |
|-----------|-----------|
| Arquivos `.py` + `requirements.txt` | Python |
| Arquivos `.js` ou `.ts` + `package.json` | Node.js |
| Arquivos `.rb` + `Gemfile` | Ruby |
| Arquivos `.php` + `composer.json` | PHP |
| Arquivos `.java` + `pom.xml` ou `build.gradle` | Java |
| Arquivos `.go` + `go.mod` | Go |

**Versão Python:** leia `python --version` ou inferir do `requires-python` em `setup.cfg` / `pyproject.toml`.
**Versão Node.js:** leia `engines.node` em `package.json` ou inferir do ambiente.

---

## 2. Detecção de Framework

### Python
| Indicador no código ou requirements | Framework |
|--------------------------------------|-----------|
| `from flask import Flask` / `flask` em requirements | Flask |
| `from django.db import models` / `django` em requirements | Django |
| `from fastapi import FastAPI` / `fastapi` em requirements | FastAPI |

### Node.js
| Indicador em package.json ou código | Framework |
|--------------------------------------|-----------|
| `"express"` em dependencies | Express |
| `"fastify"` em dependencies | Fastify |
| `"koa"` em dependencies | Koa |
| `"@nestjs/core"` em dependencies | NestJS |

**Versão do framework:** leia `requirements.txt` (Python) ou `package.json > dependencies` (Node.js).

---

## 3. Detecção de Banco de Dados

### SQL Raw (sem ORM)
| Indicador | Banco |
|-----------|-------|
| `sqlite3.connect(...)` em Python | SQLite |
| `new sqlite3.Database(...)` em Node.js | SQLite |
| `psycopg2.connect(...)` | PostgreSQL |
| `mysql.connector.connect(...)` | MySQL |
| Strings SQL com `SELECT`, `INSERT`, `UPDATE`, `DELETE` concatenadas com variáveis | SQL Injection risk |

### ORM
| Indicador | ORM |
|-----------|-----|
| `from flask_sqlalchemy import SQLAlchemy` | SQLAlchemy via Flask |
| `from sqlalchemy import ...` | SQLAlchemy puro |
| `const { Sequelize } = require('sequelize')` | Sequelize |
| `const { PrismaClient } = require('@prisma/client')` | Prisma |

**Tabelas:** procure por `CREATE TABLE` em scripts de inicialização, `db.Model` subclasses (SQLAlchemy), ou `run("CREATE TABLE ...")` (sqlite3 Node.js).

---

## 4. Mapeamento de Arquitetura

### Monolito (tudo em 1-3 arquivos)
**Sinais:**
- Arquivo único > 200 linhas contendo rotas + queries SQL + lógica de negócio
- Funções de roteamento no mesmo arquivo que funções de banco
- Sem diretórios de separação (models/, controllers/, routes/)

**Exemplos típicos:**
- `app.py` com rotas, queries e lógica misturadas
- `AppManager.js` com DB init, routes e business logic na mesma classe

### MVC Parcial
**Sinais:**
- Diretórios `models/`, `routes/`, `services/` existem, mas:
  - Routes contêm lógica de negócio além de roteamento
  - Models contêm validação que deveria estar no controller
  - Não existe diretório `controllers/`
  - Config está hardcoded em vez de em arquivo separado

### MVC Completo
**Sinais:**
- `models/` — apenas acesso a dados e relacionamentos
- `controllers/` — apenas coordenação de fluxo (recebe request, chama model, retorna response)
- `routes/` — apenas registro de endpoints e delegação para controllers
- `config/` — configurações separadas do código
- `middlewares/` — tratamento de erros e autenticação centralizados

---

## 5. Inventário de Arquivos

Para cada arquivo-fonte (.py, .js, .ts excluindo node_modules, .venv, __pycache__):

1. Conte as linhas
2. Identifique a responsabilidade principal:
   - `entry-point` — inicializa e sobe a aplicação
   - `route` — registra endpoints HTTP
   - `controller` — coordena fluxo de request/response
   - `model` — acesso a dados
   - `service` — lógica de negócio
   - `middleware` — interceptadores de request/response
   - `config` — configurações
   - `util` — funções auxiliares
   - `mixed` — múltiplas responsabilidades (code smell)

---

## 6. Domínio da Aplicação

Infira o domínio pelas tabelas do banco e pelos nomes de rotas/endpoints:

| Tabelas / Rotas encontradas | Domínio provável |
|-----------------------------|------------------|
| produtos, pedidos, usuarios | E-commerce API |
| courses, enrollments, payments | LMS / Plataforma de cursos |
| tasks, users, categories | Task Manager |
| posts, comments, users | Blog / CMS |
| patients, appointments | Healthcare |

---

## 7. Formato do Bloco de Resumo

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python 3.x / Node.js 18.x
Framework:     Flask 3.1.1 / Express 4.18.2
Dependencies:  flask-cors, flask-sqlalchemy / sqlite3, bcryptjs
Domain:        E-commerce API (produtos, pedidos, usuários)
Architecture:  Monolítica — 4 arquivos, sem separação de camadas
Source files:  4 files analyzed (~800 lines total)
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================
```

# Desafio Skills — Refatoração Arquitetural Automatizada

Skill `/refactor-arch` para Claude Code que automatiza análise, auditoria e refatoração de projetos legados para o padrão MVC.

---

## Análise Manual

### Projeto 1 — code-smells-project (Python/Flask)

| Severidade | Problema | Arquivo |
|-----------|----------|---------|
| CRITICAL | SQL Injection via concatenação em todos os métodos | models.py:28, 48, 56, 68, 92, 108 |
| CRITICAL | SECRET_KEY hardcoded | app.py:7 |
| CRITICAL | SECRET_KEY exposta na resposta do /health | controllers.py:289 |
| CRITICAL | Endpoint /admin/query executa SQL arbitrário sem auth | app.py:59-78 |
| CRITICAL | Senhas em plaintext no banco (seed + login) | database.py:76-83 |
| HIGH | Senhas expostas nas respostas GET /usuarios | models.py:82-86 |
| HIGH | Notificações (side effects) dentro do controller | controllers.py:208-210 |
| MEDIUM | Query N+1 em pedidos (cursor2, cursor3 dentro de loop) | models.py:171-200 |
| MEDIUM | Variável global mutável para conexão DB | database.py:4 |
| LOW | Import `sqlite3` não utilizado | models.py:2 |

**Justificativas principais:**
- **SQL Injection** é o mais crítico: toda a camada de dados usa concatenação, tornando 100% dos endpoints vulneráveis a ataques de banco.
- **Admin sem autenticação** permite destruição total dos dados por qualquer usuário.
- **Senhas plaintext** garantem vazamento completo de credenciais em caso de dump do banco.

---

### Projeto 2 — ecommerce-api-legacy (Node.js/Express)

| Severidade | Problema | Arquivo |
|-----------|----------|---------|
| CRITICAL | Credenciais de produção hardcoded (dbPass, paymentGatewayKey) | src/utils.js:1-7 |
| CRITICAL | God Class: DB + rotas + pagamento + audit numa classe | src/AppManager.js:1-141 |
| CRITICAL | Callback hell de 5 níveis no /checkout | src/AppManager.js:28-78 |
| HIGH | badCrypto: base64 como "hash" de senha | src/utils.js:17-23 |
| HIGH | /admin/financial-report sem autenticação | src/AppManager.js:80 |
| HIGH | DELETE de usuário deixa matrículas e pagamentos órfãos | src/AppManager.js:131-137 |
| MEDIUM | In-memory database — dados perdidos ao reiniciar | src/AppManager.js:7 |
| MEDIUM | Query N+1 no relatório financeiro | src/AppManager.js:88-128 |
| LOW | Nomes de variáveis crípticos (u, e, p, cid, cc) | src/AppManager.js:29-34 |
| LOW | `totalRevenue` exportado mas nunca usado | src/utils.js:10 |

**Justificativas principais:**
- **God Class** é a violação arquitetural mais grave: impede qualquer teste ou evolução isolada.
- **Chave de pagamento `pk_live_`** hardcoded representa risco financeiro direto.
- **Cascade delete ausente** é mencionado na própria resposta da API, confirmando o bug intencional.

---

### Projeto 3 — task-manager-api (Python/Flask)

| Severidade | Problema | Arquivo |
|-----------|----------|---------|
| CRITICAL | Credenciais SMTP hardcoded (email + senha) | services/notification_service.py:9-10 |
| CRITICAL | Token JWT fake e previsível (`fake-jwt-token-` + id) | routes/user_routes.py:210 |
| HIGH | Falta de camada Controller — lógica nas routes | routes/*.py |
| HIGH | is_overdue duplicado em 5 lugares (método já existe no Model) | routes/task_routes.py, user_routes.py |
| HIGH | Senha com MD5 (reversível com rainbow tables) | models/user.py:27-32 |
| MEDIUM | Model.query.get() deprecated em SQLAlchemy 2.0 | routes/task_routes.py:67 (e outros) |
| MEDIUM | Bare except silencia todos os erros | routes/task_routes.py:62, 138 |
| MEDIUM | Campo password exposto em User.to_dict() | models/user.py:16-25 |
| LOW | Mínimo de senha: 4 caracteres (insuficiente) | routes/user_routes.py:64 |
| LOW | process_task_data() em helpers duplica validação das routes | utils/helpers.py:57-108 |

**Justificativas principais:**
- Mesmo com organização parcial existente, a **ausência de controllers** faz as routes acumularem 300+ linhas.
- **MD5 para senhas** é pior que bcrypt pois não tem salt e é otimizado para velocidade — ideal para atacantes.
- **Token previsível** torna qualquer autenticação inútil.

---

## Construção da Skill

### Estrutura do SKILL.md

A skill foi estruturada em 3 fases sequenciais com instruções explícitas de comportamento:

1. **Fase 1 (Análise)** — somente leitura, produz bloco de resumo padronizado
2. **Fase 2 (Auditoria)** — cruzamento com catálogo, relatório formatado, **pausa obrigatória** antes de qualquer escrita
3. **Fase 3 (Refatoração)** — escrita guiada pelo `refactoring-guide.md`, com validação de boot ao final

A pausa na Fase 2 é implementada como instrução direta: "Aguarde a resposta do usuário. Se a resposta não for 'y' ou 'yes', encerre sem modificar nenhum arquivo."

### Arquivos de Referência

**`analysis-heuristics.md`** — Cobre detecção de linguagem (por extensão + arquivo de dependências), framework (por imports), banco de dados (ORM vs SQL raw), e mapeamento de arquitetura em 3 níveis (monolito, MVC parcial, MVC completo).

**`antipatterns-catalog.md`** — 13 anti-patterns com sinais de detecção específicos e acionáveis (não "código ruim", mas "query SQL dentro de for loop"). Inclui o template exato do relatório que a Fase 2 deve gerar.

**`refactoring-guide.md`** — Tabela de responsabilidades MVC + estrutura de diretórios alvo para Python e Node.js + 10 padrões de transformação com exemplos de código antes/depois.

### Agnóstica de Tecnologia

A skill é agnóstica por design:
- `analysis-heuristics.md` tem tabelas de detecção para Python, Node.js, Ruby, PHP, Java
- Os sinais de detecção de anti-patterns incluem equivalentes Python e Node.js (ex: SQL Injection em ambas as sintaxes)
- O `refactoring-guide.md` tem estruturas de diretório e exemplos de código para Python/Flask E Node.js/Express
- A instrução de validação na Fase 3 tem os dois comandos: `python -c "from app import app"` OU `node --check src/app.js`

### Desafios e Soluções

**Desafio:** Como fazer a skill adaptar a refatoração ao contexto (monolito vs. MVC parcial)?
**Solução:** Regras explícitas no SKILL.md: "Monolito → criar estrutura MVC completa do zero; MVC Parcial → melhorar incrementalmente mantendo o que já funciona."

**Desafio:** Garantir que a Fase 2 sempre pause antes de modificar arquivos.
**Solução:** Instrução em negrito + exemplo do prompt exato que o agente deve fazer ao usuário.

---

## Resultados

### Resumo dos Relatórios de Auditoria

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---------|----------|------|--------|-----|-------|
| code-smells-project | 5 | 2 | 2 | 1 | 10 |
| ecommerce-api-legacy | 3 | 3 | 2 | 2 | 10 |
| task-manager-api | 2 | 3 | 3 | 2 | 10 |

### Comparação Antes/Depois

#### Projeto 1 — code-smells-project
| Aspecto | Antes | Depois |
|---------|-------|--------|
| Arquitetura | 4 arquivos planos (app, controllers, models, database) | src/{config,models,controllers,middlewares} |
| SQL Injection | Toda a models.py vulnerável | Queries parametrizadas em 100% dos métodos |
| Senhas | Plaintext no banco | werkzeug.security hash |
| Config | SECRET_KEY hardcoded | os.environ.get() + .env.example |
| Admin | /admin/query executa SQL arbitrário | Endpoint removido |
| Health | Expõe secret_key | Apenas status e contagens |

#### Projeto 2 — ecommerce-api-legacy
| Aspecto | Antes | Depois |
|---------|-------|--------|
| Arquitetura | 1 God Class (AppManager) | models + controllers + routes + database |
| Callback depth | 5 níveis aninhados | async/await linear |
| Criptografia | base64 "hash" (10 chars) | bcryptjs (cost factor 12) |
| Credenciais | 3 chaves de produção no código | process.env + .env.example |
| Delete | Dados órfãos no banco | Cascade delete completo |

#### Projeto 3 — task-manager-api
| Aspecto | Antes | Depois |
|---------|-------|--------|
| Arquitetura | Routes com 300+ linhas de lógica | Routes finas + controllers dedicados |
| is_overdue | Duplicado em 5 lugares | t.is_overdue() centralizado |
| Senha hash | MD5 (reversível) | werkzeug.security |
| Credenciais | SMTP hardcoded | config/settings.py via env |
| SQLAlchemy | Model.query.get() deprecated | db.session.get(Model, id) |
| Erros | Bare except silencioso | except Exception as e com rollback |

### Checklist de Validação

#### Projeto 1
- [x] Linguagem detectada: Python
- [x] Framework detectado: Flask 3.1.1
- [x] Domínio: E-commerce API
- [x] 4 arquivos analisados
- [x] Relatório gerado com template correto
- [x] Findings com arquivo e linha exatos
- [x] Ordenado CRITICAL → LOW
- [x] 10 findings identificados (> 5)
- [x] Pelo menos 1 CRITICAL
- [x] Skill pausa antes da Fase 3
- [x] Estrutura MVC criada (src/{config,models,controllers,middlewares})
- [x] Config extraída para settings.py
- [x] Models com queries parametrizadas
- [x] Controllers separados por domínio
- [x] Error handling centralizado
- [x] Application boots: `Boot OK`
- [x] Endpoints preservados

#### Projeto 2
- [x] Linguagem: Node.js
- [x] Framework: Express 4.18.2
- [x] Domínio: LMS API (cursos, matrículas, pagamentos)
- [x] 3 arquivos analisados
- [x] 10 findings com arquivo:linha
- [x] Ordenado CRITICAL → LOW
- [x] Pelo menos 1 CRITICAL
- [x] Estrutura MVC: src/{config,database,models,controllers,routes,middlewares}
- [x] Credenciais → process.env
- [x] Callback hell → async/await
- [x] badCrypto → bcryptjs
- [x] Syntax OK: `node --check`

#### Projeto 3
- [x] Linguagem: Python
- [x] Framework: Flask 3.0.0 + SQLAlchemy
- [x] Domínio: Task Manager
- [x] 11 arquivos analisados
- [x] 10 findings identificados
- [x] Inclui detecção de API deprecated (SQLAlchemy)
- [x] Camada controllers/ criada
- [x] is_overdue centralizado no Model
- [x] werkzeug.security no lugar do MD5
- [x] SMTP credentials → env vars
- [x] Bare except → except Exception com rollback
- [x] Application boots: `Boot OK`

### Comportamento em Stacks Diferentes

A skill se adaptou corretamente ao nível de organização de cada projeto:

- **Projeto 1 (monolito):** criou estrutura MVC completa do zero, movendo queries SQL para models parametrizados e validação para controllers.
- **Projeto 2 (Node.js):** aplicou async/await e bcryptjs nativamente; a detecção de callback hell (padrão específico de JS) funcionou conforme esperado.
- **Projeto 3 (MVC parcial):** não reestruturou o que já estava correto (models/ e routes/ existentes), apenas adicionou a camada controllers/ ausente e corrigiu problemas de qualidade.

---

## Como Executar

### Pré-requisitos
- Claude Code instalado e configurado
- Python 3.10+ (projetos 1 e 3)
- Node.js 18+ (projeto 2)

### Projeto 1 — code-smells-project

```bash
cd code-smells-project
pip install -r requirements.txt
claude "/refactor-arch"
```

### Projeto 2 — ecommerce-api-legacy

```bash
cd ecommerce-api-legacy
npm install
claude "/refactor-arch"
```

### Projeto 3 — task-manager-api

```bash
cd task-manager-api
pip install -r requirements.txt
claude "/refactor-arch"
```

### Validando que a Refatoração Funcionou

**Python (projetos 1 e 3):**
```bash
python3 -c "from app import app; print('Boot OK')"
```

**Node.js (projeto 2):**
```bash
node --check src/app.js && echo "Syntax OK"
```

### Iniciando as aplicações

**Projetos Python:**
```bash
# Criar .env a partir do .env.example
cp .env.example .env
python3 app.py
```

**Projeto Node.js:**
```bash
cp .env.example .env
npm start
```

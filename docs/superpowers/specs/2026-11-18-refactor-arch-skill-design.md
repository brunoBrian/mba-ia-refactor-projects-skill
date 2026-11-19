# Skill refactor-arch — Design

Data: 2026-11-18

## Objetivo

Criar a skill `/refactor-arch` para Claude Code que automatiza análise, auditoria e refatoração de projetos legados para o padrão MVC. Executar a skill nos 3 projetos fornecidos e entregar o repositório completo com código refatorado, relatórios de auditoria e documentação.

## Estrutura da Skill

Localização: `.claude/skills/refactor-arch/` (copiada para os 3 projetos)

Arquivos:
- `SKILL.md` — instruções das 3 fases sequenciais
- `analysis-heuristics.md` — heurísticas de detecção de stack e arquitetura
- `antipatterns-catalog.md` — catálogo de anti-patterns com sinais de detecção e severidades
- `refactoring-guide.md` — guidelines MVC + playbook de transformações antes/depois

## Fases da Skill

### Fase 1 — Análise
- Detectar linguagem, framework, versão e dependências
- Mapear arquitetura atual (monolito / MVC parcial / MVC completo)
- Inventariar arquivos-fonte e banco de dados
- Imprimir resumo formatado

### Fase 2 — Auditoria
- Cruzar código contra `antipatterns-catalog.md`
- Gerar relatório estruturado: severidade, arquivo:linha, descrição, impacto, recomendação
- Ordenar: CRITICAL → HIGH → MEDIUM → LOW
- Incluir detecção de APIs deprecated
- **Parar e pedir confirmação** antes de qualquer escrita

### Fase 3 — Refatoração
- Reestruturar para MVC conforme `refactoring-guide.md`
- Adaptar ao contexto: monolito vs. projeto parcialmente organizado
- Validar: boot da aplicação + endpoints respondendo
- Imprimir estrutura final e resultado da validação

## Catálogo de Anti-Patterns (mínimo 12)

| Anti-Pattern | Severidade | Sinal de Detecção |
|---|---|---|
| SQL Injection via concatenação | CRITICAL | `"SELECT..." + var` em queries |
| Credenciais hardcoded | CRITICAL | `password =`, `SECRET_KEY =`, `api_key =` com literal |
| God Class / God Method | CRITICAL | Arquivo > 200 linhas com DB + lógica + roteamento |
| Senha plaintext / crypto fraca | CRITICAL | Senha sem hash ou base64 como "hash" |
| Segredo exposto em resposta HTTP | CRITICAL | `secret_key` ou `password` em `jsonify()` / `res.json()` |
| Lógica de negócio no Controller | HIGH | Cálculos, regras de negócio dentro do handler HTTP |
| Callback Hell | HIGH | Funções aninhadas > 3 níveis em Node.js |
| Token fake/previsível | HIGH | `'fake-jwt-token-' + id` |
| Rota admin sem autenticação | HIGH | Endpoint `/admin/*` sem middleware de auth |
| Query N+1 | MEDIUM | Query dentro de `for` loop sem JOIN |
| Validação duplicada | MEDIUM | Mesmo bloco de validação em 3+ lugares |
| Bare except / catch | MEDIUM | `except:` sem tipo ou `catch` sem tratamento |
| API deprecated | LOW | `Model.query.get()` (SQLAlchemy ≥ 2.0), `bodyParser` (Express ≥ 4.16) |

## Projetos-Alvo

### Projeto 1 — code-smells-project (Python/Flask monolito)
Problemas chave: SQL Injection em toda models.py, SECRET_KEY exposta no /health, /admin/query sem auth, senhas plaintext, N+1 em pedidos.

Estrutura alvo após refatoração:
```
src/
├── config/settings.py
├── models/produto.py, usuario.py, pedido.py
├── controllers/produto_ctrl.py, usuario_ctrl.py, pedido_ctrl.py
├── middlewares/error_handler.py
└── app.py
```

### Projeto 2 — ecommerce-api-legacy (Node.js/Express)
Problemas chave: God Class AppManager.js, credenciais hardcoded em utils.js, callback hell 5 níveis, badCrypto, DELETE com dados órfãos.

Estrutura alvo:
```
src/
├── config/index.js
├── models/User.js, Course.js, Enrollment.js
├── controllers/checkoutController.js, reportController.js
├── routes/api.js
├── middlewares/errorHandler.js
└── app.js
```

### Projeto 3 — task-manager-api (Python/Flask parcialmente organizado)
Problemas chave: credenciais SMTP hardcoded, token JWT fake, is_overdue duplicado em 4 lugares, Model.query.get() deprecated, bare except, falta de camada Controller.

Estrutura alvo:
```
src/
├── config/settings.py
├── models/          (reorganizado do existente)
├── controllers/task_ctrl.py, user_ctrl.py, report_ctrl.py
├── routes/          (apenas roteamento)
├── services/notification_service.py
└── app.py
```

## Deliverables

- `.claude/skills/refactor-arch/` nos 3 projetos
- Código refatorado commitado nos 3 projetos
- `reports/audit-project-{1,2,3}.md`
- README com seções: Análise Manual, Construção da Skill, Resultados, Como Executar

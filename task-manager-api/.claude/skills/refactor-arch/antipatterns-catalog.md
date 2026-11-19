# Catálogo de Anti-Patterns

## Escala de Severidades

| Severidade | Critério |
|------------|----------|
| **CRITICAL** | Falha de segurança grave (exposição de dados, execução arbitrária de código) ou violação completa de separação de responsabilidades |
| **HIGH** | Violação forte de MVC/SOLID que compromete manutenção e testes, ou falta de autenticação em rotas sensíveis |
| **MEDIUM** | Problemas de qualidade, duplicação, performance moderada ou validação ausente |
| **LOW** | Legibilidade, nomenclatura, magic numbers, APIs obsoletas |

---

## Anti-Patterns com Sinais de Detecção

### AP-01 — SQL Injection via Concatenação de String
**Severidade:** CRITICAL

**Sinais de detecção:**
- Python: `cursor.execute("SELECT ... WHERE id = " + str(id))`
- Python: `cursor.execute(f"SELECT ... WHERE email = '{email}'")`
- Python: `query = "SELECT * FROM " + tabela`
- Node.js: `db.run("SELECT * FROM users WHERE id = " + id)`
- Qualquer query SQL construída com `+`, `%s` % var, ou f-string com variáveis externas

**Impacto:** Permite que um atacante execute queries arbitrárias, leia/destrua dados, bypass de autenticação.

**Recomendação:** Usar queries parametrizadas: `cursor.execute("SELECT ... WHERE id = ?", (id,))` ou `db.run("SELECT ... WHERE id = ?", [id])`.

---

### AP-02 — Credenciais Hardcoded
**Severidade:** CRITICAL

**Sinais de detecção:**
- `SECRET_KEY = "valor-literal"` em qualquer arquivo .py ou .js
- `password = "senha123"` ou `api_key = "pk_live_..."` com valor literal
- `dbPass: "senha_super_secreta_prod_123"` em objeto de configuração
- `self.email_password = 'senha123'` em classe de serviço
- `paymentGatewayKey: "pk_live_..."` em qualquer arquivo de código

**Impacto:** Credenciais comprometidas se o repositório for público ou acessado por pessoa não autorizada.

**Recomendação:** Mover para variáveis de ambiente. Python: `os.environ.get('SECRET_KEY')` com `python-dotenv`. Node.js: `process.env.SECRET_KEY` com `dotenv`.

---

### AP-03 — God Class / God Method
**Severidade:** CRITICAL

**Sinais de detecção:**
- Arquivo ou classe única > 200 linhas com responsabilidades mistas
- Presença simultânea de: definição de rotas + queries SQL + lógica de negócio + configuração
- Classe com métodos `initDb()`, `setupRoutes()`, `processPayment()` todos juntos
- Arquivo `app.py` ou `app.js` com mais de 150 linhas e múltiplas funções de domínio

**Impacto:** Impossível testar componentes em isolamento; qualquer mudança pode quebrar funcionalidades não relacionadas.

**Recomendação:** Separar em Model (acesso a dados), Controller (fluxo), Service (lógica de negócio), Config (configuração).

---

### AP-04 — Senha em Plaintext ou Criptografia Fraca
**Severidade:** CRITICAL

**Sinais de detecção:**
- Python: `hashlib.md5(pwd.encode()).hexdigest()` para armazenar senhas
- Senhas inseridas diretamente no banco sem hash: `INSERT INTO users (..., senha) VALUES (..., '123456')`
- Node.js: função de "hash" usando `btoa()`, `Buffer.from(pwd).toString('base64')`, ou loop de base64
- `self.password = password` sem transformação em método `set_password()`

**Impacto:** Senhas recuperáveis em caso de vazamento do banco de dados.

**Recomendação:** Python: `werkzeug.security.generate_password_hash()` / `check_password_hash()`. Node.js: `bcryptjs.hash(password, 12)` / `bcryptjs.compare()`.

---

### AP-05 — Segredo Exposto em Resposta HTTP
**Severidade:** CRITICAL

**Sinais de detecção:**
- `jsonify({..., "secret_key": app.config["SECRET_KEY"]})` em qualquer endpoint
- `res.json({..., password: user.password})` sem filtrar o campo
- `to_dict()` que inclui o campo `password` no dicionário retornado
- Endpoint `/health` ou `/status` que retorna chaves de configuração

**Impacto:** Exposição direta de credenciais via API pública.

**Recomendação:** Nunca incluir campos sensíveis em respostas HTTP. Remover `password`, `secret_key`, `api_key` de qualquer `to_dict()` ou serialização de resposta.

---

### AP-06 — Endpoint Administrativo Sem Autenticação
**Severidade:** CRITICAL

**Sinais de detecção:**
- Rota `/admin/query` que aceita SQL arbitrário sem verificar autenticação
- Rota `/admin/reset-db` ou similar sem middleware de auth
- Endpoint `/api/admin/financial-report` sem verificação de role/token
- Qualquer rota com `/admin` no path que não aplica middleware de autenticação

**Impacto:** Qualquer usuário pode executar operações privilegiadas, incluindo execução de SQL arbitrário.

**Recomendação:** Aplicar middleware de autenticação e verificação de role em todas as rotas `/admin`. Se for apenas para desenvolvimento, remover da versão de produção.

---

### AP-07 — Lógica de Negócio no Controller
**Severidade:** HIGH

**Sinais de detecção:**
- Cálculos de total de pedido dentro de função de rota/controller
- Validações complexas de estoque no handler HTTP
- Regras de desconto calculadas diretamente no controller
- Envio de notificações (email, SMS, push) `print("ENVIANDO EMAIL...")` dentro do handler

**Impacto:** Não é possível testar a lógica de negócio sem fazer uma requisição HTTP; lógica duplicada em múltiplos endpoints.

**Recomendação:** Extrair para camada Service ou Model. Controllers devem apenas: receber request → chamar service/model → retornar response.

---

### AP-08 — Callback Hell (Pyramid of Doom)
**Severidade:** HIGH

**Sinais de detecção (Node.js):**
- Funções callback aninhadas em mais de 3 níveis de profundidade
- Pattern: `db.get(..., (err, row) => { db.run(..., (err) => { db.get(..., (err) => {...}) }) })`
- Contador manual de operações pendentes para controlar quando responder (`coursesPending--; if (coursesPending === 0) res.json(...)`)

**Impacto:** Código impossível de manter, difícil de fazer tratamento de erros, alta probabilidade de bugs de concorrência.

**Recomendação:** Converter para `async/await` com `util.promisify()` ou wrapper de Promises sobre a API sqlite3.

---

### AP-09 — Token de Autenticação Fake ou Previsível
**Severidade:** HIGH

**Sinais de detecção:**
- `'fake-jwt-token-' + str(user.id)` ou `'fake-jwt-' + id`
- Token que é apenas o ID do usuário ou derivação trivial
- Ausência completa de verificação de token em rotas protegidas

**Impacto:** Qualquer pessoa pode forjar um token válido para qualquer usuário sabendo apenas o ID.

**Recomendação:** Usar JWT real com `PyJWT` (Python) ou `jsonwebtoken` (Node.js) com chave secreta. Ou, para o escopo do projeto, documentar claramente que é um stub e adicionar TODO.

---

### AP-10 — Query N+1
**Severidade:** MEDIUM

**Sinais de detecção:**
- Query dentro de loop `for`: `for item in items: cursor.execute("SELECT ... WHERE id = ?", (item_id,))`
- Node.js: `enrollments.forEach(enr => { db.get("SELECT ... WHERE id = ?", [enr.user_id], ...) })`
- Múltiplos cursors aninhados (`cursor2`, `cursor3`) dentro de um loop

**Impacto:** Performance degrada linearmente com o volume de dados. 100 pedidos com 5 itens cada = 500+ queries desnecessárias.

**Recomendação:** Usar JOIN para buscar dados relacionados em uma única query. Ex: `SELECT p.*, ip.* FROM pedidos p JOIN itens_pedido ip ON ip.pedido_id = p.id WHERE p.usuario_id = ?`.

---

### AP-11 — Validação Duplicada
**Severidade:** MEDIUM

**Sinais de detecção:**
- Mesmo bloco de validação (`if len(title) < 3`, `if status not in [...]`) em 3+ lugares
- Lógica `is_overdue` calculada inline em múltiplas funções quando já existe método no Model
- Função `process_task_data()` em helpers que duplica validação já feita na rota

**Impacto:** Inconsistências quando a regra muda (precisa atualizar em N lugares).

**Recomendação:** Centralizar validação em um único lugar — no Model (método `validate()`), em um schema (marshmallow, Zod), ou em um helper chamado por todas as rotas.

---

### AP-12 — Bare Except / Catch Genérico
**Severidade:** MEDIUM

**Sinais de detecção:**
- Python: `except:` sem especificar o tipo de exceção
- Python: `except Exception as e:` seguido de `pass` ou log sem re-raise
- Node.js: `catch(err) { }` vazio ou apenas `console.log`
- `try: ... except: return jsonify({'error': 'Erro interno'}), 500` sem log do erro real

**Impacto:** Erros silenciosos, debugging impossível, pode mascarar problemas críticos de lógica.

**Recomendação:** Especificar tipos: `except ValueError as e:`, `except SQLAlchemyError as e:`. Sempre logar o erro: `app.logger.error(f"Erro: {e}")`. Re-raise se não puder tratar.

---

### AP-13 — API Deprecated
**Severidade:** LOW

**Sinais de detecção — Python/SQLAlchemy:**
- `Model.query.get(id)` — deprecated em SQLAlchemy 2.0, removido em 2.1
- Substituição: `db.session.get(Model, id)`
- `Model.query.filter_by(...).first()` ainda válido, mas preferir `db.session.execute(select(Model).filter_by(...))`

**Sinais de detecção — Node.js/Express:**
- `const bodyParser = require('body-parser')` — desnecessário desde Express 4.16, usar `express.json()`
- `app.use(express.static(...))` com callback de erro omitido — sem problema, apenas padrão antigo
- `req.param(name)` — removido no Express 5, usar `req.params`, `req.query` ou `req.body`

**Impacto:** Warnings no console, quebra em atualizações futuras do framework.

**Recomendação:** Atualizar para a API moderna conforme documentação do framework.

---

## Template do Relatório de Auditoria

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: [nome do diretório]
Stack:   [linguagem + framework]
Files:   [N analyzed] | [~X lines of code]

## Summary
CRITICAL: N | HIGH: N | MEDIUM: N | LOW: N

## Findings

### [CRITICAL] [Nome do Anti-Pattern]
File: [arquivo.py:linha]
Description: [descrição específica do problema encontrado no código]
Impact: [impacto concreto no sistema]
Recommendation: [ação específica para corrigir]

### [HIGH] [Nome do Anti-Pattern]
File: [arquivo.py:linha-linha]
Description: [descrição específica]
Impact: [impacto]
Recommendation: [recomendação]

[... continuar para todos os findings ordenados CRITICAL → LOW ...]

================================
Total: N findings
================================
```

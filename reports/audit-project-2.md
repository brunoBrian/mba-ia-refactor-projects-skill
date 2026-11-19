================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   Node.js + Express 4.18.2
Files:   3 analyzed | ~200 lines of code

## Summary
CRITICAL: 3 | HIGH: 3 | MEDIUM: 2 | LOW: 2

## Findings

### [CRITICAL] Hardcoded Production Credentials
File: src/utils.js:1-7
Description: Credenciais de produção hardcoded: `dbPass: "senha_super_secreta_prod_123"`, `paymentGatewayKey: "pk_live_1234567890abcdef"`, `smtpUser: "no-reply@fullcycle.com.br"`.
Impact: Qualquer pessoa com acesso ao repositório tem as credenciais do banco de produção e da gateway de pagamento. Chave de pagamento `pk_live_` ativa pode ser usada para transações fraudulentas.
Recommendation: Mover para variáveis de ambiente com `dotenv`.

### [CRITICAL] God Class — AppManager
File: src/AppManager.js:1-141
Description: Classe única com 141 linhas concentra: inicialização do banco (initDb), definição de todas as rotas (setupRoutes), lógica de pagamento, criação de usuários, audit logging e resposta HTTP — tudo misturado.
Impact: Impossível testar qualquer funcionalidade em isolamento. Qualquer mudança no banco afeta as rotas e vice-versa.
Recommendation: Separar em models (User, Course, Enrollment), controllers (checkoutController, reportController), routes (api.js) e database (index.js).

### [CRITICAL] Callback Hell — 5 Níveis de Aninhamento
File: src/AppManager.js:28-78
Description: A rota POST /api/checkout tem callbacks aninhados em 5 níveis de profundidade: `db.get → db.get → processPaymentAndEnroll → db.run → db.run → db.run`. Inclui contador manual `coursesPending--` para controlar quando responder.
Impact: Código impossível de manter; erros em qualquer callback silenciosamente não são tratados; alta probabilidade de race conditions e double-response bugs.
Recommendation: Converter para async/await usando `util.promisify()` sobre a API do sqlite3.

### [HIGH] Weak/Broken Cryptography (badCrypto)
File: src/utils.js:17-23
Description: Função `badCrypto` usa 10.000 iterações de base64 e trunca para 10 caracteres como "hash" de senha. Base64 é encoding, não hashing — completamente reversível.
Impact: Senhas recuperáveis trivialmente por qualquer atacante com acesso ao banco.
Recommendation: Usar `bcryptjs.hash(password, 12)` e `bcryptjs.compare()`.

### [HIGH] Admin Route Sem Autenticação
File: src/AppManager.js:80
Description: `GET /api/admin/financial-report` retorna dados financeiros de todos os cursos e alunos sem qualquer verificação de autenticação ou autorização.
Impact: Dados financeiros da empresa expostos publicamente.
Recommendation: Adicionar middleware de autenticação que verifique token JWT e role admin antes de processar a requisição.

### [HIGH] DELETE de Usuário com Dados Órfãos
File: src/AppManager.js:131-137
Description: `DELETE /api/users/:id` deleta apenas o registro em `users`, deixando enrollments e payments com `user_id` apontando para usuário inexistente. A própria mensagem de resposta reconhece o bug: "as matrículas e pagamentos ficaram sujos no banco."
Impact: Corrupção do banco de dados; relatórios financeiros com dados inconsistentes.
Recommendation: Implementar cascade delete: deletar payments → enrollments → user em sequência.

### [MEDIUM] In-Memory Database
File: src/AppManager.js:7
Description: `new sqlite3.Database(':memory:')` — todos os dados são perdidos ao reiniciar a aplicação.
Impact: Nenhuma persistência de dados. Adequado apenas para testes; não para ambiente de desenvolvimento ou produção.
Recommendation: Usar caminho de arquivo: `new sqlite3.Database(config.dbPath)` com `DB_PATH` em variável de ambiente.

### [MEDIUM] Query N+1 no Financial Report
File: src/AppManager.js:88-128
Description: Para cada course, busca enrollments; para cada enrollment, busca user E payment em callbacks separados. Para 10 cursos com 20 alunos cada: 10 + 200 + 200 = 410 queries.
Impact: Performance degrada exponencialmente com volume de dados.
Recommendation: Usar JOINs ou reduzir queries com `IN` clause.

### [LOW] Variáveis com Nomes Crípticos
File: src/AppManager.js:29-34
Description: Variáveis `u` (name), `e` (email), `p` (password), `cid` (course_id), `cc` (card) sem nomes descritivos.
Impact: Código difícil de entender e manter.
Recommendation: Usar nomes completos: `const { usr: name, eml: email, pwd: password, c_id: courseId, card } = req.body`.

### [LOW] Variável Exportada Não Utilizada
File: src/utils.js:10, 25
Description: `let totalRevenue = 0` é exportado em `module.exports` mas nunca atualizado ou utilizado em nenhum outro arquivo.
Impact: Dead code confunde mantenedores.
Recommendation: Remover a variável.

================================
Total: 10 findings
================================

## Phase 3 — Refactoring Applied

### New Project Structure
```
ecommerce-api-legacy/
├── src/
│   ├── app.js                          # Entry point (reescrito com async/await)
│   ├── config/index.js                 # Credenciais via process.env
│   ├── database/index.js               # DB com promisify (getAsync, runAsync, allAsync)
│   ├── models/
│   │   ├── User.js                     # CRUD de usuários com cascade delete
│   │   ├── Course.js                   # Busca de cursos
│   │   └── Enrollment.js               # Matrículas, pagamentos, audit logs
│   ├── controllers/
│   │   ├── checkoutController.js       # async/await, bcryptjs
│   │   └── reportController.js         # Relatório financeiro
│   ├── routes/api.js                   # Roteamento limpo
│   └── middlewares/errorHandler.js     # Error handler centralizado
├── .env.example
└── package.json                        # + bcryptjs
```

### Changes Applied
- AP-02: Credenciais → process.env em config/index.js
- AP-03: God Class decomposta em models + controllers + routes + database
- AP-05: Callback hell → async/await com promisify
- AP-04: badCrypto → bcryptjs.hash(password, 12)
- AP-06: DELETE de usuário com cascade (payments → enrollments → user)
- AP-10: In-memory DB → configurável via DB_PATH env var

### Validation
  ✓ Syntax check passed (node --check)
  ✓ All endpoints preserved (/api/checkout, /api/admin/financial-report, /api/users/:id)
  ✓ Zero hardcoded credentials remaining

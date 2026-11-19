# Guia de Refatoração — MVC

## 1. Arquitetura MVC Alvo

### Responsabilidades por Camada

| Camada | O que FAZ | O que NÃO FAZ |
|--------|-----------|----------------|
| **Model** | Acesso ao banco (queries), relacionamentos, serialização simples | Lógica de negócio, validação de requisição HTTP, envio de emails |
| **Controller** | Recebe request, valida entrada, chama Model/Service, retorna response | Queries SQL diretas, lógica de negócio complexa |
| **Route/View** | Registra endpoints e delega para Controller | Qualquer lógica além de `return controller.acao()` |
| **Service** | Lógica de negócio que envolve múltiplos Models | Acesso direto ao banco, construção de responses HTTP |
| **Config** | Valores de configuração via env vars | Lógica de aplicação |
| **Middleware** | Autenticação, logging, tratamento de erros globais | Lógica de domínio |

---

## 2. Estrutura de Diretórios Alvo

### Python/Flask
```
projeto/
├── app.py                    # Entry point: cria app, registra blueprints
├── database.py               # Inicialização do banco (SQLAlchemy ou sqlite3)
├── .env.example              # Variáveis de ambiente documentadas
├── requirements.txt
├── config/
│   └── settings.py           # SECRET_KEY, DATABASE_URL, DEBUG via os.environ
├── models/
│   ├── __init__.py
│   ├── produto.py            # CRUD de produtos (queries parametrizadas)
│   └── usuario.py            # CRUD de usuários (hash de senha)
├── controllers/
│   ├── __init__.py
│   ├── produto_ctrl.py       # Validação + chama model + retorna jsonify
│   └── usuario_ctrl.py
├── routes/
│   ├── __init__.py
│   └── api.py                # Blueprint com apenas add_url_rule / @bp.route
├── middlewares/
│   └── error_handler.py      # @app.errorhandler(404), @app.errorhandler(500)
└── services/                 # (opcional) lógica de negócio complexa
    └── notification.py
```

### Node.js/Express
```
projeto/
├── src/
│   ├── app.js                # Entry point: cria Express app, registra rotas
│   ├── config/
│   │   └── index.js          # process.env com defaults
│   ├── database/
│   │   └── index.js          # Inicialização e helpers do banco
│   ├── models/
│   │   ├── User.js           # Funções CRUD com queries parametrizadas
│   │   └── Course.js
│   ├── controllers/
│   │   ├── checkoutController.js   # async/await, sem callbacks aninhados
│   │   └── reportController.js
│   ├── routes/
│   │   └── api.js            # router.get/post/put/delete + controller
│   └── middlewares/
│       ├── errorHandler.js   # Express error middleware (err, req, res, next)
│       └── auth.js           # Verificação de token
├── .env.example
└── package.json
```

---

## 3. Playbook de Transformações

### PT-01: SQL Injection → Queries Parametrizadas

**Antes (Python):**
```python
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
cursor.execute("INSERT INTO usuarios (nome, email) VALUES ('" + nome + "', '" + email + "')")
```

**Depois (Python):**
```python
cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
cursor.execute("INSERT INTO usuarios (nome, email) VALUES (?, ?)", (nome, email))
```

**Antes (Node.js):**
```javascript
db.get("SELECT * FROM users WHERE id = " + id, callback)
```

**Depois (Node.js):**
```javascript
db.get("SELECT * FROM users WHERE id = ?", [id], callback)
```

---

### PT-02: Credenciais Hardcoded → Variáveis de Ambiente

**Antes (Python):**
```python
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
self.email_password = 'senha123'
```

**Depois (Python — config/settings.py):**
```python
import os
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-only-change-in-production')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')
DATABASE_PATH = os.environ.get('DATABASE_PATH', 'app.db')
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
```

**Antes (Node.js):**
```javascript
const config = {
    dbPass: "senha_super_secreta_prod_123",
    paymentGatewayKey: "pk_live_1234567890abcdef",
};
```

**Depois (Node.js — config/index.js):**
```javascript
require('dotenv').config();
module.exports = {
    dbPass: process.env.DB_PASS || '',
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
    port: parseInt(process.env.PORT) || 3000,
};
```

**.env.example:**
```
SECRET_KEY=your-secret-key-here
DATABASE_PATH=app.db
DEBUG=False
EMAIL_PASSWORD=
PAYMENT_GATEWAY_KEY=
```

---

### PT-03: Senhas Plaintext → Hash Seguro

**Antes (Python — MD5 ou plaintext):**
```python
import hashlib
self.password = hashlib.md5(pwd.encode()).hexdigest()
# ou
cursor.execute("INSERT INTO usuarios (senha) VALUES (?)", (senha,))  # sem hash
```

**Depois (Python — werkzeug):**
```python
from werkzeug.security import generate_password_hash, check_password_hash

def set_password(self, pwd):
    self.password = generate_password_hash(pwd)

def check_password(self, pwd):
    return check_password_hash(self.password, pwd)
```

**Antes (Node.js — badCrypto):**
```javascript
function badCrypto(pwd) {
    let hash = "";
    for(let i = 0; i < 10000; i++) {
        hash += Buffer.from(pwd).toString('base64').substring(0, 2);
    }
    return hash.substring(0, 10);
}
```

**Depois (Node.js — bcryptjs):**
```javascript
const bcrypt = require('bcryptjs');

async function hashPassword(pwd) {
    return bcrypt.hash(pwd, 12);
}

async function verifyPassword(pwd, hash) {
    return bcrypt.compare(pwd, hash);
}
```

---

### PT-04: God Class → Separação em MVC

**Antes (Node.js — tudo em AppManager):**
```javascript
class AppManager {
    initDb() { /* cria tabelas */ }
    setupRoutes(app) {
        app.post('/checkout', (req, res) => {
            // validação + db query + lógica de pagamento + db insert + audit log
        });
    }
}
```

**Depois — separado em camadas:**

`database/index.js`:
```javascript
const sqlite3 = require('sqlite3').verbose();
const { promisify } = require('util');

const db = new sqlite3.Database(process.env.DB_PATH || ':memory:');
db.getAsync = promisify(db.get.bind(db));
db.runAsync = promisify(db.run.bind(db));
db.allAsync = promisify(db.all.bind(db));

module.exports = db;
```

`models/Course.js`:
```javascript
const db = require('../database');

async function findById(id) {
    return db.getAsync('SELECT * FROM courses WHERE id = ? AND active = 1', [id]);
}
module.exports = { findById };
```

`controllers/checkoutController.js`:
```javascript
const CourseModel = require('../models/Course');
const UserModel = require('../models/User');
const bcrypt = require('bcryptjs');

async function checkout(req, res) {
    const { usr, eml, pwd, c_id, card } = req.body;
    if (!usr || !eml || !c_id || !card) return res.status(400).json({ error: 'Bad Request' });
    // ... lógica sem callbacks aninhados
}
module.exports = { checkout };
```

`routes/api.js`:
```javascript
const router = require('express').Router();
const checkoutCtrl = require('../controllers/checkoutController');
router.post('/checkout', checkoutCtrl.checkout);
module.exports = router;
```

---

### PT-05: Callback Hell → Async/Await

**Antes:**
```javascript
db.get("SELECT * FROM courses WHERE id = ?", [cid], (err, course) => {
    db.get("SELECT id FROM users WHERE email = ?", [email], (err, user) => {
        db.run("INSERT INTO enrollments ...", [userId, cid], function(err) {
            db.run("INSERT INTO payments ...", [this.lastID, ...], function(err) {
                res.json({ success: true });
            });
        });
    });
});
```

**Depois:**
```javascript
async function checkout(req, res) {
    try {
        const course = await db.getAsync('SELECT * FROM courses WHERE id = ? AND active = 1', [cid]);
        if (!course) return res.status(404).json({ error: 'Curso não encontrado' });

        let user = await db.getAsync('SELECT id FROM users WHERE email = ?', [email]);
        if (!user) {
            const hash = await bcrypt.hash(pwd || '123456', 12);
            const result = await db.runAsync('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', [usr, email, hash]);
            user = { id: result.lastID };
        }

        const enr = await db.runAsync('INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)', [user.id, cid]);
        await db.runAsync('INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)', [enr.lastID, course.price, 'PAID']);

        res.status(200).json({ msg: 'Sucesso', enrollment_id: enr.lastID });
    } catch (err) {
        res.status(500).json({ error: 'Erro interno' });
    }
}
```

---

### PT-06: N+1 Queries → JOIN

**Antes:**
```python
cursor.execute("SELECT * FROM pedidos WHERE usuario_id = ?", (usuario_id,))
pedidos = cursor.fetchall()
for pedido in pedidos:
    cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = ?", (pedido["id"],))
    for item in cursor2.fetchall():
        cursor3.execute("SELECT nome FROM produtos WHERE id = ?", (item["produto_id"],))
```

**Depois:**
```python
cursor.execute("""
    SELECT p.id, p.status, p.total, p.criado_em,
           ip.produto_id, ip.quantidade, ip.preco_unitario,
           pr.nome as produto_nome
    FROM pedidos p
    LEFT JOIN itens_pedido ip ON ip.pedido_id = p.id
    LEFT JOIN produtos pr ON pr.id = ip.produto_id
    WHERE p.usuario_id = ?
""", (usuario_id,))
```

---

### PT-07: Remoção de Endpoint Inseguro

**Antes:**
```python
@app.route("/admin/query", methods=["POST"])
def executar_query():
    dados = request.get_json()
    query = dados.get("sql", "")
    cursor.execute(query)  # executa SQL ARBITRÁRIO
```

**Depois:** Remover completamente o endpoint `/admin/query`. Se necessidade de debug, usar ferramentas de banco diretamente, nunca via API.

---

### PT-08: Validação Duplicada → Centralização

**Antes (mesma lógica is_overdue em 4 arquivos):**
```python
# Em task_routes.py, user_routes.py, report_routes.py:
if t.due_date:
    if t.due_date < datetime.utcnow():
        if t.status != 'done' and t.status != 'cancelled':
            task_data['overdue'] = True
```

**Depois (usar o método que já existe no Model):**
```python
# Task já tem:
def is_overdue(self):
    if self.due_date and self.due_date < datetime.utcnow():
        return self.status not in ('done', 'cancelled')
    return False

# Usar em todos os lugares:
task_data['overdue'] = t.is_overdue()
```

---

### PT-09: API Deprecated → API Moderna (SQLAlchemy)

**Antes:**
```python
task = Task.query.get(task_id)
user = User.query.get(user_id)
```

**Depois (SQLAlchemy 2.0+):**
```python
task = db.session.get(Task, task_id)
user = db.session.get(User, user_id)
```

---

### PT-10: Segredo Exposto em Resposta → Remoção

**Antes:**
```python
return jsonify({
    "status": "ok",
    "secret_key": "minha-chave-super-secreta-123",
    "debug": True
}), 200
```

**Depois:**
```python
return jsonify({
    "status": "ok",
    "database": "connected",
    "version": "1.0.0"
}), 200
```

---

## 4. Regras de Adaptação por Contexto

### Projeto Monolito (tudo em 1-3 arquivos)
1. Criar estrutura de diretórios do zero
2. Extrair queries de cada domínio para seu próprio Model
3. Mover validações do arquivo de routes para Controllers
4. Criar `config/settings.py` ou `config/index.js`
5. Criar `middlewares/error_handler.py`

### Projeto MVC Parcial (já tem models/, routes/ mas falta controllers/)
1. Criar diretório `controllers/`
2. Mover lógica das routes para controllers (routes ficam finas)
3. Corrigir problemas de segurança (creds, queries)
4. Atualizar APIs deprecated
5. Não reestruturar o que já está correto

### Regra Geral
- Nunca remover funcionalidade — apenas reorganizar e corrigir
- Todos os endpoints originais devem continuar respondendo após a refatoração
- Manter compatibilidade com o banco de dados existente

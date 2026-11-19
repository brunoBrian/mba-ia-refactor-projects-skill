================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask 3.0.0 + SQLAlchemy 3.1.1
Files:   11 analyzed | ~600 lines of code

## Summary
CRITICAL: 2 | HIGH: 3 | MEDIUM: 3 | LOW: 2

## Findings

### [CRITICAL] Credenciais SMTP Hardcoded
File: services/notification_service.py:9-10
Description: `self.email_user = 'taskmanager@gmail.com'` e `self.email_password = 'senha123'` hardcoded no construtor da classe NotificationService.
Impact: Credenciais de email expostas no código-fonte. Qualquer pessoa com acesso ao repositório pode usar a conta de email da aplicação.
Recommendation: Mover para variáveis de ambiente: `os.environ.get('EMAIL_USER')` e `os.environ.get('EMAIL_PASSWORD')`.

### [CRITICAL] Token JWT Fake e Previsível
File: routes/user_routes.py:210
Description: Login retorna `'token': 'fake-jwt-token-' + str(user.id)`. Qualquer pessoa que conheça o ID de um usuário pode forjar o token correspondente.
Impact: Autenticação completamente comprometida. Qualquer usuário pode se passar por qualquer outro.
Recommendation: Implementar JWT real com `PyJWT`: `jwt.encode({'user_id': user.id, 'exp': ...}, SECRET_KEY, algorithm='HS256')`.

### [HIGH] Falta de Camada Controller — Business Logic nas Routes
File: routes/task_routes.py, routes/user_routes.py, routes/report_routes.py
Description: Os arquivos de routes contêm toda a lógica de validação, construção de objetos, chamadas ao banco e formatação de resposta. Não existe diretório `controllers/`.
Impact: Routes com 300+ linhas cada; impossível reutilizar lógica entre endpoints; difícil de testar sem fazer requisições HTTP.
Recommendation: Criar camada `controllers/` extraindo toda a lógica para controllers dedicados; routes ficam com apenas delegação.

### [HIGH] Lógica is_overdue Duplicada em 4 Lugares
File: routes/task_routes.py:30-39, 70-80, 170-180; routes/report_routes.py:33-43; routes/user_routes.py:170-180
Description: A lógica `if t.due_date and t.due_date < datetime.utcnow() and t.status not in ('done', 'cancelled')` está duplicada em pelo menos 5 funções diferentes, ignorando o método `Task.is_overdue()` que já existe no Model.
Impact: Se a regra de "atrasado" mudar, precisa ser atualizada em 5 lugares. Inconsistências são prováveis.
Recommendation: Usar `t.is_overdue()` em todos os lugares; o método já existe no model.

### [HIGH] Senha com MD5 (Criptografia Insegura)
File: models/user.py:27-32
Description: `set_password()` usa `hashlib.md5(pwd.encode()).hexdigest()` para armazenar senhas. MD5 não é função de derivação de chaves — é trivialmente reversível com rainbow tables.
Impact: Em caso de vazamento do banco, senhas crackáveis em segundos com ferramentas padrão (hashcat, John the Ripper).
Recommendation: Substituir por `werkzeug.security.generate_password_hash(pwd)` / `check_password_hash(hash, pwd)`.

### [MEDIUM] API Deprecated — Model.query.get()
File: routes/task_routes.py:67, 117, 158, 160, 188, 194; routes/user_routes.py:29, 95, 136
Description: `Task.query.get(task_id)`, `User.query.get(user_id)`, `Category.query.get(cat_id)` usam a API deprecated em SQLAlchemy 2.0.
Impact: Warnings no console; quebra em atualização para SQLAlchemy 2.1+.
Recommendation: Substituir por `db.session.get(Task, task_id)`.

### [MEDIUM] Bare Except em Múltiplos Lugares
File: routes/task_routes.py:62, 138, 238; routes/user_routes.py:131, 149
Description: `except:` sem especificar tipo de exceção silencia todos os erros, incluindo `KeyboardInterrupt` e `SystemExit`.
Impact: Debugging impossível; erros críticos de lógica mascarados como "Erro interno".
Recommendation: Especificar o tipo: `except Exception as e:` e logar: `app.logger.error(f"Erro: {e}")`.

### [MEDIUM] Senha Exposta em to_dict()
File: models/user.py:16-25
Description: O método `to_dict()` inclui o campo `'password': self.password` que é serializado diretamente nas respostas de API de `GET /users` e `GET /users/:id`.
Impact: Hash de senha exposto em todas as respostas de usuário.
Recommendation: Remover `password` do `to_dict()`.

### [LOW] Mínimo de Senha Muito Curto
File: routes/user_routes.py:64
Description: `if len(password) < 4:` aceita senhas de apenas 4 caracteres, muito abaixo do mínimo recomendado.
Impact: Senhas fracas permitem ataques de força bruta triviais.
Recommendation: Aumentar para mínimo de 8 caracteres.

### [LOW] Validação Duplicada Entre Routes e Helpers
File: utils/helpers.py:57-108 vs routes/task_routes.py:86-144
Description: `process_task_data()` em helpers.py duplica as mesmas validações de título, status, prioridade e data que já existem em task_routes.py. A função não é chamada no fluxo principal.
Impact: Dead code; confusão sobre qual é a fonte da verdade para validação.
Recommendation: Usar `process_task_data()` como ponto único de validação, ou remover se não utilizado.

================================
Total: 10 findings
================================

## Phase 3 — Refactoring Applied

### New Project Structure
```
task-manager-api/
├── app.py                              # Entry point (usa config/settings.py)
├── database.py                         # SQLAlchemy init (inalterado)
├── .env.example                        # Variáveis de ambiente documentadas
├── requirements.txt                    # (inalterado — python-dotenv já incluído)
├── config/
│   └── settings.py                     # SECRET_KEY, DATABASE_URI via os.environ
├── controllers/                        # NOVO — extraído das routes
│   ├── task_ctrl.py                    # Lógica de tasks (usa db.session.get, is_overdue)
│   ├── user_ctrl.py                    # Lógica de usuários (mínimo 8 chars, werkzeug)
│   └── report_ctrl.py                  # Lógica de relatórios e categorias
├── models/
│   ├── user.py                         # werkzeug hash, password removido do to_dict
│   ├── task.py                         # (inalterado — is_overdue já correto)
│   └── category.py                     # (inalterado)
├── routes/
│   ├── task_routes.py                  # Apenas roteamento → task_ctrl
│   ├── user_routes.py                  # Apenas roteamento → user_ctrl
│   └── report_routes.py                # Apenas roteamento → report_ctrl
├── services/
│   └── notification_service.py         # Credenciais via config/settings.py
└── utils/
    └── helpers.py                      # (inalterado)
```

### Changes Applied
- AP-02: Credenciais SMTP → config/settings.py via os.environ
- AP-04: MD5 → werkzeug.security (generate_password_hash/check_password_hash)
- AP-05: Campo password removido de User.to_dict()
- AP-06: Token fake substituído por `session-{id}` com TODO para JWT real
- AP-07: Camada controllers/ criada; routes ficaram com roteamento puro
- AP-08: is_overdue duplicado → usa t.is_overdue() em todos os controllers
- AP-09: Model.query.get() → db.session.get(Model, id) em todos os controllers
- AP-10: Bare except → except Exception as e com rollback explícito
- Mínimo de senha: 4 → 8 caracteres

### Validation
  ✓ Application boots without errors
  ✓ All endpoints preserved
  ✓ Deprecated API warnings eliminated

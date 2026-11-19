# refactor-arch Skill — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the `/refactor-arch` skill files and execute the 3-phase refactoring on 3 legacy projects.

**Architecture:** Skill with SKILL.md + 3 reference files. Each project gets the skill copied in, then Phase 1/2/3 executed. Security fixes applied directly to code.

**Tech Stack:** Python/Flask (projects 1 & 3), Node.js/Express (project 2), SQLite, werkzeug.security, python-dotenv

---

## File Map

**Skill files (copied to each project):**
- `code-smells-project/.claude/skills/refactor-arch/SKILL.md`
- `code-smells-project/.claude/skills/refactor-arch/analysis-heuristics.md`
- `code-smells-project/.claude/skills/refactor-arch/antipatterns-catalog.md`
- `code-smells-project/.claude/skills/refactor-arch/refactoring-guide.md`

**Project 1 refactored:**
- `code-smells-project/src/config/settings.py` (new)
- `code-smells-project/src/models/produto.py` (new, fixes SQL injection)
- `code-smells-project/src/models/usuario.py` (new, fixes SQL injection + plaintext passwords)
- `code-smells-project/src/models/pedido.py` (new, fixes SQL injection + N+1)
- `code-smells-project/src/controllers/produto_ctrl.py` (new)
- `code-smells-project/src/controllers/usuario_ctrl.py` (new)
- `code-smells-project/src/controllers/pedido_ctrl.py` (new)
- `code-smells-project/src/middlewares/error_handler.py` (new)
- `code-smells-project/app.py` (modified: remove /admin/query, use settings)
- `code-smells-project/database.py` (modified: use settings, hash seed passwords)
- `code-smells-project/requirements.txt` (add python-dotenv)

**Project 2 refactored:**
- `ecommerce-api-legacy/src/config/index.js` (new, env vars)
- `ecommerce-api-legacy/src/database/index.js` (new)
- `ecommerce-api-legacy/src/models/User.js` (new)
- `ecommerce-api-legacy/src/models/Course.js` (new)
- `ecommerce-api-legacy/src/models/Enrollment.js` (new)
- `ecommerce-api-legacy/src/controllers/checkoutController.js` (new, async/await)
- `ecommerce-api-legacy/src/controllers/reportController.js` (new)
- `ecommerce-api-legacy/src/middlewares/errorHandler.js` (new)
- `ecommerce-api-legacy/src/routes/api.js` (new)
- `ecommerce-api-legacy/src/app.js` (rewritten)
- `ecommerce-api-legacy/package.json` (add bcryptjs)

**Project 3 refactored:**
- `task-manager-api/config/settings.py` (new)
- `task-manager-api/controllers/task_ctrl.py` (new, extracted from routes)
- `task-manager-api/controllers/user_ctrl.py` (new)
- `task-manager-api/controllers/report_ctrl.py` (new)
- `task-manager-api/routes/task_routes.py` (modified: thin routing only)
- `task-manager-api/routes/user_routes.py` (modified: thin routing only)
- `task-manager-api/routes/report_routes.py` (modified: thin routing only)
- `task-manager-api/models/user.py` (fix MD5 → werkzeug, remove password from to_dict)
- `task-manager-api/services/notification_service.py` (fix hardcoded creds)
- `task-manager-api/app.py` (use config)
- `task-manager-api/.env.example` (new)

**Reports + docs:**
- `reports/audit-project-1.md`
- `reports/audit-project-2.md`
- `reports/audit-project-3.md`
- `README.md`

---

## Task 1: Create Skill Files

**Files:**
- Create: `code-smells-project/.claude/skills/refactor-arch/SKILL.md`
- Create: `code-smells-project/.claude/skills/refactor-arch/analysis-heuristics.md`
- Create: `code-smells-project/.claude/skills/refactor-arch/antipatterns-catalog.md`
- Create: `code-smells-project/.claude/skills/refactor-arch/refactoring-guide.md`

- [ ] Create SKILL.md with 3-phase instructions (see content below)
- [ ] Create analysis-heuristics.md
- [ ] Create antipatterns-catalog.md
- [ ] Create refactoring-guide.md
- [ ] Commit: `git add code-smells-project/.claude && git commit -m "feat: add refactor-arch skill"`

---

## Task 2: Refactor code-smells-project

- [ ] Create `src/config/settings.py`
- [ ] Create `src/models/produto.py` (parameterized queries)
- [ ] Create `src/models/usuario.py` (werkzeug password hash)
- [ ] Create `src/models/pedido.py` (parameterized + JOIN fix for N+1)
- [ ] Create `src/controllers/produto_ctrl.py`
- [ ] Create `src/controllers/usuario_ctrl.py`
- [ ] Create `src/controllers/pedido_ctrl.py`
- [ ] Create `src/middlewares/error_handler.py`
- [ ] Rewrite `app.py` (remove /admin/query, fix routes)
- [ ] Update `database.py` (hash seed passwords, use settings)
- [ ] Update `requirements.txt` (add python-dotenv)
- [ ] Validate: `cd code-smells-project && python -c "from app import app; print('OK')"`
- [ ] Save `reports/audit-project-1.md`
- [ ] Commit refactored project 1

---

## Task 3: Refactor ecommerce-api-legacy

- [ ] `npm install bcryptjs` in ecommerce-api-legacy
- [ ] Create `src/config/index.js`
- [ ] Create `src/database/index.js`
- [ ] Create `src/models/User.js`, `Course.js`, `Enrollment.js`
- [ ] Create `src/controllers/checkoutController.js` (async/await, bcryptjs)
- [ ] Create `src/controllers/reportController.js`
- [ ] Create `src/middlewares/errorHandler.js`
- [ ] Create `src/routes/api.js`
- [ ] Rewrite `src/app.js`
- [ ] Copy skill to `ecommerce-api-legacy/.claude/skills/refactor-arch/`
- [ ] Validate: `node --check src/app.js`
- [ ] Save `reports/audit-project-2.md`
- [ ] Commit refactored project 2

---

## Task 4: Refactor task-manager-api

- [ ] Create `config/settings.py`
- [ ] Create `.env.example`
- [ ] Fix `models/user.py` (MD5 → werkzeug, remove password from to_dict)
- [ ] Create `controllers/task_ctrl.py` (business logic from routes)
- [ ] Create `controllers/user_ctrl.py`
- [ ] Create `controllers/report_ctrl.py`
- [ ] Slim down `routes/task_routes.py` (routing only)
- [ ] Slim down `routes/user_routes.py`
- [ ] Slim down `routes/report_routes.py`
- [ ] Fix `services/notification_service.py` (env vars)
- [ ] Update `app.py` (use config)
- [ ] Copy skill to `task-manager-api/.claude/skills/refactor-arch/`
- [ ] Validate: `cd task-manager-api && python -c "from app import app; print('OK')"`
- [ ] Save `reports/audit-project-3.md`
- [ ] Commit refactored project 3

---

## Task 5: Write README

- [ ] Write `README.md` with sections: Análise Manual, Construção da Skill, Resultados, Como Executar
- [ ] Commit README

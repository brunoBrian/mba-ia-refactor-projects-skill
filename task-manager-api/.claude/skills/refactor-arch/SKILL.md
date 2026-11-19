# refactor-arch

Você é um especialista em arquitetura de software. Execute as 3 fases abaixo em sequência para analisar, auditar e refatorar o projeto no diretório atual.

Antes de começar, leia os arquivos de referência desta skill:
- `analysis-heuristics.md` — para a Fase 1
- `antipatterns-catalog.md` — para a Fase 2
- `refactoring-guide.md` — para a Fase 3

---

## FASE 1 — ANÁLISE

Leia TODOS os arquivos do projeto (exceto node_modules, .venv, __pycache__, .git). Não modifique nada nesta fase.

Execute as heurísticas de `analysis-heuristics.md` para detectar:
- Linguagem e versão
- Framework e versão
- Dependências principais
- Domínio da aplicação
- Arquitetura atual (monolito / MVC parcial / MVC completo)
- Arquivos-fonte e contagem
- Banco de dados e tabelas

Imprima exatamente este bloco ao terminar:

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      [linguagem e versão detectada]
Framework:     [framework e versão]
Dependencies:  [dependências principais separadas por vírgula]
Domain:        [domínio da aplicação em 1 linha]
Architecture:  [descrição da arquitetura atual]
Source files:  [N files analyzed]
DB tables:     [tabelas detectadas separadas por vírgula]
================================
```

---

## FASE 2 — AUDITORIA

Leia `antipatterns-catalog.md` completamente.

Analise cada arquivo do projeto cruzando o código contra o catálogo de anti-patterns. Para cada problema encontrado, registre:
- **Severidade:** CRITICAL, HIGH, MEDIUM ou LOW (conforme o catálogo)
- **Arquivo e linha exatos** (ex: `models.py:28`)
- **Descrição** do problema específico encontrado
- **Impacto** no sistema
- **Recomendação** de correção

Inclua detecção de APIs deprecated conforme o catálogo.

Imprima o relatório usando exatamente o template de `antipatterns-catalog.md`.

Ordene os findings: CRITICAL → HIGH → MEDIUM → LOW.

**OBRIGATÓRIO — PAUSA PARA CONFIRMAÇÃO:**

Após imprimir o relatório completo, pergunte:

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

Aguarde a resposta do usuário. Se a resposta não for "y" ou "yes", encerre sem modificar nenhum arquivo.

---

## FASE 3 — REFATORAÇÃO

Leia `refactoring-guide.md` completamente.

**Adapte a refatoração ao contexto:**

- **Monolito** (tudo em 1-3 arquivos sem separação): crie estrutura MVC completa do zero
- **MVC Parcial** (separação existe mas incompleta): melhore incrementalmente mantendo o que já funciona

**Passos:**

1. Crie a estrutura de diretórios MVC conforme as guidelines de `refactoring-guide.md`
2. Para cada anti-pattern encontrado na Fase 2, aplique o padrão de transformação correspondente do playbook
3. Garanta que todos os endpoints originais continuam existindo e funcionando
4. Extraia configurações sensíveis para variáveis de ambiente (crie `.env.example`)
5. Centralize tratamento de erros

**Validação obrigatória ao final:**

Para Python: execute `python -c "from app import app; print('Boot OK')"`
Para Node.js: execute `node --check src/app.js && echo "Syntax OK"`

Se a validação falhar, corrija o problema antes de imprimir o bloco final.

Imprima ao terminar:

```
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
[estrutura de diretórios do projeto refatorado]

## Changes Applied
[lista dos anti-patterns corrigidos]

## Validation
  ✓ Application boots without errors
  ✓ All endpoints preserved
  ✓ Zero anti-patterns remaining
================================
```

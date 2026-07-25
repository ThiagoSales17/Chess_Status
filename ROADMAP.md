# Chess_Status v2 — ROADMAP

> Chess Discord Rich Presence — Refatoração completa com correção de bugs e novas features.

## Milestone 1: Bug Fixes + Testes Base

**Objetivo:** Corrigir os 4 bugs críticos, adicionar testes, criar PR para o repo original.

### Fase 1.1 — Correção de Bugs
- [ ] B1: Tratamento de erros separado (InvalidID vs erros de rede)
- [ ] B2: Retry/backoff exponencial para chamadas à API
- [ ] B3: Cleanup proper do RPC (try/finally + signal handler)
- [ ] B4: Username case-insensitive (lowercase automático)

### Fase 1.2 — Testes Base
- [ ] T1: Testes unitários para funções auxiliares
- [ ] T2: Mock da Chess.com API para testes de integração
- [ ] T3: Validação de que bugs estão corrigidos

### Fase 1.3 — PR + Merge
- [ ] PR1: Criar PR para repo original (Saul-Goodman6/Chess_Status)
- [ ] MERGE1: Merge da branch bugs na main

**Entregáveis:** Branch `bugs-fix` com PR aberto, testes passando.

---

## Milestone 2: Features + Arquitetura

**Objetivo:** Refatorar arquitetura, implementar features moderadas e avançadas.

### Fase 2.1 — Arquitetura Base
- [ ] A1: Criar `config.py` — argparse + .env + hot reload
- [ ] A2: Criar `chess_api.py` — wrapper com cache e rate limiting
- [ ] A3: Criar `models.py` — dataclasses tipados
- [ ] A4: Criar `presence.py` — gerenciamento RPC
- [ ] A5: Criar `utils.py` — helpers (winrate, flags, format)

### Fase 2.2 — Features Moderadas
- [ ] F1: Múltiplos modos de jogo (seleção interativa)
- [ ] F2: Win rate + stats detalhadas
- [ ] F3: Avatar, país, last_online, followers
- [ ] F4: League progress bar

### Fase 2.3 — Features Avançadas
- [ ] F5: Live game detection (jogo atual no Rich Presence)
- [ ] F6: Rating change notifications
- [ ] F7: Múltiplas contas + leaderboard local
- [ ] F8: Streamer mode

### Fase 2.4 — Integração Final
- [ ] I1: Refatorar `main.py` com nova arquitetura
- [ ] I2: Hot reload de config
- [ ] I3: Seleção interativa de modo de jogo

### Fase 2.5 — QA + Docs
- [ ] Q1: Testes unitários completos
- [ ] Q2: Testes de integração com mocks
- [ ] Q3: Review de segurança
- [ ] D1: Atualizar README.md
- [ ] D2: Criar CONFIG.md

**Entregáveis:** Branch `features-v2` com todas as features implementadas.

---

## Estratégia de Commits

Cada feature/bug será commitada individualmente no GitHub:

```
Main (current)
  └─ bugs-fix
       ├── fix: username case-insensitive
       ├── fix: error handling separado (InvalidID vs rede)
       ├── fix: RPC cleanup com signal handlers
       ├── fix: retry/backoff exponencial para API
       ├── test: testes unitários para bugs fix
       └── PR → Merge
            └─ features-v2
                 ├── feat: config.py (argparse + .env + hot reload)
                 ├── feat: chess_api.py (wrapper com cache)
                 ├── feat: models.py (dataclasses tipados)
                 ├── feat: utils.py (helpers winrate/flags)
                 ├── feat: presence.py (gerenciamento RPC)
                 ├── feat: múltiplos modos de jogo
                 ├── feat: win rate + stats detalhadas
                 ├── feat: avatar, país, last_online, followers
                 ├── feat: league progress bar
                 ├── feat: live game detection
                 ├── feat: rating change notifications
                 ├── feat: múltiplas contas + leaderboard
                 ├── feat: streamer mode
                 ├── refactor: main.py integrado
                 ├── test: testes completos
                 ├── docs: README.md atualizado
                 └── docs: CONFIG.md criado
```

## Ordem de Execução

```
Main (current)
  └─ bugs-fix → commits individuais → PR → Merge
       └─ features-v2 → commits individuais por feature → PR → Merge
```

### Regras de Commit
1. **Uma feature = um commit** (atomic commits)
2. **Mensagem no formato Conventional Commits**: `feat:`, `fix:`, `test:`, `docs:`, `refactor:`
3. **Cada commit deve ser funcional** (não quebrar o código existente)
4. **Push a cada commit** para manter o GitHub atualizado

## Dependências Críticas

1. **config.py** deve existir antes de features que dependem de configuração
2. **chess_api.py** deve ter retry/cache antes de features que fazem muitas chamadas
3. **models.py** deve existir antes de qualquer feature que use dados tipados
4. **Testes** devem passar antes de cada merge

## Riscos Identificados

1. Rate limiting da Chess.com API — mitigar com cache TTL 30s
2. Live game detection — race conditions entre detectar e mostrar
3. Hot reload — usar mtime check em vez de file watcher
4. Múltiplas contas — limitar a 3-5 contas para evitar throttling

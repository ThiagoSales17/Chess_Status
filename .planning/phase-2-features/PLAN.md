# Fase 2 — Features + Arquitetura

## Objetivo
Refatorar a arquitetura do projeto e implementar todas as features moderadas e avançadas, com commits individuais por feature.

## Estrutura de Commits

Cada feature será um commit atômico com mensagem no formato Conventional Commits:

```
feat(config): argparse + .env + hot reload
feat(chess_api): wrapper com cache e rate limiting
feat(models): dataclasses tipados para Player, GameStats, LiveGame
feat(utils): helpers para winrate, bandeiras, formatação
feat(presence): gerenciamento RPC com cleanup
feat(game-modes): múltiplos modos de jogo (Rapid/Blitz/Bullet/Daily)
feat(stats): win rate + stats detalhadas
feat(profile): avatar, país, last_online, followers
feat(league): barra de progresso da league
feat(live-game): detecção de jogo atual no Rich Presence
feat(notifications): mudanças de rating com notificações
feat(multi-account): múltiplas contas + leaderboard local
feat(streamer): modo streamer
refactor(main): integração da nova arquitetura
test(completo): testes unitários e de integração
docs(readme): README.md atualizado com novas features
docs(config): CONFIG.md criado
```

## Ordem de Implementação (com dependências)

### Wave 1: Fundação (sem dependências)
| Commit | Arquivo | Descrição |
|--------|---------|-----------|
| 1 | `config.py` | argparse + .env + hot reload |
| 2 | `models.py` | Dataclasses tipados |
| 3 | `chess_api.py` | Wrapper com cache + retry |
| 4 | `utils.py` | Helpers (winrate, flags, format) |
| 5 | `presence.py` | Gerenciamento RPC |

### Wave 2: Features Moderadas (dependem de Wave 1)
| Commit | Arquivo | Descrição |
|--------|---------|-----------|
| 6 | `main.py` | Múltiplos modos de jogo (seleção interativa) |
| 7 | `main.py` | Win rate + stats detalhadas |
| 8 | `main.py` | Avatar, país, last_online, followers |
| 9 | `main.py` | League progress bar |

### Wave 3: Features Avançadas (dependem de Wave 1-2)
| Commit | Arquivo | Descrição |
|--------|---------|-----------|
| 10 | `main.py` | Live game detection |
| 11 | `main.py` | Rating change notifications |
| 12 | `main.py` | Múltiplas contas + leaderboard |
| 13 | `main.py` | Streamer mode |

### Wave 4: Integração
| Commit | Arquivo | Descrição |
|--------|---------|-----------|
| 14 | `main.py` | Refatoração final com nova arquitetura |
| 15 | `tests/` | Testes completos |
| 16 | `README.md` | Documentação atualizada |
| 17 | `CONFIG.md` | Guia de configuração |

## Regras de Commit

1. **Uma feature = um commit** (atomic commits)
2. **Cada commit deve ser funcional** — não quebrar código existente
3. **Push a cada commit** — GitHub sempre atualizado
4. **Mensagem descritiva** — explicar O QUE mudou e POR QUÊ
5. **Não committar secrets** — .env no .gitignore

## Comandos de Commit (exemplo)

```bash
# Após criar config.py
git add config.py .env.example
git commit -m "feat(config): argparse + .env + hot reload para configuração"
git push origin features-v2

# Após criar models.py
git add models.py
git commit -m "feat(models): dataclasses tipados para Player, GameStats, LiveGame, League"
git push origin features-v2

# ... e assim por diante para cada feature
```

## Branch Strategy

```
main (após merge de bugs-fix)
  └─ features-v2
       ├── commits individuais por feature (1-17)
       └── PR → Merge
```

## Critérios de Aceite

- [ ] Cada feature tem seu próprio commit
- [ ] Cada commit é funcional (código não quebra)
- [ ] GitHub está atualizado após cada commit
- [ ] Todas as features funcionam juntas
- [ ] Testes passam
- [ ] Documentação está atualizada
- [ ] PR criado e mergeado

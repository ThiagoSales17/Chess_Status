# Fase 1.1 — Correção de Bugs

## Objetivo
Corrigir os 4 bugs críticos identificados no código atual, garantindo robustez e confiabilidade.

## Bugs a Corrigir

### Bug 1: Tratamento de erros de ID uniforme (Linha 34)
**Problema:** `InvalidID` e qualquer outra exceção são capturados juntos, então um erro de rede é interpretado como "ID inválido".

**Solução:**
```python
# ANTES (problemático)
except (InvalidID, Exception):
    print("❌ Error: The Discord Application ID is invalid or incorrect!")

# DEPOIS (corrigido)
except InvalidID:
    print("❌ Error: The Discord Application ID is invalid or incorrect!")
except DiscordNotFound:
    print("❌ Error: Discord desktop app is not running!")
except Exception as e:
    print(f"❌ Error: Unexpected error connecting to Discord: {e}")
```

**Arquivo:** `main.py` (linhas 28-36)

---

### Bug 2: Sem retry/backoff para API
**Problema:** Se a API do Chess.com cair, o loop continua fazendo request a cada 15s sem tolerância a falha.

**Solução:** Implementar retry com exponential backoff:
```python
import time

MAX_RETRIES = 3
BASE_DELAY = 2  # segundos

def fetch_with_retry(url, headers, max_retries=MAX_RETRIES):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise
            delay = BASE_DELAY * (2 ** attempt)
            print(f"⚠️ Request failed (attempt {attempt + 1}/{max_retries}): {e}")
            print(f"   Retrying in {delay}s...")
            time.sleep(delay)
```

**Arquivo:** `main.py` (função de fetch) + novo módulo ou inline

---

### Bug 3: RPC.connect() nunca é fechado
**Problema:** Se o script crashar, o socket IPC fica aberto.

**Solução:** Usar try/finally + signal handler:
```python
import signal
import sys

rpc = None

def cleanup(signum=None, frame=None):
    if rpc:
        try:
            rpc.close()
            print("🔌 RPC connection closed.")
        except:
            pass
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

try:
    rpc = Presence(app_id)
    rpc.connect()
    # ... loop principal
finally:
    cleanup()
```

**Arquivo:** `main.py` (setup e cleanup)

---

### Bug 4: Username case-sensitive
**Problema:** `Twg2000` vs `twg2000` pode dar 404 dependendo da API.

**Solução:** Forçar lowercase no username:
```python
username = input("Enter your chess.com account username: ").strip().lower()
```

**Arquivo:** `main.py` (linha 6)

---

## Plano de Implementação

### Step 1: Criar branch `bugs-fix`
```bash
git checkout -b bugs-fix
```

### Step 2: Corrigir Bug 4 (mais simples)
- Editar `main.py` linha 6: adicionar `.strip().lower()`

### Step 3: Corrigir Bug 1 (tratamento de erros)
- Reescrever bloco try/except (linhas 28-36) com tratamento separado

### Step 4: Corrigir Bug 3 (cleanup RPC)
- Adicionar signal handlers
- Adicionar try/finally no main
- Fechar RPC no cleanup

### Step 5: Corrigir Bug 2 (retry/backoff)
- Criar função `fetch_with_retry()`
- Substituir chamadas diretas no loop

### Step 6: Adicionar testes
- Testar cada correção com mocks

### Step 7: Commits incrementais (um por bug)
Cada correção será commitada separadamente:

```bash
# Após corrigir Bug 4
git add main.py
git commit -m "fix: username case-insensitive (lowercase automático)"
git push origin bugs-fix

# Após corrigir Bug 1
git add main.py
git commit -m "fix: error handling separado (InvalidID vs erros de rede)"
git push origin bugs-fix

# Após corrigir Bug 3
git add main.py
git commit -m "fix: RPC cleanup com signal handlers (SIGINT/SIGTERM)"
git push origin bugs-fix

# Após corrigir Bug 2
git add main.py
git commit -m "fix: retry/backoff exponencial para Chess.com API"
git push origin bugs-fix

# Após adicionar testes
git add tests/
git commit -m "test: testes unitários para correções de bugs"
git push origin bugs-fix
```

### Step 8: Criar PR
- Criar PR para `main` via `gh pr create`
- Título: "fix: Correção de 4 bugs críticos + testes base"
- Descrição listar cada bug corrigido

## Critérios de Aceite
- [ ] Username é automaticamente lowercased
- [ ] Erros de rede são tratados separadamente de erros de ID
- [ ] RPC é fechado corretamente em qualquer cenário (crash, SIGINT, SIGTERM)
- [ ] API tem retry com backoff exponencial (máx 3 tentativas)
- [ ] Todos os testes passam
- [ ] PR criado e revisado

## Riscos
1. Signal handlers podem interferir com input() — testar em ambiente controlado
2. Retry pode causar delay excessivo se API estiver fora — limitar a 3 tentativas

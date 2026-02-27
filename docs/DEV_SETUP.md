# DEV_SETUP (Local)

## Modos de execução suportados
- **On-prem (host OS)**: serviços API/Web/Worker rodam direto no sistema operacional local.
- **Docker Compose**: mantém o fluxo já existente em containers.

O ponto único de entrada é `./scripts/run.sh --mode onprem|docker <comando>`.

## Pré-requisitos
### On-prem (host OS)
- Python 3.11+
- Node.js 20+
- PostgreSQL e Redis rodando localmente (ou apontados via env)
- Dependências instaladas em:
  - `services/api` (inclui alembic, uvicorn)
  - `services/worker`
  - `services/web` (`npm install`)

### Docker
- Docker + Docker Compose

## Primeiro boot (On-prem recomendado)
1. Criar env on-prem:
   - `cp config/.env.onprem.example config/.env.onprem`
2. Bootstrap on-prem:
   - `./scripts/run.sh --mode onprem bootstrap`
   - O bootstrap gera automaticamente `JWT_SECRET_KEY` forte quando necessário.
3. Aplicar migrações sem Docker:
   - `./scripts/run.sh --mode onprem migrate`
   - (equivalente direto: `alembic upgrade head` em `services/api`)
4. Popular dados iniciais sem Docker:
   - Seed básico: `./scripts/run.sh --mode onprem seed`
   - Seed admin: `./scripts/run.sh --mode onprem seed-admin`
     - (equivalente direto: `python -m app.seed_admin` em `services/api`)
   - Seed completo: `./scripts/run.sh --mode onprem seed-comprehensive`
     - (equivalente direto: `python -m app.seed_comprehensive` em `services/api`)
5. Subir stack on-prem:
   - `./scripts/run.sh --mode onprem up`
6. Healthcheck:
   - `./scripts/run.sh --mode onprem health`

## Operação diária (On-prem)
- Status: `./scripts/run.sh --mode onprem status`
- Logs: `./scripts/run.sh --mode onprem logs`
- Migrações: `./scripts/run.sh --mode onprem migrate`
- Seeds: `./scripts/run.sh --mode onprem seed-admin` / `seed-comprehensive`
- Desligar: `./scripts/run.sh --mode onprem down`

## Fluxo Docker (permanece suportado)
1. Copiar env:
   - `cp infra/compose/.env.example infra/compose/.env`
2. Bootstrap:
   - `./scripts/run.sh --mode docker bootstrap`
   - O bootstrap gera automaticamente `JWT_SECRET_KEY` forte quando necessário.
3. Subir stack:
   - `./scripts/run.sh --mode docker up`
4. Healthcheck:
   - `./scripts/run.sh --mode docker health`
5. Migrações e seed:
   - `./scripts/run.sh --mode docker migrate`
   - `./scripts/run.sh --mode docker seed-admin`
   - `./scripts/run.sh --mode docker seed-comprehensive`

## URLs
- Web: http://localhost:3000
- API Docs: http://localhost:8000/docs
- API Health: http://localhost:8000/health

## Autenticação
### Usuário Admin (padrão)
- Email: `admin@mev.com`
- Senha: `admin123`
- Acesso: Dashboard administrativo completo

### Usuários Pacientes (seed_comprehensive)
- Emails: `nome.sobrenome1@paciente.com` até `nome.sobrenome30@paciente.com`
- Senha padrão: `paciente123`
- Acesso: Interface do paciente

### Endpoints de Autenticação
- Login: `POST /api/v1/auth/login`
- Registro: `POST /api/v1/auth/register`
- Usuários: `GET /api/v1/auth/users` (apenas admin)

## Reset total (Docker / APAGA DB)
- `./scripts/reset.sh`
- ⚠️ Remove todos os volumes do Docker incluindo dados do banco
- Após reset, executar migrações e seed novamente


## Worker on-prem: registro e monitoramento do processo
No modo on-prem, o instalador (`./scripts/run.sh --mode onprem bootstrap`) prepara diretórios de runtime em `.runtime/onprem` para registrar PID e logs. O processo do worker é gerenciado por `scripts/onprem/worker.sh`, que delega para funções comuns de serviço (`start_service`, `stop_service`, `status_service`) em `scripts/onprem/common.sh`.

### Como o registro funciona
- **Start**: `./scripts/run.sh --mode onprem up` executa `worker.sh start`, iniciando `python -m app.main` com `nohup`.
- **PID file**: o PID fica em `.runtime/onprem/pids/worker.pid`.
- **Logs**: saída padrão e erro vão para `.runtime/onprem/logs/worker.log`.
- **Recuperação de PID stale**: ao iniciar, se o PID existir mas não estiver vivo, ele é removido automaticamente antes do novo start.

### Como monitorar e operar
- **Status rápido**: `./scripts/run.sh --mode onprem status`
- **Logs em tempo real**: `./scripts/run.sh --mode onprem logs`
- **Parada graciosa**: `./scripts/run.sh --mode onprem down` (com fallback para `kill -9` se necessário).

### Variáveis recomendadas para o worker
- `CELERY_BROKER_URL` (opcional; fallback para `REDIS_URL`)
- `CELERY_RESULT_BACKEND` (opcional; fallback para `REDIS_URL`)
- `CELERY_RUN_MODE=worker|beat|both` (padrão: `both`)
- `STREAK_RECALC_CRON`, `BADGE_ASSIGN_CRON`, `REMINDER_CRON` para customizar agenda

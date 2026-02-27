# Copilot Context — Motor Clínico (Gamificação Lifestyle)

## Objetivo
Plataforma de gamificação para aderência a hábitos (medicina de estilo de vida).
MVP: Programas -> Hábitos -> Check-ins -> Pontos/Streak/Badges + Painel Admin.

## Arquitetura (monorepo)
- services/api: FastAPI (REST) + Postgres + Redis
- services/worker: Jobs assíncronos (streak, badges, lembretes, rotinas)
- services/web: Next.js (UI paciente + admin)
- infra/compose: docker-compose e .env
- scripts: comandos de operação local

## Regras de engenharia
- Containers stateless: nada crítico no disco do container.
- Estado fica em Postgres/Redis/Storage (quando existir).
- API é a única que fala com DB (web nunca acessa DB direto).
- Endpoints versionados: /api/v1/...
- Eventos comportamentais devem ser registráveis (analytics/event table).

## Padrões de código
Python:
- Pydantic schemas para request/response
- SQLAlchemy 2 + Alembic migrations
- black line-length 100, isort profile black
- logs em stdout (JSON quando possível)

Web:
- Consumir API via NEXT_PUBLIC_API_BASE_URL
- Evitar lógica de negócio complexa no frontend

## Convenções de dados (canônicas)
Entidades: User, Program, Habit, Enrollment, CheckIn, PointsLedger, Badge, UserBadge, NotificationEvent, Streak.
Streak: sequência de dias cumpridos por hábito/programa.
Pontuação: ledger (event-sourced) em vez de coluna "pontos" mutável sem histórico.
Autenticação: JWT tokens, roles (admin/patient), bcrypt hashing.

## Autenticação e Autorização
- Sistema de autenticação baseado em JWT (24h expiration)
- Roles: `admin` (acesso total) e `patient` (acesso limitado)
- Middleware: `require_admin` para endpoints administrativos
- Senhas: hash bcrypt via passlib

## Interface Admin
Páginas disponíveis:
- `/admin` - Dashboard principal
- `/admin/analytics` - Métricas e insights do sistema
- `/admin/rewards-config` - Configuração de pontos
- `/admin/badges` - Gerenciamento de badges
- `/admin/programs` - CRUD de programas e hábitos
- `/admin/patients` - Gerenciamento de usuários

## Comandos úteis
- Subir stack: ./scripts/up.sh
- Logs: ./scripts/logs.sh
- Migrações: ./scripts/migrate.sh
- Seed básico: ./scripts/seed.sh
- Criar admin: docker compose exec api python -m app.seed_admin
- Seed completo (30 pacientes): docker compose exec api python -m app.seed_comprehensive

## Novo domínio: Protocolos Clínicos (Young Forever)
- Novas entidades: `ProtocolTemplate`, `ProtocolPhase`, `ArtifactDefinition`, `ProtocolRun`, `ArtifactInstance`, `InterventionTemplate`, `ProtocolGeneratedItem`.
- Fluxo principal: iniciar run -> submeter artefatos (triagem/baseline/wearable) -> computar prioridade (`top_function`) -> gerar intervenções -> avançar fases -> reteste.
- Integração com MEV: intervenções geram `Habit` com `source_type="protocol"`, `source_ref_id=<run_id>` e `target_metric_key`.
- `CheckIn` agora suporta métricas estruturadas (`metric_key`, `value_numeric`, `value_text`) mantendo compatibilidade com uso legado.
- Milestones de protocolo podem gerar pontos em `PointsLedger` usando `event_type="protocol_milestone"`.

### Endpoints novos
- Admin templates:
  - `GET /api/v1/admin/protocol-templates/`
  - `POST /api/v1/admin/protocol-templates/`
  - `GET /api/v1/admin/protocol-templates/{id}`
  - `PUT /api/v1/admin/protocol-templates/{id}`
- Runs:
  - `POST /api/v1/protocol-runs/`
  - `GET /api/v1/protocol-runs/{id}`
  - `POST /api/v1/protocol-runs/{id}/artifacts/{artifact_key}`
  - `POST /api/v1/protocol-runs/{id}/generate-interventions`
  - `POST /api/v1/protocol-runs/{id}/advance-phase`
  - `GET /api/v1/protocol-runs/{id}/timeline`

### Seed
- Novo seed dedicado: `python -m app.seed_young_forever`.
- Inclui template `young_forever_core_v1`, fases base, artefatos (`q_7_functions`, `lab_baseline_panel`, `wearable_core`) e intervenções mínimas (sono/movimento/alimentação).

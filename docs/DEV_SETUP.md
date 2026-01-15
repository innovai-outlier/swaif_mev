# DEV_SETUP (Local)

## Pré-requisitos
- Docker + Docker Compose
- VSCode
- (Recomendado no Windows) WSL2

## Primeiro boot
1. Copiar env:
   - `cp infra/compose/.env.example infra/compose/.env`
2. Bootstrap:
   - `./scripts/bootstrap.sh`
3. Subir stack:
   - `./scripts/up.sh`
4. Healthcheck:
   - `./scripts/health.sh`
5. Aplicar migrações:
   - `./scripts/migrate.sh`
6. Popular dados iniciais:
   - Criar admin: `docker compose -f infra/compose/docker-compose.yml exec api python -m app.seed_admin`
   - Criar dados completos: `docker compose -f infra/compose/docker-compose.yml exec api python -m app.seed_comprehensive`

## Operação diária
- Logs: `./scripts/logs.sh`
- Migrações: `./scripts/migrate.sh`
- Seed básico: `./scripts/seed.sh`
- Seed admin: Criar usuário admin@mev.com
- Seed completo: 30 pacientes + programas + histórico de check-ins
- Desligar: `./scripts/down.sh`

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

## Reset total (APAGA DB)
- `./scripts/reset.sh`
- ⚠️ Remove todos os volumes do Docker incluindo dados do banco
- Após reset, executar migrações e seed novamente

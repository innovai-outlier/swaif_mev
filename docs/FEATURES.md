# Motor Clínico - Features Documentation

## Visão Geral
Motor Clínico é uma plataforma de gamificação para medicina de estilo de vida, focada em aumentar a aderência dos pacientes a programas de hábitos saudáveis através de mecânicas de gamificação.

## Arquitetura do Sistema

### Backend (FastAPI)
- **API RESTful** com OpenAPI/Swagger docs em `/docs`
- **Autenticação JWT** com roles (admin/patient)
- **PostgreSQL** para persistência
- **Redis** para cache e sessões
- **Alembic** para migrações de banco de dados

### Frontend (Next.js)
- **Interface do Paciente**: Dashboard pessoal, check-ins, progresso
- **Interface Admin**: Gerenciamento completo da plataforma
- **Tailwind CSS** para estilização
- **Componentes reutilizáveis** (UIComponents)

### Worker (Background Jobs)
- Cálculo de streaks
- Atribuição automática de badges
- Lembretes e notificações
- Rotinas agendadas

## Funcionalidades Principais

### 1. Autenticação e Usuários

#### Registro e Login
- Endpoint: `POST /api/v1/auth/register`
- Endpoint: `POST /api/v1/auth/login`
- JWT tokens com expiração de 24 horas
- Senhas criptografadas com bcrypt

#### Roles de Usuário
- **Admin**: Acesso completo ao painel administrativo
- **Patient**: Acesso limitado às funcionalidades do paciente

#### Gerenciamento de Usuários (Admin)
- Listar todos os usuários
- Criar novos usuários
- Visualizar estatísticas por usuário
- Filtros por role e status

### 2. Programas e Hábitos

#### Criação de Programas
- Nome e descrição customizáveis
- Status ativo/inativo
- Múltiplos hábitos por programa

#### Hábitos
- Vinculados a programas específicos
- Pontos configuráveis por check-in
- Descrição e instruções
- Status ativo/inativo

#### Inscrições (Enrollments)
- Usuários se inscrevem em programas
- Acompanhamento de progresso individual
- Status de inscrição ativa/inativa

### 3. Check-ins

#### Registro de Check-ins
- Endpoint: `POST /api/v1/check-ins`
- Data do check-in
- Notas opcionais
- Validação de duplicatas

#### Visualização de Check-ins
- Histórico completo por usuário
- Filtro por programa/hábito
- Filtro por período

### 4. Sistema de Pontuação

#### Points Ledger (Event-Sourced)
- Todos os pontos registrados como eventos
- Histórico imutável
- Rastreamento de origem (check-in, badge, etc.)
- Cálculo de totais sob demanda

#### Tipos de Eventos de Pontos
- `check_in`: Pontos por check-in concluído
- `streak_milestone`: Bônus por sequências
- `badge_earned`: Pontos por conquista de badge

#### Configuração de Recompensas (Admin)
- Pontos por check-in
- Pontos por streaks
- Pontos por badges

### 5. Streaks

#### Cálculo Automático
- Sequência de dias consecutivos
- Por hábito ou programa
- Current streak (ativo)
- Longest streak (recorde)

#### Worker Background
- Atualização diária de streaks
- Detecção de quebra de sequência
- Atribuição de pontos bônus

### 6. Badges (Conquistas)

#### Tipos de Badges
- **Iniciante**: Primeiro check-in
- **Consistente**: 7 dias de streak
- **Dedicado**: 30 dias de streak
- **Mestre**: 100 check-ins
- Customizáveis pelo admin

#### Atribuição Automática
- Worker verifica critérios periodicamente
- Notificação ao usuário
- Registro em `user_badges`
- Pontos de recompensa

#### Gerenciamento (Admin)
- Criar novos badges
- Editar existentes
- Definir critérios
- Configurar pontos de recompensa

### 7. Analytics Dashboard (Admin)

#### Métricas do Sistema
- Total de pacientes
- Programas ativos
- Total de check-ins
- Pontos distribuídos
- Inscrições ativas
- Badges conquistados
- Check-ins últimos 7/30 dias
- Taxa de engajamento

#### Top Performers
- Usuários mais ativos
- Programas mais populares
- Rankings por check-ins

#### Performance de Programas
- Inscrições por programa
- Check-ins por programa
- Pontos distribuídos
- Média de check-ins por inscrição

#### Estatísticas de Badges
- Total de badges disponíveis
- Badges mais conquistados
- Distribuição de conquistas

#### Engagement Trends
- Check-ins diários
- Usuários ativos diários
- Períodos configuráveis (7/30/90 dias)

### 8. Interface Administrativa

#### Dashboard Principal (`/admin`)
- Cards de navegação rápida
- Visão geral do sistema
- Atalhos para principais funcionalidades

#### Analytics (`/admin/analytics`)
- Métricas em tempo real
- Gráficos e tabelas
- Top performers
- Tendências de engajamento

#### Recompensas (`/admin/rewards-config`)
- Configurar pontos por check-in
- Configurar pontos por streaks
- Configurar pontos por badges
- Atualização em tempo real

#### Badges (`/admin/badges`)
- Listar todos os badges
- Criar novo badge
- Editar badge existente
- Estatísticas de conquistas

#### Programas (`/admin/programs`)
- CRUD completo de programas
- Gerenciar hábitos associados
- Ativar/desativar programas
- Visualizar inscrições

#### Pacientes (`/admin/patients`)
- Listar todos os usuários
- Criar novos pacientes
- Visualizar estatísticas individuais
- Filtros e busca
- Gerenciar status

### 9. Componentes UI Reutilizáveis

#### UIComponents.tsx
- **LoadingSpinner**: Indicador de carregamento (sm/md/lg)
- **PageLoading**: Estado de carregamento de página completa
- **ErrorAlert**: Alertas de erro com dismiss
- **SuccessAlert**: Alertas de sucesso com dismiss
- **EmptyState**: Estado vazio com ícone e ação
- **TableSkeleton**: Skeleton loader para tabelas
- **StatCard**: Card de estatística com cores e ícones
- **Badge**: Badge de status (success/warning/error/info)

#### AdminHeader
- Navegação persistente
- Links para todas as páginas admin
- Informações do usuário
- Botão de logout

### 10. Seeds e Dados de Teste

#### seed_admin.py
- Cria usuário administrador padrão
- Email: `admin@mev.com`
- Senha: `admin123`

#### seed_comprehensive.py
- **30 pacientes** com nomes brasileiros
- **12 programas** de lifestyle medicine
- **43 hábitos** distribuídos pelos programas
- **14 badges** de conquista
- **Histórico de 60 dias** de check-ins
- **Pontuação acumulada**
- **Streaks calculados**
- **Badges conquistados**

#### Dados de Teste
- Atividade realista (30-95% taxa de check-in)
- Distribuição natural de streaks
- Múltiplos programas por usuário
- Variação de engajamento

## Endpoints da API

### Autenticação
- `POST /api/v1/auth/register` - Registrar novo usuário
- `POST /api/v1/auth/login` - Login e obter token JWT
- `GET /api/v1/auth/users` - Listar usuários (admin)
- `GET /api/v1/auth/me` - Dados do usuário atual

### Programas
- `GET /api/v1/programs` - Listar programas
- `POST /api/v1/programs` - Criar programa (admin)
- `GET /api/v1/programs/{id}` - Detalhes do programa
- `PUT /api/v1/programs/{id}` - Atualizar programa (admin)
- `DELETE /api/v1/programs/{id}` - Deletar programa (admin)

### Hábitos
- `GET /api/v1/programs/{program_id}/habits` - Listar hábitos
- `POST /api/v1/programs/{program_id}/habits` - Criar hábito (admin)
- `PUT /api/v1/habits/{id}` - Atualizar hábito (admin)
- `DELETE /api/v1/habits/{id}` - Deletar hábito (admin)

### Check-ins
- `POST /api/v1/check-ins` - Registrar check-in
- `GET /api/v1/check-ins` - Listar check-ins do usuário
- `GET /api/v1/check-ins/habit/{habit_id}` - Check-ins por hábito

### Pontos
- `GET /api/v1/users/{user_id}/points` - Total de pontos
- `GET /api/v1/users/{user_id}/points/history` - Histórico de pontos

### Badges
- `GET /api/v1/badges` - Listar badges disponíveis
- `GET /api/v1/users/{user_id}/badges` - Badges do usuário
- `POST /api/v1/admin/badges` - Criar badge (admin)
- `PUT /api/v1/admin/badges/{id}` - Atualizar badge (admin)

### Analytics (Admin)
- `GET /api/v1/admin/analytics/overview` - Visão geral do sistema
- `GET /api/v1/admin/analytics/engagement-trends` - Tendências de engajamento
- `GET /api/v1/admin/analytics/program-performance` - Performance de programas
- `GET /api/v1/admin/analytics/badge-statistics` - Estatísticas de badges

## Fluxo de Trabalho Típico

### Para Administrador
1. Login em `/login` com credenciais admin
2. Visualizar analytics em `/admin/analytics`
3. Criar programas em `/admin/programs`
4. Configurar badges em `/admin/badges`
5. Ajustar recompensas em `/admin/rewards-config`
6. Gerenciar pacientes em `/admin/patients`

### Para Paciente
1. Login em `/login` com credenciais de paciente
2. Visualizar programas disponíveis
3. Inscrever-se em programas
4. Realizar check-ins diários
5. Acompanhar progresso (pontos, streaks, badges)
6. Visualizar badges conquistados

## Próximas Features (Roadmap)

### Analytics Avançado
- Gráficos de tendências interativos
- Exportação de relatórios
- Comparações período a período
- Segmentação de usuários

### Notificações
- Lembretes de check-in
- Notificações de badges
- Alertas de quebra de streak
- Email/Push notifications

### Gamificação Avançada
- Desafios entre usuários
- Leaderboards públicos
- Recompensas físicas
- Níveis e progressão

### Integração
- Wearables (Fitbit, Apple Health)
- Calendário (Google Calendar)
- Exportação de dados
- API pública

### Mobile
- App nativo iOS/Android
- Notificações push
- Offline support
- Camera para check-in visual

## Tecnologias Utilizadas

### Backend
- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy** - ORM para PostgreSQL
- **Alembic** - Migrações de banco de dados
- **Pydantic** - Validação de dados
- **passlib + bcrypt** - Hash de senhas
- **python-jose** - JWT tokens
- **PostgreSQL** - Banco de dados relacional
- **Redis** - Cache e sessões

### Frontend
- **Next.js 14** - React framework com App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first CSS
- **React Hooks** - State management

### DevOps
- **Docker** - Containerização
- **Docker Compose** - Orquestração local
- **Git** - Controle de versão
- **GitHub** - Repositório

## Boas Práticas Implementadas

### Segurança
- Senhas nunca armazenadas em texto plano
- JWT tokens com expiração
- CORS configurado
- Validação de input (Pydantic)
- Proteção de rotas admin

### Performance
- Event-sourced points ledger
- Índices de banco de dados
- Lazy loading de componentes
- Cache Redis

### Manutenibilidade
- Código modular
- Componentes reutilizáveis
- Documentação inline
- Tipagem forte (TypeScript/Pydantic)
- Padrões de projeto consistentes

### UX/UI
- Loading states
- Error handling gracioso
- Feedback visual imediato
- Design responsivo
- Navegação intuitiva

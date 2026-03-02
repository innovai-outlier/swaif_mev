Você é o Codex (engenheiro full-stack) e vai PLANEJAR e IMPLEMENTAR uma nova versão do sistema “Motor Clínico MVP / MEV” para suportar uma jornada clínica baseada no livro “Jovem Para Sempre” (Parte III), mantendo compatibilidade com o que já existe.

## CONTEXTO DO REPO (já existente)
Repo (zip analisado): /mnt/data/swaif_mev-main.zip

Arquitetura:
- services/api: FastAPI + SQLAlchemy 2 + Alembic + Postgres + Redis
- services/web: Next.js (mev-web)
- services/worker: Celery (ainda placeholder em worker/app/main.py)
- infra/compose/docker-compose.yml: db (postgres), redis, api, worker, web

Modelos atuais (services/api/app/models.py):
- Program, Habit, Enrollment, CheckIn
- PointsLedger (event-sourcing de pontos)
- Badge, UserBadge
- Streak
- RewardConfig
Esses itens NÃO podem quebrar.

## OBJETIVO (NOVA JORNADA “JOVEM PARA SEMPRE”)
Adicionar suporte a “Protocolos Clínicos” como templates executáveis + execuções por paciente (runs), com:
- Triagem estruturada (questionários)
- Baseline (painel de exames)
- Monitoramento (wearables / métricas)
- Intervenções (gerar hábitos e check-ins no motor MEV existente)
- Reavaliação / Reteste (ciclos)
- Priorização por “funções” (ranking do que está mais desequilibrado)

A regra de ouro: Protocolo NÃO é “só uma lista de hábitos”. Protocolo é um pipeline que gera hábitos e cobra evidências.

## REQUISITOS FUNCIONAIS
1) Templates:
   - Criar “ProtocolTemplate” versionado (ex.: young_forever_core_v1)
   - Fases/etapas ordenadas (triage, baseline, intervene, retest)
   - Definições de artefatos (questionário 7 funções, painel lab baseline, wearable core, etc.)
2) Execução por paciente:
   - Criar “ProtocolRun” para um paciente (user_id)
   - Armazenar instâncias de artefatos (respostas, resultados de exames, payloads de wearable)
   - Calcular scores e destacar prioridades (ex.: top_function + score)
3) Integração com MEV:
   - Intervenções do protocolo devem gerar Habits no Program existente (ou anexar ao Program do paciente)
   - Check-ins devem suportar valor numérico e chave de métrica (ex.: energy_0_10, sleep_hours)
   - PointsLedger, Streak, Badges devem continuar funcionando (e poder pontuar milestones do protocolo)
4) Admin / Clinica:
   - CRUD de ProtocolTemplate (admin)
   - Iniciar/pausar/finalizar ProtocolRun (admin/clinica)
   - Submeter artefatos (admin/clinica e/ou paciente, conforme rota)
   - Endpoint “generate_interventions” para criar hábitos e checkins-alvo com base nas prioridades
5) Ciclo:
   - Fases com critérios simples de avanço (ex.: “triage completo” -> baseline; baseline completo -> intervene; etc.)
   - Reteste: permitir criar um novo ArtifactInstance de um mesmo artifact_definition e comparar com baseline (sem overwrites)
6) Seed:
   - Criar seed “young_forever_core_v1” com:
     - fases básicas
     - artifact_definitions: q_7_functions, lab_baseline_panel, wearable_core
     - um conjunto mínimo de interventions templates (ex.: sono fundação, movimento, alimentação base)
   - Incluir um Program “Young Forever - Core” opcional para receber hábitos gerados
7) Qualidade:
   - Adicionar testes (pytest) para fluxo principal: criar template, iniciar run, submeter questionário, gerar intervenções, criar hábitos, check-in com valores, avançar fase.
   - Migrations Alembic completas.
   - Atualizar docs (COPILOT_CONTEXT.md e/ou docs/ se existir) explicando o novo domínio.

## REQUISITOS NÃO-FUNCIONAIS / GUARDRAILS
- Não remover colunas/tabelas existentes.
- Alterações em Habit/CheckIn devem ser backwards-compatible (nullable + default).
- Persistência de artefatos deve usar JSONB no Postgres (se já estiver em uso) OU Text JSON serializado se a stack atual não estiver configurada; preferir JSONB se possível.
- Índices para performance:
  - artifact_instances: (protocol_run_id, artifact_definition_id, collected_at desc)
  - protocol_runs: (user_id, status)
  - habits: (program_id, source_type, source_ref_id)
  - check_ins: (user_id, metric_key, check_in_date) se metric_key adicionado
- Worker: não é obrigatório automatizar tudo, mas criar ao menos uma tarefa Celery “recompute_protocol_run” opcional (placeholder útil).

## MODELAGEM (IMPLEMENTAR)
Adicionar modelos SQLAlchemy:

1) protocol_templates
- id (int)
- code (string unique)
- name
- version
- description (text)
- is_active (bool)
- default_program_id (nullable FK -> programs.id)
- created_at / updated_at

2) protocol_phases
- id
- protocol_template_id (FK)
- name (string)
- phase_key (string ex.: triage/baseline/intervene/retest)
- phase_order (int)
- entry_criteria_json (nullable)
- exit_criteria_json (nullable)

3) artifact_definitions
- id
- protocol_template_id (FK)
- artifact_key (string ex.: q_7_functions)
- type (string enum-ish)
- name
- schema_json (nullable)
- scoring_json (nullable)

4) protocol_runs
- id
- user_id (int)
- protocol_template_id (FK)
- status (string)
- current_phase_id (nullable FK -> protocol_phases.id)
- started_at
- completed_at (nullable)
- created_at / updated_at

5) artifact_instances
- id
- protocol_run_id (FK)
- artifact_definition_id (FK)
- collected_at (datetime)
- payload_json (nullable)
- computed_json (nullable)  # scores, top_function, flags
- source (string nullable: patient/admin/integration)

6) intervention_templates (opcional, mas recomendado)
- id
- protocol_template_id (FK)
- intervention_key
- type (habit|supplement|diet|appointment|task)
- name
- description
- habit_blueprint_json (nullable)  # se type=habit: pontos, metric_key, frequência etc.
- activation_rules_json (nullable)

7) protocol_generated_items (opcional)
- id
- protocol_run_id
- intervention_template_id
- generated_habit_id (FK -> habits.id, nullable)
- created_at

ALTERAÇÕES COMPATÍVEIS EM MODELOS EXISTENTES:
A) Habit:
- source_type (string, default "manual", nullable=False)
- source_ref_id (int nullable)
- target_metric_key (string nullable)  # ex.: sleep_hours

B) CheckIn:
- metric_key (string nullable)
- value_numeric (Numeric/Float nullable)
- value_text (Text nullable)

## SCHEMAS Pydantic (services/api/app/schemas*.py)
Criar schemas novos:
- ProtocolTemplateCreate/Update/Out
- ProtocolRunCreate/Out
- ArtifactDefinitionOut
- ArtifactInstanceCreate/Out
- GenerateInterventionsRequest/Response
- PhaseAdvanceRequest/Response (opcional)

## ROTAS / ENDPOINTS (services/api/app/routers/)
Criar router: protocol_templates.py (admin)
- GET /admin/protocol-templates
- POST /admin/protocol-templates
- GET /admin/protocol-templates/{id}
- PUT /admin/protocol-templates/{id}
- POST /admin/protocol-templates/{id}/seed-young-forever (opcional) OU usar seed script

Criar router: protocol_runs.py
- POST /protocol-runs (admin/clinica inicia run para user_id + template_code)
- GET /protocol-runs/{id}
- POST /protocol-runs/{id}/artifacts/{artifact_key}  (submete ArtifactInstance)
- POST /protocol-runs/{id}/generate-interventions (gera hábitos no Program associado)
- POST /protocol-runs/{id}/advance-phase (avança fase se critérios mínimos satisfeitos)
- GET /protocol-runs/{id}/timeline (retorna fases + artefatos + intervenções geradas)

Integrar no app/main.py para incluir routers.

## LÓGICA DE NEGÓCIO (MVP)
1) Scoring do questionário “7 funções”:
- Recebe payload com respostas (sim/não ou escala)
- Computa score por função e “top_function”
- Salva em computed_json
2) Critérios de fase:
- triage: existe artifact_instance de q_7_functions
- baseline: existe artifact_instance de lab_baseline_panel (mesmo que parcial)
- intervene: pelo menos 1 habit gerado OU plano criado
- retest: novo artifact_instance do mesmo lab_panel após X dias (não enforced por tempo no MVP)
3) Generate interventions:
- Se top_function = X, gerar um conjunto mínimo de hábitos (blueprints) associados:
  - Ex.: Sono/ritmo, Movimento, Alimentação base (mantém generalista mas dirigido)
- Criar Habits no Program:
  - Se template.default_program_id existir: usar ele
  - Senão: criar Program por run (ex.: “Protocolo <nome> - <paciente>”) e manter enrollment
- Gerar também “checkins-métrica” se necessário (via hábito + checkin)
4) Pontos:
- Ao completar artefatos-chave (triage/baseline/retest), registrar PointsLedger “protocol_milestone” (pontos configuráveis via RewardConfig)
- Badges opcionais: “Baseline concluído”, “Primeiro reteste”

## WORKER (OPCIONAL MAS BEM-VINDO)
- Implementar Celery básico em services/worker com config via REDIS_URL
- Criar tarefa: recompute_protocol_run(protocol_run_id) para recalcular computed_json (ex.: se artefatos novos chegarem)

## MIGRATIONS
- Criar migrations Alembic:
  - novas tabelas
  - add columns em habits e check_ins
  - índices necessários

## TESTES
Criar testes pytest para:
- criar template seed “young_forever_core_v1”
- iniciar run para user_id=1
- submeter questionário -> computed_json inclui top_function
- gerar intervenções -> cria habits com source_type="protocol"
- criar check-in com value_numeric e metric_key
- advance-phase funcionando

## WEB (NÃO OBRIGATÓRIO NO MVP, MAS SE DER)
No services/web (Next.js):
- Tela admin simples:
  - listar templates
  - iniciar run
  - submeter artefato (form JSON simples)
  - visualizar timeline do run

## ENTREGÁVEIS
1) Código implementado no repo seguindo padrões atuais (FastAPI routers, schemas, models, alembic)
2) Seeds (script em app/seed_comprehensive.py ou novo seed_young_forever.py)
3) Testes + instruções de execução local via docker-compose
4) Documentação breve do domínio “Protocolos” e como plugar com o motor MEV

## PASSOS DE EXECUÇÃO (faça nesta ordem)
1) Mapear padrões existentes: como routers fazem CRUD, como DB session é gerenciada, auth/roles
2) Criar modelos novos + relationships
3) Criar migrations Alembic
4) Criar schemas Pydantic
5) Criar routers + serviços (funções internas) para:
   - start run
   - submit artifact
   - compute scoring
   - generate interventions (criar program/habits)
   - advance phase
6) Seed young_forever_core_v1
7) Testes
8) (Opcional) Worker e Web admin

COMECE PRODUZINDO UM PLANO TÉCNICO EM TÓPICOS (arquivos a criar/alterar, migrations, endpoints) E EM SEGUIDA FAÇA OS COMMITS/ALTERAÇÕES NO CÓDIGO.

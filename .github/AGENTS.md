---
spark: true
scf_file_role: "config"
scf_version: "1.2.0"
scf_merge_strategy: "replace"
scf_protected: false
scf_owner: "spark-base"
scf_merge_priority: 10
---

# AGENTS Index

## Base Agents (spark-base)

- spark-assistant — executor — workspace entrypoint, onboarding, package lifecycle, diagnostics
- spark-guide — executor — user entrypoint, framework orientation, routing to spark-assistant
- Agent-Orchestrator — executor — orchestration, workflow, runtime-state
- Agent-Git — executor — git, commit, push, merge, tag proposal
- Agent-Helper — executor — framework-help, discovery, routing hints
- Agent-Release — executor — release-coordination, semver, packaging guidance
- Agent-FrameworkDocs — executor — framework-docs, changelog, AGENTS index
- Agent-Welcome — executor — setup, project-profile, onboarding
- Agent-Research — support/internal — fallback research, unknown-stack briefing
- Agent-Analyze — dispatcher — analyze
- Agent-Plan — dispatcher — plan
- Agent-Docs — dispatcher — docs
- Agent-Validate — dispatcher — validate

## Plugin Agents

Questa sezione viene popolata dai plugin installati tramite file `AGENTS-{plugin-id}.md`.
Il motore aggrega i file disponibili tramite `scf://agents-index`.

## MCP Runtime Tools (engine v2.4.0 — feature introdotte tra v1.5.0 e v1.6.0)

I tool seguenti sono disponibili e operativi nel motore corrente (v2.4.0).

### Runtime State (da v1.5.0)

- `scf_get_runtime_state()` — legge `.github/runtime/orchestrator-state.json`
- `scf_update_runtime_state(patch)` — aggiorna lo stato runtime dell'orchestratore con merge parziale
- `scf://runtime-state` — resource JSON con lo stato runtime corrente
- `scf://agents-index` — aggrega `AGENTS.md` e `AGENTS-{plugin-id}.md`

### Package Management (da v1.6.0)

- `scf_check_updates()` — restituisce solo i pacchetti installati con aggiornamento disponibile
- `scf_update_package(package_id)` — aggiorna un singolo pacchetto preservando i file modificati dall'utente

***

## Agenti di Supporto Interno

Questi agenti non fanno parte del workflow principale ANALYZE→RELEASE.
Vengono invocati automaticamente da altri agenti in condizioni specifiche.
L'utente non li chiama direttamente.

### Agent-Research

- **Ruolo**: fallback per linguaggi senza plugin SCF specializzato
- **Visibilità**: internal
- **Invocato da**: Agent-Analyze, Agent-Plan, Agent-Docs, Agent-Orchestrator, Agent-Validate
- **Produce**: context brief in `.github/runtime/research-cache/{language}-{task-type}.md`
- **Limite**: non sostituisce un plugin testato — fallback trasparente dichiarato

<!-- SCF:BEGIN:agents-index -->

# AGENTS — Indice agenti SPARK

> Generato automaticamente da `scf_bootstrap_workspace`. NON modificare manualmente il blocco fra i marker SCF.

## Agenti engine

- `@spark-assistant` — owner: `spark-framework-engine`
- `@spark-engine-maintainer` — owner: `spark-framework-engine`
- `@spark-guide` — owner: `spark-framework-engine`
- `@spark-welcome` — owner: `spark-framework-engine`

## Agenti pacchetto

### spark-base

- `@Agent-Analyze` — Agente di discovery e analisi codebase. Attivalo per analizzare architettura,
- `@Agent-Docs` — Agente per sincronizzazione documentazione. Aggiorna API.md, ARCHITECTURE.md,
- `@Agent-FrameworkDocs` — Agente esclusivo per la manutenzione del Framework Copilot. Aggiorna
- `@Agent-Git` — Agente specializzato nella gestione delle operazioni git autorizzate.
- `@Agent-Helper` — Agente consultivo sul Framework Copilot. Risponde a domande su agenti,
- `@Agent-Orchestrator` — Orchestratore autonomo del ciclo E2E. Coordina agenti, verifica gate e gestisce confidence.
- `@Agent-Plan` — Agente per breaking down architetturale in fasi implementabili. Crea
- `@Agent-Release` — Agente per versioning semantico, build con cx_freeze, package creation
- `@Agent-Research` — Agente di fallback per ricerca linguaggio-dominio e best practice sintetizzate.
- `@Agent-Validate` — Agente di validazione e test coverage. Esegue test, genera report, propone
- `@Agent-Welcome` — Agente di setup e manutenzione del profilo progetto. Raccoglie le informazioni
- `@spark-assistant` — >
- `@spark-guide` — >
<!-- SCF:END:agents-index -->

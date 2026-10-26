# 🧠 Psych-AI: Autonomous Agentic Cognitive Twin Platform

> **A forensic-grade, self-evaluating cognitive twin platform coordinating multi-agent dialectical deliberation, autobiographical episodic memory, circadian rhythm forecasting, and verifiable decision integrity.**

---

## ⚡ Overview

**Psych-AI** is an advanced cognitive architecture designed to observe, model, and actively safeguard psychological energy and focus. Unlike passive mood trackers or generic chatbots, Psych-AI maintains a stateful digital twin of user cognition, executing parallel multi-agent debate, forecasting 4-branch counterfactual trajectories, and enforcing adversarial safety vetoes against burnout-accelerating consensus.

```
                                  [ User Scenario / Ambient Rhythms ]
                                                   │
                        ┌──────────────────────────┴──────────────────────────┐
                        ▼                                                     ▼
           [ Circadian Rhythm Engine ]                            [ Episodic Memory Engine ]
        (Diurnal capacity & velocity spike)                    (Hebbian graph & schemas)
                        │                                                     │
                        └──────────────────────────┬──────────────────────────┘
                                                   ▼
                                       [ Orchestrator Bus ]
         ┌───────────────────┬───────────────────┼───────────────────┬───────────────────┐
         ▼                   ▼                   ▼                   ▼                   ▼
  [PerceptionAgent]   [CognitionAgent]   [PredictionAgent]   [StrategyAgent]       [MetaAgent]
  - Sensory triage    - Bias & distortion - 4-Branch shadow   - Adaptive Q-policy  - Ethical bounds
  - Stress rating     - Cognitive flags   - Burnout forecast  - Precedent match    - Conflict rule
         │                   │                   │                   │                   │
         └───────────────────┴───────────────────┼───────────────────┴───────────────────┘
                                                 ▼
                                     [ Calibration Engine ]
                                  (Dynamic weights: 0.98^days)
                                                 ▼
                                      [ Synthesis / Debate ]
                                                 ▼
                                  [ Adversarial Red-Team Gate ]
                                 (Audit sycophancy & toxic cheer)
                                            │        │
                                     [Veto] ▼        ▼ [Approved]
                             (Paced Micro-Reset)   [ Cryptographic SHA-256 Hashing ]
                                                             │
                                        ┌────────────────────┴────────────────────┐
                                        ▼                                         ▼
                            [ Forensic Decision Replay ]               [ Telemetry & Metrics ]
                             (Bit-for-bit replayability)             (Prometheus & Health Probes)
```

---

## 🏛️ Core Architectural Pillars

### 1. Multi-Agent Dialectical Deliberation
- **PerceptionAgent**: Triage and classification of acute stress, contextual environment, and psychological energy reserves.
- **CognitionAgent**: Identification of cognitive distortions (e.g., catastrophizing, all-or-nothing thinking, emotional reasoning).
- **PredictionAgent**: Longitudinal trajectory forecasting assessing immediate burnout risk and friction velocity.
- **StrategyAgent**: Contextual action formulation querying Q-learning policy matrices and historical precedent.
- **MetaAgent**: Master arbiter resolving inter-agent ideological conflicts and enforcing hard ethical guardrails.

### 2. Reliability & Calibration Engine (Phase 10)
- **Recency Decay Formula**: Older successes decay dynamically: $\text{Effective Accuracy} = \text{Accuracy} \times 0.98^{\text{days}}$.
- **Trust Tiers**: Continuous assignment into `Trusted`, `Stable`, `Uncertain`, or `Degraded`.
- **Dynamic Weighting**: $\text{Weight} = \text{Confidence} \times \text{Reliability} \times \text{Effective Accuracy}$.

### 3. Autobiographical Episodic & Associative Memory (Phase 11)
- **Hebbian Association Network**: Dynamic edges linking concepts via `triggers`, `mitigated_by`, and `escalates_to` relationships.
- **Semantic Retrieval**: Jaccard token overlap blended with emotional valence proximity.
- **Sleep-Like Schema Consolidation**: Offline batch processing extracting recurring patterns into universal behavioral schemas.

### 4. Circadian Cognitive Rhythm & Counterfactual Shadow Engine (Phase 12)
- **Diurnal Capacity Curve**: 5 distinct daily cognitive phases (Morning Focus, Midday Surge, Afternoon Dip, Evening Wind-Down, Late-Night Vulnerability).
- **Stress Velocity Detection**: Instant identification of acute acceleration in user tension.
- **4-Branch "What-If" Multi-Path Simulation**: Evaluates proposed actions (Break, Reframe, Push-Through, Sleep) across simulated burnout and composite payoff scores.

### 5. Adversarial Red-Teaming & Forensic Post-Mortem (Phase 13)
- **Pre-Dispatch Auditing**: Enforces strict safety vetoes on toxic positivity, sycophantic enabling, or over-optimistic friction traps.
- **Root-Cause Attribution**: Forensically penalizes culpable agents upon negative user feedback.

### 6. Forensic Decision Replay & Zero-Knowledge Vault (Phase 14)
- **SHA-256 Decision Hashing**: Deterministic cryptographic signatures sealing all scenario inputs, agent states, and version registries.
- **Real-Time Deliberation Streaming**: Progressive Server-Sent Events (SSE) pipe exposing inner agent deliberations.
- **Privacy Vault**: Zero-knowledge complete twin JSON export and selective episode pruning.

---

## 🌐 Application Route Map

| Route | View | Description |
|---|---|---|
| **`/`** | **Platform Landing** | System status, live agent bus preview, architectural pillars, and onboarding. |
| **`/login`** | **Auth Gateway** | User registration, sign-in, and instant guest demo mode. |
| **`/dashboard`** | **Cognitive State** | Real-time state orb, mood timeline, ambient rhythm banners, retrospective memory query, and privacy vault. |
| **`/simulate`** | **Multi-Agent Simulator** | Deliberation console, agent trust tables, decision pipeline, counterfactual branching, and forensic replay. |
| **`/evolution`** | **Longitudinal Identity** | Archetype drift trajectory, Hebbian associative graph visualization, and post-mortem failure feed. |

---

## 🚀 Quickstart

### Prerequisites
- [Docker](https://www.docker.com/) & Docker Compose (or Python 3.11+ and Node.js 20+)

### Option 1: Docker Compose (Full Stack)

```bash
# Clone the repository
git clone https://github.com/your-username/psych-ai.git
cd psych-ai

# Start PostgreSQL, FastAPI Backend, and Next.js Frontend
docker compose up --build -d
```

- **Frontend Application**: [http://localhost:3000](http://localhost:3000)
- **Backend API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Prometheus Telemetry**: [http://localhost:8000/metrics](http://localhost:8000/metrics)
- **Container Health**: [http://localhost:8000/api/v1/metrics/healthz](http://localhost:8000/api/v1/metrics/healthz)

### Option 2: Local Development Setup

#### 1. Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

#### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 🧪 Testing & Verification

The platform maintains a deterministic testing and preflight verification suite:

```bash
# 1. Run all 20 backend unit tests
cd backend
.\venv\Scripts\python -m unittest discover -s tests -p "test_*.py" -v

# 2. Run the 6-stage production preflight diagnostic suite
python scripts/preflight_check.py

# 3. Verify frontend TypeScript compilation
cd frontend
npx tsc --noEmit
```

### Preflight Diagnostics Included:
1. `[1/6]` **System Version Matrix**: Confirms centralized module registry tracking.
2. `[2/6]` **Database Model Mapping**: Validates 19 registered SQLAlchemy metadata tables.
3. `[3/6]` **Cryptographic Tamper Resistance**: Confirms SHA-256 decision hash generation and replay.
4. `[4/6]` **Adversarial Red-Team Gatekeeper**: Verifies mandatory veto on burnout traps.
5. `[5/6]` **Episodic Memory Engine**: Tests keyword extraction and semantic Jaccard overlap.
6. `[6/6]` **Agent Trust Tier Calibration**: Confirms dynamic reliability score classification.

---

## 📁 Repository Structure

```
Psych-AI/
├── .github/
│   └── workflows/
│       └── ci.yml                 # Automated CI/CD pipeline
├── backend/
│   ├── alembic/                   # Database migration environment
│   │   └── versions/
│   │       └── 001_initial_schema.py
│   ├── agents/                    # Perception, Cognition, Prediction, Strategy, Meta
│   ├── api/                       # FastAPI router endpoints
│   ├── core/                      # Versioning, configuration, security
│   ├── db/                        # PostgreSQL connection & migration runner
│   ├── models/                    # 19 SQLAlchemy database entities
│   ├── services/                  # Reliability, Red-Team, Replay, Memory, Health
│   ├── tests/                     # 20-Point deterministic test suite
│   ├── Dockerfile                 # Multi-stage production backend image
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/                   # Next.js App Router (/, /login, /dashboard, /simulate, /evolution)
│   │   ├── components/            # Visual cognitive UI widgets & modals
│   │   └── lib/                   # API client bindings
│   ├── Dockerfile                 # Multi-stage standalone Next.js image
│   └── package.json
├── scripts/
│   ├── preflight_check.py         # Production readiness diagnostic script
│   └── seed_demo_data.py          # Synthetic cognitive twin data seeder
├── docker-compose.yml             # Orchestration for Postgres, Backend, Frontend
└── README.md
```

---

## 🔒 Security & Data Sovereignty

- **Zero-Knowledge Privacy Vault**: Complete autobiographical memory and state history can be exported as standard JSON or permanently pruned at any time.
- **Forensic Tamper Resistance**: All multi-agent deliberation traces are sealed cryptographically with SHA-256 hashes, ensuring provable auditability without third-party vendor lock-in.

---

## 📄 License
MIT License &copy; 2026 Psych-AI Platform Contributors.

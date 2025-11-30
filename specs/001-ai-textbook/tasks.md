# Tasks: Physical AI & Humanoid Robotics Educational Textbook

**Input**: Design documents from `/specs/001-ai-textbook/`
**Prerequisites**: spec.md (user stories with priorities P1-P3)

**Organization**: Tasks grouped by user story for independent implementation and testing

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend**: `frontend/docs/`, `frontend/src/`
- **Backend**: `backend/app/`, `backend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify Docusaurus structure and prepare for content creation

- [ ] T001 Verify Docusaurus project structure in frontend/
- [ ] T002 Update frontend/sidebars.ts with 4-module structure
- [ ] T003 [P] Configure Prism syntax highlighting for Python, C++, YAML, Bash
- [ ] T004 [P] Verify responsive layout on mobile/tablet/desktop viewports

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core structure that ALL user stories depend on

**⚠️ CRITICAL**: No content or features can be added until this is complete

- [ ] T005 Create module directory structure: frontend/docs/module-01-ros2/, module-02-simulation/, module-03-isaac/, module-04-vla/
- [ ] T006 [P] Create intro.md placeholders for all 4 modules
- [ ] T007 [P] Update frontend/sidebars.ts with complete navigation hierarchy
- [ ] T008 [P] Create frontend/static/code-examples/ directory for downloadable code
- [ ] T009 Verify Docusaurus build completes in <2 minutes (constitution requirement)

**Checkpoint**: Directory structure ready - content creation can begin in parallel

---

## Phase 3: User Story 1 - Learning Core Content (Priority: P1) 🎯 MVP

**Goal**: Students access comprehensive educational content on Physical AI through 4 progressive modules with chapters, code examples, and exercises

**Independent Test**: Navigate through all 4 modules, read chapters, view code examples with inline comments, complete exercises - delivers complete educational value standalone

### Module 1: ROS 2 Fundamentals (Weeks 3-5)

- [ ] T010 [P] [US1] Write frontend/docs/module-01-ros2/intro.md - Module overview, learning outcomes, prerequisites
- [ ] T011 [P] [US1] Write frontend/docs/module-01-ros2/week-3-basics.md - ROS 2 architecture, installation (Ubuntu 22.04), first workspace
- [ ] T012 [P] [US1] Write frontend/docs/module-01-ros2/week-3-nodes-topics.md - Creating nodes, publishers/subscribers, topic communication with Python code examples
- [ ] T013 [P] [US1] Write frontend/docs/module-01-ros2/week-4-services-actions.md - Service client/server pattern, action servers, parameters with code examples
- [ ] T014 [P] [US1] Write frontend/docs/module-01-ros2/week-4-packages.md - Creating custom ROS 2 packages, package.xml, CMakeLists.txt, colcon build
- [ ] T015 [P] [US1] Write frontend/docs/module-01-ros2/week-5-urdf.md - URDF for humanoid robots, joint types, visual/collision geometry, Xacro macros
- [ ] T016 [P] [US1] Write frontend/docs/module-01-ros2/week-5-control.md - ros2_control framework, controllers, hardware interfaces for humanoid joints
- [ ] T017 [P] [US1] Create frontend/static/code-examples/module-01/ with working ROS 2 Python examples (publisher, subscriber, service, URDF)

### Module 2: Gazebo & Unity Simulation (Weeks 6-7)

- [ ] T018 [P] [US1] Write frontend/docs/module-02-simulation/intro.md - Why simulation matters for Physical AI, comparison of Gazebo vs Unity
- [ ] T019 [P] [US1] Write frontend/docs/module-02-simulation/week-6-gazebo-basics.md - Gazebo installation, SDF models, physics engines (ODE, Bullet), spawning robots
- [ ] T020 [P] [US1] Write frontend/docs/module-02-simulation/week-6-physics.md - Gravity, collisions, friction, contact forces, rigid body dynamics for humanoids
- [ ] T021 [P] [US1] Write frontend/docs/module-02-simulation/week-7-sensors.md - Simulating LiDAR, depth cameras (Intel RealSense), IMUs, joint encoders
- [ ] T022 [P] [US1] Write frontend/docs/module-02-simulation/week-7-unity.md - Unity for robotics, Unity Robotics Hub, URDF importer, articulation bodies
- [ ] T023 [P] [US1] Write frontend/docs/module-02-simulation/week-7-worlds.md - Building custom environments, terrains, obstacles, lighting for realistic sim-to-real
- [ ] T024 [P] [US1] Create frontend/static/code-examples/module-02/ with Gazebo SDF files and Unity scene setup instructions

### Module 3: NVIDIA Isaac Platform (Weeks 8-10)

- [ ] T025 [P] [US1] Write frontend/docs/module-03-isaac/intro.md - NVIDIA Isaac ecosystem overview, Isaac Sim vs Isaac ROS vs Isaac SDK
- [ ] T026 [P] [US1] Write frontend/docs/module-03-isaac/week-8-isaac-sim.md - Installing Isaac Sim, photorealistic rendering, Omniverse, USD format
- [ ] T027 [P] [US1] Write frontend/docs/module-03-isaac/week-8-synthetic-data.md - Generating synthetic training data, domain randomization, perception ground truth
- [ ] T028 [P] [US1] Write frontend/docs/module-03-isaac/week-9-isaac-ros.md - Isaac ROS GEMs, hardware-accelerated VSLAM, stereo vision, DNN inference
- [ ] T029 [P] [US1] Write frontend/docs/module-03-isaac/week-9-perception.md - Object detection, pose estimation, depth perception for manipulation tasks
- [ ] T030 [P] [US1] Write frontend/docs/module-03-isaac/week-10-nav2.md - Nav2 stack for humanoid navigation, costmaps, path planning (Dij kstra, A*), recovery behaviors
- [ ] T031 [P] [US1] Write frontend/docs/module-03-isaac/week-10-bipedal-locomotion.md - Bipedal walking controllers, ZMP stability, gait generation
- [ ] T032 [P] [US1] Create frontend/static/code-examples/module-03/ with Isaac Sim Python scripts and Nav2 config files

### Module 4: Vision-Language-Action (VLA) Integration (Weeks 11-13)

- [ ] T033 [P] [US1] Write frontend/docs/module-04-vla/intro.md - Convergence of LLMs and robotics, what is VLA, embodied AI agents
- [ ] T034 [P] [US1] Write frontend/docs/module-04-vla/week-11-voice-to-action.md - OpenAI Whisper for speech recognition, command parsing, intent classification
- [ ] T035 [P] [US1] Write frontend/docs/module-04-vla/week-11-llm-planning.md - Using GPT-4 for task planning, ReAct pattern, chain-of-thought for robots
- [ ] T036 [P] [US1] Write frontend/docs/module-04-vla/week-12-multimodal.md - Vision + language fusion, CLIP for visual grounding, referring expressions
- [ ] T037 [P] [US1] Write frontend/docs/module-04-vla/week-12-gesture-recognition.md - Hand gesture detection (MediaPipe), pose estimation for HRI
- [ ] T038 [P] [US1] Write frontend/docs/module-04-vla/week-13-capstone-intro.md - Capstone project: Autonomous humanoid with conversational AI
- [ ] T039 [P] [US1] Write frontend/docs/module-04-vla/week-13-capstone-implementation.md - Step-by-step integration: voice → planning → navigation → manipulation
- [ ] T040 [P] [US1] Create frontend/static/code-examples/module-04/ with Whisper integration, GPT-4 planning scripts, full capstone code

### Content Quality Assurance

- [ ] T041 [US1] Review all chapters for technical accuracy (constitution: Content Quality NON-NEGOTIABLE)
- [ ] T042 [US1] Verify all code examples have inline comments and explanations (FR-004)
- [ ] T043 [US1] Ensure consistent terminology across all 4 modules (constitution requirement)
- [ ] T044 [US1] Test all code examples in isolated environments (constitution: Testing NON-NEGOTIABLE)
- [ ] T045 [US1] Validate navigation: any chapter reachable in <3 clicks (FR-003, SC-002)
- [ ] T046 [US1] Run Lighthouse audit to verify <3s page load on 3G (FR-020, SC-005)
- [ ] T047 [US1] Run axe DevTools to verify WCAG 2.1 AA accessibility (FR-021, SC-008)
- [ ] T048 [US1] Verify responsive design on mobile (375px), tablet (768px), desktop (1920px) (FR-005)

**Checkpoint**: At this point, User Story 1 (MVP) is complete - full textbook with 4 modules accessible and tested ✅

---

## Phase 4: User Story 2 - AI-Powered Learning Assistant (Priority: P2)

**Goal**: Students interact with intelligent RAG chatbot for contextual Q&A with source citations and >85% accuracy

**Independent Test**: Submit queries about course topics, verify responses cite correct sources, measure accuracy on 50-query validation set, confirm <3s response time

### Backend Setup

- [ ] T049 [P] [US2] Initialize backend/ directory with Python 3.11 project structure
- [ ] T050 [P] [US2] Create backend/requirements.txt with FastAPI, openai, qdrant-client, psycopg, langchain dependencies
- [ ] T051 [P] [US2] Create backend/app/config.py for environment variables (OPENAI_API_KEY, QDRANT_URL, DATABASE_URL)
- [ ] T052 [P] [US2] Create backend/app/main.py with FastAPI app initialization
- [ ] T053 [P] [US2] Setup CORS middleware in backend/app/main.py for frontend origin

### Database & Vector Store

- [ ] T054 [P] [US2] Create backend/app/db/postgres.py with async Neon Postgres connection pool
- [ ] T055 [P] [US2] Create backend/app/db/qdrant.py with Qdrant client initialization
- [ ] T056 [P] [US2] Create backend/app/models/chat.py with ChatConversation, ChatMessage Pydantic models
- [ ] T057 [P] [US2] Create backend/app/db/repositories/chat_repository.py for conversation CRUD operations

### RAG Pipeline

- [ ] T058 [P] [US2] Create backend/app/services/embedding_service.py for OpenAI text-embedding-3-small (1536 dimensions)
- [ ] T059 [US2] Create backend/scripts/seed_embeddings.py to chunk all markdown content (512 tokens max, sentence-grouped per research.md)
- [ ] T060 [US2] Run seed_embeddings.py to populate Qdrant collection "content_embeddings" with module/chapter metadata
- [ ] T061 [P] [US2] Create backend/app/services/rag_service.py for vector retrieval (top 5 passages, <200ms per FR-007)
- [ ] T062 [US2] Create backend/app/services/chatbot_service.py for GPT-4 response generation with source citations (FR-009)

### API Endpoints

- [ ] T063 [P] [US2] Create backend/app/api/chat.py with POST /api/chat/query endpoint (FR-006)
- [ ] T064 [US2] Implement query processing: embedding → Qdrant search → GPT-4 generation → source formatting
- [ ] T065 [US2] Add response time validation: <3s end-to-end (FR-008, SC-004)
- [ ] T066 [P] [US2] Create backend/app/api/chat.py with GET /api/chat/history/{user_id} endpoint

### Frontend Integration

- [ ] T067 [P] [US2] Create frontend/src/theme/Root.tsx wrapper component per research.md decision
- [ ] T068 [P] [US2] Create frontend/src/context/ChatContext.tsx for global chat state
- [ ] T069 [P] [US2] Create frontend/src/components/ChatWidget/ChatWidget.tsx persistent chat UI
- [ ] T070 [P] [US2] Create frontend/src/components/ChatWidget/MessageList.tsx with source citation links
- [ ] T071 [P] [US2] Create frontend/src/components/ChatWidget/InputBox.tsx with text selection handler
- [ ] T072 [P] [US2] Create frontend/src/services/chat.ts API client with credentials: 'include'
- [ ] T073 [US2] Implement window.getSelection() for selected text → chatbot query UX

### RAG Validation

- [ ] T074 [P] [US2] Create backend/tests/validation/test_queries.json with 50 test queries covering all modules
- [ ] T075 [US2] Create backend/scripts/test_rag_accuracy.py to measure accuracy against validation set
- [ ] T076 [US2] Run RAG accuracy validation, ensure >85% correctness (FR-010, SC-003, constitution: AI Integration)
- [ ] T077 [US2] Optimize chunking/prompts if accuracy <85%, re-test until passing

**Checkpoint**: User Story 2 complete - RAG chatbot functional with >85% accuracy, <3s responses ✅

---

## Phase 5: User Story 3 - Personalized Learning Experience (Priority: P3)

**Goal**: Students receive customized content based on background (undergraduate/graduate/professional) after authentication

**Independent Test**: Create accounts with different backgrounds, verify content adapts appropriately for each user type

### Authentication Backend

- [ ] T078 [P] [US3] Create backend/app/models/user.py with User, UserProfile Pydantic models
- [ ] T079 [P] [US3] Create backend/app/db/repositories/user_repository.py for user CRUD
- [ ] T080 [P] [US3] Create backend/app/services/auth_service.py with better-auth integration
- [ ] T081 [P] [US3] Implement bcrypt password hashing (10+ rounds per constitution)
- [ ] T082 [P] [US3] Create backend/app/utils/security.py for HTTP-only cookie configuration (FR-015)

### API Endpoints

- [ ] T083 [P] [US3] Create backend/app/api/auth.py with POST /api/auth/signup endpoint (FR-011)
- [ ] T084 [P] [US3] Add background questionnaire fields to signup (education_level, experience_years, learning_goals per FR-012)
- [ ] T085 [P] [US3] Create backend/app/api/auth.py with POST /api/auth/login endpoint
- [ ] T086 [P] [US3] Implement session cookie with Secure, HttpOnly, SameSite=None for cross-origin (research.md decision)
- [ ] T087 [P] [US3] Create backend/app/api/user.py with GET /api/user/preferences endpoint
- [ ] T088 [P] [US3] Create backend/app/api/user.py with PUT /api/user/preferences endpoint

### Frontend Auth UI

- [ ] T089 [P] [US3] Create frontend/src/components/AuthForms/LoginForm.tsx
- [ ] T090 [P] [US3] Create frontend/src/components/AuthForms/SignupForm.tsx
- [ ] T091 [P] [US3] Create frontend/src/components/AuthForms/BackgroundQuestionnaire.tsx (undergraduate/graduate/professional radio buttons)
- [ ] T092 [P] [US3] Create frontend/src/services/auth.ts with login/signup API calls (credentials: 'include')
- [ ] T093 [P] [US3] Create frontend/src/hooks/useAuth.ts for auth state management

### Personalization

- [ ] T094 [P] [US3] Create backend/app/services/personalization_service.py to adapt content complexity (FR-014)
- [ ] T095 [P] [US3] Create frontend/src/components/PersonalizedContent/PersonalizedContent.tsx wrapper
- [ ] T096 [US3] Implement content adaptation logic: undergraduate (more explanations), graduate (balanced), professional (production focus)
- [ ] T097 [US3] Store user preferences in Neon Postgres (FR-013)

**Checkpoint**: User Story 3 complete - Auth working, content personalized by background ✅

---

## Phase 6: User Story 4 - Multilingual Access (Priority: P3)

**Goal**: Urdu-speaking students can translate content while preserving technical terms and code blocks

**Independent Test**: Translate chapters to Urdu, verify technical terms in English, code blocks unchanged, formatting maintained

### Translation Backend

- [ ] T098 [P] [US4] Create backend/app/models/translation.py with TranslationRequest, TranslationCache Pydantic models
- [ ] T099 [P] [US4] Create backend/app/db/repositories/translation_cache_repository.py
- [ ] T100 [P] [US4] Create backend/app/services/translation_service.py with OpenAI GPT-4 translation (FR-016)
- [ ] T101 [US4] Implement prompt engineering to preserve technical terms in English (FR-017, research.md strategy)
- [ ] T102 [US4] Implement code block extraction/restoration to prevent translation (FR-018, research.md regex approach)
- [ ] T103 [P] [US4] Implement SHA256 hash-based caching (30-day TTL per research.md)

### API Endpoints

- [ ] T104 [P] [US4] Create backend/app/api/translate.py with POST /api/translate endpoint
- [ ] T105 [P] [US4] Create backend/app/api/translate.py with GET/PUT /api/translate/preference for language persistence (FR-019)

### Frontend Integration

- [ ] T106 [P] [US4] Create frontend/src/components/Translation/LanguageToggle.tsx (English/Urdu switcher)
- [ ] T107 [P] [US4] Create frontend/src/services/translation.ts API client
- [ ] T108 [P] [US4] Create frontend/src/hooks/useTranslation.ts for translation state
- [ ] T109 [US4] Implement language preference persistence in localStorage
- [ ] T110 [US4] Add translation toggle to Docusaurus navbar

### Translation Validation

- [ ] T111 [US4] Manually review 20 sample translations with Urdu speaker
- [ ] T112 [US4] Verify 100% of technical terms preserved in English (SC-007)
- [ ] T113 [US4] Verify all code blocks unchanged after translation
- [ ] T114 [US4] Test cache hit ratio (target 80% per research.md estimate)

**Checkpoint**: User Story 4 complete - Urdu translation working with technical accuracy ✅

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements affecting multiple user stories

- [ ] T115 [P] Update frontend/README.md with setup instructions
- [ ] T116 [P] Update backend/README.md with API documentation
- [ ] T117 [P] Create backend/.env.example with required environment variables
- [ ] T118 [P] Add rate limiting middleware (100 req/min per user per constitution)
- [ ] T119 [P] Add request logging for all API endpoints
- [ ] T120 [P] Create .github/workflows/frontend-ci.yml for Docusaurus build + deploy
- [ ] T121 [P] Create .github/workflows/backend-ci.yml for pytest + lint
- [ ] T122 Verify final build time <2 minutes (SC-009, constitution requirement)
- [ ] T123 Run full constitution compliance check across all features
- [ ] T124 Create deployment guide for GitHub Pages (frontend) + Render (backend)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational - MVP! Can deliver independently
- **User Story 2 (Phase 4)**: Depends on Foundational + US1 content existing (needs text to embed)
- **User Story 3 (Phase 5)**: Depends on Foundational - independent of US1/US2
- **User Story 4 (Phase 6)**: Depends on Foundational + US1 content existing (needs text to translate)
- **Polish (Phase 7)**: Depends on desired user stories being complete

### User Story Dependencies

- **US1 (P1)**: Independent - only needs Foundational phase
- **US2 (P2)**: Needs US1 content to exist (can't embed empty textbook)
- **US3 (P3)**: Independent - auth/personalization doesn't require other stories
- **US4 (P3)**: Needs US1 content to exist (can't translate empty textbook)

### Parallel Opportunities

**Within User Story 1 (MVP):**
- All module chapters can be written in parallel (T010-T040)
- T041-T048 quality checks must run sequentially after content complete

**Within User Story 2 (RAG):**
- T049-T057 backend setup tasks can run in parallel
- T058, T061, T062 services can be developed in parallel
- T067-T072 frontend components can be developed in parallel

**Across User Stories:**
- US3 (auth) can start in parallel with US2 (RAG) after US1 completes
- US4 (translation) must wait for US1 content but can run with US2/US3

---

## Parallel Example: Module Content Creation

```bash
# ALL module chapters can be written simultaneously:
Task: "Write frontend/docs/module-01-ros2/week-3-basics.md"
Task: "Write frontend/docs/module-02-simulation/week-6-gazebo-basics.md"
Task: "Write frontend/docs/module-03-isaac/week-8-isaac-sim.md"
Task: "Write frontend/docs/module-04-vla/week-11-voice-to-action.md"
# (31 total parallel content tasks: T010-T040)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only) - RECOMMENDED FOR HACKATHON

1. Complete Phase 1: Setup (T001-T004) - 10 min
2. Complete Phase 2: Foundational (T005-T009) - 20 min
3. Complete Phase 3: User Story 1 (T010-T048) - **CORE WORK** - Parallel content creation
4. **STOP and VALIDATE**: Test navigation, code examples, responsive design
5. **Deploy to GitHub Pages** - 100 base points secured! ✅

**Estimated Time**: ~6-8 hours for comprehensive educational content (4 modules × 3-4 chapters each)

### Incremental Delivery (Add Bonus Features)

After MVP deployed:

1. **Add US2 (RAG Chatbot)**: +50 bonus points
   - Complete Phase 4 (T049-T077)
   - Test chatbot accuracy >85%
   - Deploy backend to Render

2. **Add US3 (Auth + Personalization)**: +30 bonus points
   - Complete Phase 5 (T078-T097)
   - Test signup/login flow

3. **Add US4 (Urdu Translation)**: +20 bonus points
   - Complete Phase 6 (T098-T114)
   - Test translation accuracy

4. **Polish**: Complete Phase 7 (T115-T124)

**Maximum Points**: 100 (base) + 200 (bonus) = 300 points

---

## Task Summary

- **Total Tasks**: 124
- **Phase 1 (Setup)**: 4 tasks
- **Phase 2 (Foundational)**: 5 tasks
- **Phase 3 (US1 - MVP)**: 39 tasks (31 parallel content + 8 QA)
- **Phase 4 (US2 - RAG)**: 29 tasks
- **Phase 5 (US3 - Auth)**: 20 tasks
- **Phase 6 (US4 - Translation)**: 17 tasks
- **Phase 7 (Polish)**: 10 tasks

**Parallel Opportunities**: 87 tasks marked [P] can run in parallel

**MVP Scope**: Phases 1-3 only (48 tasks) = Functional textbook with 4 modules ✅

---

## Notes

- [P] = Parallelizable (different files, no blocking dependencies)
- [US1/US2/US3/US4] = User story traceability
- File paths are absolute from repository root
- Constitution compliance verified at T041-T048, T123
- All code examples must be tested per constitution NON-NEGOTIABLE requirement
- Focus: Deliver MVP (US1) first for maximum visible progress and base points

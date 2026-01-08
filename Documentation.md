Gmail	Chhavi Jain <chhavi.jain@gmail.com>
prep
Chhavi Jain <Chhavi.Jain@lplfinancial.com>	Wed, Jan 7, 2026 at 3:22 PM
To: TVLR <chhavi.jain@gmail.com>
# DevFlow: Complete Documentation

 

## Table of Contents

 

1. [Introduction & Philosophy](#introduction--philosophy)

2. [System Architecture Overview](#system-architecture-overview)

3. [The Kanban Board System](#the-kanban-board-system)

4. [Agent System Deep Dive](#agent-system-deep-dive)

5. [The Spec Pipeline](#the-spec-pipeline)

6. [Git Worktrees & Parallel Execution](#git-worktrees--parallel-execution)

7. [Memory Layer (Graphiti)](#memory-layer-graphiti)

8. [AI-Powered Merge Conflict Resolution](#ai-powered-merge-conflict-resolution)

9. [QA Validation Loop](#qa-validation-loop)

10. [Agent Terminals](#agent-terminals)

11. [Insights & Ideation](#insights--ideation)

12. [Roadmap Generation](#roadmap-generation)

13. [Changelog & GitHub Integration](#changelog--github-integration)

14. [Frontend Architecture (Electron)](#frontend-architecture-electron)

15. [Backend Architecture (Python)](#backend-architecture-python)

16. [Installation & Setup](#installation--setup)

17. [CLI Usage](#cli-usage)

18. [Security Model](#security-model)

19. [Configuration Reference](#configuration-reference)

20. [Troubleshooting](#troubleshooting)

21. [Reference-Based Code Generation](#reference-based-code-generation)

22. [Reference Code Examples & Product Requirements](#reference-code-examples--product-requirements)

 

---

 

## Introduction & Philosophy

 

### What is DevFlow?

 

DevFlow is a **production-ready framework for autonomous multi-session AI coding**. It transforms the way developers interact with AI by moving from a simple chat interface to a structured, visual workflow management system.

 

### The Core Philosophy Shift

 

Traditional AI coding assistants operate as chatbots - you type a command, wait for output, and manage the session manually. **You are effectively babysitting the AI.**

 

DevFlow changes this dynamic:

- **From Babysitter to Manager**: Instead of being in the loop for every action, you define tasks and let AI agents execute autonomously

- **From Chat to Workflow**: Instead of a blank terminal, you have a Kanban board with columns for Planning, In Progress, AI Review, Human Review, and Done

- **From Single-threaded to Parallel**: Run multiple AI agents simultaneously on different parts of your project

- **From Forgetful to Persistent**: The AI remembers your codebase architecture across sessions

 

### Key Value Propositions

 

1. **Context Preservation**: Solves "context amnesia" - AI retains knowledge about your codebase

2. **Parallel Execution**: Multiple agents work simultaneously without conflicts

3. **Self-Validation**: Built-in QA loop catches issues before human review

4. **Visual Management**: Kanban board treats AI like a team member

5. **Isolation**: All work happens in Git worktrees - your main branch stays safe

 

---

 

## System Architecture Overview

 

### High-Level Structure

 

```

DevFlow/

├── apps/

│   ├── backend/           # Python - Core AI framework

│   │   ├── agents/        # Agent implementations (Planner, Coder, QA)

│   │   ├── core/          # Client, auth, security, workspace

│   │   ├── integrations/  # Graphiti memory, Linear, GitHub

│   │   ├── merge/         # AI-powered merge conflict resolution

│   │   ├── prompts/       # Agent system prompts (47 .md files)

│   │   ├── qa/            # QA validation pipeline

│   │   ├── spec/          # Spec creation pipeline

│   │   └── runners/       # Entry points and orchestrators

│   │

│   └── frontend/          # Electron Desktop Application

│       ├── src/main/      # Electron main process

│       ├── src/renderer/  # React UI components

│       ├── src/preload/   # IPC bridge APIs

│       └── src/shared/    # Shared types and constants

│

├── tests/                 # Test suite

├── guides/                # Additional documentation

└── scripts/               # Build utilities

```

 

### Component Interaction Flow

 

```

┌─────────────────────────────────────────────────────────────────┐

│                    ELECTRON FRONTEND (UI)                        │

│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │

│  │  Kanban  │  │ Terminals│  │ Insights │  │ Settings │        │

│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘        │

└───────┼─────────────┼───────────────┼───────────────┼───────────┘

        │             │               │               │

        │      IPC (Inter-Process Communication)      │

        ▼             ▼               ▼               ▼

┌─────────────────────────────────────────────────────────────────┐

│                    PYTHON BACKEND (CORE)                         │

│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │

│  │  Agents  │  │  Specs   │  │   QA     │  │  Merge   │        │

│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘        │

└───────┼─────────────┼───────────────┼───────────────┼───────────┘

        │             │               │               │

        ▼             ▼               ▼               ▼

┌─────────────────────────────────────────────────────────────────┐

│                    CLAUDE AGENT SDK                              │

│         (Anthropic API with security & tool permissions)         │

└─────────────────────────────────────────────────────────────────┘

        │

        ▼

┌─────────────────────────────────────────────────────────────────┐

│                    EXTERNAL SERVICES                             │

│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │

│  │ Graphiti │  │  GitHub  │  │  Linear  │  │  GitLab  │        │

│  │ (Memory) │  │  (PRs)   │  │  (Tasks) │  │  (MRs)   │        │

│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │

└─────────────────────────────────────────────────────────────────┘

```

 

---

 

## The Kanban Board System

 

### Overview

 

The Kanban board is the central interface of DevFlow. It provides visual task management from planning through completion, replacing the traditional chat interface.

 

### Kanban Columns (Task Lifecycle)

 

| Column | Description |

|--------|-------------|

| **Backlog** | Tasks waiting to be started |

| **Planning** | AI is analyzing codebase and creating implementation plan |

| **In Progress** | AI agents are actively coding |

| **AI Review** | AI self-reviews its own work before presenting to human |

| **Human Review** | Ready for you to test and approve |

| **Done** | Completed and merged (or archived) |

 

### Task Lifecycle Flow

 

```

┌──────────┐    ┌───────────┐    ┌────────────┐    ┌───────────┐    ┌──────────────┐    ┌──────┐

│ Backlog  │ -> │ Planning  │ -> │ In Progress│ -> │ AI Review │ -> │ Human Review │ -> │ Done │

└──────────┘    └───────────┘    └────────────┘    └───────────┘    └──────────────┘    └──────┘

     │               │                 │                 │                  │               │

     │               │                 │                 │                  │               │

  Create         Planner           Coder            QA Loop            User Tests      Merge to

   Task           Agent            Agent            (Auto)            & Approves        Main

```

 

### Creating a Task

 

When you create a task:

 

1. **Title**: Give it a descriptive name

2. **Description**: Describe what you want (can paste screenshots!)

3. **Reference Files**: Drag & drop files for context

4. **Model Selection**: Choose Claude model or use Auto (Optimized)

5. **Human Review Option**: Toggle if you want to review plan before coding

 

### Task Card Features

 

Each task card shows:

- Task title and description

- Current status with visual indicator

- Subtask progress (e.g., "3/5 subtasks complete")

- Execution phase badge

- Time elapsed

- One-click access to logs, files, and diffs

 

### Behind the Scenes

 

When you click "Start" on a task:

 

1. **Spec Creation Phase**: AI analyzes your codebase to understand patterns

2. **Planning Phase**: Planner Agent creates implementation plan with subtasks

3. **Coding Phase**: Coder Agent implements subtasks in isolated worktree

4. **QA Phase**: QA Agent validates against acceptance criteria

5. **Review Phase**: Changes staged for your approval

 

---

 

## Agent System Deep Dive

 

### The Multi-Agent Architecture

 

DevFlow uses specialized agents for different phases:

 

```

┌─────────────────────────────────────────────────────────────────┐

│                      AGENT PIPELINE                              │

├─────────────────────────────────────────────────────────────────┤

│                                                                  │

│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐  │

│  │   PLANNER    │  ->  │    CODER     │  ->  │  QA REVIEWER │  │

│  │    AGENT     │      │    AGENT     │      │    AGENT     │  │

│  └──────────────┘      └──────────────┘      └──────────────┘  │

│         │                    │                      │           │

│         ▼                    ▼                      ▼           │

│  Creates plan with    Implements each       Validates work      │

│  subtasks, phases     subtask, commits      against criteria    │

│                                                    │            │

│                                             ┌──────▼──────┐     │

│                                             │  QA FIXER   │     │

│                                             │   AGENT     │     │

│                                             └─────────────┘     │

│                                             Fixes issues found  │

│                                             by QA Reviewer      │

└─────────────────────────────────────────────────────────────────┘

```

 

### Agent Roles

 

#### 1. Planner Agent (`prompts/planner.md`)

 

**Purpose**: Creates the implementation plan - the blueprint for what to build.

 

**Key Responsibilities**:

- Deep codebase investigation (Phase 0 - MANDATORY)

- Reads project structure and existing patterns

- Creates `implementation_plan.json` with phases and subtasks

- Defines verification strategies for each subtask

- Analyzes parallelism opportunities

 

**Output Files**:

- `implementation_plan.json` - The complete build plan

- `project_index.json` - Project structure analysis

- `context.json` - Task-specific context

- `init.sh` - Environment setup script

- `build-progress.txt` - Human-readable progress

 

#### 2. Coder Agent (`prompts/coder.md`)

 

**Purpose**: Implements the actual code changes, one subtask at a time.

 

**Key Responsibilities**:

- Reads implementation plan

- Implements subtasks in dependency order

- Follows patterns from `patterns_from` field

- Runs verification after each subtask

- Commits changes with descriptive messages

- Can spawn subagents for parallel work

 

**Critical Rules**:

- One subtask at a time

- Each subtask = one git commit

- Verification must pass before marking complete

- Never modify files outside subtask scope

 

#### 3. QA Reviewer Agent (`prompts/qa_reviewer.md`)

 

**Purpose**: Validates completed work against acceptance criteria.

 

**Key Responsibilities**:

- Checks all success criteria from spec

- Runs automated tests

- Verifies code quality and patterns

- Creates `qa_report.md` with findings

- If issues found, creates `QA_FIX_REQUEST.md`

 

#### 4. QA Fixer Agent (`prompts/qa_fixer.md`)

 

**Purpose**: Fixes issues identified by QA Reviewer.

 

**Key Responsibilities**:

- Reads `QA_FIX_REQUEST.md`

- Applies targeted fixes

- Re-runs verification

- Updates status

 

### Agent Communication via Files

 

Agents communicate through the spec directory:

 

```

.devflow/specs/001-feature-name/

├── spec.md                  # Feature specification

├── requirements.json        # Structured requirements

├── context.json             # Codebase context

├── implementation_plan.json # Subtask-based plan

├── qa_report.md             # QA validation results

├── QA_FIX_REQUEST.md        # Issues to fix

├── PAUSE                    # Signal to pause

└── HUMAN_INPUT.md           # Human instructions

```

 

### Agent Profiles

 

Users can select different agent profiles for different tasks:

 

| Profile | Model | Use Case |

|---------|-------|----------|

| **Auto (Optimized)** | Dynamic | Recommended - system chooses best model |

| **Balanced** | Sonnet | Good for most tasks |

| **Performance** | Opus | Complex planning/architecture |

| **Fast** | Haiku | Simple fixes, quick iterations |

 

---

 

## The Spec Pipeline

 

### What is a Spec?

 

A "spec" (specification) is a structured description of a task that includes:

- What to build

- Which files to modify

- What patterns to follow

- How to verify success

 

### Complexity Tiers

 

The spec pipeline automatically assesses complexity:

 

| Tier | Phases | When Used |

|------|--------|-----------|

| **SIMPLE** | 3 phases | 1-2 files, single service, no integrations (UI fixes, text changes) |

| **STANDARD** | 6-7 phases | 3-10 files, 1-2 services, minimal integrations (features, bug fixes) |

| **COMPLEX** | 8 phases | 10+ files, multiple services, external integrations |

 

### Spec Creation Phases

 

#### SIMPLE Pipeline (3 phases)

```

Discovery → Quick Spec → Validate

```

 

#### STANDARD Pipeline (6-7 phases)

```

Discovery → Requirements → [Research] → Context → Spec → Plan → Validate

```

 

#### COMPLEX Pipeline (8 phases)

```

Discovery → Requirements → Research → Context → Spec → Plan → Self-Critique → Validate

```

 

### Workflow Types

 

Different workflow types have different phase structures:

 

#### FEATURE Workflow

Phases follow service dependency order:

1. Backend/API Phase - Can be tested with curl

2. Worker Phase - Background jobs

3. Frontend Phase - UI components

4. Integration Phase - Wire everything together

 

#### REFACTOR Workflow

Phases follow migration stages:

1. Add New Phase - Build new system alongside old

2. Migrate Phase - Move consumers to new system

3. Remove Old Phase - Delete deprecated code

4. Cleanup Phase - Polish and verify

 

#### INVESTIGATION Workflow

Phases follow debugging process:

1. Reproduce Phase - Create reliable reproduction

2. Investigate Phase - Analyze, form hypotheses

3. Fix Phase - Implement solution (BLOCKED until phase 2)

4. Harden Phase - Add tests, prevent recurrence

 

#### MIGRATION Workflow

Phases follow data flow:

1. Prepare Phase - Write scripts, setup

2. Test Phase - Small batch, verify

3. Execute Phase - Full migration

4. Cleanup Phase - Remove old, verify

 

---

 

## Git Worktrees & Parallel Execution

 

### What are Git Worktrees?

 

Git worktrees are a way to check out multiple branches of the same repository simultaneously in different folders. This is **crucial** for DevFlow's parallel execution.

 

### Why Worktrees Matter

 

**Traditional Git:**

```

my-project/

├── src/

└── .git/

     └── (only one branch checked out at a time)

```

 

**With Worktrees:**

```

my-project/

├── src/                          # main branch

├── .git/

└── .worktrees/

    ├── devflow/feature-a/    # Working on CSS fixes

    ├── devflow/feature-b/    # Refactoring database

    └── devflow/feature-c/    # Adding new API endpoint

```

 

### Parallel Agent Execution

 

DevFlow can run **up to 12 agent terminals** simultaneously!

 

```

┌─────────────────────────────────────────────────────────────────┐

│                    PARALLEL EXECUTION                            │

├─────────────────────────────────────────────────────────────────┤

│                                                                  │

│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │

│  │  Terminal 1  │  │  Terminal 2  │  │  Terminal 3  │    ...   │

│  │  CSS Fixes   │  │   DB Schema  │  │   API Docs   │          │

│  │  (worktree)  │  │  (worktree)  │  │  (worktree)  │          │

│  └──────────────┘  └──────────────┘  └──────────────┘          │

│         │                 │                 │                   │

│         └────────────────────────────────────┘                  │

│                          │                                      │

│                          ▼                                      │

│              MERGE CONFLICT AI LAYER                            │

│              (Resolves conflicts automatically)                  │

│                          │                                      │

│                          ▼                                      │

│                    MAIN BRANCH                                  │

│                                                                  │

└─────────────────────────────────────────────────────────────────┘

```

 

### Branch Strategy

 

All branches stay **LOCAL** until you explicitly push:

 

```

main (your branch)

└── devflow/{spec-name}  ← spec branch (isolated worktree)

```

 

**Key Principles:**

- ONE branch per spec

- NO automatic pushes to GitHub

- User controls when to push

- Merge: spec branch → main (after user approval)

 

---

 

## Memory Layer (Graphiti)

 

### The Problem: Context Amnesia

 

Standard AI chat interfaces forget:

- Your file structure

- Your coding patterns

- Previous conversations

- Project architecture

 

### The Solution: Graph Memory System

 

DevFlow uses **Graphiti** - a graph memory system with semantic RAG (Retrieval Augmented Generation).

 

### How It Works

 

```

┌─────────────────────────────────────────────────────────────────┐

│                    GRAPHITI MEMORY SYSTEM                        │

├─────────────────────────────────────────────────────────────────┤

│                                                                  │

│  ┌──────────────┐        ┌──────────────┐                       │

│  │   LadybugDB  │  <-->  │   Semantic   │                       │

│  │ (Graph Store)│        │   Embeddings │                       │

│  └──────────────┘        └──────────────┘                       │

│         │                       │                                │

│         │     ┌─────────────────┘                                │

│         ▼     ▼                                                  │

│  ┌───────────────────────────────────────────────────────────┐  │

│  │                   KNOWLEDGE GRAPH                          │  │

│  │                                                            │  │

│  │   [Component A] ──uses──> [Service B]                      │  │

│  │        │                       │                           │  │

│  │      imports                 calls                         │  │

│  │        │                       │                           │  │

│  │        ▼                       ▼                           │  │

│  │   [Utils Module]          [Database]                       │  │

│  │                                                            │  │

│  └───────────────────────────────────────────────────────────┘  │

│                                                                  │

│  The more you use DevFlow, the smarter it gets!             │

│                                                                  │

└─────────────────────────────────────────────────────────────────┘

```

 

### Memory Features

 

1. **Project Indexing**: Automatically indexes your entire project

2. **Relationship Tracking**: Understands file dependencies

3. **Pattern Learning**: Learns your coding patterns over time

4. **Cross-Session Context**: Retains insights between sessions

5. **Semantic Search**: Finds relevant code by meaning, not just keywords

 

### Memory Providers

 

DevFlow supports multiple LLM and embedding providers:

 

| Provider | LLM | Embeddings |

|----------|-----|------------|

| OpenAI | ✅ | ✅ |

| Anthropic | ✅ | ❌ |

| Ollama (Local) | ✅ | ✅ |

| Google AI (Gemini) | ✅ | ✅ |

| OpenRouter | ✅ | ✅ |

| Voyage AI | ❌ | ✅ |

| Azure OpenAI | ✅ | ✅ |

 

### Cost Efficiency

 

**The more you use DevFlow, the cheaper it becomes!**

 

As the memory system learns your codebase:

- Smaller context windows needed

- More precise code retrieval

- Fewer tokens per request

 

---

 

## AI-Powered Merge Conflict Resolution

 

### The Challenge

 

When multiple agents work in parallel, they may modify related files. This normally causes merge conflict hell.

 

### The Solution

 

DevFlow has a dedicated **AI Merge Layer**:

 

```

┌─────────────────────────────────────────────────────────────────┐

│                    MERGE CONFLICT RESOLUTION                     │

├─────────────────────────────────────────────────────────────────┤

│                                                                  │

│   Task A Changes        Task B Changes                           │

│        │                     │                                   │

│        └────────┬────────────┘                                   │

│                 │                                                │

│                 ▼                                                │

│   ┌──────────────────────────────────┐                          │

│   │    CONFLICT DETECTOR             │                          │

│   │    Identifies overlapping files   │                          │

│   └───────────────┬──────────────────┘                          │

│                   │                                              │

│                   ▼                                              │

│   ┌──────────────────────────────────┐                          │

│   │    SEMANTIC ANALYZER             │                          │

│   │    Understands change intent      │                          │

│   └───────────────┬──────────────────┘                          │

│                   │                                              │

│                   ▼                                              │

│   ┌──────────────────────────────────┐                          │

│   │    AI RESOLVER                   │                          │

│   │    Merges intelligently          │                          │

│   └───────────────┬──────────────────┘                          │

│                   │                                              │

│                   ▼                                              │

│   ┌──────────────────────────────────┐                          │

│   │    VERIFICATION                  │                          │

│   │    Tests merged result           │                          │

│   └──────────────────────────────────┘                          │

│                                                                  │

└─────────────────────────────────────────────────────────────────┘

```

 

### Merge Process

 

1. **Stage Changes**: Click "Stage Changes" in Human Review

2. **Conflict Detection**: System checks for overlapping modifications

3. **AI Resolution**: If conflicts exist, AI understands both changes and merges intelligently

4. **Verification**: Merged code is tested

5. **Final Merge**: Clean merge into your main branch

 

### Path-Aware Resolution

 

The merge AI understands:

- Which changes are additive (can be combined)

- Which changes are conflicting (need resolution)

- The semantic meaning of each change

- Lock file handling (special rules for package locks)

 

---

 

## QA Validation Loop

 

### The QA Pipeline

 

After all subtasks complete, QA validation runs automatically:

 

```

┌─────────────────────────────────────────────────────────────────┐

│                       QA VALIDATION LOOP                         │

├─────────────────────────────────────────────────────────────────┤

│                                                                  │

│   ┌───────────────────┐                                         │

│   │   QA REVIEWER     │                                         │

│   │   Validates work  │                                         │

│   └─────────┬─────────┘                                         │

│             │                                                    │

│             ▼                                                    │

│   ┌───────────────────────────────────────────────────┐         │

│   │              ALL CRITERIA MET?                     │         │

│   └───────────────────────┬───────────────────────────┘         │

│                           │                                      │

│            ┌──────────────┴──────────────┐                      │

│            │                             │                      │

│            ▼ NO                          ▼ YES                  │

│   ┌───────────────────┐         ┌───────────────────┐           │

│   │  Creates          │         │  APPROVED!        │           │

│   │  QA_FIX_REQUEST   │         │  Ready for        │           │

│   └─────────┬─────────┘         │  Human Review     │           │

│             │                   └───────────────────┘           │

│             ▼                                                    │

│   ┌───────────────────┐                                         │

│   │   QA FIXER        │                                         │

│   │   Applies fixes   │                                         │

│   └─────────┬─────────┘                                         │

│             │                                                    │

│             └─────────────────> (Back to QA Reviewer)           │

│                                                                  │

│   Loop repeats up to 50 iterations until approved               │

│                                                                  │

└─────────────────────────────────────────────────────────────────┘

```

 

### QA Checks

 

The QA Reviewer validates:

 

1. **Acceptance Criteria**: All success criteria from spec

2. **Unit Tests**: Run and pass

3. **Integration Tests**: Run and pass (if applicable)

4. **Code Quality**: Follows patterns, no obvious issues

5. **Security**: No secrets, no vulnerabilities (for high-risk changes)

6. **E2E Tests**: For frontend changes (via Electron MCP)

 

### Risk-Based Validation

 

| Risk Level | Test Requirements | Security | Staging |

|------------|-------------------|----------|---------|

| **Trivial** | Skip validation (docs only) | No | No |

| **Low** | Unit tests only | No | No |

| **Medium** | Unit + Integration | No | No |

| **High** | Unit + Integration + E2E | Yes | Maybe |

| **Critical** | Full suite + Manual review | Yes | Yes |

 

---

 

## Agent Terminals

 

### Overview

 

The Agent Terminals view provides hands-on access to AI agents. You can spawn up to **12 different terminals** simultaneously!

 

### Use Cases

 

```

┌─────────────────────────────────────────────────────────────────┐

│                    AGENT TERMINALS VIEW                          │

├─────────────────────────────────────────────────────────────────┤

│                                                                  │

│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │

│  │ Terminal 1  │  │ Terminal 2  │  │ Terminal 3  │   ...       │

│  │ "Write      │  │ "Update     │  │ "Experiment │             │

│  │  Tests"     │  │  Docs"      │  │  Feature"   │             │

│  └─────────────┘  └─────────────┘  └─────────────┘             │

│                                                                  │

│  Features:                                                       │

│  • Rename terminals for organization                             │

│  • Reference tasks directly (auto-context)                       │

│  • Session persistence (survives app restart)                    │

│  • One-click Claude invocation                                   │

│                                                                  │

└─────────────────────────────────────────────────────────────────┘

```

 

### Smart Features

 

1. **Task Reference**: Type `@task-001` to inject task context

2. **Auto-Rename**: Terminal auto-renames based on referenced task

3. **Session Restore**: Terminal state persists across app restarts

4. **Parallel Work**: Different terminals = different worktrees

 

### Terminal vs Kanban

 

| Use Kanban When... | Use Terminals When... |

|-------------------|----------------------|

| You want autonomous execution | You want hands-on control |

| Complex multi-step features | Quick experiments |

| You'll be away from computer | You want to watch/guide |

| Multiple related tasks | Single focused task |

 

---

 

## Insights & Ideation

 

### Insights Chat

 

A chat interface for exploring your codebase with AI:

 

- **Contextual**: AI has access to your entire project

- **Persistent History**: Conversations are saved

- **Sparring Partner**: Great for brainstorming

- **Investigation**: Ask "how" and "why" questions

 

### Ideation Generator

 

AI-powered feature discovery:

 

```

┌─────────────────────────────────────────────────────────────────┐

│                    IDEATION TYPES                                │

├─────────────────────────────────────────────────────────────────┤

│                                                                  │

│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐       │

│  │   Security    │  │  Performance  │  │ Code Quality  │       │

│  │  Improvements │  │ Enhancements  │  │  Suggestions  │       │

│  └───────────────┘  └───────────────┘  └───────────────┘       │

│                                                                  │

│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐       │

│  │    UI/UX      │  │ Documentation │  │  Quick Wins   │       │

│  │ Improvements  │  │    Updates    │  │  Low-Hanging  │       │

│  └───────────────┘  └───────────────┘  └───────────────┘       │

│                                                                  │

└─────────────────────────────────────────────────────────────────┘

```

 

### Ideation to Task

 

1. AI analyzes your project

2. Suggests improvements by category

3. You review suggestions

4. Click "Create Task" → Goes to Kanban

5. AI builds it automatically!

 

Example insights:

- "Missing error handling in `auth.py`"

- "Consider implementing dark mode"

- "SQL query in `users.py` could be optimized"

- "No rate limiting on API endpoints"

 

---

 

## Roadmap Generation

 

### AI-Assisted Feature Planning

 

The Roadmap feature helps you plan your project's future:

 

```

┌─────────────────────────────────────────────────────────────────┐

│                    ROADMAP GENERATION                            │

├─────────────────────────────────────────────────────────────────┤

│                                                                  │

│  1. AI analyzes your codebase                                   │

│  2. Identifies target audience                                  │

│  3. Performs competitor analysis                                │

│  4. Suggests features by priority                               │

│  5. Creates roadmap with phases                                 │

│                                                                  │

│  ┌───────────────────────────────────────────────────────────┐  │

│  │                    ROADMAP VIEW                            │  │

│  │                                                            │  │

│  │  Q1 2025          Q2 2025          Q3 2025                │  │

│  │  ┌──────┐         ┌──────┐         ┌──────┐               │  │

│  │  │Auth  │         │Teams │         │API   │               │  │

│  │  │System│         │Collab│         │V2    │               │  │

│  │  └──────┘         └──────┘         └──────┘               │  │

│  │                                                            │  │

│  └───────────────────────────────────────────────────────────┘  │

│                                                                  │

└─────────────────────────────────────────────────────────────────┘

```

 

### Roadmap to Tasks

 

Click on any roadmap feature → Converts to a task → Ready for AI execution!

 

---

 

## Changelog & GitHub Integration

 

### Changelog Generator

 

Automatically generate changelogs from:

 

1. **Completed Tasks**: All tasks marked as done

2. **Git History**: Commits since last version

3. **Combination**: Both sources merged

 

Features:

- Formatted with emojis

- Grouped by: Features, Improvements, Bug Fixes

- Markdown output

- One-click GitHub Release creation

 

### GitHub Integration

 

```

┌─────────────────────────────────────────────────────────────────┐

│                    GITHUB INTEGRATION                            │

├─────────────────────────────────────────────────────────────────┤

│                                                                  │

│  ┌───────────────────────────────────────────────────────────┐  │

│  │   IMPORT ISSUES                                            │  │

│  │   - Fetch issues from your repo                           │  │

│  │   - AI analyzes and triages                               │  │

│  │   - Create tasks directly                                  │  │

│  └───────────────────────────────────────────────────────────┘  │

│                                                                  │

│  ┌───────────────────────────────────────────────────────────┐  │

│  │   PR REVIEW                                                │  │

│  │   - AI reviews incoming PRs                               │  │

│  │   - Security scanning                                      │  │

│  │   - Automated feedback                                     │  │

│  └───────────────────────────────────────────────────────────┘  │

│                                                                  │

│  ┌───────────────────────────────────────────────────────────┐  │

│  │   RELEASE CREATION                                         │  │

│  │   - Generate changelog                                     │  │

│  │   - Create GitHub release                                  │  │

│  │   - Draft release notes                                    │  │

│  └───────────────────────────────────────────────────────────┘  │

│                                                                  │

└─────────────────────────────────────────────────────────────────┘

```

 

### GitLab Support

 

DevFlow also supports GitLab for:

- Merge Request creation

- Issue import

- Release management

 

---

 

## Frontend Architecture (Electron)

 

### Technology Stack

 

- **Electron**: Cross-platform desktop framework

- **React 18**: UI library

- **TypeScript**: Type safety

- **Zustand**: State management

- **TailwindCSS**: Styling

- **Radix UI**: Accessible components

 

### Project Structure

 

```

apps/frontend/src/

├── main/                    # Electron main process

│   ├── agent/               # Agent management & lifecycle

│   ├── changelog/           # Changelog generation service

│   ├── claude-profile/      # Profile & token management

│   ├── insights/            # Code analysis service

│   ├── ipc-handlers/        # 108+ IPC communication handlers

│   ├── terminal/            # PTY daemon & management

│   └── updater/             # Auto-update service

│

├── preload/                 # Electron preload (IPC bridge)

│   └── api/                 # API modules exposed to renderer

│

├── renderer/                # React frontend

│   ├── components/          # UI components (363 files!)

│   │   ├── tasks/           # Kanban, task cards, creation

│   │   ├── terminals/       # Terminal emulator

│   │   ├── settings/        # Configuration UI

│   │   ├── roadmap/         # Roadmap visualization

│   │   └── ui/              # Base UI components

│   ├── stores/              # Zustand state stores

│   └── hooks/               # React hooks

│

└── shared/                  # Shared between main/renderer

    ├── types/               # TypeScript definitions

    ├── constants/           # Application constants

    └── i18n/                # Internationalization (en, fr)

```

 

### Key IPC Handlers

 

The frontend communicates with backend through IPC:

 

| Handler Category | Purpose |

|-----------------|---------|

| `task-handlers` | Task CRUD, status updates |

| `spec-handlers` | Spec creation, management |

| `terminal-handlers` | PTY spawn, input/output |

| `worktree-handlers` | Git worktree operations |

| `memory-handlers` | Graphiti memory queries |

| `github-handlers` | GitHub API integration |

| `settings-handlers` | App/project settings |

 

---

 

## Backend Architecture (Python)

 

### Technology Stack

 

- **Python 3.12+**: Core language

- **Claude Agent SDK**: AI interaction (NOT raw Anthropic API)

- **asyncio**: Async operations

- **Graphiti + LadybugDB**: Memory system

 

### Project Structure

 

```

apps/backend/

├── agents/              # Agent implementations

│   ├── planner.py       # Planning agent

│   ├── coder.py         # Coding agent

│   ├── memory_manager.py # Session memory

│   └── session.py       # Agent session execution

│

├── core/                # Core infrastructure

│   ├── client.py        # Claude SDK client factory

│   ├── auth.py          # OAuth token management

│   ├── security.py      # Command allowlisting

│   └── workspace.py     # Workspace management

│

├── integrations/        # External services

│   ├── graphiti/        # Memory system (36 files!)

│   └── linear/          # Linear task sync

│

├── merge/               # AI merge system

│   ├── ai_resolver/     # Conflict resolution

│   ├── conflict_detector.py

│   ├── semantic_analyzer.py

│   └── orchestrator.py

│

├── prompts/             # Agent prompts (47 .md files)

│   ├── planner.md

│   ├── coder.md

│   ├── qa_reviewer.md

│   ├── qa_fixer.md

│   └── github/          # PR review prompts

│

├── qa/                  # QA validation

├── spec/                # Spec creation pipeline

├── runners/             # Entry points (91 files!)

└── security/            # Security scanning

```

 

### Key Entry Points

 

| File | Purpose |

|------|---------|

| `run.py` | Main build runner |

| `runners/spec_runner.py` | Spec creation |

| `agent.py` | Agent orchestration |

| `qa_loop.py` | QA validation loop |

 

### Claude SDK Usage

 

**CRITICAL**: DevFlow uses the Claude Agent SDK, NOT the raw Anthropic API:

 

```python

from core.client import create_client

 

# Create SDK client with security hooks

client = create_client(

    project_dir=project_dir,

    spec_dir=spec_dir,

    model="claude-sonnet-4-5-20250929",

    agent_type="coder",

    max_thinking_tokens=None

)

 

# Run agent session

response = client.create_agent_session(

    name="coder-agent-session",

    starting_message="Implement the feature"

)

```

 

---

 

## Installation & Setup

 

### Prerequisites

 

| Requirement | Version | Notes |

|-------------|---------|-------|

| **Claude Pro/Max** | - | Subscription required |

| **Claude Code CLI** | Latest | `npm install -g @anthropic-ai/claude-code` |

| **Node.js** | 24.0.0+ | For frontend |

| **Python** | 3.12+ | For backend |

| **Git** | 2.20+ | With worktree support |

| **CMake** | Latest | For building native deps |

 

### Quick Install (Pre-built)

 

1. **Download** from [Releases](https://github.com/AndyMik90/DevFlow/releases)

2. **Install** the app for your platform

3. **Open your project** folder

4. **Initialize** DevFlow when prompted

5. **Connect** your Claude account via OAuth

 

### Development Install

 

```bash

# Clone repository

git clone https://github.com/AndyMik90/DevFlow.git

cd DevFlow

 

# Install all dependencies

npm run install:all

 

# Run in development mode

npm run dev

 

# Or build and run production

npm start

```

 

### Backend Setup (Manual)

 

```bash

cd apps/backend

 

# Create virtual environment

python -m venv .venv

 

# Activate (Windows)

.venv\Scripts\activate

 

# Activate (macOS/Linux)

source .venv/bin/activate

 

# Install dependencies

pip install -r requirements.txt

 

# Configure environment

cp .env.example .env

# Edit .env with your OAuth token

```

 

### Getting OAuth Token

 

```bash

# Run in terminal

claude setup-token

 

# Copy the token to apps/backend/.env:

# CLAUDE_CODE_OAUTH_TOKEN=your-token-here

```

 

---

 

## CLI Usage

 

### When to Use CLI

 

- Headless server operation

- CI/CD integration

- Terminal-only workflows

- Scripting

 

### Core Commands

 

```bash

cd apps/backend

 

# Create spec interactively

python runners/spec_runner.py --interactive

 

# Create spec from description

python runners/spec_runner.py --task "Add user authentication"

 

# Force complexity level

python runners/spec_runner.py --task "Fix button" --complexity simple

 

# List all specs

python run.py --list

 

# Run a spec

python run.py --spec 001

 

# Run with iteration limit

python run.py --spec 001 --max-iterations 5

 

# Review changes

python run.py --spec 001 --review

 

# Merge completed build

python run.py --spec 001 --merge

 

# Discard build

python run.py --spec 001 --discard

 

# Run QA manually

python run.py --spec 001 --qa

 

# Check QA status

python run.py --spec 001 --qa-status

```

 

### Interactive Controls

 

While agent is running:

- **Ctrl+C (once)**: Pause and add instructions

- **Ctrl+C (twice)**: Exit immediately

 

File-based control:

```bash

# Pause after current session

touch specs/001-name/PAUSE

 

# Add instructions

echo "Focus on login bug first" > specs/001-name/HUMAN_INPUT.md

```

 

---

 

## Security Model

 

### Three-Layer Defense

 

```

┌─────────────────────────────────────────────────────────────────┐

│                    SECURITY LAYERS                               │

├─────────────────────────────────────────────────────────────────┤

│                                                                  │

│  LAYER 1: OS SANDBOX                                            │

│  ├── Bash commands run in isolation                             │

│  └── Process-level restrictions                                  │

│                                                                  │

│  LAYER 2: FILESYSTEM PERMISSIONS                                 │

│  ├── Operations restricted to project directory                  │

│  └── No access outside workspace                                 │

│                                                                  │

│  LAYER 3: DYNAMIC COMMAND ALLOWLIST                             │

│  ├── Only approved commands based on project stack              │

│  ├── Python project → python, pip, pytest allowed               │

│  ├── Node project → npm, node, jest allowed                     │

│  └── Cached in .devflow-security.json                        │

│                                                                  │

└─────────────────────────────────────────────────────────────────┘

```

 

### Security Features

 

1. **Secrets Scanning**: Detects hardcoded secrets before commit

2. **SAST Scanning**: Static analysis for security vulnerabilities

3. **Command Validation**: AI commands checked against allowlist

4. **Worktree Isolation**: Changes never affect main branch directly

5. **Release Verification**: All releases include SHA256 checksums

 

---

 

## Configuration Reference

 

### Environment Variables

 

#### Core Settings

 

| Variable | Required | Default | Description |

|----------|----------|---------|-------------|

| `CLAUDE_CODE_OAUTH_TOKEN` | Yes | - | OAuth token from `claude setup-token` |

| `AUTO_BUILD_MODEL` | No | claude-opus-4-5-20251101 | Override Claude model |

| `DEFAULT_BRANCH` | No | auto-detect | Base branch for worktrees |

| `DEBUG` | No | false | Enable debug logging |

| `DEBUG_LEVEL` | No | 1 | Debug verbosity (1-3) |

 

#### Memory Layer (Graphiti)

 

| Variable | Required | Default | Description |

|----------|----------|---------|-------------|

| `GRAPHITI_ENABLED` | No | true | Enable Memory Layer |

| `GRAPHITI_LLM_PROVIDER` | No | anthropic | LLM: openai, anthropic, ollama, google, openrouter |

| `GRAPHITI_EMBEDDER_PROVIDER` | No | openai | Embedder: openai, voyage, ollama, google, openrouter |

| `ANTHROPIC_API_KEY` | Conditional | - | Required if using anthropic provider |

| `OPENAI_API_KEY` | Conditional | - | Required if using openai provider |

 

#### Integrations

 

| Variable | Required | Description |

|----------|----------|-------------|

| `LINEAR_API_KEY` | No | Linear API key for task sync |

| `GITHUB_TOKEN` | No | GitHub Personal Access Token |

| `GITLAB_TOKEN` | No | GitLab Personal Access Token |

| `GITLAB_INSTANCE_URL` | No | GitLab instance URL |

 

### App Settings (UI)

 

Settings are persisted in user data directory:

 

- **General**: Theme, scale, language

- **Agent Profiles**: Model selection per task type

- **Memory**: Provider configuration

- **Updates**: Auto-update preferences

- **Integrations**: GitHub, Linear, GitLab

 

---

 

## Troubleshooting

 

### Common Issues

 

#### "tree-sitter not available"

**Safe to ignore** - Uses regex fallback for code parsing.

 

#### Missing module errors

```bash

cd apps/backend

pip install -r requirements.txt

```

 

#### npm not found

Reinstall Node.js and ensure "Add to PATH" is checked.

 

#### Native module errors (node-pty)

```bash

cd apps/frontend

npm run rebuild

```

 

#### Windows build tools required

1. Download [Visual Studio Build Tools 2022](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

2. Select "Desktop development with C++" workload

3. Restart terminal and run `npm install` again

 

#### Python ENOENT error

Ensure Python is in PATH and virtual environment is activated.

 

#### Task stuck in "ai_review"

UI has fallback to prevent stuck tasks. If persists, restart app.

 

### Debug Mode

 

```bash

# Enable debug logging

DEBUG=true DEBUG_LEVEL=2 python run.py --spec 001

```

 

### Getting Help

 

- **Discord**: [Join Community](https://discord.gg/KCXaPBr4Dj)

- **GitHub Issues**: [Report bugs](https://github.com/AndyMik90/DevFlow/issues)

- **Discussions**: [Ask questions](https://github.com/AndyMik90/DevFlow/discussions)

 

---

 

## Reference-Based Code Generation

 

### Overview

 

The **Reference-Based Code Generation** feature allows you to provide a complete reference folder containing:

- Product requirements documents

- SQL schema files

- Implementation code

- Tests and metadata

 

This reference becomes a template that DevFlow learns from. When you provide new requirements, it generates similar code following the patterns from your reference.

 

### How It Works

 

```

┌─────────────────────────────────────────────────────────────────┐

│               REFERENCE-BASED CODE GENERATION                   │

├─────────────────────────────────────────────────────────────────┤

│                                                                  │

│   YOUR REFERENCE FOLDER              NEW REQUIREMENTS            │

│   ┌─────────────────────┐           ┌─────────────────────┐     │

│   │ requirements/       │           │ product-catalog.md  │     │

│   │   └── user-auth.md  │           │ - List products     │     │

│   │ sql/                │   +       │ - Filter by category│     │

│   │   └── users.sql     │           │ - Search products   │     │

│   │ src/                │           │ - Product details   │     │

│   │   ├── UserService   │           └─────────────────────┘     │

│   │   ├── UserRepo      │                    │                  │

│   │   └── UserController│                    │                  │

│   └─────────────────────┘                    │                  │

│              │                               │                  │

│              ▼                               ▼                  │

│   ┌──────────────────────────────────────────────────────────┐  │

│   │                REFERENCE GENERATOR SERVICE                │  │

│   │                                                          │  │

│   │  1. Pattern Extractor → Learns code patterns             │  │

│   │  2. SQL Converter → Transforms schemas                   │  │

│   │  3. Requirement Mapper → Maps old to new requirements   │  │

│   │  4. Code Generator → Generates new implementation       │  │

│   └──────────────────────────────────────────────────────────┘  │

│                               │                                  │

│                               ▼                                  │

│   ┌──────────────────────────────────────────────────────────┐  │

│   │                    GENERATED OUTPUT                       │  │

│   │                                                          │  │

│   │  generated/                                              │  │

│   │  ├── schema/                                             │  │

│   │  │   └── generated_schema.sql  (products table)         │  │

│   │  ├── services/                                           │  │

│   │  │   └── product_service.py    (ProductService)         │  │

│   │  ├── repositories/                                       │  │

│   │  │   └── product_repository.py (ProductRepository)      │  │

│   │  ├── controllers/                                        │  │

│   │  │   └── product_controller.py (ProductController)      │  │

│   │  └── tests/                                              │  │

│   │      └── test_product.py       (Test templates)         │  │

│   └──────────────────────────────────────────────────────────┘  │

│                                                                  │

└─────────────────────────────────────────────────────────────────┘

```

 

### Service Architecture

 

The feature is implemented in `apps/backend/services/reference_generator/`:

 

```

apps/backend/services/reference_generator/

├── __init__.py              # Package exports

├── models.py                # Data models (ReferenceProject, CodePattern, etc.)

├── reference_manager.py     # Load, store, and index reference projects

├── pattern_extractor.py     # Extract code patterns from reference files

├── sql_converter.py         # Transform SQL schemas for new entities

├── code_generator.py        # Generate code using patterns

└── service.py               # Main ReferenceGeneratorService orchestrator

```

 

### Usage Examples

 

#### 1. Loading a Reference Project

 

```python

from services.reference_generator import ReferenceGeneratorService

 

# Initialize service

service = ReferenceGeneratorService(project_dir="/my/project")

 

# Load reference folder containing requirements, SQL, and code

reference = await service.load_reference(

    reference_path="examples/user-authentication",

    name="user-auth-feature"

)

 

# View what was extracted

print(f"Files found: {len(reference.files)}")

print(f"Patterns extracted: {len(reference.patterns)}")

print(f"Requirements parsed: {len(reference.requirements)}")

print(f"SQL tables: {reference.sql_tables}")

print(f"Tech stack: {reference.tech_stack}")

```

 

#### 2. Generating Code for New Requirements

 

```python

# Generate code for a new feature using the reference

result = await service.generate_from_reference(

    reference_name="user-auth-feature",

    new_requirements_path="specs/product-catalog.md",

    entity_mappings=[

        {"reference": "User", "new": "Product"},

        {"reference": "UserService", "new": "ProductService"},

        {"reference": "UserRepository", "new": "ProductRepository"},

    ],

    output_dir="generated/product-catalog"

)

 

# Check results

if result.success:

    print(f"Generated {len(result.generated_files)} files")

    for file in result.generated_files:

        print(f"  - {file.path} (from pattern: {file.source_pattern})")

else:

    print(f"Errors: {result.errors}")

```

 

#### 3. CLI Usage

 

```bash

cd apps/backend

 

# Load a reference project

python -m services.reference_generator.service \

    --action load \

    --reference examples/user-auth \

    --name user-authentication

 

# List saved references

python -m services.reference_generator.service --action list

 

# Generate code for new requirements

python -m services.reference_generator.service \

    --action generate \

    --name user-authentication \

    --requirements specs/product-catalog.md \

    --output generated/product-catalog

 

# Get info about a reference

python -m services.reference_generator.service \

    --action info \

    --name user-authentication \

    --json

```

 

### Reference Folder Structure

 

Your reference folder should contain:

 

```

my-reference/

├── requirements/           # Product requirements

│   ├── PRD.md             # Product requirements document

│   └── user-stories.md    # User stories

│

├── sql/                   # SQL schemas and migrations

│   ├── schema.sql         # CREATE TABLE statements

│   └── migrations/        # Migration files

│       └── 001_create_users.sql

│

├── src/                   # Implementation code

│   ├── services/          # Business logic

│   │   └── user_service.py

│   ├── repositories/      # Data access

│   │   └── user_repository.py

│   ├── models/            # Data models

│   │   └── user.py

│   └── controllers/       # API endpoints

│       └── user_controller.py

│

├── tests/                 # Test files

│   └── test_user.py

│

└── config/               # Configuration files

    └── settings.json

```

 

### Pattern Types Extracted

 

The Pattern Extractor identifies these pattern types:

 

| Pattern Type | Description | Example |

|-------------|-------------|---------|

| `SERVICE_CLASS` | Business logic services | `UserService`, `AuthService` |

| `REPOSITORY` | Data access layer | `UserRepository`, `ProductRepo` |

| `CONTROLLER` | Request handlers | `UserController`, `APIHandler` |

| `DATABASE_MODEL` | ORM models | `User`, `Product` |

| `API_ENDPOINT` | REST/GraphQL routes | `@router.get("/users")` |

| `VALIDATION` | Input validation | `UserValidator`, `validate_email` |

| `TRANSFORMATION` | Data transformers | `UserConverter`, `to_dto` |

| `AUTHENTICATION` | Auth patterns | `AuthMiddleware`, `login` |

| `ERROR_HANDLING` | Error handlers | `APIException`, `handle_error` |

| `UTILITY` | Helper functions | `format_date`, `hash_password` |

 

### SQL Transformation

 

The SQL Converter handles:

 

1. **Table Renaming**: `users` → `products`

2. **Column Mapping**: `user_id` → `product_id`

3. **Foreign Key Updates**: `REFERENCES users(id)` → `REFERENCES products(id)`

4. **Migration Generation**: Creates migration scripts

 

```python

from services.reference_generator import SQLConverter

 

converter = SQLConverter()

 

# Transform SQL schema

converted_sql, transformations = converter.convert_schema(

    original_sql="""

    CREATE TABLE users (

        id SERIAL PRIMARY KEY,

        user_name VARCHAR(255) NOT NULL,

        user_email VARCHAR(255) UNIQUE,

        created_at TIMESTAMP DEFAULT NOW()

    );

    """,

    table_mappings={"users": "products"},

    column_mappings={

        "users": {

            "user_name": "product_name",

            "user_email": "product_sku",

        }

    }

)

 

print(converted_sql)

# CREATE TABLE products (

#     id SERIAL PRIMARY KEY,

#     product_name VARCHAR(255) NOT NULL,

#     product_sku VARCHAR(255) UNIQUE,

#     created_at TIMESTAMP DEFAULT NOW()

# );

```

 

### Reference Generator UI ✅ IMPLEMENTED

 

The Reference Generator has a dedicated frontend UI accessible from the sidebar. It provides a step-by-step wizard for generating code from references.

 

Access it by clicking **"Reference Generator"** in the sidebar (shortcut: `E`).

 

```

┌─────────────────────────────────────────────────────────────────┐

│               REFERENCE GENERATOR UI                             │

├─────────────────────────────────────────────────────────────────┤

│                                                                  │

│  STEP 1: SELECT REFERENCE                                       │

│  ┌─────────────────────┐  ┌─────────────────────┐              │

│  │ 📁 orders-pipeline  │  │ 📁 user-auth        │              │

│  │ Lambda, Glue, Redis │  │ JWT, Sessions       │              │

│  │ 6 Lambdas, 2 Glue   │  │ 4 Cache patterns    │              │

│  │ ✅ Ready            │  │ ✅ Ready            │              │

│  └─────────────────────┘  └─────────────────────┘              │

│                                                                  │

│  STEP 2: UPLOAD REQUIREMENTS                                    │

│  ┌──────────────────────────────────────────────────────────┐  │

│  │ # Inventory Management Feature                            │  │

│  │                                                           │  │

│  │ ## Features                                               │  │

│  │ - Track product stock levels                              │  │

│  │ - Record stock movements                                  │  │

│  │ - Generate low stock alerts                               │  │

│  └──────────────────────────────────────────────────────────┘  │

│                                                                  │

│  STEP 3: CONFIGURE ENTITY MAPPINGS                              │

│  ┌──────────────────┐     ┌──────────────────┐                 │

│  │  orders          │ ──► │  inventory       │                 │

│  └──────────────────┘     └──────────────────┘                 │

│  [+ Add More Mappings]  [🪄 Auto-Suggest]                      │

│                                                                  │

│  STEP 4: REVIEW & GENERATE                                      │

│  • Target: inventory                                            │

│  • Environment: dev                                             │

│  • Region: us-east-1                                            │

│  [▶ Generate Code]                                              │

│                                                                  │

│  STEP 5: PREVIEW RESULTS                                        │

│  ┌───────────┐  ┌────────────────────────────────────────────┐ │

│  │ 📄 Files  │  │ # inventory_service.py                     │ │

│  │           │  │                                            │ │

│  │ terraform/│  │ class InventoryService:                    │ │

│  │  lambda.tf│  │     def __init__(self, db):                │ │

│  │  glue.tf  │  │         self.db = db                       │ │

│  │           │  │                                            │ │

│  │ services/ │  │     async def get_by_id(self, id):         │ │

│  │  service  │  │         return await self.repo.get(id)     │ │

│  │  cache    │  │                                            │ │

│  └───────────┘  └────────────────────────────────────────────┘ │

│                                                                  │

│  [⬇ Download ZIP]  [✓ Apply to Project]                        │

│                                                                  │

└─────────────────────────────────────────────────────────────────┘

```

 

#### Accessing the Reference Generator

 

1. Open DevFlow

2. Select your project from the sidebar

3. Click **"Reference Generator"** (shortcut: `E`)

4. Follow the step-by-step wizard

 

#### Reference Card Features

 

Each reference project card shows:

- **Name & Description**: What the reference contains

- **Tech Stack Badges**: Languages, frameworks, databases, infrastructure

- **Pattern Counts**: Lambda, Glue, Services, Cache patterns

- **Usage Stats**: How many times used, last used date

- **Status Indicator**: Ready, Loading, or Error state

 

#### Entity Mapping Wizard

 

The mapping wizard helps you transform entities:

- **Primary Entity Mapping**: Main transformation (e.g., orders → inventory)

- **Auto-Suggest**: Automatically suggests common mappings based on your reference

- **Additional Mappings**: Fine-grained control over specific transformations

- **Infrastructure Config**: AWS region, environment, resource prefix

- **Cache Config**: Redis host, port, TTL, key prefix

 

#### Generation Preview

 

After generation, you can:

- **Browse files** in a tree view grouped by type

- **Preview content** with syntax highlighting

- **See confidence scores** for each generated file

- **View applied patterns** and SQL transformations

- **Download as ZIP** or apply directly to project

 

### Integration with Kanban Board

 

To use Reference-Based Generation with the Kanban Board workflow:

 

1. **Create Reference**: Save your best implementation as a reference

   ```

   DevFlow UI → Sidebar → Reference Generator → Add Reference

   ```

 

2. **Create Task with Reference**: When creating a new task, attach a reference

   ```

   New Task → "Build Product Catalog"

   Reference: user-authentication

   New Requirements: [paste your PRD]

   ```

 

3. **Planner Uses Reference**: The Planner Agent will:

   - Analyze the reference patterns

   - Map requirements to reference

   - Generate implementation plan based on reference architecture

 

4. **Coder Follows Patterns**: The Coder Agent will:

   - Follow the exact patterns from reference

   - Apply entity substitutions automatically

   - Maintain consistency with reference style

 

### Best Practices

 

1. **Clean Reference Code**: Your reference should be your best, cleanest implementation

2. **Complete Examples**: Include all layers (model, service, repository, controller, tests)

3. **Clear Requirements**: Write clear requirements that map to implementation

4. **Consistent Naming**: Use consistent naming patterns across your reference

5. **Include Tests**: Reference tests help generate test templates for new code

 

---

 

### Infrastructure-as-Code Support

 

The Reference-Based Code Generation feature fully supports **Infrastructure-as-Code** patterns including:

 

| Technology | File Types | Patterns Extracted |

|-----------|------------|-------------------|

| **Terraform** | `.tf` | Resources, Modules, Data Sources, Variables, Outputs |

| **AWS CloudFormation** | `.json`, `.yaml` | All AWS resource types |

| **AWS CDK** | `.ts`, `.py` | Constructs, Stacks |

| **Serverless Framework** | `serverless.yml` | Functions, Events, Resources |

 

#### Supported AWS Resource Patterns

 

```

┌─────────────────────────────────────────────────────────────────┐

│               INFRASTRUCTURE PATTERN TYPES                       │

├─────────────────────────────────────────────────────────────────┤

│                                                                  │

│  COMPUTE                    DATA PROCESSING                      │

│  ├── AWS Lambda             ├── AWS Glue Jobs                   │

│  ├── Lambda Layers          ├── Glue Crawlers                   │

│  └── Lambda Triggers        ├── Glue Data Catalog               │

│                             └── Step Functions                   │

│                                                                  │

│  STORAGE                    INTEGRATION                          │

│  ├── S3 Buckets             ├── API Gateway                     │

│  ├── S3 Policies            ├── EventBridge Rules               │

│  ├── DynamoDB Tables        ├── SQS Queues                      │

│  └── RDS Instances          └── SNS Topics                      │

│                                                                  │

│  SECURITY                   NETWORKING                           │

│  ├── IAM Roles              ├── VPC                             │

│  ├── IAM Policies           ├── Subnets                         │

│  └── Policy Attachments     └── Security Groups                 │

│                                                                  │

└─────────────────────────────────────────────────────────────────┘

```

 

#### Infrastructure Pattern Extraction

 

The system extracts patterns from Terraform files like this:

 

**Reference Terraform (`orders/lambda.tf`):**

```hcl

resource "aws_lambda_function" "process_orders" {

  function_name = "${var.prefix}-process-orders"

  role          = aws_iam_role.orders_lambda_role.arn

  runtime       = "python3.11"

  handler       = "handler.process"

  timeout       = 30

  memory_size   = 256

 

  environment {

    variables = {

      ORDERS_TABLE = aws_dynamodb_table.orders.name

      S3_BUCKET    = aws_s3_bucket.orders_data.id

    }

  }

}

 

resource "aws_glue_job" "orders_etl" {

  name     = "${var.prefix}-orders-etl"

  role_arn = aws_iam_role.glue_role.arn

 

  glue_version      = "4.0"

  worker_type       = "G.1X"

  number_of_workers = 2

 

  command {

    script_location = "s3://${var.scripts_bucket}/orders_etl.py"

    python_version  = "3"

  }

}

 

resource "aws_sfn_state_machine" "orders_workflow" {

  name     = "${var.prefix}-orders-workflow"

  role_arn = aws_iam_role.sfn_role.arn

 

  definition = <<EOF

{

  "StartAt": "ProcessOrders",

  "States": {

    "ProcessOrders": {

      "Type": "Task",

      "Resource": "${aws_lambda_function.process_orders.arn}",

      "Next": "RunETL"

    },

    "RunETL": {

      "Type": "Task",

      "Resource": "arn:aws:states:::glue:startJobRun.sync",

      "Parameters": {

        "JobName": "${aws_glue_job.orders_etl.name}"

      },

      "End": true

    }

  }

}

EOF

}

```

 

**Entity Mapping:**

```python

entity_mapping = InfraEntityMapping(

    reference_name="orders",

    new_name="inventory",

    resource_prefix="myapp-prod",

    environment="prod",

    region="us-west-2",

)

```

 

**Generated Terraform (`inventory/lambda.tf`):**

```hcl

resource "aws_lambda_function" "process_inventory" {

  function_name = "${var.prefix}-process-inventory"

  role          = aws_iam_role.inventory_lambda_role.arn

  runtime       = "python3.11"

  handler       = "handler.process"

  timeout       = 30

  memory_size   = 256

 

  environment {

    variables = {

      INVENTORY_TABLE = aws_dynamodb_table.inventory.name

      S3_BUCKET       = aws_s3_bucket.inventory_data.id

    }

  }

}

 

resource "aws_glue_job" "inventory_etl" {

  name     = "${var.prefix}-inventory-etl"

  role_arn = aws_iam_role.glue_role.arn

 

  glue_version      = "4.0"

  worker_type       = "G.1X"

  number_of_workers = 2

 

  command {

    script_location = "s3://${var.scripts_bucket}/inventory_etl.py"

    python_version  = "3"

  }

}

 

# ... Step Functions also transformed

```

 

#### Step Functions Pattern Handling

 

Step Functions state machine definitions are parsed and transformed:

 

```

┌─────────────────────────────────────────────────────────────────┐

│               STEP FUNCTION TRANSFORMATION                       │

├─────────────────────────────────────────────────────────────────┤

│                                                                  │

│   REFERENCE STATE MACHINE           NEW STATE MACHINE            │

│   ┌────────────────────┐           ┌────────────────────┐       │

│   │   ProcessOrders    │    ->     │  ProcessInventory  │       │

│   │   (Lambda)         │           │  (Lambda)          │       │

│   └────────┬───────────┘           └────────┬───────────┘       │

│            │                                │                    │

│            ▼                                ▼                    │

│   ┌────────────────────┐           ┌────────────────────┐       │

│   │   OrdersETL        │    ->     │   InventoryETL     │       │

│   │   (Glue Job)       │           │   (Glue Job)       │       │

│   └────────┬───────────┘           └────────┬───────────┘       │

│            │                                │                    │

│            ▼                                ▼                    │

│   ┌────────────────────┐           ┌────────────────────┐       │

│   │   NotifyComplete   │    ->     │   NotifyComplete   │       │

│   │   (SNS)            │           │   (SNS)            │       │

│   └────────────────────┘           └────────────────────┘       │

│                                                                  │

│   • Lambda ARNs transformed                                     │

│   • Glue job names mapped                                       │

│   • State names updated                                         │

│   • Resource references adjusted                                 │

│                                                                  │

└─────────────────────────────────────────────────────────────────┘

```

 

#### Glue Job Script Generation

 

When you include Glue ETL scripts (PySpark), they are also transformed:

 

**Reference Glue Script (`orders_etl.py`):**

```python

from awsglue.transforms import *

from awsglue.context import GlueContext

 

# Read orders from S3

orders_frame = glueContext.create_dynamic_frame.from_options(

    connection_type="s3",

    connection_options={"paths": ["s3://data-bucket/orders/"]},

    format="parquet"

)

 

# Transform orders

mapped_orders = ApplyMapping.apply(

    frame=orders_frame,

    mappings=[

        ("order_id", "long", "order_id", "long"),

        ("order_date", "string", "order_date", "timestamp"),

    ]

)

```

 

**Generated Glue Script (`inventory_etl.py`):**

```python

from awsglue.transforms import *

from awsglue.context import GlueContext

 

# Read inventory from S3

inventory_frame = glueContext.create_dynamic_frame.from_options(

    connection_type="s3",

    connection_options={"paths": ["s3://data-bucket/inventory/"]},

    format="parquet"

)

 

# Transform inventory

mapped_inventory = ApplyMapping.apply(

    frame=inventory_frame,

    mappings=[

        ("inventory_id", "long", "inventory_id", "long"),

        ("inventory_date", "string", "inventory_date", "timestamp"),

    ]

)

```

 

#### Lambda Handler Generation

 

Lambda handlers are generated or transformed:

 

```python

# Generated handler template with trigger-specific code

 

def handler(event: dict, context) -> dict:

    """Lambda handler for inventory processing."""

   

    # S3 trigger handling (auto-detected from Terraform)

    for record in event.get("Records", []):

        bucket = record["s3"]["bucket"]["name"]

        key = record["s3"]["object"]["key"]

        logger.info(f"Processing S3 object: s3://{bucket}/{key}")

       

        # TODO: Implement inventory processing

```

 

#### Complete Infrastructure Example

 

**Reference Project Structure:**

```

reference-orders-pipeline/

├── requirements/

│   └── orders-pipeline.md

├── terraform/

│   ├── lambda.tf           # Lambda functions

│   ├── glue.tf             # Glue jobs and crawlers

│   ├── step_functions.tf   # Step Functions state machines

│   ├── s3.tf               # S3 buckets

│   ├── iam.tf              # IAM roles and policies

│   └── variables.tf        # Input variables

├── lambda/

│   └── process_orders/

│       └── handler.py      # Lambda handler code

├── glue/

│   └── orders_etl.py       # Glue ETL script

└── step_functions/

    └── orders_workflow.json # State machine definition

```

 

**Command to Generate New Feature:**

```bash

python -m services.reference_generator.service \

    --action generate \

    --name orders-pipeline \

    --requirements inventory-pipeline.md \

    --entity-mapping '{"reference": "orders", "new": "inventory"}' \

    --output generated/inventory-pipeline

```

 

**Generated Output:**

```

generated/inventory-pipeline/

├── terraform/

│   ├── lambda.tf           # process_inventory Lambda

│   ├── glue.tf             # inventory_etl Glue job

│   ├── step_functions.tf   # inventory_workflow state machine

│   ├── s3.tf               # inventory_data bucket

│   ├── iam.tf              # inventory IAM roles

│   ├── variables.tf        # Updated variables

│   ├── providers.tf        # Provider config

│   └── outputs.tf          # Output definitions

├── lambda/

│   └── process_inventory/

│       └── handler.py      # Transformed handler

├── glue/

│   └── inventory_etl.py    # Transformed Glue script

└── step_functions/

    └── inventory_workflow.json # Transformed state machine

```

 

#### Infrastructure Mappings Reference

 

| Reference Pattern | Generated Pattern | Transformations |

|------------------|-------------------|-----------------|

| `orders_bucket` | `inventory_bucket` | Name substitution |

| `ProcessOrders` | `ProcessInventory` | Lambda function name |

| `orders_etl` | `inventory_etl` | Glue job name |

| `orders_workflow` | `inventory_workflow` | Step Function name |

| `ORDERS_TABLE` | `INVENTORY_TABLE` | Environment variables |

| `s3://data/orders/` | `s3://data/inventory/` | S3 paths |

| `aws_lambda_function.orders` | `aws_lambda_function.inventory` | Terraform references |

 

---

 

### Caching, Memory & Context Management Support

 

The Reference-Based Code Generation also handles **caching patterns**, **memory stores**, and **context management**:

 

```

┌─────────────────────────────────────────────────────────────────┐

│               CACHING & CONTEXT PATTERN TYPES                    │

├─────────────────────────────────────────────────────────────────┤

│                                                                  │

│  CACHING PATTERNS               MEMORY STORES                    │

│  ├── @lru_cache decorators      ├── AWS ElastiCache (Redis)     │

│  ├── @ttl_cache (cachetools)    ├── AWS ElastiCache (Memcached) │

│  ├── Redis cache-aside          ├── DynamoDB DAX                │

│  ├── Write-through cache        └── Redis Cluster configs       │

│  ├── Write-behind cache                                          │

│  └── Cache invalidation                                          │

│                                                                  │

│  CONTEXT PATTERNS               SESSION PATTERNS                 │

│  ├── Context managers           ├── Session stores (Redis)      │

│  ├── @contextmanager            ├── JWT session handling        │

│  ├── Async context managers     ├── Request-scoped context      │

│  ├── contextvars.ContextVar     └── Transaction contexts        │

│  └── Thread-local storage                                        │

│                                                                  │

└─────────────────────────────────────────────────────────────────┘

```

 

#### Python Caching Pattern Extraction

 

The system extracts caching patterns from Python code:

 

**Reference Code (`orders/cache.py`):**

```python

from functools import lru_cache

from cachetools import TTLCache, cached

import redis.asyncio as aioredis

 

# LRU cache decorator

@lru_cache(maxsize=256)

def get_order_by_id(order_id: int) -> dict:

    return db.query(Order).filter(Order.id == order_id).first()

 

# TTL cache with cachetools

@cached(cache=TTLCache(maxsize=100, ttl=300))

def get_order_summary(order_id: int) -> dict:

    return calculate_order_summary(order_id)

 

# Redis cache-aside pattern

class OrderCacheService:

    def __init__(self, redis_client: aioredis.Redis):

        self.redis = redis_client

        self.prefix = "orders:"

        self.ttl = 3600

   

    async def get_order(self, order_id: int) -> dict:

        # Try cache first

        cached = await self.redis.get(f"{self.prefix}{order_id}")

        if cached:

            return json.loads(cached)

       

        # Cache miss - fetch from DB

        order = await self.repository.get_by_id(order_id)

       

        # Store in cache

        await self.redis.set(

            f"{self.prefix}{order_id}",

            json.dumps(order),

            ex=self.ttl

        )

        return order

   

    async def invalidate_order(self, order_id: int):

        await self.redis.delete(f"{self.prefix}{order_id}")

```

 

**Generated Code (`inventory/cache.py`):**

```python

from functools import lru_cache

from cachetools import TTLCache, cached

import redis.asyncio as aioredis

 

# LRU cache decorator - entity transformed

@lru_cache(maxsize=256)

def get_inventory_by_id(inventory_id: int) -> dict:

    return db.query(Inventory).filter(Inventory.id == inventory_id).first()

 

# TTL cache with cachetools

@cached(cache=TTLCache(maxsize=100, ttl=300))

def get_inventory_summary(inventory_id: int) -> dict:

    return calculate_inventory_summary(inventory_id)

 

# Redis cache-aside pattern - fully transformed

class InventoryCacheService:

    def __init__(self, redis_client: aioredis.Redis):

        self.redis = redis_client

        self.prefix = "inventory:"  # Updated prefix

        self.ttl = 3600

   

    async def get_inventory(self, inventory_id: int) -> dict:

        cached = await self.redis.get(f"{self.prefix}{inventory_id}")

        if cached:

            return json.loads(cached)

       

        inventory = await self.repository.get_by_id(inventory_id)

        await self.redis.set(

            f"{self.prefix}{inventory_id}",

            json.dumps(inventory),

            ex=self.ttl

        )

        return inventory

   

    async def invalidate_inventory(self, inventory_id: int):

        await self.redis.delete(f"{self.prefix}{inventory_id}")

```

 

#### Context Manager Pattern Handling

 

**Reference Context Manager:**

```python

from contextvars import ContextVar

from contextlib import asynccontextmanager

 

# Request context using ContextVar

order_context: ContextVar[OrderContext] = ContextVar("order_context")

 

@asynccontextmanager

async def order_request_context(request_id: str, user_id: str):

    ctx = OrderContext(request_id=request_id, user_id=user_id)

    token = order_context.set(ctx)

    try:

        yield ctx

    finally:

        order_context.reset(token)

 

class OrderTransactionContext:

    """Context manager for order transactions."""

   

    def __init__(self, session):

        self.session = session

   

    async def __aenter__(self):

        await self.session.begin()

        return self

   

    async def __aexit__(self, exc_type, exc_val, exc_tb):

        if exc_type:

            await self.session.rollback()

        else:

            await self.session.commit()

```

 

**Generated Context Manager:**

```python

from contextvars import ContextVar

from contextlib import asynccontextmanager

 

# Request context - transformed

inventory_context: ContextVar[InventoryContext] = ContextVar("inventory_context")

 

@asynccontextmanager

async def inventory_request_context(request_id: str, user_id: str):

    ctx = InventoryContext(request_id=request_id, user_id=user_id)

    token = inventory_context.set(ctx)

    try:

        yield ctx

    finally:

        inventory_context.reset(token)

 

class InventoryTransactionContext:

    """Context manager for inventory transactions."""

   

    def __init__(self, session):

        self.session = session

   

    async def __aenter__(self):

        await self.session.begin()

        return self

   

    async def __aexit__(self, exc_type, exc_val, exc_tb):

        if exc_type:

            await self.session.rollback()

        else:

            await self.session.commit()

```

 

#### ElastiCache Terraform Pattern

 

**Reference ElastiCache (`orders/terraform/elasticache.tf`):**

```hcl

resource "aws_elasticache_replication_group" "orders_redis" {

  replication_group_id       = "${var.prefix}-orders-redis"

  description                = "Redis for orders caching"

 

  engine                     = "redis"

  engine_version             = "7.0"

  node_type                  = "cache.t3.micro"

  num_cache_clusters         = 2

 

  port                       = 6379

 

  subnet_group_name          = aws_elasticache_subnet_group.orders_cache.name

  security_group_ids         = [aws_security_group.orders_cache_sg.id]

 

  at_rest_encryption_enabled = true

  transit_encryption_enabled = true

  auth_token                 = var.redis_auth_token

 

  automatic_failover_enabled = true

  multi_az_enabled           = true

}

```

 

**Generated ElastiCache (`inventory/terraform/elasticache.tf`):**

```hcl

resource "aws_elasticache_replication_group" "inventory_redis" {

  replication_group_id       = "${var.prefix}-inventory-redis"

  description                = "Redis for inventory caching"

 

  engine                     = "redis"

  engine_version             = "7.0"

  node_type                  = "cache.t3.micro"

  num_cache_clusters         = 2

 

  port                       = 6379

 

  subnet_group_name          = aws_elasticache_subnet_group.inventory_cache.name

  security_group_ids         = [aws_security_group.inventory_cache_sg.id]

 

  at_rest_encryption_enabled = true

  transit_encryption_enabled = true

  auth_token                 = var.redis_auth_token

 

  automatic_failover_enabled = true

  multi_az_enabled           = true

}

```

 

#### Generated Cache Service

 

When you generate code, you also get a complete cache service:

 

```python

# Generated: inventory/cache/service.py

 

class CacheService:

    """Cache service with Redis backend."""

   

    async def get_or_fetch(self, key: str, fetch_func, ttl: int = 3600):

        """Cache-aside pattern helper."""

        cached = await self.get(key)

        if cached is not None:

            return cached

       

        value = await fetch_func()

        if value is not None:

            await self.set(key, value, ttl=ttl)

       

        return value

   

    async def invalidate_pattern(self, pattern: str) -> int:

        """Invalidate all keys matching pattern."""

        ...

 

# Usage in your code:

cache = await get_cache_service()

inventory = await cache.get_or_fetch(

    key=f"inventory:{id}",

    fetch_func=lambda: repository.get_by_id(id),

    ttl=300

)

```

 

#### Caching Mappings Reference

 

| Reference Pattern | Generated Pattern | Notes |

|------------------|-------------------|-------|

| `@lru_cache` | `@lru_cache` | Function names transformed |

| `orders_cache` | `inventory_cache` | Cache key prefixes |

| `ORDER_CACHE_TTL` | `INVENTORY_CACHE_TTL` | Environment variables |

| `orders_redis` | `inventory_redis` | ElastiCache cluster names |

| `order_context` | `inventory_context` | ContextVar names |

| `OrderCacheService` | `InventoryCacheService` | Class names |

| `redis.get("orders:")` | `redis.get("inventory:")` | Key prefixes in code |

 

---

 

### Lucid Flowchart XML as Input Reference

 

In addition to generating Lucid flowcharts from SQL and documentation, you can also **use Lucid XML flowcharts as input** for code generation. This allows you to:

 

1. Design your system visually in Lucidchart
2. Export the flowchart as XML
3. Import it into DevFlow as a reference
4. Generate code patterns automatically from the visual design

 

```

┌─────────────────────────────────────────────────────────────────┐

│          FLOWCHART XML AS INPUT REFERENCE                        │

├─────────────────────────────────────────────────────────────────┤

│                                                                  │

│   YOUR LUCID FLOWCHART           DEVFLOW PARSER                  │

│   ┌─────────────────────┐       ┌─────────────────────┐         │

│   │  ┌─────┐            │       │ LucidXMLParser      │         │

│   │  │Start│            │   ->  │ • Extract nodes     │         │

│   │  └──┬──┘            │       │ • Parse connections │         │

│   │     ▼               │       │ • Detect types      │         │

│   │  ┌──────┐           │       └──────────┬──────────┘         │

│   │  │Validate│         │                  │                    │

│   │  └──┬──┘            │                  ▼                    │

│   │     ▼               │       ┌─────────────────────┐         │

│   │  ┌──────┐           │       │ EXTRACTED:          │         │

│   │  │ Save │           │       │ • Requirements      │         │

│   │  └──────┘           │       │ • Processes         │         │

│   └─────────────────────┘       │ • Data flows        │         │

│                                 │ • Code patterns     │         │

│                                 └──────────┬──────────┘         │

│                                            │                    │

│                                            ▼                    │

│                                 ┌─────────────────────┐         │

│                                 │ GENERATED CODE      │         │

│                                 │ services/           │         │

│                                 │ repositories/       │         │

│                                 │ models/             │         │

│                                 └─────────────────────┘         │

│                                                                  │

└─────────────────────────────────────────────────────────────────┘

```

 

#### Supported XML Formats

 

| Format | Description |

|--------|-------------|

| **Lucidchart XML** | Native Lucidchart export format |

| **draw.io/diagrams.net** | mxGraphModel format |

| **DevFlow XML** | Custom flowchart XML format |

 

#### Node Type Detection

 

The parser automatically detects node types from shapes and labels:

 

| Shape/Pattern | Detected Type | Generated Pattern |

|--------------|---------------|-------------------|

| Ellipse + "Start" | Start/End | - |

| Diamond | Decision | Conditional logic |

| Rectangle | Process | Service method |

| Cylinder | Database | Repository pattern |

| Parallelogram | Data | Data model |

| Document | Document | Requirements |

 

#### Usage: Load Flowchart as Reference

 

```python

from services.reference_generator import ReferenceGeneratorService

 

service = ReferenceGeneratorService(project_dir="/my/project")

 

# Load the Lucid XML as a reference

reference = await service.load_flowchart_as_reference(

    xml_path="designs/order_workflow.xml",

    name="order-workflow",

    description="Order processing workflow from Lucidchart"

)

 

print(f"Patterns extracted: {len(reference.patterns)}")

print(f"Requirements found: {len(reference.requirements)}")

 

# Now use this reference for code generation

result = await service.generate_from_reference(

    reference_name="order-workflow",

    new_requirements_path="specs/inventory-workflow.md",

    entity_mappings=[{"reference": "Order", "new": "Inventory"}],

    output_dir="generated/inventory"

)

```

 

#### Usage: Parse and Inspect Flowchart

 

```python

# Parse the flowchart without loading as reference

result = service.parse_flowchart_xml("designs/workflow.xml")

 

if result.success:

    print(f"Flowchart: {result.flowchart.name}")

    print(f"Nodes: {len(result.flowchart.nodes)}")

    

    # View extracted requirements

    for req in result.requirements:

        print(f"  REQ: {req.title}")

    

    # View extracted processes

    for proc in result.processes:

        print(f"  PROCESS: {proc.name} ({proc.process_type})")

        print(f"    Inputs: {proc.inputs}")

        print(f"    Outputs: {proc.outputs}")

    

    # View data flows

    for df in result.data_flows:

        print(f"  DATA: {df.operation.upper()} on {df.table_name}")

    

    # View generated patterns

    for pattern in result.generated_patterns:

        print(f"  PATTERN: {pattern.name} ({pattern.pattern_type.value})")

```

 

#### Usage: Generate Code Directly from Flowchart

 

```python

# Skip loading as reference - generate directly

result = await service.generate_from_flowchart(

    xml_path="designs/workflow.xml",

    entity_mappings=[{"reference": "Order", "new": "Shipment"}],

    output_dir="generated/shipment"

)

 

if result.success:

    for file in result.generated_files:

        print(f"Generated: {file.path}")

```

 

#### CLI Commands

 

```bash

cd apps/backend

 

# Parse a flowchart and view extracted information

python -m services.reference_generator.service \

    --action parse-flowchart \

    --xml-file designs/order_workflow.xml

 

# Load flowchart as a reference

python -m services.reference_generator.service \

    --action load-flowchart \

    --xml-file designs/order_workflow.xml \

    --name order-workflow \

    --description "Order processing workflow"

 

# Generate code directly from flowchart

python -m services.reference_generator.service \

    --action generate-from-flowchart \

    --xml-file designs/order_workflow.xml \

    --entity-mapping '{"reference": "Order", "new": "Inventory"}' \

    --output generated/inventory

 

# With JSON output for scripting

python -m services.reference_generator.service \

    --action parse-flowchart \

    --xml-file designs/workflow.xml \

    --json

```

 

#### Example: Complete Workflow with Visual Design

 

**Step 1: Design in Lucidchart**

Create your system flowchart showing:

- Process steps (rectangles)

- Decision points (diamonds)

- Data operations (cylinders for database)

- Connections with labels

 

**Step 2: Export as XML**

In Lucidchart: File → Download → XML

 

**Step 3: Parse and Review**

```bash

python -m services.reference_generator.service \

    --action parse-flowchart \

    --xml-file order_workflow.xml

```

 

Output:

```

✅ Parsed flowchart: Order Processing

   Nodes: 12

   Connections: 15

 

   Requirements extracted: 3

     - Validate order details

     - Check inventory availability

     - Process payment

 

   Processes extracted: 8

     - Validate Order (action)

     - Check Stock (action)

     - Sufficient Stock? (decision)

     - Create Order Record (action)

     ...

 

   Data flows extracted: 4

     - READ on orders

     - READ on inventory

     - WRITE on orders

     - UPDATE on inventory

 

   Patterns generated: 6

```

 

**Step 4: Generate Code**

```bash

python -m services.reference_generator.service \

    --action generate-from-flowchart \

    --xml-file order_workflow.xml \

    --entity-mapping '{"reference": "Order", "new": "Shipment"}' \

    --output generated/shipment

```

 

**Step 5: Review Generated Files**

```

generated/shipment/

├── services/

│   ├── shipment_service.py      # From process nodes

│   └── validation_service.py

├── repositories/

│   └── shipment_repository.py   # From database nodes

└── models/

    └── shipment.py              # From data flows

```

 

#### Pattern Generation from Flowchart Elements

 

| Flowchart Element | Generated Code |

|------------------|----------------|

| Process node "Validate Order" | `async def validate_order(self, ...)` |

| Decision "Is Valid?" | Conditional logic with branches |

| Database "Read Orders" | `OrderRepository.get_by_id()` |

| Database "Write Orders" | `OrderRepository.create()` |

| Subprocess "Process Payment" | Separate service class |

 

---

 

### Example: Complete Workflow

 

**Step 1: Prepare Reference Folder**

 

```

user-auth-reference/

├── requirements.md

├── schema.sql

├── services/

│   └── user_service.py

├── repositories/

│   └── user_repository.py

└── tests/

    └── test_user.py

```

 

**Step 2: Load Reference**

 

```bash

python -m services.reference_generator.service \

    --action load \

    --reference user-auth-reference \

    --name user-auth

```

 

**Step 3: Create New Requirements (product-catalog.md)**

 

```markdown

# Product Catalog Requirements

 

## Features

- List all products with pagination

- Filter products by category

- Search products by name

- View product details

- Create new products (admin only)

- Update product information

- Delete products (soft delete)

 

## Acceptance Criteria

- Products have: id, name, description, price, category, sku

- API responds within 200ms

- Pagination supports 20 items per page

```

 

**Step 4: Generate Code**

 

```bash

python -m services.reference_generator.service \

    --action generate \

    --name user-auth \

    --requirements product-catalog.md \

    --output generated/product

```

 

**Step 5: Review Generated Files**

 

```

generated/product/

├── schema/

│   └── generated_schema.sql

├── services/

│   └── product_service.py

├── repositories/

│   └── product_repository.py

├── models/

│   └── product.py

├── controllers/

│   └── product_controller.py

└── tests/

    └── test_product.py

```

 

---

 

### Example: Oracle to AWS PostgreSQL Migration

 

A complete example is provided in `apps/backend/services/reference_generator/examples/oracle-to-postgres/` demonstrating how to migrate a feature from Oracle/SQL to AWS PostgreSQL/Python.

 

#### Scenario

 

You have an existing **Order Management System** with:

- Oracle Database with PL/SQL stored procedures

- SQL-based business logic

- Java/JDBC data access layer

 

You want to migrate to:

- AWS PostgreSQL (RDS/Aurora)

- Python with async SQLAlchemy

- Modern repository/service patterns

 

#### Reference Structure

 

```

oracle-to-postgres/

├── requirements/

│   └── order-management.md      # Original feature requirements

│

├── oracle/                      # Oracle source (reference)

│   ├── schema.sql               # CREATE TABLE with Oracle types

│   └── procedures/

│       ├── create_order.sql     # SP_CREATE_ORDER

│       ├── update_order.sql     # SP_UPDATE_ORDER_STATUS

│       └── get_order_details.sql # SP_GET_ORDER_DETAILS

│

└── expected-output/             # Generated PostgreSQL/Python

    ├── schema/

    │   └── postgres_schema.sql  # PostgreSQL schema with ENUMs

    ├── models/

    │   └── order.py             # SQLAlchemy models

    ├── repositories/

    │   └── order_repository.py  # Async repository pattern

    └── services/

        └── order_service.py     # Business logic service

```

 

#### Oracle to PostgreSQL Transformations

 

| Oracle | PostgreSQL/Python |

|--------|------------------|

| `NUMBER(10)` | `INTEGER` / `SERIAL` |

| `NUMBER(10,2)` | `DECIMAL(10,2)` |

| `VARCHAR2(255)` | `VARCHAR(255)` |

| `SYSTIMESTAMP` | `NOW()` / `CURRENT_TIMESTAMP` |

| `SYSDATE` | `CURRENT_DATE` |

| PL/SQL Procedure | Python async method |

| `SYS_REFCURSOR` | SQLAlchemy query result |

| Sequence | `SERIAL` / `IDENTITY` |

| Oracle triggers | PostgreSQL trigger functions |

 

#### Stored Procedure to Python Mapping

 

**Oracle SP_CREATE_ORDER:**

```sql

CREATE OR REPLACE PROCEDURE SP_CREATE_ORDER (

    p_customer_id    IN NUMBER,

    p_items          IN SYS.ODCIVARCHAR2LIST,

    p_shipping_addr  IN VARCHAR2,

    p_order_id       OUT NUMBER,

    p_status         OUT VARCHAR2

) AS

BEGIN

    -- PL/SQL implementation

END;

```

 

**Python Equivalent:**

```python

class OrderService:

    async def create_order(

        self,

        customer_id: int,

        items: list[OrderItemInput],

        shipping_address: str,

    ) -> CreateOrderResult:

        """

        Create a new order with items.

        Replaces Oracle SP_CREATE_ORDER procedure.

        """

        # Validate customer

        if not await self.customer_repo.exists(customer_id):

            return CreateOrderResult(success=False, message="Customer not found")

       

        # Validate stock

        for item in items:

            if not await self.product_repo.check_stock(item.product_id, item.quantity):

                return CreateOrderResult(success=False, message="Insufficient stock")

       

        # Create order with items

        order = Order(

            customer_id=customer_id,

            order_number=self._generate_order_number(),

            status=OrderStatus.PENDING,

        )

       

        for item in items:

            product = await self.product_repo.get_by_id(item.product_id)

            order.items.append(OrderItem(

                product_id=item.product_id,

                quantity=item.quantity,

                unit_price=product.unit_price,

                line_total=product.unit_price * item.quantity,

            ))

       

        order.calculate_totals()

        await self.order_repo.create(order)

        await self.session.commit()

       

        return CreateOrderResult(success=True, order_id=order.order_id)

```

 

#### Using the Migration Reference

 

**Step 1: Load the Oracle reference**

```bash

python -m services.reference_generator.service \

    --action load \

    --reference apps/backend/services/reference_generator/examples/oracle-to-postgres \

    --name oracle-order-management

```

 

**Step 2: Create new requirements for a different feature**

 

Create `inventory-management.md`:

```markdown

# Inventory Management Requirements

 

## Features

- Track product stock levels

- Record stock movements (in/out)

- Generate low stock alerts

- Audit trail for all changes

 

## Data Model

- Inventory: product_id, quantity, location, last_counted

- StockMovement: movement_type, quantity, reference, timestamp

```

 

**Step 3: Generate PostgreSQL/Python implementation**

```bash

python -m services.reference_generator.service \

    --action generate \

    --name oracle-order-management \

    --requirements inventory-management.md \

    --output generated/inventory-postgres

```

 

**Step 4: Review generated code**

 

The generator produces:

- `postgres_schema.sql` - Tables using PostgreSQL types

- `inventory.py` - SQLAlchemy models with relationships

- `inventory_repository.py` - Async repository with proper queries

- `inventory_service.py` - Business logic replacing stored procedures

- `test_inventory.py` - Test templates

 

#### Key Benefits

 

1. **Pattern Consistency**: New features follow the same patterns as the reference

2. **Tech Stack Migration**: Oracle concepts translate to PostgreSQL/Python equivalents

3. **Async Support**: Generated code uses async/await patterns

4. **Modern Python**: Type hints, dataclasses, and modern SQLAlchemy 2.0

5. **Test Coverage**: Automatic test template generation

 

---

 

## Reference Code Examples & Product Requirements

 

This section provides practical examples of how DevFlow's codebase is organized and demonstrates how to create effective product requirements using the Kanban board approach.

 

### Code Reference Structure

 

DevFlow's backend follows a modular service-oriented architecture. Here are key reference folders:

 

#### Service Orchestrator (`apps/backend/services/`)

 

The services folder demonstrates the orchestration pattern for multi-service environments:

 

```

apps/backend/services/

├── __init__.py           # Package exports

├── context.py            # Context management service

├── orchestrator.py       # Multi-service orchestration (Docker, monorepo)

└── recovery.py           # Error recovery service

```

 

**Example: ServiceOrchestrator Class**

 

```python

# apps/backend/services/orchestrator.py

 

@dataclass

class ServiceConfig:

    """Configuration for a single service."""

    name: str

    path: str | None = None

    port: int | None = None

    type: str = "docker"  # docker, local, mock

    health_check_url: str | None = None

    startup_command: str | None = None

    startup_timeout: int = 120

 

 

class ServiceOrchestrator:

    """Orchestrates multi-service environments."""

   

    def __init__(self, project_dir: Path) -> None:

        self.project_dir = Path(project_dir)

        self._services: list[ServiceConfig] = []

        self._discover_services()

   

    def is_multi_service(self) -> bool:

        """Check if this is a multi-service project."""

        return len(self._services) > 1

   

    def start_services(self, timeout: int = 120) -> OrchestrationResult:

        """Start all services with health check waiting."""

        # Implementation handles Docker Compose and local services

        pass

 

 

# Context manager for easy service lifecycle

class ServiceContext:

    """Context manager for service orchestration."""

   

    def __enter__(self) -> "ServiceContext":

        if self.orchestrator.is_multi_service():

            self.result = self.orchestrator.start_services()

        return self

   

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:

        self.orchestrator.stop_services()

```

 

#### Spec Pipeline (`apps/backend/spec/`)

 

The spec pipeline demonstrates phase-based execution architecture:

 

```

apps/backend/spec/

├── pipeline/

│   ├── orchestrator.py   # Main spec creation orchestrator

│   ├── agent_runner.py   # Agent execution wrapper

│   └── models.py         # Spec data models

├── phases/

│   ├── discovery_phases.py     # Project analysis

│   ├── requirements_phases.py  # Requirements gathering

│   ├── spec_phases.py          # Spec document writing

│   └── planning_phases.py      # Implementation planning

└── validate_pkg/

    ├── spec_validator.py       # Validation logic

    └── validators/             # Specific validators

```

 

#### Implementation Plan (`apps/backend/implementation_plan/`)

 

Demonstrates subtask-based planning:

 

```

apps/backend/implementation_plan/

├── __init__.py       # Package exports

├── enums.py          # WorkflowType, PhaseType, SubtaskStatus

├── subtask.py        # Subtask model (unit of work)

├── phase.py          # Phase model (groups subtasks)

├── plan.py           # Complete implementation plan

├── verification.py   # Test verification models

└── factories.py      # Factory functions for plan creation

```

 

---

 

### Example Product Requirement (Existing Feature)

 

Below is an example of how a product requirement flows through the Kanban board:

 

#### **PRD: Task Card Title Readability Improvement**

 

**Kanban Stage**: Done ✅

 

```json

{

  "spec_id": "025-improving-task-card-title-readability",

  "subtasks": [

    {

      "id": "1",

      "title": "Restructure TaskCard header: Remove flex wrapper, make title full width",

      "status": "completed"

    },

    {

      "id": "2",

      "title": "Relocate status badges from header to metadata section",

      "status": "completed"

    },

    {

      "id": "3",

      "title": "Add localization for security severity badge label",

      "status": "completed"

    }

  ],

  "qa_signoff": {

    "status": "fixes_applied",

    "timestamp": "2026-01-01T11:58:40Z",

    "issues_fixed": [

      {

        "title": "Missing localization for hardcoded 'severity' string",

        "fix_commit": "de0c8e4"

      }

    ]

  }

}

```

 

**Requirements Document (`requirements.json`):**

 

```json

{

  "task_description": "Improve task card title readability by restructuring the header layout",

  "workflow_type": "feature",

  "services_involved": ["frontend"],

  "user_requirements": [

    "Task titles should have full width for better readability",

    "Status badges should not compete with title space",

    "All UI text must be localized"

  ],

  "acceptance_criteria": [

    "Title occupies full width of card header",

    "Status badges moved to metadata section",

    "No hardcoded strings in UI components",

    "Existing tests pass"

  ],

  "constraints": [

    "Must maintain backward compatibility",

    "No breaking changes to task data structure"

  ]

}

```

 

---

 

### New Feature Product Requirement Template

 

Use this template to create new feature requests following the Kanban board approach:

 

#### **PRD: [Feature Name]**

 

**Kanban Stage**: Backlog 📋

 

```

┌─────────────────────────────────────────────────────────────────┐

│  KANBAN WORKFLOW FOR NEW FEATURE                                 │

├─────────────────────────────────────────────────────────────────┤

│                                                                  │

│  ┌──────────┐    ┌───────────┐    ┌────────────┐                │

│  │ Backlog  │ -> │ Planning  │ -> │ In Progress│ ->             │

│  │          │    │           │    │            │                │

│  │ Create   │    │ Planner   │    │ Coder      │                │

│  │ Task     │    │ Agent     │    │ Agent      │                │

│  └──────────┘    └───────────┘    └────────────┘                │

│                                                                  │

│  ┌───────────┐    ┌──────────────┐    ┌──────┐                  │

│  │ AI Review │ -> │ Human Review │ -> │ Done │                  │

│  │           │    │              │    │      │                  │

│  │ QA Loop   │    │ User Tests   │    │Merged│                  │

│  └───────────┘    └──────────────┘    └──────┘                  │

│                                                                  │

└─────────────────────────────────────────────────────────────────┘

```

 

---

 

### Example: New Feature - "Smart Code Suggestions Service"

 

Here's a complete example of a new feature following the Kanban approach:

 

#### **Stage 1: Backlog (Create Task)**

 

**Task Title**: Add Smart Code Suggestions Service

 

**Task Description**:

Create a new backend service that analyzes code patterns in the project and provides intelligent suggestions to the Coder Agent during implementation. The service should integrate with the existing Memory Layer (Graphiti) to learn from past successful implementations.

 

**Reference Files** (drag & drop):

- `apps/backend/services/orchestrator.py` - Service pattern reference

- `apps/backend/integrations/graphiti/` - Memory integration pattern

- `apps/backend/agents/coder.py` - Agent integration point

 

---

 

#### **Stage 2: Planning (Planner Agent Creates Plan)**

 

**`requirements.json`** (auto-generated):

 

```json

{

  "task_description": "Create Smart Code Suggestions Service for enhanced AI coding assistance",

  "workflow_type": "feature",

  "services_involved": ["backend", "graphiti"],

  "user_requirements": [

    "Analyze codebase patterns for suggestion generation",

    "Integrate with Graphiti memory for learning",

    "Provide suggestions API for Coder Agent consumption",

    "Support caching for performance optimization"

  ],

  "acceptance_criteria": [

    "Service starts and responds to health checks",

    "Suggestions endpoint returns relevant code patterns",

    "Integration with Graphiti retrieves historical patterns",

    "Response time under 500ms for suggestions",

    "Unit tests cover core functionality",

    "Integration tests verify Graphiti communication"

  ],

  "constraints": [

    "Must follow existing service patterns in apps/backend/services/",

    "Memory queries must use existing Graphiti integration",

    "No external API dependencies beyond Graphiti"

  ]

}

```

 

**`implementation_plan.json`** (auto-generated):

 

```json

{

  "spec_id": "026-smart-code-suggestions-service",

  "workflow_type": "feature",

  "phases": [

    {

      "id": "phase-1",

      "name": "Backend Service Foundation",

      "type": "backend",

      "subtasks": [

        {

          "id": "1.1",

          "title": "Create SuggestionConfig dataclass in apps/backend/services/suggestions.py",

          "files_to_modify": ["apps/backend/services/suggestions.py"],

          "patterns_from": ["apps/backend/services/orchestrator.py"],

          "verification": {

            "type": "unit",

            "command": "pytest tests/test_suggestions_config.py -v"

          }

        },

        {

          "id": "1.2",

          "title": "Implement SuggestionService class with pattern analysis",

          "files_to_modify": ["apps/backend/services/suggestions.py"],

          "depends_on": ["1.1"],

          "verification": {

            "type": "unit",

            "command": "pytest tests/test_suggestions_service.py -v"

          }

        }

      ]

    },

    {

      "id": "phase-2",

      "name": "Graphiti Integration",

      "type": "integration",

      "subtasks": [

        {

          "id": "2.1",

          "title": "Add suggestion queries to Graphiti integration",

          "files_to_modify": ["apps/backend/integrations/graphiti/queries.py"],

          "patterns_from": ["apps/backend/integrations/graphiti/memory.py"],

          "verification": {

            "type": "integration",

            "command": "pytest tests/test_graphiti_suggestions.py -v"

          }

        },

        {

          "id": "2.2",

          "title": "Wire SuggestionService to use Graphiti queries",

          "files_to_modify": ["apps/backend/services/suggestions.py"],

          "depends_on": ["1.2", "2.1"],

          "verification": {

            "type": "integration",

            "command": "pytest tests/test_suggestions_integration.py -v"

          }

        }

      ]

    },

    {

      "id": "phase-3",

      "name": "Agent Integration",

      "type": "integration",

      "subtasks": [

        {

          "id": "3.1",

          "title": "Add suggestions hook to Coder Agent",

          "files_to_modify": ["apps/backend/agents/coder.py"],

          "depends_on": ["2.2"],

          "verification": {

            "type": "unit",

            "command": "pytest tests/test_coder_suggestions.py -v"

          }

        },

        {

          "id": "3.2",

          "title": "Export SuggestionService in services/__init__.py",

          "files_to_modify": ["apps/backend/services/__init__.py"],

          "depends_on": ["3.1"],

          "verification": {

            "type": "unit",

            "command": "python -c 'from services import SuggestionService; print(\"OK\")'"

          }

        }

      ]

    }

  ]

}

```

 

---

 

#### **Stage 3: In Progress (Coder Agent Implements)**

 

The Coder Agent creates files following the patterns from reference files:

 

**New File: `apps/backend/services/suggestions.py`**

 

```python

#!/usr/bin/env python3

"""

Smart Code Suggestions Service

==============================

 

Provides intelligent code suggestions based on codebase patterns

and historical implementations from Graphiti memory.

 

Usage:

    from services import SuggestionService

   

    suggestions = SuggestionService(project_dir)

    patterns = await suggestions.get_patterns_for_file("component.tsx")

"""

 

from dataclasses import dataclass, field

from pathlib import Path

from typing import Any

 

 

@dataclass

class SuggestionConfig:

    """Configuration for a suggestion query."""

   

    file_path: str

    context_lines: int = 50

    max_suggestions: int = 5

    include_historical: bool = True

    cache_ttl: int = 300  # seconds

 

 

@dataclass

class CodeSuggestion:

    """A single code suggestion."""

   

    pattern_name: str

    source_file: str

    code_snippet: str

    confidence: float

    explanation: str

 

 

@dataclass

class SuggestionResult:

    """Result of suggestion query."""

   

    success: bool = False

    suggestions: list[CodeSuggestion] = field(default_factory=list)

    from_cache: bool = False

    errors: list[str] = field(default_factory=list)

 

 

class SuggestionService:

    """Provides code suggestions based on project patterns."""

   

    def __init__(self, project_dir: Path) -> None:

        self.project_dir = Path(project_dir)

        self._cache: dict[str, SuggestionResult] = {}

        self._graphiti_client = None

   

    async def initialize(self) -> bool:

        """Initialize service and connect to Graphiti."""

        try:

            from integrations.graphiti import get_client

            self._graphiti_client = await get_client(self.project_dir)

            return True

        except Exception:

            return False

   

    async def get_patterns_for_file(

        self,

        file_path: str,

        config: SuggestionConfig | None = None

    ) -> SuggestionResult:

        """Get code pattern suggestions for a file."""

        if config is None:

            config = SuggestionConfig(file_path=file_path)

       

        # Check cache first

        cache_key = f"{file_path}:{config.max_suggestions}"

        if cache_key in self._cache:

            result = self._cache[cache_key]

            result.from_cache = True

            return result

       

        # Query patterns from memory

        result = await self._query_patterns(config)

       

        # Cache successful results

        if result.success:

            self._cache[cache_key] = result

       

        return result

   

    async def _query_patterns(self, config: SuggestionConfig) -> SuggestionResult:

        """Query Graphiti for relevant patterns."""

        if not self._graphiti_client:

            return SuggestionResult(

                success=False,

                errors=["Graphiti client not initialized"]

            )

       

        try:

            # Get file extension to filter pattern types

            ext = Path(config.file_path).suffix

           

            # Query memory for similar patterns

            patterns = await self._graphiti_client.search_patterns(

                file_type=ext,

                limit=config.max_suggestions,

                include_historical=config.include_historical

            )

           

            suggestions = [

                CodeSuggestion(

                    pattern_name=p["name"],

                    source_file=p["source"],

                    code_snippet=p["snippet"],

                    confidence=p["confidence"],

                    explanation=p["explanation"]

                )

                for p in patterns

            ]

           

            return SuggestionResult(success=True, suggestions=suggestions)

           

        except Exception as e:

            return SuggestionResult(

                success=False,

                errors=[f"Pattern query failed: {str(e)}"]

            )

   

    def clear_cache(self) -> None:

        """Clear the suggestion cache."""

        self._cache.clear()

   

    def to_dict(self) -> dict[str, Any]:

        """Convert service state to dictionary."""

        return {

            "project_dir": str(self.project_dir),

            "cache_size": len(self._cache),

            "graphiti_connected": self._graphiti_client is not None

        }

```

 

---

 

#### **Stage 4: AI Review (QA Loop)**

 

**`qa_report.md`** (auto-generated):

 

```markdown

# QA Report: Smart Code Suggestions Service

 

## Summary

- **Status**: APPROVED ✅

- **Iterations**: 2

- **Issues Found**: 1 (fixed)

 

## Validation Results

 

### Unit Tests

| Test | Status | Notes |

|------|--------|-------|

| test_suggestion_config | ✅ PASS | Default values validated |

| test_suggestion_service_init | ✅ PASS | Service initializes correctly |

| test_pattern_query | ✅ PASS | Patterns returned as expected |

| test_cache_behavior | ✅ PASS | Cache hit/miss verified |

 

### Integration Tests 

| Test | Status | Notes |

|------|--------|-------|

| test_graphiti_connection | ✅ PASS | Memory layer connected |

| test_pattern_search | ✅ PASS | Historical patterns retrieved |

 

### Issues Fixed

1. **Missing error handling for empty results**

   - File: `apps/backend/services/suggestions.py`

   - Fix: Added empty list handling in `_query_patterns`

   - Commit: `abc1234`

 

## QA Sign-off

- [x] All unit tests pass

- [x] All integration tests pass

- [x] Code follows established patterns

- [x] No security vulnerabilities

- [x] Documentation complete

```

 

---

 

#### **Stage 5: Human Review**

 

At this stage, you can:

1. **Review the diff** - See all changes made

2. **Test manually** - Run the service locally

3. **Approve** - Move to Done and merge

4. **Request changes** - Add instructions via `HUMAN_INPUT.md`

 

---

 

#### **Stage 6: Done (Merged)**

 

Task is merged to main branch. The suggestion service is now available:

 

```python

# Usage in other parts of the codebase

from services import SuggestionService

 

async def enhance_coder_context(project_dir: Path, target_file: str):

    suggestions = SuggestionService(project_dir)

    await suggestions.initialize()

   

    result = await suggestions.get_patterns_for_file(target_file)

    if result.success:

        for suggestion in result.suggestions:

            print(f"Pattern: {suggestion.pattern_name}")

            print(f"From: {suggestion.source_file}")

            print(f"Confidence: {suggestion.confidence:.0%}")

```

 

---

 

### Creating Your Own Feature Request

 

Follow this checklist when creating new feature requests:

 

1. **Define Clear Title**: Make it specific and actionable

2. **Write Description**: Include the "what" and "why"

3. **Add Reference Files**: Drag & drop existing code patterns

4. **Specify Acceptance Criteria**: How will you know it's done?

5. **Consider Constraints**: What should NOT change?

6. **Select Model**: Choose appropriate agent profile (Auto/Balanced/Performance)

7. **Enable Human Review**: Toggle if you want to approve the plan first

 

The Kanban board will then:

- **Backlog** → Task created and waiting

- **Planning** → Planner Agent analyzes codebase, creates plan

- **In Progress** → Coder Agent implements subtasks

- **AI Review** → QA Agent validates against criteria

- **Human Review** → You test and approve

- **Done** → Merged to main branch

 

---

 

## Summary

 

DevFlow transforms AI coding from a chat experience into a managed workflow:

 

| Traditional AI Chat | DevFlow |

|--------------------|-----------.|

| You type, wait, manage | You define tasks, AI executes |

| Single-threaded | Up to 12 parallel agents |

| Forgets context | Persistent memory layer |

| Manual testing | Self-validating QA loop |

| Direct branch edits | Isolated worktrees |

| Merge conflict hell | AI-powered conflict resolution |

 

**The workflow becomes:**

1. **You** define the "what"

2. **AI** handles the "how"

3. **You** verify the result

 

---

 

### Flowchart Importer UI

 

The Flowchart Importer provides a dedicated frontend interface for importing Lucidchart XML files and generating code from visual designs. Access it from the sidebar by clicking **"Flowchart Importer"** (shortcut: `F`).

 

```

┌─────────────────────────────────────────────────────────────────┐

│               FLOWCHART IMPORTER UI                              │

├─────────────────────────────────────────────────────────────────┤

│                                                                  │

│  STEP 1: UPLOAD XML                                             │

│  ┌──────────────────────────────────────────────────────────┐  │

│  │  ┌────────────────────────────────────────────────────┐  │  │

│  │  │                                                    │  │  │

│  │  │     📄 Drop Lucidchart XML file here              │  │  │

│  │  │           or click to browse                       │  │  │

│  │  │                                                    │  │  │

│  │  └────────────────────────────────────────────────────┘  │  │

│  │                                                          │  │

│  │  Supported formats: Lucidchart XML, draw.io, mxGraph    │  │

│  └──────────────────────────────────────────────────────────┘  │

│                                                                  │

│  STEP 2: PREVIEW PARSED DATA                                    │

│  ┌──────────────────────────────────────────────────────────┐  │

│  │  Requirements: 3 extracted                               │  │

│  │    • Validate order details                              │  │

│  │    • Check inventory availability                        │  │

│  │    • Process payment                                     │  │

│  │                                                          │  │

│  │  Processes: 8 extracted                                  │  │

│  │    • Validate Order (inputs: OrderData)                  │  │

│  │    • Check Stock (inputs: ProductID)                     │  │

│  │    • Create Order Record (outputs: OrderID)              │  │

│  │                                                          │  │

│  │  Data Flows: 4 extracted                                 │  │

│  │    • READ on orders                                      │  │

│  │    • WRITE on inventory                                  │  │

│  │                                                          │  │

│  │  Code Patterns: 6 inferred                               │  │

│  │    • OrderService (SERVICE_CLASS)                        │  │

│  │    • OrderRepository (REPOSITORY)                        │  │

│  └──────────────────────────────────────────────────────────┘  │

│                                                                  │

│  STEP 3: CONFIGURE ENTITY MAPPINGS                              │

│  ┌──────────────────┐     ┌──────────────────┐                 │

│  │  Order           │ ──► │  Shipment        │                 │

│  └──────────────────┘     └──────────────────┘                 │

│  [+ Add Mapping]  [🪄 Auto-Suggest]                             │

│                                                                  │

│  Output Directory: [ generated/shipment          ]              │

│                                                                  │

│  STEP 4: GENERATE CODE                                          │

│  ┌──────────────────────────────────────────────────────────┐  │

│  │  ⏳ Generating code from flowchart...                     │  │

│  │  ████████████░░░░░░░░ 60%                                 │  │

│  │                                                          │  │

│  │  ✓ Parsing flowchart XML                                 │  │

│  │  ✓ Extracting patterns                                   │  │

│  │  → Generating service classes...                         │  │

│  │  ○ Creating repositories                                 │  │

│  │  ○ Writing model files                                   │  │

│  └──────────────────────────────────────────────────────────┘  │

│                                                                  │

│  STEP 5: REVIEW RESULTS                                         │

│  ┌───────────┐  ┌────────────────────────────────────────────┐ │

│  │ 📄 Files  │  │ # shipment_service.py                     │ │

│  │           │  │                                            │ │

│  │ services/ │  │ class ShipmentService:                     │ │

│  │  shipment │  │     def __init__(self, db):                │ │

│  │  validate │  │         self.db = db                       │ │

│  │           │  │                                            │ │

│  │ repos/    │  │     async def validate(self, data):        │ │

│  │  shipment │  │         # Generated from flowchart         │ │

│  │           │  │         return await self.repo.get(id)     │ │

│  │ models/   │  │                                            │ │

│  │  shipment │  │                                            │ │

│  └───────────┘  └────────────────────────────────────────────┘ │

│                                                                  │

│  [⬇ Download ZIP]  [✓ Apply to Project]  [📋 Copy All]         │

│                                                                  │

└─────────────────────────────────────────────────────────────────┘

```

 

#### Flowchart Importer Features

 

| Feature | Description |

|---------|-------------|

| **Drag & Drop Upload** | Drop XML files directly onto the upload area |

| **Multi-Format Support** | Lucidchart, draw.io, mxGraph XML formats |

| **Live Preview** | See extracted requirements, processes, and data flows |

| **Entity Mapping** | Map flowchart entities to new names |

| **Auto-Suggest** | AI suggests common entity mappings |

| **Progress Tracking** | Real-time generation progress |

| **Syntax Highlighting** | View generated code with highlighting |

| **Download/Apply** | Download as ZIP or apply directly to project |

 

#### Accessing the Flowchart Importer

 

1. Open DevFlow

2. Select your project from the sidebar

3. Click **"Flowchart Importer"** or press `F`

4. Follow the step-by-step wizard

 

#### Integration with Kanban Board

 

Generated code from the Flowchart Importer can be:

- Applied directly to your project

- Used as a starting point for a new Kanban task

- Combined with existing reference projects

 

---

 

*Documentation generated based on DevFlow v2.7.2*

*Last updated: January 7, 2026*

*Added: Reference-Based Code Generation feature (Section 21)*

*Added: Reference Code Examples & Product Requirements section with Kanban workflow examples (Section 22)*

*Added: Full Frontend UI for Reference Generator with step-by-step wizard*

*Added: Flowchart Importer UI for importing Lucidchart XML and generating code*

*Added: Reference Generator UI for reference-based code generation*

 



# Routing Learning Modernization Architecture

## Objective

Modernize the current Python/tkinter routing study application into a maintainable, interactive web app while preserving the existing educational content, quiz logic, and lab concepts.

## Current State

The application is a single-file desktop app with:

- Python logic in `app.py`
- routing question data in `questions.json`
- study material in `study_content.md`
- user settings and history in generated JSON files
- route visualizations and OSPF lab diagrams embedded in tkinter canvas code

This is functional, but it mixes concerns across data, UI, logic, simulation, and persistence.

## Design Goals

1. Keep the learning content as the source of truth.
2. Separate quiz logic from the UI.
3. Modernize the interface to a React + TypeScript web frontend.
4. Preserve the current feature set and scoring behavior.
5. Make the app easier to extend with more labs, analytics, and accessibility.

## Target Architecture

### 1. Presentation Layer

A React + TypeScript frontend using Vite.

Responsibilities:
- navigate between Study, Quiz, Lab, and History views
- render routing and OSPF visualizations
- manage user input and feedback states
- present explanations, hints, and results screens

Technology choices:
- React
- TypeScript
- Vite
- CSS Modules or Tailwind
- SVG or Canvas for visual labs

### 2. Application State Layer

A small state management layer for quiz flow and user session state.

Responsibilities:
- selected difficulty
- number of questions
- active question index
- selected answer
- score and progress
- review list and missed questions
- timer/attempt history

Recommended approach:
- React state for UI
- custom hooks for quiz flow and persistence
- simple reducer pattern for complex quiz transitions

### 3. Domain Logic Layer

A reusable logic module that owns the learning rules and scoring behavior.

Responsibilities:
- load question bank
- select random filtered questions
- score answers
- determine review list
- compute performance summaries
- calculate last-attempt history

This layer should not depend on tkinter or browser UI code.

### 4. Data Layer

The data layer manages the static assets and per-user data.

Static data:
- `questions.json`
- `study_content.md`
- route-lab scenario definitions
- OSPF-lab scenario definitions

User-generated data:
- settings
- score history
- review list

Recommended storage:
- localStorage for small app usage
- optional SQLite or IndexedDB for richer persistence later

### 5. Visual Lab Layer

A dedicated simulation/visualization layer for route behavior and OSPF concepts.

Responsibilities:
- render route tables and topology diagrams
- compute longest-prefix-match explanation
- highlight best path logic
- visualize OSPF area boundaries and roles
- show DR/BDR and LSA flow

Implementation approach:
- SVG for topology representations
- reusable components for nodes, edges, and route rows
- deterministic scenario data sourced from JSON

## Proposed Folder Structure

```text
Routing_Learning/
├── README.md
├── ARCHITECTURE.md
├── questions.json
├── study_content.md
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   ├── features/
│   │   ├── lib/
│   │   ├── types/
│   │   └── data/
│   ├── public/
│   ├── package.json
│   └── vite.config.ts
├── legacy/
│   └── app.py
└── scripts/
    └── migration-notes.md
```

## Component Breakdown

### App Shell
- top navigation
- tab or route-based navigation
- global settings panel
- app footer or status area

### Study View
- chapter-based study content
- searchable topics
- notion-like reading experience
- important concept callouts

### Quiz View
- difficulty selection
- question count selector
- progress indicator
- answer choices
- explanation panel
- hint toggle
- scoring summary

### Review View
- missed-question list
- retry button
- review persistence

### History View
- recent attempt log
- result percentage breakdown
- selected difficulty and timestamps

### Labs
- Route Lab: prefix matching visualizer
- OSPF Lab: area/DR/LSA infographic

## Data Model

```ts
interface Question {
  id: string;
  difficulty: 'easy' | 'medium' | 'hard';
  question: string;
  choices: string[];
  answer: string;
  explanation: string;
  hint?: string;
}
```

```ts
interface QuizSession {
  difficulty: string;
  questionCount: number;
  selectedQuestions: Question[];
  currentIndex: number;
  score: number;
  reviewList: string[];
}
```

## Migration Strategy

### Milestone 1: Extract Logic
- isolate scoring functions
- isolate question selection and review rules
- add automated tests

### Milestone 2: Build React Shell
- recreate navigation and layout
- port Study tab
- port Quiz tab
- port History tab

### Milestone 3: Port Labs
- rebuild Route Lab diagram in SVG
- rebuild OSPF Lab diagram in SVG
- keep the same scenarios and concepts

### Milestone 4: Polish and UX
- theme and motion polish
- accessibility improvements
- responsive layout

## Risks and Constraints

- The question bank is rich and should be treated as a core asset.
- Some desktop features such as `winsound` are platform-specific and should be replaced by browser-native audio or disabled on unsupported devices.
- The current project mixes UI and simulation logic; separating them will reduce long-term maintenance risk.

## Recommended Next Step

Create the first React app shell around the current quiz and study model, then port each feature incrementally. This gives an immediate modern interface while preserving the original learning content and logic.

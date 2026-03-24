# Mission Control Dashboard Proposal

## Overview
A Next.js dashboard app running on `localhost:3000` that provides real-time visibility into all OpenClaw agents, tasks, memories, and projects. The app reads directly from the brain/ folder and workspace files.

---

## Architecture

### Tech Stack
- **Framework:** Next.js 14+ (App Router)
- **Styling:** Tailwind CSS with custom color theme
- **Data Source:** Local filesystem (brain/ and workspace/)
- **Port:** 3000 (replaces or coexists with FocusChrist)

### Data Integration
The dashboard reads from:
- `brain/cortex/current-tasks.md` — Active tasks
- `brain/knowledge/projects/*.md` — Project files
- `brain/knowledge/me/identity.md` — Agent info
- `memory/*.md` — Daily memories
- `workspace/*.md` — Docs and configs

---

## Color Theme (from jesus.jpg)

| Name | Hex | Usage |
|------|-----|-------|
| Golden Yellow | `#E8C245` | Primary accent, highlights |
| Deep Ochre | `#B48C40` | Secondary accent, borders |
| Dark Brown | `#332314` | Card backgrounds |
| Warm Tan | `#9E7B5C` | Secondary backgrounds |
| Pale Beige | `#D9CBB6` | Text on dark, light sections |
| Near-Black | `#1A1108` | Page background |

---

## 7 Screens

### 1. Task Board (/)
**Purpose:** Kanban view of what each agent is working on

**Data Source:** `brain/cortex/current-tasks.md`

**Features:**
- Three columns: To Do | In Progress | Done
- Drag-and-drop cards
- Each card shows: task name, agent assignee, priority tag
- Auto-refresh every 30 seconds
- Add/edit tasks inline

**UI:** Dark cards on near-black background, golden accent borders

---

### 2. Calendar (/calendar)
**Purpose:** Visualize cron jobs and scheduled tasks

**Data Source:** 
- OpenClaw cron configs
- brain/knowledge/tools/automation.md

**Features:**
- Month view with colored dots for scheduled tasks
- Click day to see task details
- Show cron expression (e.g., "Daily 2am")
- Color-coded: Gold = critical, Ochre = normal, Tan = low priority

**UI:** Warm tan header, dark brown day cells

---

### 3. Projects (/projects)
**Purpose:** Track major projects and their progress

**Data Source:** `brain/knowledge/projects/*.md`

**Features:**
- Card grid of all projects
- Each card shows: project name, status badge, last updated, key milestones
- Click to expand project details
- Progress bar based on checked items in source file

**UI:** Grid layout, cards in dark brown with golden progress bars

---

### 4. Memories (/memories)
**Purpose:** Browse memories organized by day

**Data Source:** `memory/*.md`

**Features:**
- Calendar-style date picker on left
- Selected day's entries displayed on right
- Search across all memories
- Tags: work, personal, decisions, lessons
- Timeline view option

**UI:** Two-panel layout, beige text on dark

---

### 5. Docs (/docs)
**Purpose:** Searchable document library

**Data Source:** All `.md` files in workspace/

**Features:**
- Full-text search with highlighting
- Filter by: folder, date modified, type
- Preview pane for selected doc
- Recent docs section
- Quick links to: AGENTS.md, USER.md, SOUL.md, TOOLS.md

**UI:** Search bar prominent at top, results as clean cards

---

### 6. Team (/team)
**Purpose:** View all agents and sub-agents

**Data Source:** 
- `brain/knowledge/me/identity.md`
- `AGENTS.md` (workspace)
- brain/ knowledge/*/

**Features:**
- Agent cards with avatar placeholder, name, role
- Status indicator (active/idle)
- Mission statement display
- Sub-agent tree view
- Quick stats: tasks completed, uptime

**UI:** Card grid, golden borders for main agent

---

### 7. Office (/office)
**Purpose:** 2D visualization of where agents are "working"

**Data Source:** 
- Agent session logs
- brain/cortex/current-tasks.md

**Features:**
- Top-down office floor plan (simple CSS/SVG)
- Room nodes: Research Lab, Dev Corner, Meeting Room, Memory Hall, Data Center
- Agents represented as dots/icons in rooms
- Activity indicators (pulsing when active)
- Task stream sidebar showing what each agent is doing

**UI:** Dark brown floor, golden agent dots, ochre room outlines

---

## File Structure

```
focuschrist-website/
├── app/
│   ├── layout.tsx          # Root layout with theme
│   ├── page.tsx            # Task Board (/)
│   ├── calendar/
│   │   └── page.tsx        # Calendar
│   ├── projects/
│   │   └── page.tsx        # Projects
│   ├── memories/
│   │   └── page.tsx        # Memories
│   ├── docs/
│   │   └── page.tsx        # Docs
│   ├── team/
│   │   └── page.tsx        # Team
│   └── office/
│       └── page.tsx        # Office
├── lib/
│   └── brain.ts            # File reading utilities
├── tailwind.config.js      # Custom colors
└── package.json
```

---

## Key Implementation Details

### Brain Reader Utility (`lib/brain.ts`)
```typescript
// Core functions needed:
- readFile(path): string
- listFiles(dir, pattern): string[]
- parseMarkdownTasks(content): Task[]
- parseMarkdownProjects(dir): Project[]
- searchDocs(query): DocResult[]
```

### Styling
- Use CSS variables for theme colors
- Apply consistently via Tailwind config
- Dark mode default (theme is already dark)

### Performance
- Server-side reads (Next.js App Router)
- Static generation for docs (ISR every 60s)
- Client-side polling for real-time task updates

---

## Next Steps for Agent B

1. ✅ Validate this proposal
2. Create `focuschrist-website/app/` structure
3. Implement lib/brain.ts reader
4. Build screens in order: Task Board → Calendar → Projects → Memories → Docs → Team → Office
5. Add navigation sidebar
6. Test with real brain data
7. Deploy to localhost:3000

---

## Notes

- The dashboard should be beautiful AND functional — use the golden theme generously
- FocusChrist currently runs on 3000 — may need to coordinate port or run dashboard on different port
- All data is local filesystem — no external APIs needed
- Consider adding a simple "refresh" button per section

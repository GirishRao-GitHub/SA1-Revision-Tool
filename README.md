# SA1 Exam Study Resources

> **Git Repo:** `github.com/GirishRao-GitHub/SA1-Revision-Tool`

This folder contains comprehensive SA1 (Health and Care) exam preparation materials.

## Important Landing Page
- **`SA1ity_Check.html`** - Main revision tool hub (central dashboard for all SA1 tools)

### How SA1ity_Check.html Works

**Source File Mapping:**
| Source | JSON Files | Naming Pattern |
|--------|------------|----------------|
| IFoA | 18 files | `20XXXX.json` (YYYYMM format) |
| IAI | 26 files | `iai_YYYYMM.json` |
| SP1 | Ch00-Ch30 | `Ch##.json` |
| Assignment | X1-X6 | `X#.json` |
| SA1 PQ | SA1PQ02-26 | `SA1PQ##.json` |

**Loading Mechanism:**
- Lazy loading: files fetched only when user selects a source
- All data stored in `SITTINGS` object in memory
- Uses `fetch('data/' + filename)` to load JSON files

## Creating New Exam Sitting JSON Files

**Process:**
1. Provide QP + Solution PDFs from source location
2. Reference existing JSON from same institute as template
3. Create new JSON following the JSON creation instructions (see above)

**Naming Convention:**
| Institute | Pattern | Example |
|-----------|---------|---------|
| IAI | `iai_YYYYMM.json` | `iai_1125` (Nov 2025) |
| IFoA | `YYYYMM.json` | `202509` (Sep 2025) |

**Required JSON Structure:**
```json
{
  "label": "Sitting Label",
  "questions": {
    "Q1": { "marks": X, "question": "...", "themes": [], "parts": { ... } }
  }
}
```

**After creating JSON:**
- If new sitting not in SOURCE_FILES list, update `SA1ity_Check.html` to include it

## Available Data Files

### Practice Questions
- `iai_*.json` - IAI exam papers (38 sittings: 1106 to 1125)
- `20XXXX.json` - IFoA exam papers (26 sittings: 200604 to 202509)
- `SA1PQ*.json` - Additional practice questions (SA1PQ02-26)

### Revision Materials
- `SA1_Revision_Notes.json` - SA1 key revision topics
- `SP1_Revision_Notes.json` - SP1 key revision topics
- `Memory_Aids.json` - Mnemonics and记忆 aids

### Reference Materials
- `Topic_Frameworks.json` - Topic-based study frameworks
- `Unified_Syllabus.json` - Combined SA1/SP1 syllabus
- `Syllabus_Structure.json` - Syllabus breakdown by chapter
- `SP1_SA1_Map.json` - Maps SP1 topics to SA1 equivalents
- `Pillars_Hooks.json` - Key concepts and connections

### Chapter Materials
- `Ch08.json` to `Ch13.json` - Content by chapter

## How to Use

When answering exam questions:
1. Read relevant revision notes first
2. Search Topic_Frameworks for key concepts
3. Reference past paper examples for question patterns

The data folder is at: `G:\Girish\IAI\SP1 and SA1 Health and Care\Practice papers\Claude Widgets\data`

---

## JSON Exam File Creation Instructions

**Source location**: `G:\Girish\IAI\SP1 and SA1 Health and Care\SA1 Health and Care Advanced`

**IAI Exam Papers**: `SA1 Health and Care Advanced\SA1 IAI Exam Papers\`
- 2006-2016: `2006 - 2016\SA1 IAI Solutions 2006-2016.zip`
- 2017-2025: `2017 - 2025\SA1 IAI Question Papers 2017-2025\` + individual solutions

**IFoA Exam Papers**: `SA1 Health and Care Advanced\SA1 IFOA Exam Papers\`
- 2005-2018: `SA1 IFoA Solutions 2005-2018.zip`
- 2019-2025: `SA1 IFoA Solutions 2019-2025\` (individual examiner reports)

To upload a new exam sitting (QP + Solution):

1. **Reference**: Use an existing JSON file as template (same naming convention)
2. **Total marks**: Must equal 100 per sitting
3. **Marks allocation**: All questions/sub-questions must have marks (default to 1 if missing)
4. **Context handling**: Any context text before a sub-question = part of that sub-question
5. **Empty scenarios**: If question begins directly with sub-question → use "Refer question" in scenario
6. **Clean up**: Remove instructions, examiner comments, page footer/header, page numbers
7. **Extraction**: STRICTLY VERBATIM - NO PARAPHRASING
8. **Output**: Save to `data` folder with same naming convention as reference file
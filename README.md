# What Quarto Can Do — A Multi-Level Tutorial

A Quarto-based tutorial website aimed at lecturers and academic staff who want to learn what Quarto is and how to use it.
The tutorial is split into three independent levels — visitors self-select the one that fits them best — and is available in German, English, Swedish, Norwegian and Danish.

**Live site:** [erasmus-ctm.github.io/Quarto-Tutorial](https://erasmus-ctm.github.io/Quarto-Tutorial/)

---

## The three levels

| Level | Who it is for | Content |
|---|---|---|
| **Beginner** | Never seen a Quarto page before | An interactive showcase: live Python code, editable exercises, interactive graphs, quizzes, citations — to show what Quarto can produce |
| **Intermediate** | Wants to create their own Quarto documents | Step-by-step guides for building a website, an exercise sheet, and a book — with screenshots and a printable PDF cheatsheet per chapter |
| **Expert** | Already uses Quarto, wants to go deeper | Deep-dives into `.yml`, `.qmd`, `.css`, extensions, multilanguage projects, and a cheatsheet |

---

## Two axes: level and language

- **Level = folder.** Each level has its own pages (`Example Page`, `Getting Started`, `Tipps and Tricks`).
- **Language = block inside each file.** Every `.qmd` contains one block per language (`when-profile="deutsch"`, `"english"`, `"svenska"`, `"norsk"`, `"dansk"`). The titles of the other languages are given as `title-en:`, `title-sv:`, `title-no:`, `title-da:` in the header.
- **Translations:** the Swedish, Norwegian and Danish blocks were translated from the English ones and still need proofreading by native speakers.

Every build has one profile of each group active, e.g. `quarto render --profile int,english`.
The details are explained on the tutorial page *Multilanguage Projects*.

---

## Project structure

```
├── Qmd Files/
│   ├── Example Page/        ← Beginner showcase pages
│   ├── Getting Started/     ← Intermediate tutorial pages (incl. *_cheatsheet.qmd, rendered to PDF)
│   └── Tipps and Tricks/    ← Expert pages
├── Img Files/
│   └── Getting Started/     ← Screenshots used in the intermediate tutorial
├── Theme/
│   ├── morph_custom.scss    ← Light theme overrides
│   ├── slate_custom.scss    ← Dark theme overrides
│   └── pdf_cheatsheet.tex   ← LaTeX header the PDF cheatsheets render with
├── docs/
│   ├── index.html           ← Redirects to de/, en/, sv/, no/ or da/ by browser language (English as fallback)
│   ├── de/                  ← German: start page, beg/, int/, exp/
│   ├── en/                  ← English: start page, beg/, int/, exp/
│   └── sv/, no/, da/        ← Swedish, Norwegian, Danish (same structure)
├── _extensions/             ← Quarto extensions
├── _quarto.yml              ← Root config: the two profile groups
├── _quarto-beg.yml          ← Level configs: which pages are rendered
├── _quarto-int.yml
├── _quarto-exp.yml
├── _quarto-root.yml         ← Start page per language
├── _quarto-deutsch.yml      ← Language configs: titles, navbar, sidebars
├── _quarto-english.yml
├── _quarto-svenska.yml
├── _quarto-norsk.yml
├── _quarto-dansk.yml
├── sprache.lua              ← Turns title-en/-sv/-no/-da into the title in that language's build
├── navigation.html          ← Language and level switch in the navbar
└── build.py                 ← Renders all combinations and serves them locally
```

---

## Extensions used

| Extension | Purpose | Install |
|---|---|---|
| [`Erasmus-CTM/pyodide-interaktiv`](https://github.com/Erasmus-CTM/pyodide-interaktiv) | Python live in the browser, in a Web Worker: shared session per page, real `input()`, Matplotlib animations, Stop button, AI feedback | `quarto add Erasmus-CTM/pyodide-interaktiv` |
| [`Erasmus-CTM/py-exercise`](https://github.com/Erasmus-CTM/py-exercise) | Editable Python exercises with hidden tests | `quarto add Erasmus-CTM/py-exercise` |
| [`Erasmus-CTM/math-exercise`](https://github.com/Erasmus-CTM/math-exercise) | Exercises with symbolic/numeric answers, checked with SymPy | `quarto add Erasmus-CTM/math-exercise` |
| `jsxgraph` (version shipped in the math-exercise repository, based on [`jsxgraph-quarto`](https://github.com/jsxgraph/jsxgraph-quarto)) | Interactive mathematical graphs, also as answers to math-exercise exercises | comes with math-exercise |
| [`parmsam/quizdown`](https://github.com/parmsam/quarto-quizdown) | Interactive quizzes | `quarto add parmsam/quizdown` |

---

## Local preview

Requires [Quarto](https://quarto.org/docs/get-started/), Python 3 and, for the PDF cheatsheets, TinyTeX (`quarto install tinytex`) with the LaTeX language packages (`tlmgr install babel-german hyphen-german babel-swedish hyphen-swedish babel-norsk hyphen-norwegian babel-danish hyphen-danish`).

```bash
python build.py
```

This renders all twenty combinations (start page and three levels, in five languages) and serves them locally at `http://localhost:8000/`.

To render without starting the server:

```bash
python build.py --no-serve
```

---

## Status

- [x] Beginner — complete
- [x] Intermediate — complete
- [x] Expert — complete

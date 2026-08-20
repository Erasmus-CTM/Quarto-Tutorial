# What Quarto Can Do — A Multi-Level Tutorial

A Quarto-based tutorial website aimed at lecturers and academic staff who want to learn what Quarto is and how to use it.
The tutorial is split into three independent levels — visitors self-select the one that fits them best.

**Live site:** [erasmus-ctm.github.io/Quarto-Tutorial](https://erasmus-ctm.github.io/Quarto-Tutorial/)

---

## The three levels

| Level | Who it is for | Content |
|---|---|---|
| **Beginner** | Never seen a Quarto page before | An interactive showcase: live Python code, editable exercises, interactive graphs, quizzes, citations — to show what Quarto can produce |
| **Intermediate** | Wants to create their own Quarto documents | Step-by-step guides for building a website, an exercise sheet, and a book — with screenshots and a printable PDF cheatsheet per chapter |
| **Expert** | Already uses Quarto, wants to go deeper | Deep-dives into `.yml`, `.qmd`, `.css`, extensions, multi-language documents, and a printable cheatsheet |

---

## Project structure

```
├── Qmd Files/
│   ├── Example Page/        ← Beginner showcase pages
│   ├── Getting Started/     ← Intermediate tutorial pages (incl. *_cheatsheet.qmd)
│   └── Tipps and Tricks/    ← Expert pages
├── Img Files/
│   └── Getting Started/     ← Screenshots used in the intermediate tutorial
├── Theme/
│   ├── morph_custom.scss    ← Light theme overrides
│   ├── slate_custom.scss    ← Dark theme overrides
│   └── pdf_cheatsheet.tex   ← LaTeX template the PDF cheatsheets render with
├── docs/
│   ├── beg/                 ← Rendered beginner site
│   ├── int/                 ← Rendered intermediate site
│   └── exp/                 ← Rendered expert site
├── _extensions/             ← Quarto extensions (pyodide-interaktiv, py-exercise, math-exercise, jsxgraph, quizdown)
├── _quarto.yml              ← Root config: profile group definition, shared theme
├── _quarto-beg.yml          ← Beginner profile config
├── _quarto-int.yml          ← Intermediate profile config
├── _quarto-exp.yml          ← Expert profile config
└── preview.py               ← Local preview script
```

---

## Extensions used

| Extension | Purpose |
|---|---|
| [`Erasmus-CTM/pyodide-interaktiv`](https://github.com/Erasmus-CTM/pyodide-interaktiv) | Fork of `coatless-quarto/pyodide`: runs Python live in the browser in a Web Worker — cells share one Python session per page, real `input()`, Matplotlib animations, and safe infinite loops |
| [`Erasmus-CTM/py-exercise`](https://github.com/Erasmus-CTM/py-exercise) | Editable Python exercises with hidden tests |
| [`Erasmus-CTM/math-exercise`](https://github.com/Erasmus-CTM/math-exercise) | Editable exercises with symbolic/numeric answers, checked with SymPy |
| [`jsxgraph/jsxgraph`](https://github.com/jsxgraph/jsxgraph) | Interactive mathematical graphs |
| [`parmsam/quizdown`](https://github.com/parmsam/quizdown) | Interactive multiple-choice quizzes |

Each of these Extensions can be added via:  
`quarto add Gituser/Reponame` (as stated above) within the Quarto CLI.

---

## Local preview

Requires [Quarto](https://quarto.org/docs/get-started/) and Python 3.

```bash
python preview.py
```

This renders all three profiles and serves them locally at `http://localhost:8000/beg/index.html`.

To skip re-rendering (serve existing output only):

```bash
python preview.py --no-render
```


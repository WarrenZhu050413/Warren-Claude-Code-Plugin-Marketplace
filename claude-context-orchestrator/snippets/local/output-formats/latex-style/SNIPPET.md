---
name: "LaTeX Problem Set Writing Style"
description: "Warren's specific LaTeX writing style for problem set solutions - direct, minimal, first-person perspective with strategic redundancy"
---

# Warren's LaTeX Writing Style for Problem Sets

## Core Characteristics

### 1. First-Person Perspective
- **Always use "I"** (never "we")
- Examples:
  - "I construct a maximum-size matching..."
  - "I claim that for all $i$..."
  - "I assign the following weights..."

### 2. Direct and Minimal
- **No preamble or fluff**
- Start immediately with the solution approach
- **Avoid:**
  - "Let's consider..."
  - "First, we observe..."
  - "In this problem, we are asked to..."
- **Use instead:**
  - "I construct..."
  - "I use..."
  - Direct statements

### 3. Strategic Redundancy Phrases
Use these specific phrases for clarity:
- **"by definition"** - for obvious logical steps
- **"directly"** - when applying definitions/theorems straightforwardly
- **"by construction"** - when using previously established objects
- **"Therefore"** - for final conclusions
- **"Thus"** - alternative to therefore
- **"By Part~\ref{...}"** - referencing previous parts
- **"By [Theorem Name]"** - citing theorems

### 4. Mathematical Precision
- Use proper LaTeX notation: `$\cup M$`, `$\subseteq$`, `$\forall$`, `$\exists$`
- Let math speak for itself - no verbose explanations of notation
- **Inline math** when possible: "we have $\cup M_i \subseteq \cup M_{i+1}$"
- **Display math** for important equations:
  ```latex
  $$w(M^*) = \sum_{v \in \cup M^*} w(v)$$
  ```
- **align* environments** for multi-line definitions

### 5. Brief Justifications
- One-sentence explanations that give just enough reasoning
- Examples:
  - "This satisfies the paired constraint: $d_1$ donates because $p_1$ receives (from $d_3$)..."
  - "By Berge's Theorem, no augmenting path exists when the algorithm terminates"
  - "Therefore no vertex is removed from the set of matched vertices"

### 6. Clean Structural Elements

**Bold labels for sections:**
- `\textbf{Maximum-size matching:}`
- `\textbf{Iteration 1:}`
- `\textbf{Case 1:}`

**Case structure:**
```latex
Case 1: [description]
[reasoning]

Case 2: [description]
[reasoning]
```

**Clear paragraph breaks** between logical steps (but not excessive)

### 7. Proof Structure Template

```latex
I construct/prove [goal] using [method/algorithm/theorem].

[Brief description of approach in 1-2 sentences]

I claim that [key property].

[Verification of claim with direct reasoning]

Therefore [conclusion].
```

### 8. Algorithm References
- Reference by name: "MaxMatchingAugPaths algorithm from Lecture 14"
- Describe what it does briefly
- Don't reproduce pseudocode unless necessary

## What to Avoid

❌ **Don't use:**
- Verbose introductions
- Excessive formality (epsilon-delta style rigor)
- Over-explaining obvious steps
- "we" or passive voice
- Complicated LaTeX formatting (theorem boxes, fancy environments)
- Too many small paragraphs (but not wall-of-text either)

## Common Patterns

### Opening Sentences
```latex
I construct a maximum-size matching $M'$ using...
I assign the following weights...
I use the MaxMatchingAugPaths algorithm...
I prove this by induction on...
```

### Transitional Phrases
```latex
By Part~\ref{part:monotonicity}
By definition of augmenting path
By Berge's Theorem
By induction
Since $\cup M_w \subseteq \cup M^*$ and all vertex weights are non-negative
```

### Concluding Sentences
```latex
Therefore no matching simultaneously maximizes both...
Thus $M^*$ simultaneously maximizes both...
This shows $\cup M \subseteq \cup M'$.
By construction, $M^*$ is a maximum-size matching.
```

## Complete Example

```latex
I construct a maximum-size matching $M'$ using the augmenting path
algorithm from Lecture 14, but starting with $M_0 = M$ instead of
$M_0 = \emptyset$. The algorithm repeatedly finds augmenting paths
and flips edges along them to build a sequence of matchings
$M_0 = M, M_1, M_2, \ldots, M_k = M'$ where $M'$ is maximum
(by Berge's Theorem, no augmenting path exists when the algorithm
terminates).

I claim that for all $i$, we have $\cup M_i \subseteq \cup M_{i+1}$.

Consider an augmenting path $P = (v_0, v_1, \ldots, v_{2\ell})$
with respect to $M_i$. By definition of augmenting path, $v_0$ and
$v_{2\ell}$ are unmatched by $M_i$, so $v_0, v_{2\ell} \notin \cup M_i$.
All internal vertices $v_1, \ldots, v_{2\ell-1}$ are matched by $M_i$,
so $v_1, \ldots, v_{2\ell-1} \in \cup M_i$.

When I flip edges along $P$ to get $M_{i+1}$, the internal vertices
$v_1, \ldots, v_{2\ell-1}$ remain matched (just to different partners),
so $v_1, \ldots, v_{2\ell-1} \in \cup M_{i+1}$. The endpoints $v_0, v_{2\ell}$
become matched, so $v_0, v_{2\ell} \in \cup M_{i+1}$.

Therefore no vertex is removed from the set of matched vertices,
so $\cup M_i \subseteq \cup M_{i+1}$.

By induction, $\cup M = \cup M_0 \subseteq \cup M_1 \subseteq \cdots
\subseteq \cup M_k = \cup M'$, so $\cup M \subseteq \cup M'$.
```

## Style Summary

**Concise, precise, and flows naturally** while maintaining mathematical rigor.
Reads like someone who deeply understands the material explaining it clearly
and efficiently. Direct statements, brief justifications, proper notation,
and strategic use of redundancy phrases for clarity.

---

# Academic Paper PDF Generation

## Standard Pandoc Command

For academic papers meeting university formatting requirements (double-spaced, 1-inch margins, 12pt font):

```bash
pandoc input.md -o output.pdf --pdf-engine=pdflatex \
  -V geometry:margin=1in \
  -V fontsize=12pt \
  -V linestretch=2 \
  -V documentclass=article
```

**Key parameters:**
- `geometry:margin=1in` - Standard 1-inch margins on all sides
- `fontsize=12pt` - Standard academic font size
- `linestretch=2` - Creates double-spacing (required for most academic papers)
- `documentclass=article` - Basic article format

## Word Count to Page Ratio

With double-spacing, 12pt font, 1-inch margins:
- **~250-260 words per page**
- 1,800 words ≈ 7 pages
- 1,600 words ≈ 6-6.5 pages
- 1,400 words ≈ 5.5-6 pages

Use this to estimate cuts needed without regenerating PDF repeatedly.

## Page Count Verification (macOS)

Fast page count check without opening PDF:
```bash
mdls -name kMDItemNumberOfPages file.pdf
```

Combined with word count:
```bash
mdls -name kMDItemNumberOfPages file.pdf && wc -w file.md
```

## Academic Paper Editing Workflow

**Systematic approach for meeting length requirements:**

1. **Grammar/spelling fixes** - Get content stable first
2. **Citation format cleanup** - MLA/Chicago/APA consistency
3. **Generate initial PDF** - Check baseline
4. **Check page count + word count** - Assess distance from target
5. **Identify sections to condense** - Opening/closing examples, anecdotes, redundant transitions
6. **Iterative cuts** - Cut ~100-200 words at a time
7. **Verify with page count** - Regenerate PDF, check progress
8. **Final generation** - Once within range

**Tips for meeting length requirements:**
- Cut opening/closing examples first (preserve core argument)
- Condense anecdotal evidence
- Remove redundant transitions
- Tighten verbose explanations
- Check word count before regenerating PDF (faster iteration)

## MLA Citation Format (9th Edition)

**Period placement:**
- Period goes **AFTER** citation bracket: `"quote"[1].` ✓
- NOT before: `"quote."[1]` ❌

**Web essay format:**
```
Author. "Title." Website Name, Month Year, url.
```
Example:
```
Graham, Paul. "Before the Startup." Paul Graham, Mar. 2014, paulgraham.com/before.html.
```

**Book format:**
```
Author. Title. Publisher, Year.
```

**Anthology/Collection:**
```
Text. Translated by Translator. Collection Title, edited by Editors, edition, Publisher, Year, pp. X-Y.
```

**Common mistakes:**
- ❌ Using http:// or https:// in URLs (modern MLA omits)
- ❌ Period before citation bracket
- ❌ Inconsistent month abbreviations (use Mar., Sept., Dec., not March, September)
- ❌ Forgetting site name for web essays

## Common Formatting Requirements

| Requirement | LaTeX Variable | Value |
|------------|---------------|-------|
| Double-spaced | `linestretch` | `2` |
| 1-inch margins | `geometry:margin` | `1in` |
| 12pt font | `fontsize` | `12pt` |
| Standard article | `documentclass` | `article` |

## Example Workflow Session

```bash
# 1. Check current state
wc -w paper.md
# 1883 words

# 2. Generate PDF
pandoc paper.md -o paper.pdf --pdf-engine=pdflatex \
  -V geometry:margin=1in -V fontsize=12pt -V linestretch=2 \
  -V documentclass=article

# 3. Check pages
mdls -name kMDItemNumberOfPages paper.pdf
# 8 pages (need to get to 6-6.5)

# 4. Calculate needed cuts
# 8 pages × 250 words/page = ~2000 words
# Target: 1600 words
# Need to cut: ~300 words

# 5. Make edits, regenerate, verify
# ... iterative process ...
```

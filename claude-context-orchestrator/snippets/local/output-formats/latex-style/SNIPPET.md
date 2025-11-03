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

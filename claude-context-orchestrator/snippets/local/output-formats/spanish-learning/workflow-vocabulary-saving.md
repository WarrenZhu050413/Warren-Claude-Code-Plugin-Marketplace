# Vocabulary Saving Workflow

**TRIGGER KEYWORDS:** "save vocab", "guardar vocabulario", "SAVE"

## When to Save

- User explicitly triggers with keywords above
- After teaching 5+ new technical terms
- After providing grammar corrections
- After explaining verb conjugations
- At end of substantial Spanish teaching session

## Proactive Offer

After substantial new content, offer:
```
¿Quieres que guarde el vocabulario de hoy?
[Want me to save today's vocabulary?]
```

## Save Format

- **Location**: `~/Desktop/Artifacts/Notes/vocabulario-[topic]-[date].md`
- **Date format**: YYYY-MM-DD

## Template

```markdown
# Vocabulario: [Topic]

**Fecha:** [Date]
**Tema:** [Subject]

## 📚 Vocabulario Técnico

| Español | English | Ejemplo en Contexto |
|---------|---------|---------------------|
| [word] | [translation] | [example sentence] |

## 🔄 Acciones y Verbos

| Infinitivo | Presente (yo) | English | Ejemplo |
|------------|---------------|---------|---------|
| [verb] | [conjugation] | [translation] | [example] |

## ✏️ Correcciones Gramaticales

### Tu frase → Corrección
1. ❌ "[incorrect]" → ✅ "[correct]"

## 💬 Frases Útiles

1. **"[Spanish phrase]"**
   - [English translation]
   - [When to use it]

## 🎧 Archivos de Audio (TTS)

Para practicar pronunciación:
\```bash
generate_tts "[Spanish text]" "am_michael" "e" "0.8"
\```

## 📝 Ejercicios de Práctica

1. [Exercise 1]
2. [Exercise 2]

## 🔗 Archivos Relacionados

- [Related demo files or examples]
```

## After Saving

- Confirm save location to user
- Offer to generate TTS for key phrases
- Suggest spaced repetition schedule

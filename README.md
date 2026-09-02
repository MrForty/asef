# ASEF

Framework operativo modulare per far lavorare un agente di coding con un
processo ingegneristico ripetibile invece che a intuito.

ASEF **non è software**: è un insieme di documenti Markdown che un agente
carica progressivamente. Nessuna dipendenza, nessun build. Si copia nel
progetto su cui stai lavorando e si attiva con un prompt.

## Come si usa

1. Copia questa cartella nel progetto target come `asef/`.
2. Apri [prompt universale ASEF.txt](prompt%20universale%20ASEF.txt), compila
   il blocco `## Richiesta` in fondo e incolla tutto all'agente.
3. L'agente legge il kernel, classifica la richiesta, carica **solo** il modulo
   necessario e genera gli artefatti nel progetto.

Il primo output è sempre lo stesso blocco: route scelta, modulo attivo,
artefatti presenti o mancanti, capacità disponibili, prossima azione, gap
aperti.

## Cosa fa, in breve

- **Instrada** la richiesta su una delle sette route (`GREENFIELD`, `MODIFY`,
  `DIAGNOSE`, `IMPROVE`, `REUSE`, `REVIEW_ONLY`, `QA_ONLY`) e percorre solo i
  nodi che servono.
- **Non ti intervista.** Ogni incognita passa per una scala che deduce, ispeziona
  il codice e ricerca prima di chiedere; quello che resta arriva in un round
  unico di domande, ognuna con default consigliato.
- **Isola la ricerca** in contesti usa-e-getta: nel contesto di lavoro rientra
  solo la risposta compressa, etichettata e con fonte.
- **Scrive artefatti**, non conversazione: `PROJECT.md`, `SPEC.md`, `PLAN.md`,
  `STATE.md`, i task e il log delle decisioni sono la memoria autorevole.
- **Verifica su tre assi** — aderenza alla specifica, qualità ingegneristica,
  rischio — più un asse per ogni trait dichiarato, poi QA proporzionata al rischio.

## Struttura

| Percorso | Contenuto |
|---|---|
| [ASEF.md](ASEF.md) | Kernel: default, runtime, gap policy, trait, Definition of Done |
| [ROUTER.md](ROUTER.md) | Classificazione dell'intento e grafi delle route |
| [DECISION-ENGINE.md](DECISION-ENGINE.md) | Scala dell'incertezza, etichette, round unico di domande |
| [CONTEXT-MANAGER.md](CONTEXT-MANAGER.md) | Livelli di memoria, ordine di caricamento, compressione |
| [ARTIFACTS.md](ARTIFACTS.md) | Artefatti, ordine di autorità, quality gate |
| [modules/](modules/) | 11 nodi di workflow + `research`, invocato in place |
| [templates/](templates/) | Scheletri degli artefatti che il progetto target genera |
| [tools/](tools/) | Linter di coerenza (non fa parte del framework caricato) |

Il kernel completo costa circa 4.400 token; un modulo ne aggiunge 400-600.
È il vincolo che spiega lo stile: tabelle e imperativi, mai prosa.

## Verifica delle modifiche

I documenti si fanno promesse a vicenda — il `Next` di un modulo deve
concordare con i grafi del router, un trait dichiarato deve accendere rigore da
qualche parte, una riga obbligatoria di template non si cancella. Il linter
controlla queste invarianti:

```bash
python3 tools/asef_lint.py -v      # controlla le invarianti
python3 tools/test_asef_lint.py    # controlla che il linter le rilevi davvero
```

Entrambi girano in CI su ogni push. Nessuna dipendenza oltre a Python 3.11.

## Convenzioni

I documenti del framework sono in inglese, il prompt di attivazione è in
italiano: l'agente risponde nella lingua dell'utente ma i nomi di file, moduli,
route ed etichette (`FACT`, `INFERENCE`, `ASSUMPTION`, `DECISION`, `OPEN`)
restano invariati, perché sono contratti con i file.

Vedi [CLAUDE.md](CLAUDE.md) per le regole di editing e [CHANGELOG.md](CHANGELOG.md)
per la storia delle versioni.

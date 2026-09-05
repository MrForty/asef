# ASEF

Framework operativo modulare per far lavorare un agente di coding con un
processo ingegneristico ripetibile invece che a intuito.

ASEF **non è software**: è un insieme di documenti Markdown che un agente
carica progressivamente. Nessuna dipendenza, nessun build. Si copia nel
progetto su cui stai lavorando e si attiva con un prompt o con un blocco in
`AGENTS.md`.

## Come si usa

1. Copia questa cartella nel progetto target come `asef/`.
2. Apri [prompt universale ASEF.txt](prompt%20universale%20ASEF.txt), compila
   il blocco `## Richiesta` in fondo e incolla tutto all'agente.
3. L'agente legge il kernel, classifica la richiesta, carica **solo** il modulo
   necessario e genera gli artefatti nel progetto.

Per non incollare il prompt a ogni sessione, copia il blocco di
[templates/AGENTS.template.md](templates/AGENTS.template.md) nell'`AGENTS.md`
o `CLAUDE.md` del progetto: ogni agente che legge quel file riparte da
`STATE.md` con il framework attivo. Il blocco `## Richiesta` resta il modo per
consegnare un nuovo compito.

Il primo output è sempre lo stesso blocco: route scelta, modulo attivo,
artefatti presenti o mancanti, capacità disponibili, prossima azione, gap
aperti, azioni umane pendenti.

## Cosa fa, in breve

- **Instrada** la richiesta su una delle otto route (`GREENFIELD`, `MODIFY`,
  `DIAGNOSE`, `IMPROVE`, `REUSE`, `REVIEW_ONLY`, `QA_ONLY`, `RELEASE`) e
  percorre solo i nodi che servono.
- **Non ti intervista.** Ogni incognita passa per una scala che deduce, ispeziona
  il codice e ricerca prima di chiedere; quello che resta arriva in un round
  unico di domande, ognuna con default consigliato. Ciò che solo tu puoi fare,
  account, chiavi, DNS, arriva come un unico blocco di istruzioni.
- **Isola la ricerca** in contesti usa-e-getta, con profondità proporzionale a
  quanto costa tornare indietro: nel contesto di lavoro rientra solo la
  risposta compressa, etichettata e con fonte, registrata in `RESEARCH.md`.
- **Scrive artefatti**, non conversazione: `PROJECT.md`, `SPEC.md`, `PLAN.md`,
  `STATE.md`, i task, il log delle decisioni, il ledger di ricerca e
  `LEARNINGS.md` sono la memoria autorevole.
- **Verifica su tre assi** — aderenza alla specifica, qualità ingegneristica,
  rischio — più un asse per trait e un threat pass per ogni risk class toccata
  (`auth`, `payments`, `tenant`, `pii`, `migration`, `concurrency`), poi QA
  proporzionata al rischio, sulla superficie renderizzata quando c'è un browser.
- **Rilascia** solo su autorizzazione, fino al passo autorizzato: commit,
  pull request, merge, deploy con verifica post-rollout e rollback.

## Struttura

| Percorso | Contenuto |
|---|---|
| [ASEF.md](ASEF.md) | Kernel: default, runtime, gap policy, trait, risk class, controllo di versione, Definition of Done |
| [ROUTER.md](ROUTER.md) | Classificazione dell'intento e grafi delle route |
| [DECISION-ENGINE.md](DECISION-ENGINE.md) | Scala dell'incertezza, etichette, round unico di domande, azioni umane |
| [CONTEXT-MANAGER.md](CONTEXT-MANAGER.md) | Livelli di memoria, ordine di caricamento, contesti paralleli, compressione |
| [ARTIFACTS.md](ARTIFACTS.md) | Artefatti, ordine di autorità, freschezza dell'evidenza, quality gate |
| [modules/](modules/) | 12 nodi di workflow + `research`, invocato in place |
| [templates/](templates/) | Scheletri degli artefatti che il progetto target genera, più il blocco di attivazione per `AGENTS.md` |
| [tools/](tools/) | Linter di coerenza (non fa parte del framework caricato) |

Il kernel completo costa circa 5.700 token; un modulo ne aggiunge da 400 a
1.200. Il linter fa rispettare un tetto per file. È il vincolo che spiega lo
stile: tabelle e imperativi, mai prosa.

## Verifica delle modifiche

I documenti si fanno promesse a vicenda — il `Next` di un modulo deve
concordare con i grafi del router, un trait dichiarato deve accendere rigore in
ogni file che la tabella promette, una risk class deve avere il suo threat
pass, una riga obbligatoria di template non si cancella, il prompt deve
nominare le stesse route, trait ed etichette del kernel. Il linter controlla
queste invarianti:

```bash
python3 tools/asef_lint.py -v      # controlla le invarianti
python3 tools/test_asef_lint.py    # controlla che il linter le rilevi davvero
```

Entrambi girano in CI su push e pull request, su Linux e Windows. Su Windows
usa `python` al posto di `python3`. Nessuna dipendenza oltre a Python 3.11 o successivo.

Sono controlli strutturali: non provano il comportamento di un agente né la
sicurezza delle sue decisioni. Il budget è una stima caratteri / 4, non una
misura del tokenizer del modello.

## Convenzioni

I documenti del framework sono in inglese, il prompt di attivazione è in
italiano: l'agente risponde nella lingua dell'utente ma i nomi di file, moduli,
route, trait, risk class ed etichette (`FACT`, `INFERENCE`, `ASSUMPTION`,
`DECISION`, `OPEN`) restano invariati, perché sono contratti con i file.

Vedi [CLAUDE.md](CLAUDE.md) per le regole di editing e [CHANGELOG.md](CHANGELOG.md)
per la storia delle versioni.

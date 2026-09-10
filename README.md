# ASEF

**Agentic Software Engineering Framework** — un processo operativo modulare per
guidare agenti di coding nella creazione e modifica di web app, SaaS e siti web
professionali.

[![Consistency](https://github.com/MrForty/asef/actions/workflows/consistency.yml/badge.svg)](https://github.com/MrForty/asef/actions/workflows/consistency.yml)
![Version](https://img.shields.io/badge/ASEF-1.8-ff7354)
![License](https://img.shields.io/badge/license-MIT-3da639)
![Dependencies](https://img.shields.io/badge/runtime_dependencies-0-174a8b)
![Mode](https://img.shields.io/badge/default-AUTO%20%2B%20ECONOMY-102752)

![Panoramica di ASEF: progetti nuovi ed esistenti attraversano un percorso adattivo verso web app, SaaS e siti web](docs/assets/asef-overview.png)

ASEF non è un generatore di codice e non sostituisce l'agente. È un insieme di
documenti Markdown che gli fornisce un metodo: comprende la richiesta, sceglie
il percorso più corto, carica soltanto il contesto necessario, produce artefatti
verificabili e controlla il risultato prima del rilascio.

- Nessuna dipendenza di runtime.
- Nessun modello, IDE, plugin o provider obbligatorio.
- Funziona su progetti nuovi ed esistenti.
- Mantiene `AUTO` per l'autonomia e `ECONOMY` per contenere il contesto.
- Non pubblica, unisce o distribuisce nulla oltre l'autorizzazione ricevuta.

## Quando usarlo

| Obiettivo | Cosa fa ASEF |
|---|---|
| Nuova web app o SaaS | Chiarisce risultato e confini, definisce comportamento e architettura minima, divide il lavoro in incrementi verificabili |
| Nuovo sito professionale | Parte da pubblico e contenuti, definisce una direzione visiva specifica, verifica una pagina rappresentativa e completa la consegna web |
| Feature su un progetto esistente | Ricostruisce soltanto la baseline interessata, preserva stack e contratti, modifica il minimo necessario e controlla le regressioni |
| Bug | Riproduce il problema, individua la causa condivisa, applica la correzione più piccola e lascia una verifica eseguibile |
| Redesign | Distingue ciò che cambia da URL, contenuti, integrazioni e identità da conservare; confronta prima e dopo |
| Refactoring o debito tecnico | Richiede un limite reale e misurabile, evita astrazioni speculative e mantiene il comportamento esterno |
| Review o QA | Controlla specifica, qualità, rischio e risultato senza forzare modifiche o fasi inutili |

## Come funziona

![Flusso ASEF dalla richiesta al rilascio autorizzato](docs/assets/asef-flow.svg)

ASEF non obbliga ogni lavoro a percorrere tutte le fasi. Il router sceglie la
route e il punto di ingresso in base all'intento:

| Route | Quando entra in gioco | Percorso tipico |
|---|---|---|
| `GREENFIELD` | Prodotto o sito nuovo | discovery → product-scope → specification → planning → slicing → implementation → review → qa |
| `MODIFY` | Funzione o comportamento da modificare | specification? → planning? → slicing? → implementation → review → qa |
| `DIAGNOSE` | Bug, regressione o causa sconosciuta | diagnose → implementation → review → qa |
| `IMPROVE` | Refactoring o limite architetturale provato | architecture-improvement → planning? → implementation → review → qa |
| `REUSE` | Codice o componente esterno da integrare | reuse-integration → specification/planning? → implementation → review → qa |
| `REVIEW_ONLY` | Analisi senza modifiche | review → fine |
| `QA_ONLY` | Verifica di un risultato esistente | qa → fine |
| `RELEASE` | Commit, PR, merge o deploy autorizzato | qa? → ship → fine |

Il simbolo `?` indica una fase caricata solo quando serve. Se un controllo
fallisce, ASEF torna alla fase che deve correggere il problema, senza ripetere
l'intero percorso.

## Avvio rapido

### 1. Installa il framework nel progetto

Copia questa repository nella cartella `asef/` del progetto:

```text
progetto/
├── asef/
│   ├── ASEF.md
│   ├── ROUTER.md
│   ├── modules/
│   ├── guides/
│   └── templates/
├── AGENTS.md              # opzionale: attivazione permanente
├── PROJECT.md             # generato solo quando necessario
├── SPEC.md                # generato solo quando necessario
└── STATE.md               # stato compatto del lavoro
```

### 2. Scegli come attivarlo

**Attivazione occasionale.** Apri
[`prompt universale ASEF.txt`](prompt%20universale%20ASEF.txt), compila il
blocco finale `## Richiesta` e incolla l'intero file nell'agente.

**Attivazione permanente.** Copia il blocco di
[`templates/AGENTS.template.md`](templates/AGENTS.template.md) nel file di
istruzioni letto dal tuo agente, per esempio `AGENTS.md` o `CLAUDE.md`. Da quel
momento puoi inviare direttamente la richiesta; l'agente riparte da `STATE.md`
quando esiste.

**Attivazione con la skill `/asef`.** Installa
[`skills/asef/`](skills/asef/) nella cartella skill del tuo agente e scrivi
l'obiettivo dopo il comando. La skill compila il prompt universale e lo esegue,
senza incollare nulla a mano. Vedi [La skill `/asef`](#la-skill-asef).

| Metodo | Quando conviene | Cosa devi fare ogni volta |
|---|---|---|
| Prompt universale | Agent senza supporto alle skill, o quando vuoi rileggere il prompt prima di inviarlo | Compilare il blocco `Richiesta` e incollare il file |
| Blocco in `AGENTS.md` | Progetto singolo su cui lavori spesso | Scrivere la richiesta e basta |
| Skill `/asef` | Uso quotidiano su più progetti e più agent | Scrivere `/asef` seguito dall'obiettivo |

I tre metodi attivano lo stesso kernel e producono lo stesso comportamento.
Cambia soltanto quanto testo devi fornire tu.

### 3. Lascia che ASEF scelga il percorso

Con qualsiasi metodo di attivazione, il primo output (definito in
[`ROUTER.md`](ROUTER.md)) dichiara route, modulo attivo, artefatti, capacità
disponibili, prossima azione, gap e azioni umane. Non devi
scegliere manualmente moduli, stack o route se non vuoi imporli come vincolo.

## La skill `/asef`

La skill è la terza via di attivazione, ed è quella pensata per l'uso
quotidiano. Scrivi `/asef` seguito dall'obiettivo e il framework parte: non devi
più aprire il prompt universale, compilarlo e incollarlo.

### Che cosa fa, in concreto

`skills/asef/SKILL.md` è un file nel formato Agent Skills, lo stesso che leggono
Claude Code, Codex, Cursor, GitHub Copilot, Gemini CLI e altri agent. La skill
**non contiene una copia del framework**: sarebbe una seconda fonte di verità
destinata a divergere dal kernel. Fa quattro cose in sequenza.

1. **Individua il framework.** Cerca `asef/` nel progetto, poi il progetto
   stesso se è un clone di questa repository, poi una copia trasportata insieme
   alla skill. Se non trova nulla te lo dice e si ferma, invece di improvvisare
   il framework a memoria.
2. **Legge il prompt universale a runtime.** Apre
   [`prompt universale ASEF.txt`](prompt%20universale%20ASEF.txt) e ne compila
   soltanto il blocco finale `Richiesta`. Tutto ciò che precede il blocco esce
   identico all'originale, quindi il prompt resta l'unica fonte di verità.
3. **Traduce le tue parole nei campi del blocco.** L'obiettivo diventa
   `Richiesta`, i limiti che hai espresso diventano vincoli, ciò che escludi
   diventa non-goal, l'eventuale permesso di rilascio diventa
   `Autorizzazioni di rilascio`. Gli artefatti già presenti nel progetto li
   rileva da sola.
4. **Esegue il prompt.** L'agente riparte dal `Bootstrap`, legge il kernel,
   classifica la route ed emette il primo output esattamente come se il prompt
   lo avessi incollato tu.

Il punto delicato è il terzo. La skill scrive **solo ciò che hai detto** e
lascia vuoto tutto il resto. Un campo vuoto non è una mancanza da colmare di
iniziativa: è un gap, e la gap policy del kernel decide se dedurlo, cercarlo o
chiedertelo. Per lo stesso motivo la skill non concede mai un'autorizzazione di
rilascio che non hai espresso: senza indicazioni vale `nessuna`.

### Prerequisiti

- Python 3.11 o successivo, già richiesto dagli strumenti della repository.
- Un agent che legga le skill nel formato Agent Skills. Se il tuo non le supporta,
  usa `/asef prompt <obiettivo>` da un agent che le supporta e incolla il
  risultato, oppure invoca direttamente il generatore.
- Il framework raggiungibile: la cartella `asef/` nel progetto, oppure una
  copia trasportata dalla skill con `--bundle-framework`.

### Installazione

Due punti di partenza: prendere tutto da GitHub, se non hai ancora nulla in
locale, oppure usare la copia del framework che hai già nel progetto.

#### Da GitHub

Serve soltanto git e Python. Il comando scarica la repository pubblica in una
cartella temporanea e installa la skill insieme a una copia del framework:

```bash
git clone --depth 1 https://github.com/MrForty/asef.git /tmp/asef-install && \
python3 /tmp/asef-install/skills/asef/scripts/install.py --agent claude --user --bundle-framework && \
rm -rf /tmp/asef-install
```

**Sostituisci `claude` con il tuo agent.** Ogni agent cerca le skill in una
cartella diversa, quindi il valore di `--agent` decide dove finisce
l'installazione: con `claude` la skill arriva solo dove la cerca Claude Code. I
valori accettati sono `claude`, `codex`, `agents`, `cursor`, `copilot`,
`gemini` e `opencode`, elencati con i rispettivi percorsi nella
[tabella più sotto](#percorsi-per-agent); per un agent non compreso, usa
`--dest` con la sua cartella skill. Il comando `--list` li stampa senza
installare niente.

`--user` la rende disponibile in tutti i tuoi progetti e `--bundle-framework`
le fa portare con sé il framework, quindi `/asef` funziona anche dove non
esiste la cartella `asef/`. Fatta l'installazione la copia temporanea non serve
più e il comando la cancella.

Per installarla solo nel progetto corrente, sostituisci `--user` con
`--project .`. Per fissare una versione precisa invece dell'ultimo stato di
`main`, aggiungi al clone `--branch <tag>` con uno dei tag elencati nella
pagina [Releases](https://github.com/MrForty/asef/releases).

Su Windows lo stesso comando diventa, in PowerShell:

```powershell
git clone --depth 1 https://github.com/MrForty/asef.git $env:TEMP\asef-install
python $env:TEMP\asef-install\skills\asef\scripts\install.py --agent claude --user --bundle-framework
Remove-Item -Recurse -Force $env:TEMP\asef-install
```

Se preferisci non installare nulla nella cartella utente, clona la repository
dove vuoi e usa `--dest` con la cartella skill del tuo agent.

#### Da una copia locale

Se il framework è già in `asef/`, l'installatore è dentro di esso:

```bash
# livello progetto: la skill vale solo in questo progetto
python3 asef/skills/asef/scripts/install.py --agent claude

# livello utente: la skill vale in tutti i tuoi progetti
python3 asef/skills/asef/scripts/install.py --agent claude --user

# qualsiasi altro agent: indica tu la cartella delle skill
python3 asef/skills/asef/scripts/install.py --dest <cartella skill>

# elenca i percorsi noti senza installare nulla
python3 asef/skills/asef/scripts/install.py --list
```

Anche qui `claude` va sostituito con il tuo agent. In questo caso
`--bundle-framework` non serve: la skill trova `asef/` nel progetto. Su Windows
usa `python` al posto di `python3`.

#### Percorsi per agent

| `--agent` | Livello progetto | Livello utente |
|---|---|---|
| `claude` | `.claude/skills/asef` | `~/.claude/skills/asef` |
| `codex`, `agents` | `.agents/skills/asef` | `~/.agents/skills/asef` |
| `cursor` | `.cursor/skills/asef` | `~/.cursor/skills/asef` |
| `copilot` | `.github/skills/asef` | `~/.copilot/skills/asef` |
| `gemini` | `.gemini/skills/asef` | `~/.gemini/skills/asef` |
| `opencode` | `.opencode/skills/asef` | `~/.config/opencode/skills/asef` |

Sono i percorsi documentati da ciascun agent al momento della pubblicazione. Se
il tuo agent li cambia, o non è in elenco, usa `--dest` con la sua cartella:
l'installazione è la stessa, cambia solo la destinazione.

#### Opzioni dell'installatore

| Opzione | A cosa serve |
|---|---|
| `--agent NOME` | Agent di destinazione. Ripetibile, per installare in più agent con un comando |
| `--user` | Installa a livello utente invece che nel progetto corrente |
| `--project DIR` | Progetto di destinazione, quando non è la cartella corrente |
| `--dest DIR` | Cartella skill di un agent non in elenco |
| `--link` | Crea un collegamento invece di copiare: la skill segue gli aggiornamenti della repository |
| `--force` | Sostituisce un'installazione esistente |
| `--bundle-framework` | Copia il framework accanto alla skill |
| `--list` | Stampa i percorsi noti ed esce |

`--bundle-framework` è l'opzione che rende la skill davvero universale.
Installata a livello utente con il framework al seguito, `/asef` funziona anche
nei progetti che non hanno la cartella `asef/`, e `/asef init` te la crea quando
serve. Senza questa opzione la skill richiede che il framework sia già nel
progetto.

#### Verifica, aggiornamento e rimozione

Per verificare che l'agent la veda, scrivi `/asef status` in un progetto con
ASEF: risponde con lo stato corrente invece di iniziare un lavoro. In
alternativa controlla il framework direttamente:

```bash
python3 asef/skills/asef/scripts/asef_prompt.py scan
```

Stampa la cartella del framework, la versione del kernel, la versione dichiarata
dal prompt e gli artefatti trovati. È il primo comando da usare quando qualcosa
non torna.

Per aggiornare, riesegui l'installatore con `--force`. Per rimuovere la skill,
cancella la cartella `asef` dalla directory skill del tuo agent.

### Uso

| Comando | Effetto |
|---|---|
| `/asef <obiettivo>` | Compila il prompt e lo esegue. È il comando normale |
| `/asef prompt <obiettivo>` | Stampa soltanto il prompt e si ferma |
| `/asef init` | Installa il framework in `asef/` se manca |
| `/asef status` | Riassume `STATE.md` senza modificare nulla |

Non devi indicare se si tratta di creazione o di modifica: la route la sceglie
il router dalle evidenze, cioè dalla richiesta, dagli artefatti presenti e dal
codice. Un progetto vuoto porta a `GREENFIELD`, una modifica a un progetto
esistente a `MODIFY`, un difetto a `DIAGNOSE`, e così via.

#### Esempio: modifica di un progetto esistente

```text
/asef Aggiungi alla pagina fatture un filtro per stato e cliente, mantenendo lo stack attuale e senza redesign; poi apri una pull request
```

La skill costruisce questo blocco e lo consegna all'agent dentro il prompt
completo:

```
Richiesta: Aggiungi alla pagina fatture un filtro per stato e cliente

Contesto di prima mano:
- chi ha il problema:
- come lo risolve oggi:
- chi me l'ha chiesto, e cosa ha fatto (non cosa ha detto):
- come capisco che funziona:

Vincoli non negoziabili:
- mantenere lo stack attuale

Non-goal:
- redesign

Autorizzazioni di rilascio: pull request

Artefatti già esistenti: PROJECT.md, SPEC.md, STATE.md, README.md
```

Le quattro righe di contesto sono vuote perché non le hai dette. L'agente non le
inventa: prova a dedurle dagli artefatti e dal codice, e te ne chiede una solo
se blocca davvero lo scope. Gli artefatti in fondo non li hai elencati tu, li ha
rilevati la skill nel progetto.

#### Esempio: progetto nuovo

```text
/asef Realizza un sito per uno studio di architettura con portfolio e modulo di contatto funzionante, usando solo i contenuti che fornisco, senza area clienti
```

Route attesa `GREENFIELD`, con la guida
[Web Experience](guides/web-experience.md). L'autorizzazione di rilascio resta
`nessuna`, quindi il lavoro si ferma al risultato locale verificato.

#### Esempio: solo il prompt

```text
/asef prompt Correggi il menu mobile che non si chiude dopo la selezione
```

Stampa il prompt completo senza eseguirlo. Serve per rileggerlo prima di
avviare il lavoro, oppure per incollarlo in un agent che non supporta le skill.

#### Come esprimere vincoli, esclusioni e permessi

Non serve una sintassi speciale: scrivi in linguaggio naturale e la skill
riconosce le formule più comuni.

| Se scrivi | Finisce in |
|---|---|
| “mantenendo lo stack attuale”, “senza toccare le API”, “in italiano” | Vincoli non negoziabili |
| “senza redesign”, “niente area clienti”, “non migrare il database” | Non-goal |
| “poi committa”, “apri una pull request”, “fai il deploy” | Autorizzazioni di rilascio |
| “il problema ce l'hanno gli operatori”, “oggi esportano in Excel” | Contesto di prima mano |

Se vuoi imporre tu la route, dillo esplicitamente nell'obiettivo, per esempio
“trattalo come una diagnosi”. Il router accetta un vincolo dell'utente, ma non
lo indovina.

### Il generatore senza la skill

Lo stesso prompt si costruisce da riga di comando, utile per automazioni o per
agent senza supporto alle skill:

```bash
python3 asef/skills/asef/scripts/asef_prompt.py build --request "..." \
  [--who ...] [--today ...] [--asked ...] [--verify ...] \
  [--constraint ...]... [--non-goal ...]... \
  [--release commit|"pull request"|merge|deploy] \
  [--artifact ...]... [--spec PATH] [--route NOME] [--block-only]
```

I comandi disponibili sono `build` per generare il prompt, `scan` per
diagnosticare l'installazione e `init` per creare `asef/` in un progetto che non
ce l'ha.

### Se qualcosa non funziona

| Sintomo | Causa e rimedio |
|---|---|
| L'agent non riconosce `/asef` | Skill nella cartella sbagliata. Controlla con `--list` e reinstalla, oppure usa `--dest` |
| “no ASEF framework found” | Manca `asef/` nel progetto. Usa `/asef init`, oppure reinstalla la skill con `--bundle-framework` |
| Avviso sulla versione del kernel | Prompt e kernel dichiarano versioni diverse. In conflitto vince il kernel; allinea la copia del framework |
| L'agente fa domande che ritieni inutili | I campi di contesto sono vuoti e la risposta blocca lo scope. Fornisci il contesto nell'obiettivo |
| L'agente non committa o non pubblica | Nessuna autorizzazione di rilascio. Va detta esplicitamente: il silenzio non autorizza |

## Il prompt universale: cosa modificare

![Anatomia del prompt universale: la parte iniziale resta invariata e si compila soltanto il blocco Richiesta](docs/assets/prompt-anatomy.svg)

Modifica **soltanto il blocco `## Richiesta` in fondo al file**. Le sezioni
`Bootstrap`, `Contratti e capacità`, `Primo output` e `Lingua ed etichette`
attivano il framework e devono rimanere invariate.

```text
Richiesta: <una frase: cosa deve fare>

Contesto di prima mano:
- chi ha il problema:
- come lo risolve oggi:
- chi me l'ha chiesto, e cosa ha fatto (non cosa ha detto):
- come capisco che funziona:

Vincoli non negoziabili:
-

Non-goal:
-

Autorizzazioni di rilascio: <nessuna | commit | pull request | merge | deploy>

Artefatti già esistenti: <nessuno | elenco>
```

### Significato dei campi

| Campo | Cosa scrivere | Esempio breve |
|---|---|---|
| `Richiesta` | Il risultato concreto, espresso come comportamento osservabile | “Aggiungi un filtro combinabile alla lista fatture” |
| `chi ha il problema` | Persona o ruolo che userà il risultato | “Operatori amministrativi di piccole agenzie” |
| `come lo risolve oggi` | Procedura o alternativa realmente usata | “Esporta in Excel e filtra manualmente” |
| `chi me l'ha chiesto...` | Evidenza concreta, quando esiste | “Due operatori hanno mostrato il foglio usato ogni giorno” |
| `come capisco che funziona` | Segnale o prova osservabile | “I filtri funzionano insieme e rispettano la paginazione” |
| `Vincoli non negoziabili` | Limiti che l'agente non deve reinterpretare | Stack esistente, compatibilità API, lingua, piattaforma |
| `Non-goal` | Risultati esplicitamente fuori dallo scope | “Nessun redesign completo” |
| `Autorizzazioni di rilascio` | L'ultimo passo esterno consentito | `nessuna`, `commit`, `pull request`, `merge`, `deploy` |
| `Artefatti già esistenti` | Documenti canonici da leggere e aggiornare | `README.md`, `SPEC.md`, documentazione API, design system |

Un campo vuoto, omesso o marcato `?` viene trattato come un gap. L'agente prova
prima a dedurlo dagli artefatti, dal codice o da ricerca mirata. Fa una domanda
solo se la risposta cambia materialmente il prodotto o blocca un'azione sicura.

### Autorizzazioni di rilascio

Le autorizzazioni fissano il limite massimo:

| Valore | ASEF può arrivare fino a |
|---|---|
| `nessuna` | Risultato locale verificato; nessuna pubblicazione |
| `commit` | Commit locale sul branch di lavoro |
| `pull request` | Commit, push del branch e apertura o aggiornamento della PR |
| `merge` | Merge della PR dopo i controlli richiesti |
| `deploy` | Distribuzione e verifica post-rilascio secondo il piano |

In caso di dubbio usa `nessuna`. Il silenzio non concede autorizzazione.

## Esempi completi di prompt

Gli esempi mostrano come cambiare soltanto il blocco finale. Copiali e sostituisci
le parti specifiche del tuo progetto.

<details>
<summary><strong>Nuovo SaaS per agenzie di viaggio</strong></summary>

```text
Richiesta: Realizza un SaaS per piccole agenzie di viaggio che permetta di creare viaggi di gruppo, gestire partecipanti, posti disponibili e pagamenti ricevuti.

Contesto di prima mano:
- chi ha il problema: agenzie di viaggio con due o cinque operatori
- come lo risolve oggi: fogli Excel, messaggi WhatsApp e ricevute controllate manualmente
- chi me l'ha chiesto, e cosa ha fatto (non cosa ha detto): due agenzie mi hanno mostrato i fogli usati per seguire prenotazioni e pagamenti
- come capisco che funziona: un operatore crea un viaggio, registra un partecipante e vede immediatamente disponibilità e saldo

Vincoli non negoziabili:
- applicazione web responsive
- separazione completa dei dati tra agenzie
- interfaccia in italiano
- esecuzione locale tramite Docker

Non-goal:
- applicazione mobile nativa
- contabilità fiscale completa
- integrazione immediata con tutti i gateway di pagamento

Autorizzazioni di rilascio: pull request

Artefatti già esistenti: nessuno
```

Route attesa: `GREENFIELD`. ASEF chiarisce il primo risultato utile, crea la
specifica, sceglie l'architettura minima e realizza una prima slice completa.

</details>

<details>
<summary><strong>Nuovo sito professionale per uno studio di architettura</strong></summary>

```text
Richiesta: Realizza un sito professionale originale per uno studio di architettura, con portfolio dei progetti, servizi, profilo dello studio e richiesta di contatto funzionante.

Contesto di prima mano:
- chi ha il problema: potenziali clienti privati e aziende che devono valutare stile ed esperienza dello studio
- come lo risolve oggi: ricevono presentazioni PDF e fotografie tramite email
- chi me l'ha chiesto, e cosa ha fatto (non cosa ha detto): lo studio ha fornito fotografie, descrizioni di otto progetti e contatti reali
- come capisco che funziona: il visitatore comprende specializzazione e stile, consulta i progetti e invia una richiesta realmente ricevuta

Vincoli non negoziabili:
- usare esclusivamente testi, fotografie e dati verificati
- design editoriale contemporaneo coerente con i progetti dello studio
- accessibilità WCAG 2.2 AA come obiettivo
- ottima esperienza mobile
- nessuna dipendenza obbligatoria da servizi proprietari

Non-goal:
- area clienti
- e-commerce
- testimonianze, riconoscimenti o statistiche inventate
- animazioni decorative invasive

Autorizzazioni di rilascio: pull request

Artefatti già esistenti: cartella assets/, brief-studio.md, contenuti-progetti.md
```

Route attesa: `GREENFIELD`, con la guida
[Web Experience](guides/web-experience.md). ASEF definisce contenuti,
gerarchia e direzione visiva, verifica una pagina rappresentativa prima di
replicarla e controlla responsive, accessibilità, URL, metadata e form reali.

</details>

<details>
<summary><strong>Nuova feature in un SaaS esistente</strong></summary>

```text
Richiesta: Aggiungi alla pagina delle fatture un filtro combinabile per stato, cliente e intervallo di date, mantenendo paginazione e separazione dei dati tra tenant.

Contesto di prima mano:
- chi ha il problema: operatori amministrativi che gestiscono centinaia di fatture
- come lo risolve oggi: scorrono le pagine oppure esportano i dati e li filtrano in Excel
- chi me l'ha chiesto, e cosa ha fatto (non cosa ha detto): un operatore ha mostrato che esporta le fatture diverse volte al giorno
- come capisco che funziona: i filtri funzionano singolarmente e insieme, restano attivi durante la paginazione e non mostrano dati di altri tenant

Vincoli non negoziabili:
- mantenere stack e design system esistenti
- non modificare il formato delle API pubbliche
- preservare le modifiche locali non collegate
- applicare autorizzazione e tenant filtering sul server

Non-goal:
- riprogettazione completa della pagina fatture
- sostituzione del database
- modifica del processo di pagamento

Autorizzazioni di rilascio: pull request

Artefatti già esistenti: README.md, PROJECT.md, SPEC.md, documentazione API esistente
```

Route attesa: `MODIFY`, con la guida
[Existing Projects](guides/existing-projects.md). ASEF ricostruisce la
baseline interessata, mantiene i contratti esistenti e verifica filtri,
paginazione, autorizzazione e isolamento dei tenant.

</details>

<details>
<summary><strong>Redesign della homepage di un sito esistente</strong></summary>

```text
Richiesta: Ridisegna la homepage mantenendo contenuti verificati, URL, identità tipografica e modulo di contatto esistente; migliora gerarchia, responsive e presentazione dei progetti.

Contesto di prima mano:
- chi ha il problema: visitatori che non comprendono rapidamente servizi e progetti principali
- come lo risolve oggi: navigano diverse pagine prima di trovare le informazioni rilevanti
- chi me l'ha chiesto, e cosa ha fatto (non cosa ha detto): il proprietario ha fornito registrazioni di sessione e richieste ricevute tramite il modulo
- come capisco che funziona: la homepage comunica attività e progetti principali, funziona alle larghezze concordate e il modulo continua a consegnare realmente le richieste

Vincoli non negoziabili:
- conservare framework, URL pubblici e integrazioni
- riutilizzare font, fotografie e contenuti approvati
- mantenere funzionante il modulo di contatto
- documentare il confronto prima e dopo

Non-goal:
- modifica delle pagine interne
- migrazione del CMS
- riscrittura dei contenuti
- testimonianze o metriche non fornite

Autorizzazioni di rilascio: pull request

Artefatti già esistenti: README.md, design-system.md, content/, public/images/
```

Route attesa: `MODIFY`, con entrambe le guide condizionali. La baseline protegge
le parti fuori dallo scope; la review visiva controlla identità, contenuti,
responsive, accessibilità e funzionamento reale del contatto.

</details>

<details>
<summary><strong>Correzione di un bug in una web app esistente</strong></summary>

```text
Richiesta: Correggi il menu mobile che non si chiude dopo la selezione di una voce e aggiungi una verifica che impedisca la regressione.

Contesto di prima mano:
- chi ha il problema: utenti della web app su smartphone
- come lo risolve oggi: chiudono manualmente il menu prima di usare la pagina
- chi me l'ha chiesto, e cosa ha fatto (non cosa ha detto): il team ha fornito una riproduzione sul browser mobile
- come capisco che funziona: dopo la selezione il menu si chiude, il focus resta corretto e la navigazione continua

Vincoli non negoziabili:
- mantenere componenti e dipendenze esistenti
- preservare navigazione desktop e uso da tastiera

Non-goal:
- redesign della navigazione
- aggiornamento generale delle dipendenze

Autorizzazioni di rilascio: commit

Artefatti già esistenti: README.md, test/e2e/, src/components/navigation/
```

Route attesa: `DIAGNOSE`. L'assenza di artefatti ASEF non rende greenfield un
progetto già funzionante: l'agente riproduce il difetto, segue i chiamanti,
corregge la causa e verifica mobile, desktop e tastiera.

</details>

## Qualità dei siti: originalità senza “AI slop”

La guida [Web Experience](guides/web-experience.md) trasforma “crea un sito
originale” in criteri osservabili:

- composizione derivata da pubblico, contenuti e azione principale;
- gerarchia e copy basati su materiale reale;
- direzione visiva e token documentati una volta, poi riutilizzati;
- niente testimonianze, loghi, premi, metriche o successi inventati;
- gradienti, card, hero enormi e pill sono scelte motivate, non default;
- una vista rappresentativa verificata su larghezza stretta e ampia prima di
  moltiplicare il pattern;
- form e azioni collegati a destinazioni reali, con errori e successo visibili;
- accessibilità, performance e indicizzazione controllate solo quando
  applicabili e senza promesse non dimostrate.

Una dashboard privata non riceve lavoro SEO inutile. Una correzione locale non
attiva un redesign. Originalità non significa sacrificare chiarezza,
accessibilità o controlli familiari.

## Modifica sicura dei progetti esistenti

La guida [Existing Projects](guides/existing-projects.md) impone una
baseline limitata al flusso interessato:

1. Leggere istruzioni locali, stato Git, manifesti, lockfile e punto d'ingresso.
2. Tracciare chiamanti, componenti, API, permessi e storage pertinenti.
3. Eseguire i controlli minimi esistenti e separare difetti precedenti da nuove
   regressioni.
4. Registrare delta richiesto, invarianti da preservare, percorsi interessati,
   verifica e rollback.
5. Modificare il punto condiviso più piccolo e controllare almeno un consumatore
   adiacente materialmente diverso.

ASEF conserva stack, versioni, route, API, schema, permessi, contenuti e design
fuori dallo scope. Una migrazione, riscrittura o sostituzione di dipendenza deve
risolvere un limite provato e avere un percorso di ritorno.

## Architettura dei file

| Percorso | Responsabilità |
|---|---|
| [`ASEF.md`](ASEF.md) | Kernel: default, runtime, gap policy, trait, risk class, version control e Definition of Done |
| [`ROUTER.md`](ROUTER.md) | Classificazione dell'intento e grafi delle route |
| [`DECISION-ENGINE.md`](DECISION-ENGINE.md) | Gestione delle incertezze, assunzioni, domande e autorizzazioni |
| [`CONTEXT-MANAGER.md`](CONTEXT-MANAGER.md) | Caricamento progressivo, memoria, fallback delle capacità e compressione |
| [`ARTIFACTS.md`](ARTIFACTS.md) | Artefatti canonici, ordine di autorità, aggiornamento ed evidenze |
| [`modules/`](modules/) | Tredici procedure caricate soltanto quando il relativo trigger scatta |
| [`guides/`](guides/) | Checklist condizionali per esperienza web e progetti esistenti |
| [`templates/`](templates/) | Scheletri di PROJECT, SPEC, PLAN, STATE, TASK, decisioni, ricerca e learnings |
| [`examples/scenarios.md`](examples/scenarios.md) | Scenari per valutare il comportamento di un agente; non caricati nel runtime |
| [`tools/`](tools/) | Linter di coerenza e test di mutazione del framework |

Gli artefatti generati (`PROJECT.md`, `SPEC.md`, `PLAN.md`, `STATE.md`, task,
decisioni, ricerca e learnings) vivono nella radice del progetto target. I file
in `asef/templates/` restano modelli riutilizzabili.

## Consumo di contesto

ASEF usa un kernel piccolo e carica progressivamente un solo modulo, le sezioni
necessarie degli artefatti e, quando applicabile, una guida condizionale.

- Kernel completo: meno di 6.000 token stimati.
- Singolo modulo o guida: massimo 1.200 token stimati.
- Prompt universale: circa 1.200 token stimati.
- `STATE.md`: puntatore compatto, non copia di specifica e piano.
- Output di ricerca e contesti paralleli: rientrano soltanto come evidenze
  compresse.

Le stime usano caratteri ÷ 4: servono come limite comparativo, non rappresentano
il tokenizer esatto di ogni modello.

## Verifica del framework

ASEF è composto soprattutto da contratti Markdown. Il linter verifica che i
file continuino a concordare su struttura, route, moduli, trait, risk class,
template, guide, riferimenti, vocabolario, versione, README, skill e budget;
i test della skill verificano che il prompt generato sia il prompt universale
con il solo blocco `Richiesta` compilato:

```bash
python3 tools/asef_lint.py -v
python3 tools/test_asef_lint.py
python3 tools/test_asef_skill.py
python3 tools/release_notes.py --self-test
```

Su Windows usa `python` al posto di `python3`. I controlli girano in CI su
Linux e Windows e richiedono soltanto Python 3.11 o successivo.

Il linter dimostra coerenza strutturale; non dimostra che ogni modello seguirà
sempre il framework né certifica qualità estetica, sicurezza o accessibilità di
un progetto concreto. Gli scenari in [`examples/scenarios.md`](examples/scenarios.md)
servono a misurare questi aspetti con agenti e progetti reali.

## Versioni e release

La versione vive in un posto solo: `asef.version` nel kernel. Cambiarla
significa aggiornare tre file insieme, cioè [`ASEF.md`](ASEF.md), la riga
`kernel vX.Y` del prompt universale e una nuova voce in
[`CHANGELOG.md`](CHANGELOG.md). Il linter fallisce se i tre non concordano.

La pubblicazione segue quella dichiarazione invece di ripeterla. Il workflow di
release ricava tag, titolo e note da kernel e changelog, e si rifiuta di
pubblicare una versione che il kernel non dichiara o che il changelog non
descrive. Le note non si scrivono a mano: si corregge la voce del changelog e si
ripubblica.

| Come parte | Quando usarlo |
|---|---|
| Push di un tag `v*` | Rilascio normale dopo il bump della versione |
| Avvio manuale del workflow `release` | Ripubblicare le note corrette, o rilasciare una versione già presente su `main` |

Il tag porta tre componenti anche quando il kernel ne dichiara due: la versione
`1.8` diventa il tag `v1.8.0`.

## Principi essenziali

1. Deduci → verifica → chiedi.
2. Carica il minimo contesto sufficiente.
3. Patcha l'artefatto canonico; non creare riassunti concorrenti.
4. Riusa codice, piattaforma e dipendenze già presenti.
5. Implementa incrementi verticali osservabili.
6. Correggi la causa condivisa, non soltanto il sintomo segnalato.
7. Applica rigore proporzionato a impatto, rischio e reversibilità.
8. Non costruire lavoro speculativo.
9. Mantieni verifiche, sicurezza, accessibilità e integrità dei dati.
10. Rilascia soltanto entro l'autorizzazione ricevuta.

## Contribuire

Per contribuire, leggi [`CONTRIBUTING.md`](CONTRIBUTING.md), crea una pull
request focalizzata ed esegui entrambi i controlli. Mantieni ogni regola in un
solo file autorevole. Consulta anche il [codice di condotta](CODE_OF_CONDUCT.md)
e la [policy di sicurezza](SECURITY.md). La cronologia delle versioni è in
[`CHANGELOG.md`](CHANGELOG.md).

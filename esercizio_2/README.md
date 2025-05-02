# Visualizzazione Avanzata di OCR ed Entità su Immagini

## Versione Python

- **Python 3.8.18**

## Dipendenze Necessarie

Le seguenti librerie devono essere installate per eseguire il progetto:

- `Pillow (PIL)` — per la manipolazione e il disegno delle immagini.
- `math` — per calcoli geometrici.
- `json` — per il parsing dei dati.

## Scelte Progettuali

### Bounding Box OCR

- Le parole riconosciute tramite OCR sono rappresentate da **rettangoli vuoti** (solo bordo, senza riempimento), per evitare di coprire il testo sottostante.
- Il testo OCR viene visualizzato **sopra ogni parola**, con un'etichetta **blu su sfondo bianco semi-trasparente**, per migliorarne la leggibilità anche su sfondi complessi.

### Bounding Box delle Entità (Entities)

- I bounding box delle entità sono **raggruppati** in un unico box complessivo per ciascuna entità.
- Questi box sono disegnati **senza bordo**, ma con **riempimento colorato trasparente**, per distinguerli chiaramente dai box OCR.
- Una **legenda laterale** mostra i colori associati a ciascun tipo di entità, rendendo immediata l’identificazione.

### Gestione della Confidenza

#### Per l'OCR

La confidenza è rappresentata, tramite una legenda posizionata a destra dell'immagine dello scontrino, attraverso il **colore del bordo** dei bounding box:

- **Verde**: confidenza ≥ 90%
- **Giallo**: confidenza tra 70% e 90%
- **Rosso**: confidenza < 70%

#### Per le Entità

La confidenza è espressa con due modalità complementari:

1. **Valore numerico** riportato nella legenda accanto al nome di ciascuna entità.
2. **Forma geometrica** del bounding box:
   - **Rettangolo** per confidenza ≥ 90%
   - **Rombo** per confidenza tra 70% e 90%
   - **Stella** per confidenza < 70%

Questi accorgimenti grafici permettono di valutare rapidamente l'affidabilità del riconoscimento, senza dover consultare direttamente i dati numerici.

## Benefici della Visualizzazione in Produzione

In un contesto produttivo, questa visualizzazione rappresenta uno strumento concreto per migliorare la comprensione e la validazione dei risultati generati dai modelli OCR.

Annotare direttamente sull'immagine i bounding box delle parole e delle entità riconosciute consente di:

- Evidenziare chiaramente il legame tra i dati estratti e il documento originale.
- Facilitare le attività di **controllo**, **revisione** e **correzione**.
- Distinguere immediatamente le informazioni OCR da quelle estratte come entità, grazie all’utilizzo di **stili visivi differenziati**.

Inoltre, la rappresentazione visiva del **livello di confidenza**, tramite **colori** per l’OCR e **forme geometriche** per le entità, consente di evidenziare rapidamente eventuali anomalie o riconoscimenti a bassa affidabilità.

L’integrazione coerente di **forme, colori** e **legenda** rende la visualizzazione **chiara, intuitiva e leggibile**, risultando particolarmente efficace in scenari in cui sono richieste **accuratezza e rapidità di revisione**.
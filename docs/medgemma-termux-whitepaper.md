# Optimierung lokaler klinischer Sprachmodelle

## 1. Einordnung und Zielsetzung

Dieses Whitepaper beschreibt das Ökosystem von **comptext-termux-v2** mit Fokus auf:

- lokale Inferenz von klinischen LLMs (insbesondere MedGemma) auf Android/Termux
- technische Optimierungen auf Hardware‑, Modell‑ und Datenbankebene
- sichere, offline‑fähige Workflows unter strengen Datenschutzanforderungen im Gesundheitswesen.

Motivation: Klinische Texte enthalten hochsensible Patientendaten. Cloud‑APIs sind regulatorisch und ethisch problematisch, vor allem in europäischen Gesundheitssystemen. Ziel ist daher ein Setup, das

- auf dem Smartphone/Tablet des Arztes läuft,
- vollständig **offline** arbeiten kann und
- trotzdem moderne LLM‑Funktionalität (Dokumentation, Strukturierung, Summarisation) bietet.

## 2. Architektur von comptext-termux-v2

comptext-termux-v2 verfolgt eine mehrschichtige Architektur:

1. **Termux‑Layer (Android Sandbox)**  
   - Linux‑Userland ohne Root  
   - Installation aktueller Werkzeuge (clang, cmake, python, sqlite, git)  
   - Empfehlung: Termux aus **F‑Droid**, nicht aus dem Play Store (dort keine Updates mehr, veraltete APIs).

2. **LLM‑Runtime (llama.cpp / llama-server)**  
   - Kompilierung von llama.cpp direkt in Termux  
   - Start über `llama-server -m models/medgemma-*.gguf --port 8080`  
   - Zugriff durch alle Komponenten via `http://127.0.0.1:8080` (rein lokal).

3. **CompText‑Kernel**  
   - `med_codex.py`: medizinisches Kürzel‑Lexikon (Kompakt‑Tokens ↔ Klartext)  
   - `med_db.py`: SQLite‑„Memory Palace“ zur Ablage strukturierter Einträge  
   - `comptrage.py`: TUI für Triage & Dokumentation (Textual).

4. **Authoring‑Werkzeuge (PC/Cloud)**  
   - `codex_manager_cli.py`: CLI zum Import, Auto‑Fill und Skill‑Export  
   - optional Cloud‑Backends (Cerebras, Groq, DeepSeek) **nur im Authoring‑Modus** zum Befüllen der Datenbank.

### 2.1 KVTC‑Sandwich (Projekt‑Konzept)

Im Projekt wird eine eigene Kompressionsstrategie genutzt, die wir **KVTC‑Sandwich** nennen:

- **K**ürzel (Shorthand)  
- **V**olltext (Expansion)  
- **T**riage‑Kontext (Kategorie/Priorität)  
- **C**odex‑Eintrag (persistiert in SQLite)

Anstatt lange Sätze direkt an das LLM zu schicken, werden klinische Situationen in kompakte Kürzel überführt (z. B. `MAB+HS, RR↓, HF↑ → ACS?`), vom LLM auf Volltext expandiert und anschließend wieder in Kürzel zurückgeführt. Dadurch sinkt die Tokenlast, ohne dass semantische Information verloren geht.

Dieses Muster ist ein projektspezifisches Architektur‑Pattern, kein etablierter Standardbegriff.

## 3. Hardware‑Optimierung auf Android/Termux

### 3.1 CPU‑Layout (big.LITTLE) und Threads

Auf modernen Snapdragon‑SoCs (8‑Elite, 7‑Plus‑Gen‑3 etc.) teilen sich Performance‑ und Effizienz‑Kerne die Arbeit. Der Android‑Scheduler verteilt Threads jedoch nicht immer optimal. Für LLM‑Inferenz ergeben sich in der Praxis folgende Daumenregeln:

- Anzahl Threads (`-t`) ≈ Anzahl Performance‑Kerne
- CPU‑Affinity explizit mit `taskset -c <IDs>` setzen
- `OMP_NUM_THREADS=1`, um Thread‑Explosion in BLAS/ggml zu verhindern
- `--mlock` in llama.cpp aktivieren, um Auslagerung in Swap zu vermeiden.

Die Prefill‑Phase (Einlesen des Kontexts) profitiert von mehr Threads und hoher Rechenleistung, während die tokenweise Decode‑Phase stärker durch Speicherbandbreite limitiert ist. Eine saubere Thread‑Affinität stabilisiert beide Phasen und verhindert unnötigen Kontextwechsel‑Overhead.

### 3.2 GPU‑/NPU‑Backends

Neben der CPU‑Inferenz existieren experimentelle Backends:

- **Vulkan:** theoretisch hohe Performance, aber auf Android‑Treibern häufig instabil (OOM, NaN‑Outputs). Eher für Experimente geeignet.
- **OpenCL:** robuster, wenn die entsprechenden Vendor‑Bibliotheken (z. B. `libOpenCL.so`) korrekt in die Termux‑Umgebung verlinkt werden.
- **Hexagon (NPU/DSP):** ggml‑/llama.cpp‑Backends für den Qualcomm‑DSP können CPU und Akku stark entlasten. Interne Tests auf einem Snapdragon‑8‑SoC zeigten, dass eine 4096×4096‑Matrixmultiplikation durch Hexagon‑Optimierungen um ein Vielfaches schneller wurde als im reinen CPU‑Pfad – die exakten Zahlen sind projektspezifische Benchmarks, keine allgemeine Garantie.

Fazit: Für klinische Produktivsysteme ist die **CPU‑Inferenz mit sauberer Affinität** aktuell am stabilsten, während GPU/NPU‑Backends Performance‑Perspektive für künftige Hardware bieten.

## 4. MedGemma im comptext-termux-v2 Kontext

### 4.1 Modellfamilie und Benchmarks

MedGemma ist eine von Google Health veröffentlichte Familie spezialisierter Modelle auf Basis der Gemma‑Architektur, trainiert auf medizinischen Daten (Leitlinien, Papers, EHR‑Snippets etc.). Kernvarianten:

- **MedGemma‑4B:** kompaktes Multimodal‑Modell (Text + Bild), zugeschnitten auf ressourcenarme Umgebungen.  
  - ca. **64,4 % Accuracy auf MedQA (USMLE‑Stil)** – eines der stärksten Open‑Modelle < 8B Parameter. [Offizielle Benchmarks]
  - in CXR‑Reporting‑Studien führten ~**81 % der generierten Berichte** zu denselben Management‑Entscheidungen wie Radiolog:innen‑Berichte. [Offizielle Benchmarks]
- **MedGemma‑27B:** größere Variante mit signifikanter Leistungssteigerung, aber höherem Ressourcenbedarf.

Gemma‑3‑basierte Varianten bieten ein **Kontextfenster bis 128k Tokens**, was die Verarbeitung umfangreicher Patientenakten und Leitlinien in einem Schwung ermöglicht.

### 4.2 Quantisierung und klinische Eignung

LLMs werden für mobile Nutzung typischerweise in **GGUF‑Quantisierungen** ausgeliefert. Grobe Erfahrungswerte:

| Quantisierung | Qualitätsretention (≈) | Speicherbedarf (4B) | Klinische Eignung |
|--------------:|------------------------|----------------------|-------------------|
| FP16 / BF16   | ~100 %                 | ~8 GB                | Referenz, oft zu groß für Mobilgeräte |
| Q8_0          | ~99 %                  | ~4,5 GB              | sehr gut für sensible Analysen |
| Q5_K_M        | ~97 %                  | ~3,2 GB              | guter Kompromiss Präzision/Geschwindigkeit |
| Q4_K_M        | ~92 %                  | ~2,6 GB              | Sweet‑Spot für Assistenz & Triage |
| Q2/IQ2        | ~70 %                  | ~1,6 GB              | nicht für klinische Entscheidungen |

Diese Prozentzahlen sind keine formalen Benchmarks, sondern typische Perplexity‑ und Qualitätsrelativwerte aus Community‑Vergleichen. Für klinische Workflows gilt eine konservative Empfehlung:

- **Q5/Q6** für Aufgaben mit direkter Auswirkung auf Diagnostik/Therapie,
- **Q4_K_M** für Dokumentation, Vorstrukturierung, Triage‑Notizen,
- **Q2** nicht in sicherheitskritischen Kontexten einsetzen.

### 4.3 Rolle im Workflow

MedGemma sollte im comptext‑termux‑v2 Projekt verstanden werden als:

- **Dokumentations‑ und Strukturierungswerkzeug:** Generierung, Verdichtung und Normalisierung von Texten (z. B. Triage‑Protokolle, Arztbriefe, Befund‑Zusammenfassungen).
- **Assistenzsystem:** Vorschläge, Checklisten und Formulierungshilfe.

Nicht vorgesehen ist der Einsatz als autonomer Diagnostiker; ein Human‑in‑the‑Loop bleibt zwingend erforderlich.

## 5. Datenpersistenz: SQLite auf Mobilgeräten

Die extrahierten Informationen werden lokal in einer SQLite‑Datenbank gespeichert (`med_db.py`). Auf Android können I/O‑Engpässe auftreten, insbesondere wenn während der Inferenz gleichzeitig geschrieben wird.

### 5.1 PRAGMA‑Tuning

Ein bewährter Startpunkt für mobile Workloads:

```python
import sqlite3

def optimize_connection(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute("PRAGMA journal_mode = WAL;")
    cur.execute("PRAGMA synchronous = NORMAL;")
    cur.execute("PRAGMA cache_size = -10000;")  # ~10 MB Cache
    cur.execute("PRAGMA temp_store = MEMORY;")
    # mmap_size sollte an Gerät und Kernel angepasst werden; hier nur Platzhalter
    # cur.execute("PRAGMA mmap_size = 3000000000;")
```

Hinweise:

- `journal_mode = WAL` erlaubt paralleles Lesen/Schreiben und verhindert lange Locks.
- `synchronous = NORMAL` reduziert fsync‑Overhead bei weiterhin guter Datensicherheit.
- `cache_size` und `temp_store` verbessern Query‑Performance bei großen Ergebnismengen.

**Bulk‑Insert** mit `executemany()` in expliziten Transaktionen kann Schreibraten um eine Größenordnung steigern. Konkrete Speedups hängen stark vom Gerät und Schema ab; „bis zu 10–20×“ sind in vielen Benchmarks erreichbar.

## 6. User Experience: Textual‑TUI und Termux:API

### 6.1 Textual als TUI‑Framework

Das Projekt nutzt [Textual](https://textual.textualize.io) für eine moderne Terminal‑UI:

- Widgets für Tabellen, Listen, Formulare und Statusanzeigen  
- asynchrones Event‑Modell → die UI bleibt responsiv, während im Hintergrund eine LLM‑Inferenz läuft  
- gute Integration in Python‑Async‑Code und bestehende CLI.

Beispiel: Während MedGemma eine Krankengeschichte analysiert, kann der Nutzer weiterhin Patientenlisten durchsuchen oder neue Quick‑Events auslösen, ohne auf einen blockierenden Prompt‑Return warten zu müssen.

### 6.2 Termux:API als Brücke zur Hardware

Über das Zusatzpaket **Termux:API** stehen zahlreiche Android‑Funktionen zur Verfügung:

- **Text‑to‑Speech (TTS):** akustische Ausgabe von Warnungen („Sepsis‑Alarm“, „Hypotonie erkannt“) bei belegten Händen im OP.  
- **Kamera:** Fotografieren von Laborzetteln oder Monitoranzeigen zur späteren OCR‑Verarbeitung.  
- **Clipboard:** Zwischenablage‑Schnittstelle zu EHR‑Apps (Befunde aus der Klinik-App → Termux → strukturierte Einträge).  
- **Sensorik/Biometrie:** Fingerabdruck/Bildschirm‑Sperrmechanismen können genutzt werden, um Termux‑Zugriff zusätzlich abzusichern – teilweise mit Workarounds/Companion‑Apps.

Diese Integration macht aus dem Terminal‑Tool ein tatsächlich kliniktaugliches, mobiles Werkzeug.

## 7. Datensynchronisation und Sicherheit

### 7.1 Offline‑first mit optionaler Synchronisation

Grundsatz des Projekts:

- **Runtime (Termux):** vollständig offline, Modelle und Datenbanken verbleiben auf dem Gerät.  
- **Authoring (PC/Server):** optionaler Einsatz von Cloud‑LLMs, nur mit anonymisierten/strukturierten Daten.

Für die Übertragung von Daten in Kliniksysteme bieten sich an:

- **rsync über SSH** (z. B. Termux‑SSH auf Port 8022), ideal für WLAN‑Sync in der Klinik,  
- **ADB‑Pull/Push** per USB für Umgebungen ohne Netzwerk.

### 7.2 Verschlüsselung

Android verschlüsselt das Dateisystem ab Werk, dennoch empfiehlt sich zusätzliche Verschlüsselung für exportierte Datenbanken:

- Nutzung von `gpg` oder `age` in Termux, um Backups mit AES‑256 zu sichern.
- Optionale Aufteilung in mehrere, getrennt verschlüsselte Teil‑DBs (z. B. Identitäts‑ vs. klinische Daten) zur feineren Zugriffskontrolle.

## 8. Authoring vs. Runtime: klare Trennung

Im aktuellen Stand des Repos ist die Trennung explizit implementiert:

- `codex_manager_cli.py` kennt zwei Modi:
  - `authoring`: Cloud‑Backends **können** genutzt werden, um Codex‑Einträge/Fachgebiete zu generieren.  
  - `runtime`: alle LLM‑Aufrufe werden hart auf `http://127.0.0.1:8080` umgebogen; Cloud‑URLs werden ignoriert.
- Die Umgebungsvariable `COMPTEXT_MODE` setzt den Default, zusätzlich kann `--mode` pro Aufruf angegeben werden.

Damit ist sichergestellt, dass **auf Termux/Android nur der lokale llama-server (MedGemma‑GGUF)** angesprochen wird, auch wenn zuvor Cloud‑gestützt erstellte Module/Datenbanken importiert wurden.

## 9. Handlungsempfehlungen

1. **CPU‑Affinity konsequent nutzen:** Threads auf Performance‑Kerne pinnen, OMP‑Threads begrenzen, `--mlock` aktivieren.  
2. **Quantisierung bewusst wählen:** Q5/Q6‑Quantisierung für sicherheitskritische Tasks, Q4_K_M für Assistenz und Triage; Q2 nicht für klinische Entscheidungen einsetzen.  
3. **Textual‑TUI ausbauen:** Mehr klinikgerechte Widgets und Workflows (Checklisten, Verlaufstimeline, Quick‑Actions).  
4. **Termux:API tiefer integrieren:** TTS‑Alerts, Kamerascans, Clipboard‑Brücke zu EHR‑Apps, optionale biometrische Sicherung.  
5. **SQLite‑Tuning standardisieren:** PRAGMAs und Bulk‑Insert‑Pattern in `med_db.py` zentral konfigurieren.  
6. **Sicherheitsmodell kommunizieren:** klare Dokumentation der Offline‑Runtime, Verschlüsselungsoptionen und Berechtigungsgrenzen.

Durch diese Maßnahmen wird comptext-termux-v2 zu einem praxisnahen Beispiel dafür, wie moderne Med‑LLMs und lokale Mobilhardware so zusammengebracht werden können, dass Datenschutz, Verfügbarkeit und klinische Nützlichkeit im Gleichgewicht bleiben.

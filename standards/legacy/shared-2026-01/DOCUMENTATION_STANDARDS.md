# DOCUMENTATION_STANDARDS.md — Standardy Dokumentacji Projektowej

**Wersja:** 1.0
**Data:** 2026-01-29
**Status:** Obowiązujący dla wszystkich projektów w workspace
**Powiązany dokument:** [DEVELOPMENT_STANDARDS.md](./DEVELOPMENT_STANDARDS.md) — sekcja 4 (skrócony przegląd)
**Szablony:** Zobacz `shared/standards/templates/`

---

## Spis treści

1. [Przegląd plików dokumentacyjnych](#1-przegląd-plików-dokumentacyjnych)
2. [CLAUDE.md — standard](#2-claudemd--standard)
3. [README.md — standard](#3-readmemd--standard)
4. [PRD.md — standard](#4-prdmd--standard)
5. [PROGRESS.md — standard](#5-progressmd--standard)
6. [CHANGELOG.md — standard](#6-changelogmd--standard)
7. [Zasady ogólne](#7-zasady-ogólne)

---

## 1. Przegląd plików dokumentacyjnych

### 1.1 Wymagane pliki

| Plik | Cel | Wymagany kiedy | Lokalizacja |
|------|-----|----------------|-------------|
| `CLAUDE.md` | Kontekst dla agenta AI | Zawsze | Korzeń projektu |
| `README.md` | Dokumentacja dla ludzi | Zawsze | Korzeń projektu |
| `docs/PROGRESS.md` | Bieżący stan prac | Zawsze | `docs/` |
| `docs/CHANGELOG.md` | Historia zmian | Po pierwszym releacie (≥ v0.1.0) | `docs/` |
| `docs/PRD.md` | Wymagania produktowe | Projekty > MVP / wieloetapowe | `docs/` |
| `docs/SCOPE.md` | Zakres In/Out/Future | Opcjonalny (może być sekcją w PRD) | `docs/` |
| `docs/ARCHITECTURE.md` | Architektura systemu | Projekty z ≥ 3 modułami | `docs/` |

### 1.2 Hierarchia dokumentów

```
CLAUDE.md          ← agent czyta PIERWSZY (samodzielny kontekst)
README.md          ← ludzie czytają PIERWSZY (opis, instalacja, użycie)
docs/
├── PROGRESS.md    ← co jest teraz (aktualizowany co sesję)
├── CHANGELOG.md   ← co się zmieniło (aktualizowany co release)
├── PRD.md         ← co ma być zbudowane (stabilny)
├── SCOPE.md       ← granice projektu (stabilny)
└── ARCHITECTURE.md ← jak jest zbudowane (aktualizowany przy zmianach arch.)
```

---

## 2. CLAUDE.md — standard

### 2.1 Cel

Agent AI powinien zrozumieć projekt po przeczytaniu **samego** CLAUDE.md, bez konieczności czytania 5+ innych plików. CLAUDE.md to jedyny plik, który agent czyta automatycznie na starcie sesji.

### 2.2 Wymagane sekcje

#### Sekcja 1: Opis projektu

1-3 zdania: co to jest, do czego służy, jaki problem rozwiązuje.

```markdown
## Opis projektu

Hydrolog — biblioteka Python do obliczeń hydrologicznych. Generuje hydrogramy
odpływu metodą SCS-CN, oblicza parametry morfometryczne zlewni, interpoluje
opady. Używana jako dependency przez Hydrograf.
```

#### Sekcja 2: Środowisko

Python, lokalizacja venv, zmienne środowiskowe, Docker (jeśli dotyczy).

```markdown
## Środowisko Python

Używaj środowiska wirtualnego z `.venv`:
- Python: `.venv/bin/python`
- Pip: `.venv/bin/pip`

Zmienne środowiskowe:
- `DATABASE_URL` — połączenie z PostgreSQL (tylko Hydrograf)
```

#### Sekcja 3: Dokumentacja do przeczytania

Priorytetyzowana lista — od najważniejszych. Agent czyta w tej kolejności, jeśli potrzebuje więcej kontekstu.

```markdown
## Dokumentacja

**Przeczytaj w kolejności:**
1. `docs/PROGRESS.md` — aktualny stan i zadania
2. `docs/SCOPE.md` — zakres projektu (co IN/OUT)
3. `docs/PRD.md` — wymagania produktowe
4. `docs/DEVELOPMENT_STANDARDS.md` → `shared/standards/DEVELOPMENT_STANDARDS.md`
```

#### Sekcja 4: Architektura / struktura modułów

Drzewo katalogów lub tabela z opisem modułów.

```markdown
## Struktura modułów

```
hydrolog/
├── runoff/          # SCS-CN, hydrogramy odpływu
├── morphometry/     # Parametry fizjograficzne zlewni
├── precipitation/   # Hietogramy, interpolacja opadów
├── network/         # Klasyfikacja sieci rzecznej
├── time/            # Czas koncentracji
├── cli/             # Interfejs wiersza poleceń
├── reports/         # Generowanie raportów
└── visualization/   # Wykresy
```
```

#### Sekcja 5: Komendy

Testy, linter, uruchomienie — kopiuj-wklej gotowe polecenia.

```markdown
## Komendy

```bash
# Testy
.venv/bin/python -m pytest tests/ -v

# Testy z pokryciem
.venv/bin/python -m pytest tests/ --cov=hydrolog --cov-report=html

# Linter
.venv/bin/python -m ruff check .

# Type checking
.venv/bin/python -m mypy hydrolog/
```
```

#### Sekcja 6: Workflow sesji

Co agent robi na start i na koniec sesji.

```markdown
## Workflow sesji

### Początek sesji
1. Przeczytaj `docs/PROGRESS.md` — sekcja "Bieżąca sesja"
2. `git status` + `git log --oneline -5`

### W trakcie sesji
- Commituj często (małe zmiany)
- Aktualizuj `docs/CHANGELOG.md` na bieżąco
- W razie wątpliwości — pytaj

### Koniec sesji
**OBOWIĄZKOWO zaktualizuj** `docs/PROGRESS.md`:
- Co zostało zrobione
- Co jest w trakcie (plik, linia, kontekst)
- Następne kroki
```

#### Sekcja 7: Specyfika projektu

Elementy unikalne: publiczne API, integracje z innymi projektami, ograniczenia, zewnętrzne źródła danych.

```markdown
## Specyfika projektu

### Zależności zewnętrzne
- **NumPy** — obliczenia numeryczne (wymagane)
- **Kartograf** — pobieranie NMT, pokrycia terenu, danych glebowych (opcjonalne)

### Integracje
- Hydrolog jest używany przez Hydrograf jako biblioteka obliczeniowa
- Hydrolog NIE zawiera funkcji pobierania danych — to zadanie Kartograf/IMGWTools
```

### 2.3 Anty-wzorce

**Anty-wzorzec: CLAUDE.md jako lista linków**

```markdown
<!-- ŹLE — 14 linii, zero kontekstu -->
## Środowisko Python
Używaj środowiska wirtualnego z `.venv`:
- Python: `.venv/bin/python`

## Dokumentacja
**Przed rozpoczęciem pracy przeczytaj:**
- `docs/IMPLEMENTATION_PROMPT.md`
- `docs/DEVELOPMENT_STANDARDS.md`
- `docs/PROGRESS.md`
```

Problem: agent nie wie co to za projekt, jaka architektura, jakie komendy. Musi przeczytać 3-4 pliki zanim zrozumie kontekst.

**Anty-wzorzec: CLAUDE.md jako kompletna specyfikacja (600+ linii)**

Problem: zbyt długi plik zużywa kontekst agenta. Szczegółowe API, wireframes, deployment — to należy do PRD.md lub ARCHITECTURE.md.

### 2.4 Optymalny rozmiar

| Rozmiar | Ocena | Przykład |
|---------|-------|---------|
| < 50 linii | Za mało — brak kontekstu | Kartograf (14), Hydrograf (14) |
| 100-300 linii | Optymalny | Hydrolog (106), SMW (120), BasicHydraulics (233) |
| 300-500 linii | Dopuszczalny dla złożonych projektów | IMGWTools (491) |
| > 500 linii | Za dużo — przenieś szczegóły do docs/ | DeBever (638) |

---

## 3. README.md — standard

### 3.1 Cel

Dokumentacja dla ludzi: deweloperów, użytkowników, współpracowników. Odpowiada na pytania: co to jest, jak zainstalować, jak używać.

### 3.2 Wymagana kolejność sekcji

```markdown
# Nazwa Projektu

Krótki opis (1-3 zdania).

## Status

Wersja, etap rozwoju, badge'e CI (jeśli są).

## Funkcjonalności

Lista kluczowych funkcji (bullets).

## Instalacja

```bash
pip install -e ".[dev]"
```

## Użycie / Quick Start

Minimalny przykład kodu lub polecenia CLI.

## Struktura projektu

Drzewo katalogów z komentarzami.

## Testy

Jak uruchomić testy.

## Dokumentacja

Linki do docs/ (PRD, SCOPE, ARCHITECTURE, CHANGELOG).

## Licencja / Autor

Licencja + dane autora.
```

### 3.3 Wytyczne

- **Język:** polski (chyba że projekt jest publiczny / anglojęzyczny)
- **Przykłady kodu:** krótkie, działające, kopiuj-wklej gotowe
- **Rozmiar:** 100-400 linii. Jeśli README > 400 linii, przenieś szczegóły API do `docs/` lub docstringów
- **Nie duplikuj** treści z CLAUDE.md — README jest dla ludzi, CLAUDE.md dla agenta
- **Sekcja Status** — podaj aktualną wersję i etap (MVP, beta, produkcja)

### 3.4 Różnica README vs CLAUDE.md

| Aspekt | README.md | CLAUDE.md |
|--------|-----------|-----------|
| Odbiorca | Człowiek (deweloper, użytkownik) | Agent AI (Claude Code) |
| Cel | Co to jest, jak zainstalować, jak używać | Jak pracować nad kodem |
| Workflow sesji | Nie | Tak (start/koniec sesji) |
| Architektura | Ogólny opis | Szczegółowa struktura modułów |
| Przykłady użycia | Tak (dla użytkownika końcowego) | Nie (komendy deweloperskie) |

---

## 4. PRD.md — standard

### 4.1 Cel

Definicja produktu: co ma być zbudowane, dla kogo, jakie są granice. Dokument stabilny — aktualizowany przy zmianie zakresu, nie co sesję.

### 4.2 Wymagane sekcje

```markdown
# PRD — Nazwa Projektu

## 1. Cel produktu

Co i dlaczego budujemy (2-5 zdań).

## 2. Zakres

### 2.1 In Scope
- Funkcjonalność A
- Funkcjonalność B

### 2.2 Out of Scope
- Co świadomie pomijamy i dlaczego

### 2.3 Future Scope (opcjonalne)
- Co może być dodane w przyszłych wersjach

## 3. Wymagania funkcjonalne

Opis funkcji systemu. Używaj JEDNEGO z dwóch formatów:

**Format A: User Stories**
- US-01: Jako [rola] chcę [akcja] żeby [cel]

**Format B: Feature Matrix**
| Funkcja | Status | Opis |
|---------|--------|------|
| Pobieranie NMT | ✅ Done | GUGiK API |

> Wybierz JEDEN format i stosuj konsekwentnie w projekcie.

## 4. Wymagania niefunkcjonalne

Wydajność, bezpieczeństwo, dostępność, kompatybilność.

## 5. Kryteria sukcesu

Mierzalne warunki, po których uznajemy produkt za gotowy.
```

### 4.3 SCOPE.md — kiedy osobny plik

| Sytuacja | Rekomendacja |
|----------|-------------|
| Prosty projekt (< 200 linii PRD) | Zakres jako sekcja 2 w PRD.md |
| Złożony projekt (> 300 linii PRD) | Osobny `docs/SCOPE.md` |
| Wiele faz / etapów | Osobny SCOPE.md z podziałem na fazy |

### 4.4 Język

PRD może być po polsku lub angielsku — ale konsekwentnie w całym pliku.

---

## 5. PROGRESS.md — standard

### 5.1 Cel

Bieżący stan prac. Aktualizowany **co sesję** przez agenta. Jedyny plik, który zmienia się przy każdej sesji roboczej.

### 5.2 Wymagane sekcje

```markdown
# PROGRESS — Nazwa Projektu

## Status projektu

| Element | Status | Uwagi |
|---------|--------|-------|
| Moduł A | ✅ Gotowy | v0.2.0 |
| Moduł B | 🔧 W trakcie | brakuje testów |
| Moduł C | ⏳ Zaplanowany | po module B |

## Checkpointy

### CP3 — Generowanie hydrogramu ✅
- Data: 2026-01-21
- Wersja: v0.3.0
- Zakres: SCS-CN + 42 scenariusze

### CP4 — CLI i cache 🔧
- Data: —
- Zakres: interfejs CLI, cache CN

## Ostatnia sesja

**Data:** 2026-01-29

### Co zrobiono
- Dodano moduł raportów (`reports/`)
- Naprawiono obliczanie CN dla grupy D (fix #12)
- 15 nowych testów (łącznie 610)

### W trakcie
- `src/visualization/charts.py:145` — brakuje obsługi pustych serii danych
- Branch: `feature/reports`

### Następne kroki
1. Dokończyć wizualizację pustych serii
2. Testy integracyjne dla raportów
3. Aktualizacja README.md

## Backlog

- [ ] Eksport do PDF
- [ ] Wsparcie dla danych godzinowych
- [ ] Optymalizacja pamięci dla dużych zlewni
```

### 5.3 Wytyczne

- **Sekcja "Ostatnia sesja"** — nadpisywana (nie dopisywana) przy każdej sesji
- **Checkpointy** — kumulatywne, nie usuwaj zakończonych
- **"W trakcie"** — podaj konkretny plik i linię, żeby następna sesja mogła kontynuować
- **Backlog** — lista zadań niezaplanowanych, porządkowana priorytetem

---

## 6. CHANGELOG.md — standard

### 6.1 Format

[Keep a Changelog 1.1.0](https://keepachangelog.com/pl/1.1.0/) + [Semantic Versioning 2.0.0](https://semver.org/).

### 6.2 Dozwolone sekcje zmian

| Sekcja | Kiedy używać |
|--------|-------------|
| `Added` | Nowa funkcjonalność |
| `Changed` | Zmiana istniejącej funkcjonalności |
| `Fixed` | Naprawa błędu |
| `Removed` | Usunięta funkcjonalność |
| `Deprecated` | Funkcjonalność oznaczona do usunięcia |
| `Security` | Poprawka bezpieczeństwa |

### 6.3 Przykład

```markdown
# Changelog

Wszystkie istotne zmiany w projekcie są dokumentowane w tym pliku.

Format oparty na [Keep a Changelog](https://keepachangelog.com/pl/1.1.0/).
Wersjonowanie zgodne z [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Moduł raportów z eksportem do HTML

## [0.3.0] - 2026-01-21

### Added
- Obsługa mozaiki NMT z wielu arkuszy
- Optymalizacja reverse trace (30% szybciej)

### Fixed
- Błąd obliczania CN dla gleb grupy D (#12)

### Changed
- Minimalna wersja NumPy: 1.26 → 2.0

## [0.2.0] - 2026-01-18

### Added
- Generowanie hydrogramu SCS-CN
- Integracja z Hydrolog v0.4.0
```

### 6.4 Wytyczne

- **Sekcja `[Unreleased]`** — zawsze obecna na górze, gromadzi zmiany do następnego releasu
- **Daty** w formacie ISO 8601: `YYYY-MM-DD`
- **Linki do porównań** (opcjonalne, na dole pliku):
  ```markdown
  [0.3.0]: https://github.com/user/repo/compare/v0.2.0...v0.3.0
  ```
- Wpisy pisz w czasie przeszłym dokonanym ("Dodano", "Naprawiono"), nie w bezokoliczniku

---

## 7. Zasady ogólne

### 7.1 Język

| Element | Język |
|---------|-------|
| Pliki `.md` (dokumentacja) | Polski |
| Docstrings w kodzie | Angielski |
| Komentarze w kodzie | Angielski |
| Commit messages | Angielski |

Wyjątek: projekty publiczne / anglojęzyczne mogą mieć dokumentację po angielsku.

### 7.2 Lokalizacja plików

```
projekt/
├── CLAUDE.md          # korzeń
├── README.md          # korzeń
└── docs/
    ├── PROGRESS.md
    ├── CHANGELOG.md
    ├── PRD.md
    ├── SCOPE.md
    └── ARCHITECTURE.md
```

### 7.3 Linkowanie

Używaj względnych ścieżek:

```markdown
<!-- DOBRZE -->
Zobacz [PRD](./docs/PRD.md) i [standardy](../../shared/standards/DEVELOPMENT_STANDARDS.md).

<!-- ŹLE -->
Zobacz [PRD](/Users/piotr/workspace/projects/Hydrolog/docs/PRD.md).
```

### 7.4 Referencja do wspólnych standardów

Projekty nie powinny duplikować treści z `shared/standards/`. Zamiast tego linkuj:

```markdown
## Standardy kodowania

Projekt stosuje [zunifikowane standardy deweloperskie](../../shared/standards/DEVELOPMENT_STANDARDS.md).

Specyficzne dla tego projektu:
- Coverage threshold: 90% (wyższy niż domyślne 80%)
- Dodatkowy linter: bandit (wymóg bezpieczeństwa)
```

### 7.5 Szablony

Szablony plików dokumentacyjnych dostępne w:

```
shared/standards/templates/
├── CLAUDE.md.template
├── README.md.template
├── PRD.md.template
├── PROGRESS.md.template
└── CHANGELOG.md.template
```

Przy tworzeniu nowego projektu skopiuj odpowiednie szablony i wypełnij.

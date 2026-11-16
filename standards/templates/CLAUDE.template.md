<!-- Szablon CLAUDE.md -->
<!-- Źródło: shared/standards/DOCUMENTATION_STANDARDS.md, sekcja 2 -->
<!-- Użycie: skopiuj do korzenia nowego projektu jako CLAUDE.md, wypełnij placeholdery -->
<!-- Docelowy rozmiar: 100-300 linii -->

# Instrukcje dla Claude Code

## Opis projektu

[NAZWA_PROJEKTU] — <!-- TODO: 1-3 zdania: co to jest, do czego służy, jaki problem rozwiązuje -->

## Środowisko Python

Używaj środowiska wirtualnego z `.venv`:
- Python: `.venv/bin/python`
- Pip: `.venv/bin/pip`

<!-- TODO: jeśli projekt używa innej lokalizacji venv (np. backend/.venv), zmień powyższe ścieżki -->

<!-- TODO: jeśli projekt wymaga zmiennych środowiskowych, dodaj sekcję:
Zmienne środowiskowe:
- `ZMIENNA` — opis
-->

## Dokumentacja

**Przeczytaj w kolejności:**
1. `docs/PROGRESS.md` — aktualny stan i zadania
2. `docs/PRD.md` — wymagania produktowe
3. `../../shared/standards/DEVELOPMENT_STANDARDS.md` — standardy kodowania

<!-- TODO: dodaj inne pliki dokumentacji specyficzne dla projektu -->

## Struktura modułów

```
[NAZWA_PROJEKTU]/
├── <!-- TODO: uzupełnij drzewo katalogów z komentarzami -->
```

## Komendy

```bash
# Testy
.venv/bin/python -m pytest tests/ -v

# Testy z pokryciem
.venv/bin/python -m pytest tests/ --cov=[NAZWA_PROJEKTU] --cov-report=html

# Linter
.venv/bin/python -m ruff check .

# Type checking
.venv/bin/python -m mypy [NAZWA_PROJEKTU]/
```

<!-- TODO: dodaj inne komendy specyficzne dla projektu (np. uruchomienie serwera, migracje) -->

## Workflow sesji

### Początek sesji
1. Przeczytaj `docs/PROGRESS.md` — sekcja "Ostatnia sesja"
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

## Git Workflow

### Gałęzie
- **main** — stabilna wersja (tylko merge z develop)
- **develop** — aktywny rozwój (ZAWSZE pracuj na tej gałęzi)

<!-- TODO: jeśli projekt używa innej strategii branchowania, zmień powyższe -->

## Specyfika projektu

### Zależności zewnętrzne

<!-- TODO: wymień kluczowe zależności z krótkim opisem:
- **NumPy** — obliczenia numeryczne (wymagane)
- **requests** — komunikacja z API (wymagane)
-->

### Integracje

<!-- TODO: opisz powiązania z innymi projektami w workspace, np.:
- [NAZWA_PROJEKTU] jest używany przez Hydrograf jako biblioteka obliczeniowa
- [NAZWA_PROJEKTU] NIE zawiera funkcji pobierania danych — to zadanie Kartograf
-->

### Ograniczenia

<!-- TODO: opisz znane ograniczenia lub nietypowe zachowania, np.:
- Brak wsparcia dla danych godzinowych (tylko dzienne)
- Maksymalny rozmiar zlewni: 500 km²
-->

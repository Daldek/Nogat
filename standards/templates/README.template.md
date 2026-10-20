<!-- Szablon README.md -->
<!-- Źródło: shared/standards/DOCUMENTATION_STANDARDS.md, sekcja 3 -->
<!-- Użycie: skopiuj do korzenia nowego projektu jako README.md, wypełnij placeholdery -->
<!-- Docelowy rozmiar: 100-400 linii -->

# [NAZWA_PROJEKTU]

<!-- TODO: 1-3 zdania opisujące projekt: co to jest, do czego służy, dla kogo -->

## Status

<!-- TODO: podaj aktualną wersję i etap rozwoju -->

- **Wersja:** 0.1.0
- **Etap:** MVP / beta / produkcja

## Funkcjonalności

<!-- TODO: lista kluczowych funkcji -->

- <!-- TODO: funkcjonalność 1 -->
- <!-- TODO: funkcjonalność 2 -->
- <!-- TODO: funkcjonalność 3 -->

## Instalacja

### Wymagania

- Python 3.12+

### Instalacja z repozytorium

```bash
git clone <!-- TODO: URL repozytorium -->
cd [NAZWA_PROJEKTU]
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Użycie

### Quick Start

<!-- TODO: minimalny przykład kodu lub polecenia CLI -->

```python
# Przykład użycia jako biblioteka
```

```bash
# Przykład użycia CLI (jeśli dotyczy)
```

## Struktura projektu

```
[NAZWA_PROJEKTU]/
├── <!-- TODO: uzupełnij drzewo katalogów z komentarzami -->
```

## Testy

```bash
# Uruchomienie testów
python -m pytest tests/ -v

# Testy z pokryciem
python -m pytest tests/ --cov=[NAZWA_PROJEKTU] --cov-report=html
```

## Dokumentacja

- [PRD — wymagania produktowe](./docs/PRD.md)
- [PROGRESS — stan prac](./docs/PROGRESS.md)
- [CHANGELOG — historia zmian](./docs/CHANGELOG.md)

<!-- TODO: dodaj linki do dodatkowych dokumentów jeśli istnieją (SCOPE, ARCHITECTURE) -->

## Licencja / Autor

<!-- TODO: podaj licencję i dane autora -->

**Autor:** <!-- TODO: imię i nazwisko / nazwa organizacji -->
**Licencja:** <!-- TODO: MIT / GPL / proprietary -->

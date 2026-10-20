# DEVELOPMENT_STANDARDS.md — Zunifikowane Standardy Deweloperskie

**Wersja:** 1.0
**Data:** 2026-01-29
**Status:** Obowiązujący dla wszystkich projektów Python w workspace
**Min. wersja Python:** 3.12

---

## Spis treści

1. [Git Workflow](#1-git-workflow)
2. [Conventional Commits](#2-conventional-commits)
3. [Code Review](#3-code-review)
4. [Dokumentacja projektowa](#4-dokumentacja-projektowa)
5. [Python — nazewnictwo](#5-python--nazewnictwo)
6. [Python — formatowanie (Ruff)](#6-python--formatowanie-ruff)
7. [Python — środowisko wirtualne](#7-python--środowisko-wirtualne)
8. [Python — struktura projektu (flat layout)](#8-python--struktura-projektu-flat-layout)
9. [Python — type hints](#9-python--type-hints)
10. [Python — docstrings](#10-python--docstrings)
11. [Python — testowanie](#11-python--testowanie)
12. [Python — obsługa błędów](#12-python--obsługa-błędów)
13. [Python — logging](#13-python--logging)
14. [Python — wydajność](#14-python--wydajność)
15. [Bezpieczeństwo](#15-bezpieczeństwo)
16. [Pre-merge checklist](#16-pre-merge-checklist)
17. [Rozszerzenia opcjonalne](#17-rozszerzenia-opcjonalne)

---

## CZĘŚĆ I: UNIWERSALNE

---

## 1. Git Workflow

### 1.1 Branching (Git Flow)

```
main              # Stabilna wersja (tylko merge z develop)
develop           # Aktywny rozwój (DOMYŚLNA GAŁĄŹ ROBOCZA)
feature/<nazwa>   # Nowe funkcjonalności
fix/<nazwa>       # Poprawki błędów
hotfix/<nazwa>    # Pilne poprawki produkcyjne (branch z main)
```

**Zasady:**
- `main` — tylko stabilny, przetestowany kod
- `develop` — integracja feature'ów, domyślna gałąź robocza
- `feature/*` — branch z `develop`, merge do `develop`
- `fix/*` — branch z `develop`, merge do `develop`
- `hotfix/*` — branch z `main`, merge do `main` i `develop`

### 1.2 Tagowanie

Tagi `v<X.Y.Z>` (SemVer) przy wydaniach:

```bash
git tag -a v1.0.0 -m "Release v1.0.0: initial stable release"
git push origin v1.0.0
```

Checkpointy robocze (CP) są śledzone tylko w `PROGRESS.md`, bez tagów Git.

### 1.3 Zasady commitów

- Każda logiczna zmiana = osobny commit
- Commituj często, małymi porcjami
- Łatwiejsze code review i rollback

---

## 2. Conventional Commits

### 2.1 Format

```
<type>(<scope>): <opis>

<body>           # opcjonalny

<footer>         # opcjonalny (np. Closes #12)
```

### 2.2 Typy

| Typ | Kiedy |
|-----|-------|
| `feat` | Nowa funkcjonalność |
| `fix` | Poprawka błędu |
| `docs` | Tylko dokumentacja |
| `test` | Dodanie/zmiana testów |
| `refactor` | Refaktoryzacja (bez zmian funkcjonalności) |
| `perf` | Optymalizacja wydajności |
| `style` | Formatowanie (nie wpływa na logikę) |
| `chore` | Config, dependencies, build |

### 2.3 Scope

Scope jest opcjonalny, ale zalecany. Używaj nazw modułów lub warstw projektu:

```bash
feat(runoff): add SCS-CN effective precipitation
fix(download): handle timeout in retry logic
docs(readme): update installation instructions
test(parser): add tests for edge cases
refactor(core): extract validation to separate module
```

---

## 3. Code Review

### 3.1 Proces

```
1. Deweloper tworzy PR
2. Automated checks (CI):
   ├─ Formatowanie (ruff format --check)
   ├─ Linting (ruff check)
   ├─ Type checking (mypy)
   └─ Testy (pytest --cov)
3. Manual review
4. Poprawki jeśli potrzeba
5. Approval → Merge
```

### 3.2 Co sprawdza reviewer

- **Poprawność** — czy kod działa zgodnie z wymaganiami?
- **Testy** — czy pokrywają nową logikę i edge cases?
- **Standardy** — zgodność z tym dokumentem
- **Czytelność** — czy kod jest zrozumiały bez nadmiernych komentarzy?
- **Bezpieczeństwo** — brak hardcoded secrets, walidacja inputu

### 3.3 Wymagania PR

- Wszystkie testy przechodzą
- Pokrycie kodu w normie (patrz sekcja 11)
- Brak błędów ruff / mypy
- Minimum 1 approval
- Brak konfliktów z target branch
- Dokumentacja zaktualizowana (jeśli potrzeba)

### 3.4 Czas odpowiedzi

- Standardowy PR: **24 godziny**
- Krytyczny PR (hotfix): **4 godziny**

---

## 4. Dokumentacja projektowa

### 4.1 Wymagana struktura

Każdy projekt powinien zawierać:

| Plik | Zawartość | Wymagany? |
|------|-----------|-----------|
| `README.md` | Opis, instalacja, użycie, testy | Tak |
| `CLAUDE.md` | Instrukcje dla Claude Code | Tak |
| `CHANGELOG.md` | Historia zmian (wg wydań) | Tak (projekty > v0.1) |
| `docs/PRD.md` | Product Requirements | Zalecany |
| `docs/SCOPE.md` | Zakres: IN / OUT / FUTURE | Zalecany |
| `docs/PROGRESS.md` | Bieżący stan i następne kroki | Zalecany |
| `docs/ARCHITECTURE.md` | Architektura systemu | Dla większych projektów |

### 4.2 Język

- **Pliki .md** — po polsku (chyba że projekt jest publiczny / anglojęzyczny)
- **Docstrings i komentarze w kodzie** — po angielsku
- **Commit messages** — po angielsku (scope i opis)

### 4.3 Szablon README.md

```markdown
# Nazwa Projektu

Krótki opis (1-2 zdania).

## Instalacja

​```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
​```

## Użycie

​```python
from modul import funkcja
result = funkcja(args)
​```

## Testy

​```bash
pytest tests/ --cov
​```
```

---

## CZĘŚĆ II: PYTHON — GŁÓWNY JĘZYK

---

## 5. Python — nazewnictwo

### 5.1 Konwencje

| Element | Konwencja | Przykład |
|---------|-----------|----------|
| Zmienne | snake_case + jednostka | `area_km2`, `time_min` |
| Funkcje | snake_case + czasownik | `calculate_cn()`, `fetch_data()` |
| Klasy | PascalCase | `WatershedDelineator` |
| Stałe | UPPER_SNAKE_CASE | `DEFAULT_TIMEOUT`, `MAX_RETRIES` |
| Pliki .py | snake_case | `sheet_parser.py` |
| Protected | `_prefix` | `self._cache` |
| Private | `__prefix` | `self.__internal_state` |

### 5.2 Jednostki w nazwach zmiennych

**ZAWSZE** dodawaj jednostkę do nazwy zmiennej fizycznej:

| Wielkość | Symbol | Przykład |
|----------|--------|----------|
| Powierzchnia | km2, m2 | `area_km2`, `cell_area_m2` |
| Długość | km, m | `length_km`, `elevation_m` |
| Opad | mm | `precipitation_mm` |
| Intensywność | mm_per_min | `intensity_mm_per_min` |
| Przepływ | m3s | `discharge_m3s` |
| Czas | min, s | `tc_min`, `duration_min` |
| Spadek | percent | `slope_percent` |

```python
# GOOD
area_km2 = 45.3
precipitation_mm = 38.5
discharge_m3s = 42.3

# BAD — unit ambiguity
area = 45.3       # km2 or m2?
rainfall = 38.5   # mm or cm?
```

### 5.3 Prefiksy semantyczne (zalecane)

| Prefiks | Znaczenie | Przykład |
|---------|-----------|----------|
| `calculate_*` | Obliczenie wyniku | `calculate_retention()` |
| `fetch_*` | Pobranie danych z API / sieci | `fetch_hydro_current()` |
| `download_*` | Pobranie pliku / archiwum | `download_sheet()` |
| `parse_*` | Parsowanie danych | `parse_daily_csv()` |
| `build_*` | Konstrukcja obiektu / URL | `build_hydro_url()` |
| `list_*` | Listowanie zasobów | `list_stations()` |

---

## 6. Python — formatowanie (Ruff)

### 6.1 Konfiguracja

```toml
# pyproject.toml
[tool.ruff]
target-version = "py312"
line-length = 88

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]

[tool.ruff.format]
quote-style = "double"
```

### 6.2 Komendy

```bash
# Formatowanie
ruff format src/ tests/

# Sprawdzenie (bez zmian)
ruff format --check src/ tests/

# Linting
ruff check src/ tests/

# Linting z auto-fix
ruff check --fix src/ tests/
```

### 6.3 Zasady formatowania

```python
# Line length: 88 characters
# Indentation: 4 spaces (NEVER tabs)

# GOOD — multi-line when exceeds 88 chars
def calculate_time_of_concentration(
    length_km: float,
    slope_percent: float,
    method: str = "kirpich",
) -> float:
    pass

# BAD — too long
def calculate_time_of_concentration(length_km: float, slope_percent: float, method: str = "kirpich") -> float:
    pass
```

### 6.4 Importy

```python
# Order: stdlib → third-party → local
# Alphabetical within groups
# Blank lines between groups
# Ruff sorts automatically (rule I)

from pathlib import Path
from typing import Any

import httpx
import numpy as np
from pydantic import BaseModel

from myproject.core import calculate_flow
from myproject.models import WatershedResult
```

---

## 7. Python — środowisko wirtualne

### 7.1 Dwa konteksty pracy

| Kontekst | Środowisko | Lokalizacja |
|----------|------------|-------------|
| Deweloper (człowiek) | venv w projekcie | `<projekt>/.venv/` |
| Agent AI (Claude Code) | Docker container | `/workspace/` mount |

### 7.2 Deweloper — lokalne venv

```bash
cd ~/workspace/projects/hydrograf
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
pip install -e ".[dev]"
```

**Zasady:**
- Każdy projekt ma własne `.venv/` (izolacja zależności)
- `.venv/` jest w `.gitignore`
- Używaj `pip install -e ".[dev]"` dla editable install

### 7.3 Agent AI — Docker

Agent pracuje w kontenerze z zamontowanym `/workspace/`:

```bash
docker run -v ~/workspace:/workspace agent-container
```

**Zasady:**
- Agent nie tworzy venv — używa środowiska kontenera
- Zależności projektu instalowane przez `pip install -e .`
- Agent ma dostęp tylko do zamontowanych katalogów

### 7.4 Uruchamianie testów

```bash
# Deweloper (z aktywnym venv)
pytest tests/

# Jawne wskazanie interpretera (bez aktywacji)
.venv/bin/python -m pytest tests/
```

---

## 8. Python — struktura projektu (flat layout)

### 8.1 Standardowa struktura katalogów

Projekty Python w workspace używają **flat layout** — kod źródłowy znajduje się
bezpośrednio w katalogu o nazwie pakietu, bez pośredniego `src/`.

Dlaczego flat layout: prostszy, mniej konfiguracji, wystarczający dla projektów
tej skali. Layout `src/` ma sens głównie w dużych projektach z wieloma pakietami.

```
projekt/
├── projekt/                # kod źródłowy (nazwa = nazwa pakietu)
│   ├── __init__.py
│   ├── core/               # główna logika
│   ├── cli/                # interfejs CLI (opcjonalnie)
│   └── utils/              # funkcje pomocnicze
│
├── tests/                  # testy
│   ├── conftest.py         # wspólne fixtures pytest
│   ├── fixtures/           # dane testowe (JSON, CSV, itp.)
│   ├── unit/               # testy jednostkowe
│   └── integration/        # testy integracyjne (opcjonalnie)
│
├── docs/                   # dokumentacja (szczegóły w DOCUMENTATION_STANDARDS.md)
│
├── examples/               # przykłady użycia (opcjonalnie)
│   └── README.md           # WYMAGANY jeśli folder istnieje
│
├── scripts/                # skrypty pomocnicze (opcjonalnie)
│
├── CLAUDE.md               # kontekst dla agenta AI
├── README.md               # dokumentacja dla ludzi
├── pyproject.toml          # zależności + konfiguracja narzędzi
├── .gitignore
└── .env                    # zmienne środowiskowe (NIE COMMITOWAĆ)
```

### 8.2 Zasady nazewnictwa katalogów

- Folder z kodem = nazwa pakietu w `snake_case`: `hydrolog/`, `imgw_tools/`
- Jeden pakiet per projekt (nie wiele pakietów w korzeniu)
- Nazwa folderu z kodem musi odpowiadać nazwie w `[project]` w `pyproject.toml`

### 8.3 Pliki wymagane vs opcjonalne

| Plik / folder | Wymagany? | Kiedy dodać |
|---------------|-----------|-------------|
| `projekt/` | Tak | Zawsze — kod źródłowy |
| `tests/` | Tak | Zawsze — testy (patrz sekcja 11) |
| `docs/` | Tak | Zawsze — PRD, PROGRESS, CHANGELOG |
| `CLAUDE.md` | Tak | Zawsze — kontekst dla agenta AI |
| `README.md` | Tak | Zawsze — dokumentacja dla ludzi |
| `pyproject.toml` | Tak | Zawsze — zależności i konfiguracja |
| `.gitignore` | Tak | Zawsze |
| `tests/fixtures/` | Zalecany | Gdy testy potrzebują danych (JSON, CSV) |
| `examples/` | Opcjonalny | Gdy projekt jest biblioteką używaną przez inne projekty |
| `scripts/` | Opcjonalny | Skrypty jednorazowe, migracje, narzędzia pomocnicze |
| `.env` | Opcjonalny | Tylko gdy projekt wymaga zmiennych środowiskowych |

### 8.4 Konfiguracja w pyproject.toml

Wszystkie narzędzia konfiguruj w jednym pliku `pyproject.toml`.
Nie twórz osobnych plików konfiguracyjnych (`setup.cfg`, `tox.ini`, `.flake8`, itp.).

```toml
[project]
name = "hydrolog"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "numpy>=2.0",
    "httpx>=0.27",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "ruff>=0.8",
    "mypy>=1.13",
]

[tool.ruff]
target-version = "py312"
line-length = 88

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]

[tool.ruff.format]
quote-style = "double"

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --tb=short"

[tool.mypy]
python_version = "3.12"
strict = true
```

### 8.5 Pliki .env

- `.env` — **NIE COMMITOWAĆ** (musi być w `.gitignore`)
- `.env.example` — **COMMITOWAĆ** (przykład bez wartości, jako dokumentacja)
- Używaj `.env` tylko gdy projekt wymaga zmiennych środowiskowych (API keys, baza danych, itp.)
- Jeśli projekt nie ma zewnętrznych sekretów — nie twórz `.env`

```bash
# .env.example — commitowany do repo
DATABASE_URL=
IMGW_API_KEY=
```

```bash
# .env — NIE commitowany, każdy deweloper tworzy własny
DATABASE_URL=postgresql://localhost:5432/hydro
IMGW_API_KEY=abc123
```

### 8.6 Standardowy .gitignore

Minimalny `.gitignore` dla projektu Python:

```gitignore
# Środowisko
.venv/
.env

# Python
__pycache__/
*.pyc
*.egg-info/
dist/

# Narzędzia
.coverage
htmlcov/
.mypy_cache/
.ruff_cache/
```

---

## 9. Python — type hints

### 9.1 Python 3.12+ style

```python
# GOOD — modern syntax
def process(items: list[str]) -> dict[str, int]:
    pass

def get_station(id: str | int | None = None) -> Station | None:
    pass

# BAD — legacy typing
from typing import List, Optional, Dict

def process(items: List[str]) -> Dict[str, int]:
    pass

def get_station(id: Optional[Union[str, int]] = None) -> Optional[Station]:
    pass
```

### 9.2 Wymagane wszędzie

Type hints są wymagane dla:
- Wszystkich argumentów funkcji publicznych
- Wartości zwracanych
- Atrybutów klas (dataclass / Pydantic)

```python
from numpy.typing import NDArray
import numpy as np

def generate_hydrograph(
    area_km2: float,
    cn: int,
    tc_min: float,
    hietogram: NDArray[np.float64],
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Generate runoff hydrograph."""
    pass
```

### 9.3 Type checking

```bash
mypy src/ --strict
```

---

## 10. Python — docstrings

### 10.1 Styl: NumPy, język: angielski

```python
def calculate_effective_precipitation(
    precipitation_mm: float,
    cn: int,
    ia_coefficient: float = 0.2,
) -> float:
    """
    Calculate effective precipitation using SCS-CN method.

    Parameters
    ----------
    precipitation_mm : float
        Total precipitation depth [mm].
    cn : int
        Curve Number (0-100).
    ia_coefficient : float, optional
        Initial abstraction coefficient, by default 0.2.

    Returns
    -------
    float
        Effective precipitation depth [mm].

    Raises
    ------
    ValueError
        If CN is not in range 0-100.

    Examples
    --------
    >>> calculate_effective_precipitation(38.5, 72)
    15.23
    """
    pass
```

### 10.2 Klasy

```python
class HydrographGenerator:
    """
    Generate runoff hydrograph using SCS-CN method.

    Parameters
    ----------
    area_km2 : float
        Watershed area [km²].
    cn : int
        Curve Number (0-100).

    Attributes
    ----------
    retention_mm : float
        Maximum retention [mm].

    Examples
    --------
    >>> gen = HydrographGenerator(area_km2=45.3, cn=72)
    >>> result = gen.generate(hietogram)
    """

    def __init__(self, area_km2: float, cn: int) -> None:
        pass
```

### 10.3 Komentarze inline

```python
# GOOD — explains "why", not "what"
# Kirpich formula requires length in meters
length_m = length_km * 1000

# Beta distribution better reflects real rainfall than block pattern
alpha, beta_param = 2.0, 5.0

# BAD — states the obvious
# Multiply by 1000
length_m = length_km * 1000
```

### 10.4 Tagi w komentarzach

```python
# TODO: Add caching for frequently used values
# FIXME: Handle edge case when CN > 100 (data error)
# HACK: Temporary workaround until module refactor
# NOTE: Algorithm follows SCS TR-55 (1986)
```

---

## 11. Python — testowanie

### 11.1 Progi pokrycia

| Warstwa | Wymagane pokrycie |
|---------|-------------------|
| Core logic (obliczenia, modele, parsery) | **≥ 80%** |
| CLI, utility, formatowanie wyjścia | **≥ 60%** |

```bash
pytest tests/ --cov=src/ --cov-report=html --cov-fail-under=80
```

**Przykładowy podział:**
- Core (80%): `src/calculations/`, `src/models/`, `src/parsers/`, `src/core/`
- Utility (60%): `src/cli/`, `src/formatters/`, `scripts/`

### 11.2 Struktura katalogów

```
tests/
├── unit/
│   ├── test_calculations.py
│   ├── test_models.py
│   └── test_parsers.py
├── integration/
│   └── test_full_pipeline.py
└── conftest.py
```

### 11.3 Nazewnictwo testów

```python
# Pattern: test_<function>_<scenario>[_<expected>]

def test_calculate_retention_typical_cn():
    """Test retention for typical CN value."""
    pass

def test_calculate_retention_cn_100_returns_zero():
    """Test that CN=100 returns zero retention."""
    pass

def test_calculate_retention_invalid_cn_raises():
    """Test that invalid CN raises ValueError."""
    pass
```

### 11.4 AAA Pattern (Arrange-Act-Assert)

```python
def test_kirpich_formula():
    # Arrange
    length_km = 8.2
    slope_percent = 2.3
    expected_tc_min = 68.5

    # Act
    result = ConcentrationTime.kirpich(length_km, slope_percent)

    # Assert
    assert abs(result - expected_tc_min) < 1.0  # ±1 min tolerance
```

### 11.5 Fixtures i mocking

```python
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def sample_watershed():
    """Fixture with sample watershed parameters."""
    return {"area_km2": 45.3, "cn": 72, "tc_min": 68.5}

def test_with_mocked_api(sample_watershed):
    """Test using fixture and mock."""
    with patch("myproject.client.fetch") as mock_fetch:
        mock_fetch.return_value = Mock(status_code=200)
        result = process(sample_watershed)
        assert result is not None
```

---

## 12. Python — obsługa błędów

### 12.1 Hierarchia wyjątków (wzorzec)

Każdy projekt definiuje własną hierarchię, ale wg tego schematu:

```python
# <project>/exceptions.py

class ProjectError(Exception):
    """Base exception for the project."""
    pass

class ValidationError(ProjectError):
    """Invalid input parameter."""
    pass

class CalculationError(ProjectError):
    """Error during computation."""
    pass

class NetworkError(ProjectError):
    """Network / external service error."""
    pass

class DataError(ProjectError):
    """Data parsing or format error."""
    pass
```

**Zasady:**
- Jeden bazowy wyjątek per projekt (np. `HydrologError`, `IMGWError`)
- Specyficzne podklasy dla różnych kategorii błędów
- Użytkownik może łapać bazowy wyjątek lub konkretny

### 12.2 Walidacja na wejściu

```python
def calculate_retention(cn: int) -> float:
    """Calculate maximum retention."""
    if not 0 <= cn <= 100:
        raise ValidationError(f"CN must be 0-100, got {cn}")

    if cn == 100:
        return 0.0
    return 25400 / cn - 254
```

---

## 13. Python — logging

### 13.1 Konfiguracja

```python
import logging

logger = logging.getLogger(__name__)
```

### 13.2 Poziomy logowania

```python
# DEBUG — development only, detailed trace
logger.debug("Parsing sheet: %s", godlo)

# INFO — normal operations
logger.info("Downloaded %s successfully", filename)

# WARNING — unusual but not an error
logger.warning("Retry %d/%d for %s", attempt, max_retries, url)

# ERROR — failure that doesn't crash the app
logger.error("Failed to fetch data: %s", exc)

# CRITICAL — app cannot continue
logger.critical("Configuration file not found")
```

### 13.3 Format

```python
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
```

**Uwaga:** Używaj `%s` formatting w loggerze (lazy evaluation), nie f-stringów.

---

## 14. Python — wydajność

### 14.1 Priorytet

```
Poprawność > Czytelność > Wydajność
```

Najpierw zrób działające, potem czytelne, na końcu szybkie (jeśli potrzeba).

### 14.2 NumPy vectorization

```python
import numpy as np

# GOOD — vectorized (fast)
def effective_precip(intensities: NDArray, cn: int) -> NDArray:
    P_cum = np.cumsum(intensities)
    S = 25400 / cn - 254
    Pe_cum = np.where(
        P_cum > 0.2 * S,
        (P_cum - 0.2 * S) ** 2 / (P_cum + 0.8 * S),
        0,
    )
    return np.diff(Pe_cum, prepend=0)

# BAD — Python loop (10-100x slower)
def effective_precip_slow(intensities, cn):
    results = []
    for i in intensities:
        results.append(compute(i))
    return results
```

### 14.3 Caching

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_cn_value(land_cover: str) -> int:
    """Cache for frequently used CN values."""
    return CN_TABLE.get(land_cover, 75)
```

### 14.4 HTTP requests

```python
# GOOD — reuse session for multiple requests
session = httpx.Client()
for url in urls:
    response = session.get(url, timeout=30)

# BAD — new connection each time
for url in urls:
    response = httpx.get(url)
```

### 14.5 Duże pliki — streaming

```python
def download_large_file(url: str, filepath: Path) -> None:
    """Download large file with streaming."""
    with httpx.stream("GET", url) as r:
        r.raise_for_status()
        with open(filepath, "wb") as f:
            for chunk in r.iter_bytes(chunk_size=8192):
                f.write(chunk)
```

---

## 15. Bezpieczeństwo

### 15.1 NIGDY

```python
# NEVER hardcode secrets
API_KEY = "sk-1234567890"  # NEVER!

# NEVER commit .env files
# .gitignore must contain:
# .env, .env.local, *.pem, *.key

# NEVER eval() on user input
eval(user_input)  # NEVER!

# NEVER string-concatenate SQL
query = f"SELECT * FROM t WHERE id = {user_id}"  # NEVER!
```

### 15.2 ZAWSZE

```python
import os

# ALWAYS use environment variables
API_KEY = os.getenv("API_KEY")

# ALWAYS validate input at system boundaries
def fetch_data(lat: float, lon: float) -> Result:
    if not (49.0 <= lat <= 55.0):
        raise ValidationError(f"Latitude {lat} outside range")
    ...

# ALWAYS set timeouts for HTTP requests
response = httpx.get(url, timeout=30)

# ALWAYS use parameterized queries (when using SQL)
from sqlalchemy import text
query = text("SELECT * FROM stations WHERE id = :id")
result = db.execute(query, {"id": station_id})
```

---

## 16. Pre-merge checklist

```markdown
- [ ] Testy przechodzą (`pytest`)
- [ ] Pokrycie kodu w normie (80% core / 60% utility)
- [ ] Formatowanie OK (`ruff format --check`)
- [ ] Linting OK (`ruff check`)
- [ ] Type hints OK (`mypy --strict`)
- [ ] Docstrings dla publicznych funkcji/klas
- [ ] Brak hardcoded secrets
- [ ] Dokumentacja zaktualizowana (jeśli potrzeba)
- [ ] PROGRESS.md / CHANGELOG.md zaktualizowany
- [ ] Minimum 1 approval
- [ ] Brak konfliktów z target branch
```

---

## CZĘŚĆ III: ROZSZERZENIA OPCJONALNE

> Stosuj poniższe sekcje tylko gdy projekt tego wymaga.
> Aktywne rozszerzenia powinny być wymienione w `CLAUDE.md` danego projektu.

---

## 17. Rozszerzenia opcjonalne

### 17.1 SQL i bazy danych

Stosować w projektach z bazą danych (np. Hydrograf/PostGIS, IMGWTools/SQLite).

#### Nazewnictwo

```sql
-- Tables: snake_case, plural
CREATE TABLE flow_network (
    id SERIAL PRIMARY KEY,
    elevation FLOAT,
    flow_accumulation INT
);

-- Indexes: idx_<table>_<column>
CREATE INDEX idx_flow_geom ON flow_network USING GIST(geom);

-- Constraints: descriptive names
CONSTRAINT valid_elevation CHECK (elevation >= -50 AND elevation <= 3000);
CONSTRAINT positive_area CHECK (cell_area > 0);
```

#### Formatowanie SQL

```sql
-- Keywords: UPPERCASE
-- Identifiers: lowercase

SELECT
    id,
    elevation,
    flow_accumulation
FROM flow_network
WHERE is_stream = TRUE
ORDER BY elevation DESC
LIMIT 100;
```

#### Wydajność baz danych

```python
# GOOD — batch query (avoid N+1)
ids = [c.downstream_id for c in cells]
results = db.query(Cell).filter(Cell.id.in_(ids)).all()

# BAD — N+1 queries
for cell in cells:
    downstream = db.query(Cell).filter(Cell.id == cell.downstream_id).first()
```

---

### 17.2 JavaScript / frontend

Stosować w projektach z frontendem webowym (np. Hydrograf).

#### Nazewnictwo

```javascript
// Variables and functions: camelCase
const watershedArea = 45.3;
let currentZoom = 10;

function calculateBounds(coordinates) { ... }
async function fetchHydrograph(lat, lon) { ... }

// Classes: PascalCase
class MapController { ... }

// Constants: UPPER_SNAKE_CASE
const API_URL = "http://localhost:8000/api";
const MAX_ZOOM = 18;

// Event handlers: prefix "on" or "handle"
function onMapClick(event) { ... }
function handleSubmit() { ... }
```

#### Formatowanie

- Długość linii: **100 znaków**
- Wcięcia: **2 spacje**
- **Zawsze** średniki
- Single quotes, template literals dla interpolacji
- Arrow functions dla callbacks

#### JSDoc

```javascript
/**
 * Display watershed boundary on map.
 *
 * @param {Object} boundaryGeoJSON - Boundary as GeoJSON Feature
 * @param {L.Map} map - Leaflet map instance
 * @returns {L.GeoJSON} Layer with watershed boundary
 */
function displayWatershed(boundaryGeoJSON, map) { ... }
```

---

### 17.3 HTML / CSS

Stosować w projektach z interfejsem webowym.

#### HTML

- Semantyczne tagi (`<main>`, `<article>`, `<nav>`, `<section>`)
- Atrybuty: kebab-case (`data-station-id`)
- Klasy CSS: BEM lub utility-first (Tailwind) — ustalić per projekt

#### CSS

- Zmienne CSS dla kolorów i spacing
- Mobile-first media queries
- Unikać `!important`

---

### 17.4 CI/CD pipeline

Stosować w projektach z GitHub Actions lub innymi systemami CI.

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Ruff format
        run: ruff format --check src/
      - name: Ruff lint
        run: ruff check src/
      - name: Mypy
        run: mypy src/

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install deps
        run: pip install -e ".[dev]"
      - name: Run tests
        run: pytest tests/ --cov=src/ --cov-report=xml
```

---

### 17.5 Monitoring

Stosować w projektach z deploymentem produkcyjnym.

**Metryki do zbierania:**
- Czas odpowiedzi (p50, p95, p99)
- Requests per minute
- Error rate (4xx, 5xx)
- CPU / Memory usage

**Narzędzia:** Prometheus + Grafana (metryki), Sentry (error tracking)

**Rate limiting (FastAPI):**

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/endpoint")
@limiter.limit("10/minute")
async def endpoint(request: Request):
    pass
```

---

### 17.6 Julia (placeholder)

> Sekcja do uzupełnienia gdy pojawią się projekty w Julii.
> Przewidywane konwencje: CamelCase dla typów, snake_case dla funkcji,
> docstrings w formacie Julia Markdown.

---

## Appendix: Struktura modułów Python

### Publiczne API przez `__init__.py`

```python
# myproject/core/__init__.py
"""Core computation module."""

from myproject.core.calculations import (
    calculate_retention,
    calculate_effective_precipitation,
)

__all__ = [
    "calculate_retention",
    "calculate_effective_precipitation",
]
```

### Import z modułu, nie z pliku

```python
# GOOD — import from module
from myproject.core import calculate_retention

# AVOID — import from internal file
from myproject.core.calculations import calculate_retention
```

---

**Wersja dokumentu:** 1.0
**Data ostatniej aktualizacji:** 2026-01-29
**Zakres:** Wszystkie projekty Python w ~/workspace/projects/

*Odstępstwa od tych standardów wymagają uzasadnienia w `CLAUDE.md` danego projektu.*

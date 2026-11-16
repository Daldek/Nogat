<!-- Szablon PRD.md -->
<!-- Źródło: shared/standards/DOCUMENTATION_STANDARDS.md, sekcja 4 -->
<!-- Użycie: skopiuj do docs/PRD.md w nowym projekcie, wypełnij placeholdery -->
<!-- Język: konsekwentnie polski LUB angielski w całym pliku -->

# PRD — [NAZWA_PROJEKTU]

## 1. Cel produktu

<!-- TODO: 2-5 zdań: co budujemy, dlaczego, jaki problem rozwiązuje, dla kogo -->

## 2. Zakres

### 2.1 In Scope

<!-- TODO: lista funkcjonalności objętych zakresem projektu -->

- <!-- TODO: funkcjonalność A -->
- <!-- TODO: funkcjonalność B -->

### 2.2 Out of Scope

<!-- TODO: co świadomie pomijamy i dlaczego -->

- <!-- TODO: co pomijamy i krótkie uzasadnienie -->

### 2.3 Future Scope

<!-- TODO: opcjonalne — co może być dodane w przyszłych wersjach -->

- <!-- TODO: potencjalne rozszerzenie -->

<!-- UWAGA: jeśli sekcja 2 (Zakres) jest rozbudowana (> 100 linii),
rozważ wydzielenie do osobnego pliku docs/SCOPE.md.
Osobny SCOPE.md rekomendowany gdy PRD > 300 linii lub projekt ma wiele faz. -->

## 3. Wymagania funkcjonalne

<!-- WAŻNE: wybierz JEDEN z poniższych formatów i stosuj konsekwentnie.
Usuń format, którego nie używasz. -->

<!-- FORMAT A: User Stories — lepszy dla projektów z jasno zdefiniowanymi rolami -->

### User Stories

- **US-01:** Jako [rola] chcę [akcja] żeby [cel]
- **US-02:** Jako [rola] chcę [akcja] żeby [cel]

<!-- FORMAT B: Feature Matrix — lepszy dla bibliotek i narzędzi technicznych -->

### Feature Matrix

| ID | Funkcja | Status | Opis |
|----|---------|--------|------|
| F-01 | <!-- TODO --> | ⏳ Planned | <!-- TODO --> |
| F-02 | <!-- TODO --> | ⏳ Planned | <!-- TODO --> |

<!-- Statusy: ⏳ Planned | 🔧 In Progress | ✅ Done | ❌ Dropped -->

## 4. Wymagania niefunkcjonalne

<!-- TODO: opisz wymagania dotyczące jakości, nie funkcji -->

- **Wydajność:** <!-- TODO: np. "Obliczenia dla zlewni 100 km² < 5 sekund" -->
- **Kompatybilność:** <!-- TODO: np. "Python 3.12+, NumPy 2.0+" -->
- **Testy:** <!-- TODO: np. "Pokrycie testami > 80%" -->

<!-- TODO: dodaj inne kategorie jeśli istotne:
- **Bezpieczeństwo:**
- **Dostępność:**
- **Skalowalność:**
-->

## 5. Kryteria sukcesu

<!-- TODO: mierzalne warunki, po których uznajemy produkt za gotowy -->

1. <!-- TODO: kryterium 1 -->
2. <!-- TODO: kryterium 2 -->
3. <!-- TODO: kryterium 3 -->

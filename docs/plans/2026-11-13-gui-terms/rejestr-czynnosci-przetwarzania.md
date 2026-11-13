# Rejestr czynności przetwarzania (art. 30 ust. 1 RODO)

Administrator: Piotr de Bever, kontakt@debever.pl, osoba prywatna. Serwisy: Hydrograf, Hydrolog i Obserwator, publiczne, bez rejestracji (regulamin 1.0, § 8). Stan na: [RRRR-MM-DD, `terms_effective`]. Rejestr jest prowadzony, bo przetwarzanie adresów IP nie ma charakteru sporadycznego (art. 30 ust. 5 RODO). Inspektora ochrony danych nie wyznaczono (art. 37 RODO nie ma zastosowania).

| Czynność | Cel i podstawa | Osoby i dane | Odbiorcy, państwa trzecie | Okres przechowywania |
|---|---|---|---|---|
| Obsługa żądań i limit żądań | dostarczenie strony, bezpieczeństwo, ochrona przed nadmierną liczbą żądań; art. 6 ust. 1 lit. f | użytkownicy; adres IP | Cloudflare, Inc. (podmiot przetwarzający, DPA w warunkach usługi); USA, EU-U.S. Data Privacy Framework | tylko w pamięci, przez okno limitu (domyślnie 60 s); nie zapisywany |
| Statystyka użycia | liczba odwiedzających, odsłon, otwartych stacji, analiz i pobrań; art. 6 ust. 1 lit. f | użytkownicy; adres IP i User-Agent jako skrót HMAC z dzienną losową wartością | brak | skróty i losowa wartość w pamięci do północy UTC; zapisywane tylko łączne liczby dzienne (`stats.jsonl`, dane anonimowe) |
| Dzienniki serwera | działanie i bezpieczeństwo serwisu; art. 6 ust. 1 lit. f | użytkownicy; czas, metoda, adres strony z parametrami (bez wartości parametrów z tekstem wyszukiwania, nazwą, adresem e-mail lub danymi logowania), kod, rozmiar, czas obsługi, losowy identyfikator żądania, rodzaj programu (przeglądarka, robot, inny program); bez adresu IP i User-Agent (DEV-12.4 do DEV-12.9) | brak | 14 dni (dziennik żądań i dziennik błędów); komunikaty o uruchomieniu, zatrzymaniu i błędach serwera, bez danych żądań, w dzienniku systemowym do jego limitu |
| Zgłoszenia „Zgłoś uwagę” | rozpatrzenie zgłoszenia; art. 6 ust. 1 lit. f | zgłaszający; treść zgłoszenia i kontekst widoku, dane osobowe tylko wpisane wbrew pouczeniu | brak | do załatwienia zgłoszenia |
| Korespondencja e-mail, w tym żądania z art. 15–21 | odpowiedź, załatwienie sprawy, wykonanie praw; art. 6 ust. 1 lit. f i lit. c (art. 12 RODO) | nadawcy; adres e-mail, imię i nazwisko, jeśli podane, treść | Apple (iCloud Mail); możliwe przetwarzanie poza EOG | do załatwienia sprawy |
| Podkłady mapowe | wyświetlenie mapy; art. 6 ust. 1 lit. f | użytkownicy widoków z mapą; adres IP przekazywany przez przeglądarkę | dostawcy podkładów (OpenFreeMap, Esri, geoportal.gov.pl) jako odrębni administratorzy | operator nie przechowuje |

Ruch przechodzący przez Cloudflare obejmuje też treść żądań, w tym zgłoszeń; Cloudflare może prowadzić własne dzienniki bezpieczeństwa jako odrębny administrator (jego polityka prywatności).

Środki bezpieczeństwa (art. 32 ust. 1): serwer na własnym sprzęcie operatora, w jego domu; ruch tylko przez TLS za Cloudflare; części administracyjne za Cloudflare Access i kluczem administracyjnym, dostępne tylko operatorowi; adres IP wyłącznie w pamięci, żaden dziennik go nie zawiera; formularz bez pól kontaktowych; usuwanie dzienników po 14 dniach i zgłoszeń po załatwieniu; [kopie zapasowe: gdzie i jak długo].

Zmiany: rejestr aktualizuje się przy każdej nowej wersji regulaminu i przy zmianie dostawcy (`processor`, `mail_provider`, hosting).

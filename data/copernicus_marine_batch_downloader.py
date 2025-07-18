"""
Skrypt do pobierania danych z Copernicus Marine Service dla wielu lokalizacji.

Umożliwia automatyczne pobieranie danych dla:
- pojedynczych punktów (CSV z kolumnami: lon, lat),
- lub obszarów (CSV z kolumnami: lon_min, lon_max, lat_min, lat_max).

Wymaga wcześniejszego założenia konta i pobrania pliku z poświadczeniami Copernicus Marine.

Sposób użycia (przykład w terminalu):
    python copernicus_marine_batch_downloader.py --locations_file example_locations.csv --dataset_id cmems_mod_bal_phy_my_P1D-m --variables sla so thetao --start_datetime 2021-01-01T00:00:00 --end_datetime 2022-12-31T00:00:00

Argumenty wymagane:
- --locations_file: plik CSV z lokalizacjami,
- --dataset_id: identyfikator zbioru danych,
- --variables: lista zmiennych do pobrania.

Opcje dodatkowe:
- --dataset_version, --min_depth, --max_depth, --coordinates_selection_method, --disable_progress_bar, --credentials_file
"""

import argparse
from pathlib import Path
import pandas as pd
import copernicusmarine


def main():
    """
    Główna funkcja skryptu.

    - Wczytuje lokalizacje z pliku CSV (punkty lub obszary),
    - Rozpoznaje typ danych (punkt vs. obszar) na podstawie nagłówków,
    - Dla każdej lokalizacji wywołuje copernicusmarine.subset() z przekazanymi parametrami.

    Wymagane argumenty CLI:
    --locations_file, --dataset_id, --variables

    Obsługiwane kolumny w pliku CSV:
    - Dla punktów: lon, lat
    - Dla obszarów: lon_min, lon_max, lat_min, lat_max
    """

    parser = argparse.ArgumentParser(
        description="Pętla po lokalizacjach i wywołanie copernicusmarine.subset dla każdej z nich."
    )

    parser.add_argument(
        "--locations_file",
        required=True,
        help="CSV z kolumnami: lon, lat LUB lon_min, lon_max, lat_min, lat_max.",
    )
    parser.add_argument("--dataset_id", required=True)
    parser.add_argument("--dataset_version", required=True)
    parser.add_argument("--variables", required=True, nargs="+")
    parser.add_argument("--start_datetime", type=str, default="1993-01-01T00:00:00")
    parser.add_argument("--end_datetime", type=str, default="2023-12-31T00:00:00")
    parser.add_argument("--min_depth", type=float, default=0.51)
    parser.add_argument("--max_depth", type=float, default=30.0)
    parser.add_argument(
        "--coordinates_selection_method", type=str, default="strict-inside"
    )
    parser.add_argument("--disable_progress_bar", action="store_true")
    parser.add_argument(
        "--credentials_file",
        default=str(
            Path.home() / ".copernicusmarine" / ".copernicusmarine-credentials"
        ),
    )

    args = parser.parse_args()

    locations = pd.read_csv(args.locations_file)

    if {"lon", "lat"}.issubset(locations.columns):
        mode = "points"
    elif {"lon_min", "lon_max", "lat_min", "lat_max"}.issubset(locations.columns):
        mode = "areas"
    else:
        raise ValueError(
            "Plik CSV musi zawierać kolumny 'lon' i 'lat' lub 'lon_min', 'lon_max', 'lat_min', 'lat_max'."
        )

    for _, loc in locations.iterrows():
        if mode == "points":
            lon_min = lon_max = loc["lon"]
            lat_min = lat_max = loc["lat"]
            print(f"Pobieranie punktu: {lon_min}, {lat_min}")
        else:  # mode == "areas"
            lon_min = loc["lon_min"]
            lon_max = loc["lon_max"]
            lat_min = loc["lat_min"]
            lat_max = loc["lat_max"]
            print(f"Pobieranie obszaru: {lon_min}–{lon_max}, {lat_min}–{lat_max}")

        copernicusmarine.subset(
            dataset_id=args.dataset_id,
            dataset_version=args.dataset_version,
            variables=args.variables,
            minimum_longitude=lon_min,
            maximum_longitude=lon_max,
            minimum_latitude=lat_min,
            maximum_latitude=lat_max,
            start_datetime=args.start_datetime,
            end_datetime=args.end_datetime,
            minimum_depth=args.min_depth,
            maximum_depth=args.max_depth,
            coordinates_selection_method=args.coordinates_selection_method,
            disable_progress_bar=args.disable_progress_bar,
            credentials_file=args.credentials_file,
        )


if __name__ == "__main__":
    main()

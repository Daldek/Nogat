"""
Skrypt do pobierania danych in-situ z Copernicus Marine Service na podstawie nazw plików.
Wymaga pliku CSV zawierającego kolumnę 'name' z nazwami stacji.

Przykłady adresów:
https://data-marineinsitu.ifremer.fr/glo_multiparameter_nrt/history/MO/NO_TS_MO_6600366.nc
https://data-marineinsitu.ifremer.fr/glo_multiparameter_nrt/history/MO/BO_TS_MO_OresundNorthCU.nc
"""

import argparse
from pathlib import Path
import os
import requests
import pandas as pd


def download_file(url, output_folder):
    """
    Pobiera plik z podanego adresu URL i zapisuje go do wskazanego katalogu.

    Parametry:
    url (str): Pełny adres URL do pliku NetCDF.
    output_folder (str lub Path): Ścieżka do folderu, w którym plik ma zostać zapisany.

    Jeśli pobieranie się nie powiedzie, zostanie wyświetlony komunikat o błędzie.
    """
    filename = url.split("/")[-1]
    output_path = Path(output_folder) / filename
    print(f"Pobieranie {url} do {output_path}")
    response = requests.get(url, stream=True, timeout=30)
    if response.status_code == 200:
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    else:
        print(f"Błąd pobierania {url}, kod statusu: {response.status_code}")


def main():
    """
    Główna funkcja skryptu.
    - Wczytuje nazwy stacji z pliku CSV,
    - Generuje URL-e do plików NetCDF,
    - Pobiera każdy plik do wskazanego katalogu.
    """
    parser = argparse.ArgumentParser(
        description="Pobieranie danych in-situ Copernicus Marine na podstawie nazw stacji."
    )
    parser.add_argument(
        "--stations_file", required=True, help="CSV z kolumną 'station_name'."
    )
    parser.add_argument(
        "--output_folder",
        default=os.path.dirname(os.path.abspath(__file__)),
        help="Folder docelowy na pobrane pliki.",
    )
    parser.add_argument(
        "--base_url",
        default="https://data-marineinsitu.ifremer.fr/glo_multiparameter_nrt/history/MO/",
        help="Bazowy adres URL katalogu danych.",
    )

    args = parser.parse_args()

    stations = pd.read_csv(args.stations_file)
    if "name" not in stations.columns:
        raise ValueError("Plik CSV musi zawierać kolumnę 'name'.")

    Path(args.output_folder).mkdir(parents=True, exist_ok=True)

    for _, row in stations.iterrows():
        station_name = row["name"].strip()
        file_url = f"{args.base_url}{station_name}.nc"
        download_file(file_url, args.output_folder)


if __name__ == "__main__":
    main()

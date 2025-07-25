library(tidyverse)
library(ncdf4)
library(argparser)

# parser argumentów
p <- arg_parser("Wizualizacja danych z NetCDF")
p <- add_argument(p, "--nc_file", help = "Ścieżka do pliku .nc", type = "character")
p <- add_argument(p, "--variable", help = "Nazwa zmiennej do wizualizacji", type = "character")
p <- add_argument(p, "--title", help = "Tytuł wykresu", type = "character", default = "Wykres liniowy wybranej zmiennej")
p <- add_argument(p, "--start_date", help = "Data początkowa w formacie YYYY-MM-DD", type = "character")
p <- add_argument(p, "--end_date", help = "Data końcowa w formacie YYYY-MM-DD", type = "character")

argv <- parse_args(p)

# ścieżka do pliku .nc z argumentu
nc_file <- argv$nc_file

# wczytanie danych z netcdf
nc <- nc_open(nc_file)

# pobierz dane z netcdf
time_raw <- ncvar_get(nc, "time")
time_units <- ncatt_get(nc, "time", "units")$value
variable <- ncvar_get(nc, argv$variable)

# funkcja spradzająca podanie daty w argumentach
is_provided <- function(x) {
  !is.null(x) && !is.na(x) && x != ""
}

# funkcja do konwersji daty
convert_nc_time <- function(time_raw, time_units) {
  # Wyodrębnij jednostkę i datę
  pattern <- "(seconds|days) since ([0-9]{4}-[0-9]{2}-[0-9]{2})(.*)?"
  if (!grepl(pattern, time_units)) {
    stop("Nieznany format jednostek czasu.")
  }
  
  parts <- regmatches(time_units, regexec(pattern, time_units))[[1]]
  unit <- parts[2]
  origin_date <- parts[3]
  
  # Wybierz odpowiednią metodę konwersji
  tryCatch({
    if (unit == "seconds") {
      as.POSIXct(time_raw, origin = origin_date, tz = "UTC")
    } else if (unit == "days") {
      as.Date(time_raw, origin = origin_date)
    } else {
      stop("Nieobsługiwana jednostka czasu.")
    }
  }, error = function(e) {
    warning("Błąd konwersji czasu: ", conditionMessage(e))
    return(NA)
  })
}

# konwersja czasu
converted_dates <- convert_nc_time(time_raw, time_units)

# Dopasuj typ daty
date_class <- class(converted_dates)[1]  # "Date" albo "POSIXct"

# Parsuj argumenty do tej samej klasy
parse_date <- function(x) {
  if (!is_provided(x)) return(NA)
  if (date_class == "Date") as.Date(x)
  else as.POSIXct(x, tz = "UTC")
}

# Jeśli daty są podane, przekształć je; jeśli nie — użyj pełnego zakresu
start_date <- if (is_provided(argv$start_date)) as.Date(argv$start_date) else min(converted_dates, na.rm = TRUE)
end_date   <- if (is_provided(argv$end_date))   as.Date(argv$end_date)   else max(converted_dates, na.rm = TRUE)

# tworzenie ramki danych
df <- tibble(
  time = converted_dates,
  variable = variable
) %>%
  mutate(
    variable = as.vector(variable),  # zmiana z tablicy na wektor
  ) %>%
  arrange(time)  # sortowanie wg daty

# filtrowanie danych do zakresu dat
df_limited <- df %>%
  filter(
    time >= start_date & time <= end_date
  )

# wykres liniowy wybranej zmiennej
p <- ggplot(
  data = df_limited,
  mapping = aes(x = time, y = variable)
  ) +
geom_line() +
labs(
  title = argv$title,
  subtitle = paste0("W okresie od ", start_date, " do ", end_date),
  x = "Czas", y = argv$variable
)

ggsave(filename = paste0(argv$title, ".png"), plot = p, width = 10, height = 6, dpi = 100)

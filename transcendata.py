import csv
import os

def extract_columns_from_csv(input_csv, output_filename):
    # Pobierz bieżący katalog roboczy
    current_directory = os.path.dirname(os.path.abspath(__file__))
    
    # Ścieżka do katalogu 'himera_transcendata'
    output_directory = os.path.join(current_directory, 'himera_transcendata')
    
    # Upewnij się, że katalog 'himera_transcendata' istnieje
    os.makedirs(output_directory, exist_ok=True)
    
    # Pełna ścieżka do pliku wynikowego
    output_txt = os.path.join(output_directory, output_filename)
    
    # Otwórz plik CSV do odczytu
    with open(input_csv, mode='r', newline='', encoding='utf-8') as csvfile:
        # Utwórz reader do odczytu danych CSV z separatorem ';'
        csvreader = csv.reader(csvfile, delimiter=';')
        
        # Pomiń pierwszy wiersz (nagłówki)
        next(csvreader, None)
        
        # Otwórz plik TXT do zapisu
        with open(output_txt, mode='w', encoding='utf-8') as txtfile:
            # Przetwarzaj każdą linię z pliku CSV
            for row in csvreader:
                # Sprawdź, czy wiersz ma wystarczającą liczbę kolumn
                if len(row) >= 9:
                    try:
                        # Zamień kolumny 7, 8 i 9 na typ float i podziel przez 100000000
                        selected_columns = [
                            str(float(row[6]) / 100000000),
                            str(float(row[7]) / 100000000),
                            str(float(row[8]) / 100000000)
                        ]
                        # Zapisz do pliku TXT, używając spacji jako separatora
                        txtfile.write(' '.join(selected_columns) + '\n')
                    except ValueError as e:
                        print(f"Nie udało się przekonwertować wiersza: {row} - Błąd: {e}")
                else:
                    print("Wiersz pominięty (zbyt mało kolumn):", row)

def main():
    # Zapytaj użytkownika o ścieżkę do pliku CSV
    input_csv = input("Podaj ścieżkę do pliku CSV: ").strip()
    
    # Zapytaj użytkownika o nazwę pliku wynikowego
    output_filename = input("Podaj nazwę pliku wynikowego (bez rozszerzenia): ").strip() + '.txt'
    
    # Wywołaj funkcję konwertującą
    extract_columns_from_csv(input_csv, output_filename)
    print(f"Plik został zapisany w katalogu 'himera_transcendata' jako '{output_filename}'.")

if __name__ == "__main__":
    main()




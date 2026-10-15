# Data Directory

Place your external book datasets here.

### Expected Files:
- `books.csv` or `books_import.csv` downloaded from Kaggle:
  - Source: [7k Books with Metadata on Kaggle](https://www.kaggle.com/datasets/dylanjcastillo/7k-books-with-metadata)
- Run the ingestion script:
  ```powershell
  .\env\Scripts\python.exe scripts/ingest_books.py data/books.csv
  ```

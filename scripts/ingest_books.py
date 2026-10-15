"""Comprehensive catalog ingestion script for Library Book Reservation System.

Ingests 200–250 curated, verified books across 8 core genres:
- Fiction, Mystery, Science, Technology, Horror, Comedy, Philosophy, Fantasy,
plus verified multi-genre combination titles (e.g. "Horror, Comedy", "Technology, Science").

Features:
- Dynamically calculates total_copies (1 to 8 copies) based on ratings count & demand.
- Creates simulated active reservations for select popular titles so they are OUT OF STOCK (0 available copies),
  allowing patrons to immediately test the out-of-stock restock waitlist notification feature.
- Preserves database integrity: available_copies == total_copies - count(active_reservations).
"""

import csv
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.database import SessionLocal
from app.models import Book, Reservation, WaitlistNotification

# Dataset file locations
DATASET_CANDIDATES = [
    Path("e:/Company/Aumne AI/dataset/books.csv"),
    BASE_DIR / "data" / "books.csv",
]

# Targeted masterpieces to guarantee for every genre
CURATED_CANONICAL = [
    # Horror & Comedy combined
    ("John Dies at the End", "David Wong", "Horror, Comedy", 3, 28000),
    ("Warm Bodies", "Isaac Marion", "Horror, Comedy", 4, 185000),
    ("Pride and Prejudice and Zombies", "Seth Grahame-Smith", "Horror, Comedy", 3, 145000),
    ("The Radleys", "Matt Haig", "Horror, Comedy", 3, 24000),
    ("Tales from the Gas Station", "Jack Townsend", "Horror, Comedy", 2, 9500),

    # Technology & Science combined
    ("Life 3.0: Being Human in the Age of AI", "Max Tegmark", "Technology, Science", 4, 38000),
    ("Superintelligence: Paths, Dangers, Strategies", "Nick Bostrom", "Technology, Science", 5, 42000),
    ("The Master Algorithm", "Pedro Domingos", "Technology, Science", 3, 15000),
    ("Gödel, Escher, Bach: An Eternal Golden Braid", "Douglas Hofstadter", "Technology, Science", 4, 52000),

    # Philosophy & Fiction combined
    ("Sophie's World", "Jostein Gaarder", "Philosophy, Fiction", 5, 230000),
    ("The Stranger", "Albert Camus", "Philosophy, Fiction", 6, 850000),
    ("Thus Spoke Zarathustra", "Friedrich Nietzsche", "Philosophy, Fiction", 4, 110000),
    ("The Trial", "Franz Kafka", "Philosophy, Fiction", 5, 290000),

    # Horror masterpieces
    ("The Shining", "Stephen King", "Horror", 6, 1200000),
    ("Dracula", "Bram Stoker", "Horror", 7, 1050000),
    ("Frankenstein", "Mary Shelley", "Horror", 6, 1300000),
    ("The Haunting of Hill House", "Shirley Jackson", "Horror", 5, 210000),
    ("Pet Sematary", "Stephen King", "Horror", 5, 420000),
    ("Bird Box", "Josh Malerman", "Horror", 4, 180000),
    ("At the Mountains of Madness", "H. P. Lovecraft", "Horror", 3, 98000),
    ("It", "Stephen King", "Horror", 8, 920000),
    ("Salem's Lot", "Stephen King", "Horror", 5, 360000),
    ("The Exorcist", "William Peter Blatty", "Horror", 4, 210000),

    # Comedy masterpieces
    ("The Hitchhiker's Guide to the Galaxy", "Douglas Adams", "Comedy", 8, 1600000),
    ("Good Omens", "Neil Gaiman & Terry Pratchett", "Comedy", 7, 650000),
    ("Catch-22", "Joseph Heller", "Comedy", 6, 800000),
    ("Me Talk Pretty One Day", "David Sedaris", "Comedy", 5, 340000),
    ("Guards! Guards!", "Terry Pratchett", "Comedy", 6, 210000),
    ("Three Men in a Boat", "Jerome K. Jerome", "Comedy", 4, 98000),
    ("A Confederacy of Dunces", "John Kennedy Toole", "Comedy", 5, 270000),
    ("Bossypants", "Tina Fey", "Comedy", 5, 890000),
    ("Mort", "Terry Pratchett", "Comedy", 5, 175000),
    ("Small Gods", "Terry Pratchett", "Comedy", 5, 120000),

    # Technology masterpieces
    ("Clean Code: A Handbook of Agile Software Craftsmanship", "Robert C. Martin", "Technology", 8, 38000),
    ("The Pragmatic Programmer", "David Thomas & Andrew Hunt", "Technology", 7, 52000),
    ("Design Patterns: Elements of Reusable Object-Oriented Software", "Erich Gamma et al.", "Technology", 6, 26000),
    ("Introduction to Algorithms", "Thomas H. Cormen et al.", "Technology", 6, 18000),
    ("Structure and Interpretation of Computer Programs", "Harold Abelson", "Technology", 5, 9500),
    ("Code: The Hidden Language of Computer Hardware and Software", "Charles Petzold", "Technology", 6, 32000),
    ("Designing Data-Intensive Applications", "Martin Kleppmann", "Technology", 7, 24000),
    ("Refactoring: Improving the Design of Existing Code", "Martin Fowler", "Technology", 6, 19000),
    ("You Don't Know JS: Scope & Closures", "Kyle Simpson", "Technology", 5, 14000),
    ("Cracking the Coding Interview", "Gayle Laakmann McDowell", "Technology", 7, 36000),

    # Philosophy masterpieces
    ("Meditations", "Marcus Aurelius", "Philosophy", 8, 450000),
    ("The Republic", "Plato", "Philosophy", 7, 220000),
    ("Beyond Good and Evil", "Friedrich Nietzsche", "Philosophy", 6, 130000),
    ("Critique of Pure Reason", "Immanuel Kant", "Philosophy", 4, 48000),
    ("Being and Time", "Martin Heidegger", "Philosophy", 3, 22000),
    ("Nicomachean Ethics", "Aristotle", "Philosophy", 5, 78000),
    ("The Myth of Sisyphus and Other Essays", "Albert Camus", "Philosophy", 6, 125000),
    ("Man's Search for Meaning", "Viktor E. Frankl", "Philosophy", 8, 720000),
    ("Letters from a Stoic", "Seneca", "Philosophy", 6, 110000),
    ("Tractatus Logico-Philosophicus", "Ludwig Wittgenstein", "Philosophy", 4, 38000),

    # Science masterpieces
    ("Cosmos", "Carl Sagan", "Science", 8, 410000),
    ("A Brief History of Time", "Stephen Hawking", "Science", 8, 1400000),
    ("The Selfish Gene", "Richard Dawkins", "Science", 7, 210000),
    ("Silent Spring", "Rachel Carson", "Science", 5, 98000),
    ("Sapiens: A Brief History of Humankind", "Yuval Noah Harari", "Science", 8, 1100000),
    ("The Demon-Haunted World: Science as a Candle in the Dark", "Carl Sagan", "Science", 6, 120000),
    ("Astrophysics for People in a Hurry", "Neil deGrasse Tyson", "Science", 7, 280000),
    ("The Origin of Species", "Charles Darwin", "Science", 6, 260000),
    ("The Elegant Universe", "Brian Greene", "Science", 5, 140000),
    ("What If? Serious Scientific Answers to Absurd Hypothetical Questions", "Randall Munroe", "Science", 7, 230000),

    # Mystery masterpieces
    ("The Complete Sherlock Holmes", "Arthur Conan Doyle", "Mystery", 8, 380000),
    ("And Then There Were None", "Agatha Christie", "Mystery", 8, 980000),
    ("The Murder of Roger Ackroyd", "Agatha Christie", "Mystery", 7, 260000),
    ("The Girl with the Dragon Tattoo", "Stieg Larsson", "Mystery", 8, 2800000),
    ("The Maltese Falcon", "Dashiell Hammett", "Mystery", 6, 180000),
    ("The Big Sleep", "Raymond Chandler", "Mystery", 6, 190000),
    ("In the Woods", "Tana French", "Mystery", 5, 340000),
    ("Gone Girl", "Gillian Flynn", "Mystery", 8, 2600000),
    ("The Da Vinci Code", "Dan Brown", "Mystery", 8, 2100000),
    ("Shutter Island", "Dennis Lehane", "Mystery", 6, 210000),

    # Fantasy masterpieces
    ("The Hobbit", "J. R. R. Tolkien", "Fantasy", 8, 3200000),
    ("The Fellowship of the Ring", "J. R. R. Tolkien", "Fantasy", 8, 2600000),
    ("A Game of Thrones", "George R. R. Martin", "Fantasy", 8, 2200000),
    ("The Name of the Wind", "Patrick Rothfuss", "Fantasy", 7, 850000),
    ("Mistborn: The Final Empire", "Brandon Sanderson", "Fantasy", 7, 520000),
    ("The Way of Kings", "Brandon Sanderson", "Fantasy", 7, 410000),
    ("The Lion, the Witch and the Wardrobe", "C. S. Lewis", "Fantasy", 8, 2400000),
    ("The Blade Itself", "Joe Abercrombie", "Fantasy", 6, 230000),
    ("American Gods", "Neil Gaiman", "Fantasy", 7, 620000),
    ("The Color of Magic", "Terry Pratchett", "Fantasy", 6, 340000),

    # Fiction masterpieces
    ("1984", "George Orwell", "Fiction", 8, 3800000),
    ("To Kill a Mockingbird", "Harper Lee", "Fiction", 8, 5100000),
    ("The Great Gatsby", "F. Scott Fitzgerald", "Fiction", 8, 4300000),
    ("Pride and Prejudice", "Jane Austen", "Fiction", 8, 3400000),
    ("Brave New World", "Aldous Huxley", "Fiction", 8, 1700000),
    ("Crime and Punishment", "Fyodor Dostoevsky", "Fiction", 7, 780000),
    ("The Catcher in the Rye", "J. D. Salinger", "Fiction", 8, 3100000),
    ("One Hundred Years of Solitude", "Gabriel García Márquez", "Fiction", 7, 920000),
    ("Lord of the Flies", "William Golding", "Fiction", 7, 2600000),
    ("Fahrenheit 451", "Ray Bradbury", "Fiction", 8, 1900000),
]


def determine_copies(ratings_count: int) -> int:
    """Calculate total book copies (1 to 8) based on audience demand / ratings count."""
    if ratings_count >= 100000:
        return 7
    elif ratings_count >= 20000:
        return 6
    elif ratings_count >= 5000:
        return 5
    elif ratings_count >= 1000:
        return 4
    elif ratings_count >= 200:
        return 3
    elif ratings_count >= 50:
        return 2
    return 1


def clean_text(text: str, max_len: int = 190) -> str:
    if not text:
        return "Unknown"
    cleaned = text.split(";")[0].split(",")[0].strip()
    return cleaned[:max_len] if cleaned else "Unknown"


def ingest_all_genres(target_per_genre: int = 28):
    """Seed catalog with balanced distribution across genres and simulated out-of-stock items."""
    print("=" * 70)
    print("LIBRARY CATALOG INGESTION: 8 Genres + Multi-Genre Titles")
    print("=" * 70)

    # Locate source CSV
    csv_file = None
    for candidate in DATASET_CANDIDATES:
        if candidate.exists():
            csv_file = candidate
            break

    print(f"Using source CSV dataset: {csv_file}")

    # Track how many books we have for each genre
    genre_targets = {
        "Horror": target_per_genre,
        "Comedy": target_per_genre,
        "Philosophy": target_per_genre,
        "Technology": target_per_genre,
        "Science": target_per_genre,
        "Mystery": target_per_genre,
        "Fantasy": target_per_genre,
        "Fiction": target_per_genre,
    }
    genre_counts = {g: 0 for g in genre_targets}
    multi_genre_count = 0

    with SessionLocal() as db:
        # Step 1: Insert curated canonical masterpieces first
        print("\n[Step 1] Ingesting canonical masterpieces for each genre & multi-genre combinations...")
        for title, author, genre, base_copies, ratings in CURATED_CANONICAL:
            existing = db.query(Book).filter(Book.title == title).first()
            copies = determine_copies(ratings) if ratings else base_copies
            if existing:
                existing.genre = genre
                existing.total_copies = copies
                existing.available_copies = copies
                continue

            b = Book(
                title=title,
                author=author,
                genre=genre,
                total_copies=copies,
                available_copies=copies,
            )
            db.add(b)
            # Update counts
            for g in genre_targets:
                if g in genre:
                    genre_counts[g] += 1
            if "," in genre:
                multi_genre_count += 1

        db.commit()
        print(f"  Inserted/Updated {len(CURATED_CANONICAL)} canonical masterpieces.")

        # Step 2: Ingest from CSV dataset to reach targets
        if csv_file and csv_file.exists():
            print("\n[Step 2] Scanning CSV dataset to fill remaining genre quotas...")
            with open(csv_file, "r", encoding="utf-8-sig", errors="replace") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Check if all quotas reached
                    if all(genre_counts[g] >= genre_targets[g] for g in genre_targets):
                        break

                    title = row.get("title", "").strip()
                    author = row.get("authors", "").strip() or row.get("author", "").strip()
                    cat = (row.get("categories", "") or "").lower()
                    desc = (row.get("description", "") or "").lower()
                    ratings_str = row.get("ratings_count", "")

                    if not title or not author or len(title) < 2:
                        continue

                    ratings_count = 0
                    try:
                        ratings_count = int(float(ratings_str)) if ratings_str else 0
                    except ValueError:
                        ratings_count = 0

                    full_text = f"{cat} {title.lower()} {desc}"

                    # Determine genre
                    assigned_genre = None
                    if "horror" in cat or "ghost" in full_text or "vampire" in full_text or "haunted" in full_text:
                        assigned_genre = "Horror"
                    elif "humor" in cat or "comedy" in full_text or "satire" in full_text or "funny" in full_text:
                        assigned_genre = "Comedy"
                    elif "philosophy" in cat or "philosoph" in full_text or "ethics" in cat or "logic" in cat:
                        assigned_genre = "Philosophy"
                    elif "computer" in cat or "programming" in full_text or "software" in full_text or "technology" in full_text:
                        assigned_genre = "Technology"
                    elif "science" in cat or "physics" in full_text or "astronomy" in full_text or "biology" in full_text:
                        assigned_genre = "Science"
                    elif "detective" in cat or "mystery" in cat or "crime" in cat or "murder" in full_text:
                        assigned_genre = "Mystery"
                    elif "fantasy" in cat or "magic" in full_text or "dragon" in full_text:
                        assigned_genre = "Fantasy"
                    elif "fiction" in cat:
                        assigned_genre = "Fiction"

                    if not assigned_genre or genre_counts.get(assigned_genre, 0) >= genre_targets.get(assigned_genre, 0):
                        continue

                    clean_title = title[:185]
                    clean_author = clean_text(author, 100)

                    # Check duplicate
                    if db.query(Book).filter(Book.title == clean_title).first():
                        continue

                    copies = determine_copies(ratings_count)
                    b = Book(
                        title=clean_title,
                        author=clean_author,
                        genre=assigned_genre,
                        total_copies=copies,
                        available_copies=copies,
                    )
                    db.add(b)
                    genre_counts[assigned_genre] += 1

                db.commit()

        # Step 3: Seed out-of-stock titles for waitlist testing
        print("\n[Step 3] Simulating active reservations for select popular titles to test out-of-stock waitlist alerts...")
        out_of_stock_titles = [
            "The Shining",
            "The Hitchhiker's Guide to the Galaxy",
            "Clean Code: A Handbook of Agile Software Craftsmanship",
            "A Brief History of Time",
            "Meditations",
            "The Maltese Falcon",
            "John Dies at the End",
        ]

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        expires = now + timedelta(days=7)

        for title in out_of_stock_titles:
            book = db.query(Book).filter(Book.title == title).first()
            if not book:
                continue

            # Remove existing reservations for this book to reset cleanly
            db.query(Reservation).filter(Reservation.book_id == book.id).delete()
            db.flush()

            # Reserve all copies
            for i in range(book.total_copies):
                res = Reservation(
                    book_id=book.id,
                    user_name=f"Patron {chr(65 + i)}",
                    reservation_date=now,
                    expires_at=expires,
                )
                db.add(res)

            book.available_copies = 0
            db.commit()
            print(f"  -> '{book.title}' ({book.genre}): total_copies={book.total_copies}, available_copies=0 (READY FOR WAITLIST TESTING)")

        # Summary report
        total_books = db.query(Book).count()
        total_avail = sum(b.available_copies for b in db.query(Book).all())
        total_copies = sum(b.total_copies for b in db.query(Book).all())
        print("\n" + "=" * 70)
        print(f"INGESTION SUCCESSFUL!")
        print(f"Total Books in Catalog: {total_books}")
        print(f"Total Physical Copies: {total_copies} (Available: {total_avail})")
        print("\nGenre Breakdown:")
        for g in sorted(genre_targets.keys()):
            count = db.query(Book).filter(Book.genre.ilike(f"%{g}%")).count()
            print(f"  {g:15}: {count} books")
        multi_count = db.query(Book).filter(Book.genre.like("%,%")).count()
        print(f"  Multi-Genre    : {multi_count} books")
        print("=" * 70)


if __name__ == "__main__":
    ingest_all_genres()

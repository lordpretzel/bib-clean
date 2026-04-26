import pytest
from bibtexparser.bparser import BibTexParser

import bibclean.bibclean as bibclean


def test_unwanted_fields_removed():
    """Test that unwanted fields are removed from bibtex entries."""
    bibtex_str = """
@article{Test2024,
    author = {John Doe},
    title = {Test Paper},
    journal = {VLDB Journal},
    year = {2024},
    url = {https://example.com},
    doi = {10.1234/test},
    abstract = {This is an abstract},
    pdf = {/path/to/pdf.pdf},
    keywords = {test, keyword},
    date-added = {2024-01-01},
    timestamp = {1234567890}
}
"""
    parser = BibTexParser()
    parser.customization = bibclean.customizations
    parser.ignore_nonstandard_types = False
    bib_db = parser.parse(bibtex_str)

    entry = bib_db.entries[0]
    removed_fields = ['url', 'doi', 'abstract', 'pdf', 'keywords', 'date-added', 'timestamp']

    for field in removed_fields:
        assert field not in entry, f"Field {field} should have been removed"


def test_conference_name_abbreviation():
    """Test that conference/journal names are abbreviated."""
    test_cases = [
        ("VLDB Journal", "VLDBJ"),
        ("International Conference on Very Large Data Bases", "VLDB"),
        ("Proceedings of the VLDB Endowment", "PVLDB"),
        ("ACM Transactions on Database Systems", "TODS"),
        ("SIGMOD International Conference", "SIGMOD"),
        ("Conference on Innovative Data Systems", "CIDR"),
    ]

    for full_name, expected_abbrev in test_cases:
        record = {
            'ENTRYTYPE': 'article',
            'journal': full_name,
            'author': 'Test Author',
            'title': 'Test',
            'year': '2024'
        }
        bibclean.fixConfJournal(record, "journal")
        assert record['journal'] == expected_abbrev, f"Expected {expected_abbrev}, got {record['journal']}"


def test_booktitle_abbreviation():
    """Test that booktitle field is also abbreviated (for inproceedings)."""
    record = {
        'ENTRYTYPE': 'inproceedings',
        'booktitle': "International Conference on Very Large Data Bases",
        'author': 'Test Author',
        'title': 'Test',
        'year': '2024'
    }
    bibclean.fixConfJournal(record, "booktitle")
    assert record['booktitle'] == "VLDB"


def test_paper_unwanted_fields():
    """Test that paper-specific fields are removed when is_for_paper is used."""
    bibtex_str = """
@article{Test2024,
    author = {John Doe},
    title = {Test Paper},
    journal = {ICDE},
    year = {2024},
    organization = {Test Org},
    ee = {https://example.com},
    pdfurl = {https://example.com/pdf}
}
"""
    parser = BibTexParser()
    parser.customization = bibclean.customizations
    parser.ignore_nonstandard_types = False
    bib_db = parser.parse(bibtex_str)

    entry = bib_db.entries[0]
    paper_fields = ['organization', 'ee', 'pdfurl']

    for field in paper_fields:
        assert field not in entry, f"Paper field {field} should have been removed"


def test_publisher_removed_for_non_books():
    """Test that publisher field is removed for articles but kept for books."""
    bibtex_str = """
@article{Test2024,
    author = {John Doe},
    title = {Test Paper},
    journal = {ICDE},
    year = {2024},
    publisher = {ACM}
}

@book{TestBook2024,
    author = {John Doe},
    title = {Test Book},
    year = {2024},
    publisher = {ACM}
}
"""
    parser = BibTexParser()
    parser.customization = bibclean.customizations
    parser.ignore_nonstandard_types = False
    bib_db = parser.parse(bibtex_str)

    article = bib_db.entries[0]
    book = bib_db.entries[1]

    assert 'publisher' not in article, "publisher should be removed from articles"
    assert 'publisher' in book, "publisher should be kept in books"
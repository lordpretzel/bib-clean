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


def test_longest_match_wins():
    """Test that a specific venue name beats a generic key that is a substring of it."""
    test_cases = [
        ("Proceedings of the 39th {ACM} {SIGMOD-SIGACT-SIGAI} Symposium on "
         "Principles of Database Systems", "PODS"),
        ("Proceedings of the seventeenth ACM SIGACT-SIGMOD-SIGART symposium on "
         "Principles of Database Systems", "PODS"),
        ("USENIX Symposium on Operating Systems Design and Implementation", "OSDI"),
        ("Proceedings of the 25th Symposium on Operating Systems Principles", "SOSP"),
        ("Data Engineering Workshops, 2006. Proceedings. 22nd International "
         "Conference on", "ICDEW"),
        ("Data Engineering (ICDE), 2013 IEEE 29th International Conference on", "ICDE"),
        ("Data Engineering", "IEEE Data Eng. Bull."),
        ("IEEE Data Engineering Bulletin", "IEEE Data Eng. Bull."),
        ("Knowledge Discovery in Databases: PKDD 2006", "PKDD"),
        ("Machine Learning and Knowledge Discovery in Databases - European "
         "Conference, {ECML} {PKDD} 2018", "ECML PKDD"),
        ("ACM SIGCOMM Computer Communication Review", "ACM SIGCOMM Comput. Commun. Rev."),
    ]

    for full_name, expected_abbrev in test_cases:
        record = {
            'ENTRYTYPE': 'inproceedings',
            'booktitle': full_name,
            'author': 'Test Author',
            'title': 'Test',
            'year': '2024'
        }
        bibclean.fixConfJournal(record, "booktitle")
        assert record['booktitle'] == expected_abbrev, f"Expected {expected_abbrev}, got {record['booktitle']}"


def test_braces_and_whitespace_are_ignored():
    """Test that braces and extra whitespace do not prevent a match."""
    test_cases = [
        ("{VLDB} J.", "VLDBJ"),
        ("{PVLDB}", "PVLDB"),
        ("  IEEE   Transactions   on   Software   Engineering  ", "TSE"),
        ("Neural Information Processing Systems ", "NeurIPS"),
    ]

    for full_name, expected_abbrev in test_cases:
        record = {'journal': full_name}
        bibclean.fixConfJournal(record, "journal")
        assert record['journal'] == expected_abbrev, f"Expected {expected_abbrev}, got {record['journal']}"


def test_unrelated_venues_are_left_alone():
    """Test that venues which merely contain a shortcut key are not renamed."""
    for full_name in [
        "Logics for databases and information systems",
        "Computer Science and Information Systems",
        "arXiv preprint arXiv:1211.6176",
        "International Journal of Software Engineering and Applications",
    ]:
        record = {'journal': full_name}
        bibclean.fixConfJournal(record, "journal")
        assert record['journal'] == full_name, f"Expected no change, got {record['journal']}"


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
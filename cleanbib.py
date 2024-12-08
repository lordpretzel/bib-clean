#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import sys
import os
import bibtexparser
import argparse as ap
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.customization import page_double_hyphen, convert_to_unicode

input = None
output_b = None
overwrite = False
VERSION = "0.1.1"

now = datetime.datetime.now()

# Let's define a function to customize our entries.
# It takes a record and return this record.

unwanted_fields = ["bdsk-file-1",
                   "bdsk-file-2",
                   "bdsk-url-1",
                   "crossref",
                   "doi",
                   "url",
                   "venueshort",
                   "abstract",
                   "file",
                   "gobbledegook",
                   "isbn",
                   "address",
                   "issn",
                   "issuedate",
                   "link",
                   "timestamp",
                   "keywords",
                   "keyword",
                   "date-added",
                   "date-modified",
                   "issue_date",
                   "dateadded",
                   "datemodified",
                   "acmid",
                   "bibsource",
                   "biburl",
                   "mendeley-tags",
                   "longversionurl",
                   "istoappear",
                   "isworkshop",
                   "annote",
                   "pmid",
                   "chapter",
                   "institution",
                   "location",
                   "series",
                   "issn",
                   "month",
                   "projects",
                   "pdf"]

paper_unwanted_fields = unwanted_fields + ["organization", "slideurl", "pdfurl", "bdskurla", "bdskurlb", "ee"]
is_for_paper = False

name_shortcuts = {
    "AAAI Conference on Artificial Intelligence": "AAAI",
    "AAAI": "AAAI",
    "ACM Computing Surveys": "CSUR",
    "CIKM": "CIKM",
    "CSUR": "CSUR",
    "Communications of the ACM": "CACM",
    "CIDR": "CIDR",
    "Conference on Innovative Data Systems": "CIDR",
    "Conference on Data Engineering": "ICDE",
    "Data Engineering Bulletin": "IEEE Data Eng. Bull.",
    "Data Warehousing and Knowledge Discovery": "DaWaK",
    "Database Systems for Advanced Applications": "DASFAA",
    "EDBT": "EDBT",
    "Extending Database Technology": "EDBT",
    "Human Factors in Computing Systems": "CHI",
    "ICDE": "ICDE",
    "ICDEAS": "IDEAS",
    "IPAW": "IPAW",
    "Information and Knowledge Management": "CIKM",
    "International Conference on Database Theory": "ICDT",
    "ICDT": "ICDT",
    "International Conference on Very Large Data Bases": "VLDB",
    "Journal of the ACM": "JACM",
    "Journal on Very Large Data Bases": "VLDBJ",
    "Knowledge and Data Engineering": "TKDE",
    "Knowl. Data Eng.": "TKDE",
    "PODS": "PODS",
    "PVDLB": "PVDLB",
    "Principles of database systems": "PODS",
    "Proc. VLDB Endow.": "PVLDB",
    "Proceedings of the VLDB Endowment": "PVLDB",
    "SIGMOD International Conference": "SIGMOD",
    "SIGMOD Conference": "SIGMOD",
    "SIGMOD Record": "SIGMOD Record",
    "SIGRAD": "SIGRAD",
    "SODA": "SODA",
    "Symposium on Discrete Algorithms": "SODA",
    "Theory and Practice of Provenance": "TaPP",
    "Trans. Database Syst.": "TODS",
    "Transactions on Database Systems": "TODS",
    "UbiComp": "UbiComp",
    "Ubiquitous Computing": "UbiComp",
    "VLDB J.": "VLDBJ",
    "VLDB Journal": "VLDBJ",
    "VLDBJ": "VLDBJ",
    "Workshop on Ontologies and Information Systems for the Semantic Web": "ONISW",
    "e-Science": "eScience",
    "eScience": "eScience",
    "international conference on Management of data": "SIGMOD",
    "symposium on Theory of computing": "STOC",
    "SDM": "SDM",
    "SIAM International Conference on Data Mining": "SDM",
    "Architectural Support for Programming Languages and Operating Systems": "ASPLOS",
    "ASPLOS": "ASPLOS",
    "Symposium on Code Generation and Optimization": "CGO",
    "Conference on Virtual Execution Environments": "VEE",
    "International Symposium on Computer Architecture": "ISCA",
    "International Conference on Parallel Processing": "ICPP",
    "International Conference on Supercomputing": "ICS",
    "International Symposium on Microarchitecture": "MICRO",
    "Conference on Network Protocols": "ICNP",
    "International Symposium on Memory Systems": "MEMSYS",
    "High-Performance Computer Architecture": "HPCA",
    "Programming Language Design and Implementation": "PLDI",
    "International Conference on Cluster Computing": "CLUSTER",
    "ICML": "ICML",
    "International Conference on Machine Learning": "ICML",
    "KDD": "SIGKDD",
    "Journal of Machine Learning Research": "JMLR",
    "International Joint Conference on Artificial Intelligence": "IJCAI",
    "Advances in Neural Information Processing Systems": "NeurIPS",
    "Neural Information Processing Systems ": "NeurIPS",
    "NeurIPS": "NeurIPS",
    "International Conference on Data Mining": "ICDM",
    "Knowledge and information systems": "KAIS",
    "Conference on Fairness, Accountability, and Transparency": "FAT",
    "FAT": "FAT",
    "DASFAA": "DASFAA",
    "international conference on computer vision": "ICCV",
    "ICCV": "ICCV",
    "Conference on Computer Vision and Pattern Recognition": "CVPR",
    "CVPR": "CVPR",
    "ICCV": "ICCV",
}

def fixConfJournal(record, fieldname):
    if fieldname in record:
        val = record[fieldname]
        for lname in name_shortcuts:
            if lname.lower() in val.lower():
                record[fieldname] = name_shortcuts[lname]


def customizations(record):
    """Use some functions delivered by the library
    :param record: a record
    :returns: -- customized record
    """
    record = type(record)
    record = page_double_hyphen(record)
    record = convert_to_unicode(record)
    # delete the following keys.
    if paper_unwanted_fields:
        unwanted = paper_unwanted_fields
    else:
        unwanted = unwanted_fields
    for val in unwanted:
        record.pop(val, None)
    if not(record['ENTRYTYPE'].lower() == 'book'):
        record.pop("publisher", None)
    fixConfJournal(record, "journal")
    fixConfJournal(record, "booktitle")
    return record


def shorten_conf_and_journal_names(record):
    return record

def checkArgs(opt):
    if not opt["input"] and not opt['bibstr']:
        raise Exception("Either need input file or bibtex string as input")
    if not opt['bibstr'] and not opt['overwrite'] and opt['output']:
        if os.path.exists(opt['output']):
            raise Exception(f"Output file {opt['output']} exists (specify -o to overwrite)")
    if (overwrite):
        opt['output'] = "_output.bib"

def readBibtex(opt):
    if opt['input']:
        print("parse bibtex file {}".format(opt['input']))
        with open(opt['input']) as bibtex_file:
            parser = BibTexParser()
            parser.customization = customizations
            parser.ignore_nonstandard_types = False
            return bibtexparser.load(bibtex_file, parser=parser)
    else:
        parser = BibTexParser()
        parser.customization = customizations
        parser.ignore_nonstandard_types = False
        return parser.parse(opt['bibstr'])


def fail(err):
    now = datetime.datetime.now()
    errstr = "{0} {1}".format(now, err)
    print(errstr)
    sys.exit(errstr)


def checkBibDatabase(opt):
    if opt['input']:
        if opt['bib_database']:
            now = datetime.datetime.now()
            success = "{0} Loaded {1} found {2} entries".format(
                now, opt['input'], len(opt['bib_database'].entries))
            print(success)
        else:
            fail(f"Failed to read {opt['input']}")
    else:
        if not ('bib_database' in opt):
            fail(f"Failed to parse {opt['bibstr']}")


def createBibtexString(opt):
    writer = BibTexWriter()
    writer.order_entries_by = ('author', 'year', 'type')
    return bibtexparser.dumps(opt['bib_database'], writer)


def writeBibtex(opt):
    opt['bibtex_str'] = createBibtexString(opt)
    # print(str(bibtex_str))
    with open(opt['output'], "w") as text_file:
        print(opt['bibtex_str'], file=text_file)
    if opt['bibtex_str']:
        now = datetime.datetime.now()
        success = "{0} Wrote to {1} with len {2}".format(
            now, opt['output'], len(opt['bibtex_str']))
        print(success)
        if opt['overwrite']:
            os.remove(opt['input'])
            os.rename(opt['output'], opt['input'])
            print("overwrote original file {}".format(opt['input']))
    else:
        now = datetime.datetime.now()
        errs = "{0} Failed to write {1}".format(now, opt['output'])
        print(errs)
        sys.exit(errs)


def printBibtex(opt):
    opt['bibtex_str'] = createBibtexString(opt)
    print(opt['bibtex_str'])


def outputBibtex(opt):
    if opt['bib_database']:
        if opt['output']:
            writeBibtex(opt)
        else:
            printBibtex(opt)


def parseOpts():
    parser = ap.ArgumentParser(prog="cleanbib",
                               description=f'cleanbib [{VERSION}] Clean up bibtex entries by removing fields and abbreviating conference and journal names.')
    parser.add_argument('-i', '--input', default=None, help="Input bibtex file to clean")
    parser.add_argument('-o', '--output', default=None, help="Write cleaned bibtex entries to this file.")
    parser.add_argument("-O", '--overwrite', default=True, help="Overwrite output file if it exists?")
    parser.add_argument("-s", '--bibstr', default=None, help="clean this string instead of reading from an input file.")
    parser.add_argument('-p', '--for-paper', type=bool, default=True, help="for papers (removes more fields")

    try:
        options = parser.parse_args()
        options = vars(options)
        checkArgs(options)
        return options
    except Exception as e:
        parser.print_usage()
        print("Exception {}\n\n{}\n", type(e), e.args)
        sys.exit(2)

def main():
    options = parseOpts()

    options['bib_database'] = readBibtex(options)
    checkBibDatabase(options)

    outputBibtex(options)


if __name__ == '__main__':
    main()

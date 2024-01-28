#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import getopt
import sys
import os
import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.customization import *

input_b = None
output_b = None
overwrite = False

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
    "NeurIPS": "NIPS",
    "Conference on Neural Information Processing Systems": "NIPS",
    "NIPS": "NIPS",
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
    "Advances in Neural Information Processing Systems": "NIPS",
    "Neural Information Processing Systems ": "NIPS",
    "International Conference on Data Mining": "ICDM",
    "Knowledge and information systems": "KAIS"
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
    if (not "input_b" in opt) and (not 'bibstr' in opt):
        print(opt)
        print(help)
        sys.exit(2)
    if ((not 'bibstr' in opt) and opt['overwrite'] is False and (not 'output_b' in opt)):
        print(opt)
        print(help)
        sys.exit(2)
    if (overwrite):
        opt['output_b'] = "_output.bib"


def readBibtex(opt):
    if 'input_b' in opt:
        print("parse bibtex file {}".format(opt['input_b']))
        with open(opt['input_b']) as bibtex_file:
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
    if 'input_b' in opt:
        if opt['bib_database']:
            now = datetime.datetime.now()
            success = "{0} Loaded {1} found {2} entries".format(
                now, opt['input_b'], len(opt['bib_database'].entries))
            print(success)
        else:
            fail("Failed to read {1}".format(opt['input_b']))
    else:
        if not ('bib_database' in opt):
            fail("Failed to parse {1}".format(opt['bibstr']))


def createBibtexString(opt):
    writer = BibTexWriter()
    writer.order_entries_by = ('author', 'year', 'type')
    return bibtexparser.dumps(opt['bib_database'], writer)


def writeBibtex(opt):
    opt['bibtex_str'] = createBibtexString(opt)
    # print(str(bibtex_str))
    with open(opt['output_b'], "w") as text_file:
        print(opt['bibtex_str'], file=text_file)
    if opt['bibtex_str']:
        now = datetime.datetime.now()
        success = "{0} Wrote to {1} with len {2}".format(
            now, opt['output_b'], len(opt['bibtex_str']))
        print(success)
        if opt['overwrite']:
            os.remove(opt['input_b'])
            os.rename(opt['output_b'], opt['input_b'])
            print("overwrote original file {}".format(opt['input_b']))
    else:
        now = datetime.datetime.now()
        errs = "{0} Failed to write {1}".format(now, opt['output_b'])
        print(errs)
        sys.exit(errs)


def printBibtex(opt):
    opt['bibtex_str'] = createBibtexString(opt)
    print(opt['bibtex_str'])


def outputBibtex(opt):
    if opt['bib_database']:
        if 'output_b' in opt:
            writeBibtex(opt)
        else:
            printBibtex(opt)


help = "bib_clean -i input.bib -o output.bib [-p]aper [-O]verwrite [-s] string (pass bibtex input as string)"
options = {}

# read options
print(f"Options: {sys.argv}")

try:
    opts, args = getopt.getopt(sys.argv[1:], "i:o:pOhs:")
except getopt.GetoptError as e:
    print(help)
    print("Exception {}\n\n{}\n", type(e), e.args)
    sys.exit(2)

# defaults
options['overwrite'] = False
options['if_for_paper'] = False

# process options
for opt, arg in opts:
    if opt == "-i":
        options['input_b'] = arg
    elif opt == "-o":
        options['output_b'] = arg
    elif opt == "-p":  # for paper, remove more
        options['if_for_paper'] = True
    elif opt == "-O":
        options['overwrite'] = True
    elif opt == "-s":
        options['bibstr'] = arg
    elif opt == "-h":
        print(help)
        sys.exit(2)
    else:
        print("unknown option {}".format(opt))
        print(help)
        sys.exit(2)

# check args
checkArgs(options)

options['bib_database'] = readBibtex(options)
checkBibDatabase(options)

outputBibtex(options)

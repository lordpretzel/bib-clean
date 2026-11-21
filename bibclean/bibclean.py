#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import sys
import os
import re
import bibtexparser
import argparse as ap
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.customization import page_double_hyphen, convert_to_unicode

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
    "Extending Database Technology": "EDBT",
    "EDBT": "EDBT",
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
    "Neural Information Processing Systems": "NeurIPS",
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
    "European Conference on Computer Vision": "ECCV",
    "ECCV": "ECCV",
    "European Conference on Computer Systems": "EuroSys",
    "Data Management for End-to-End Machine Learning": "DEEM",
    "North American Chapter of the Association for Computational Linguistics: Human Language Technologies": "NAACL-HLT",
    "International Conference on Learning Representations": "ICLR",
    "Human-In-the-Loop Data Analytics": "HILDA",
    "ACM SIGKDD Conference on Knowledge Discovery and Data Mining": "SIGKDD",
    "ACM SIGPLAN International Conference on Programming Language Design and Implementation": "PLDI",
    "ACM SIGSAC Conference on Computer and Communications Security": "CCS",
    "ACM SIGIR Conference on Research and Development in Information Retrieval": "SIGIR",
    "ACM SIGPLAN Notices": "SIGPLAN",
    "ACM SIGPLAN": "SIGPLAN",
    "ACM SIGKDD": "SIGKDD",
    "ACM SIGSAC": "SIGSAC",
    "ACM SIGIR": "SIGIR",
    "ACM SIGCOMM": "SIGCOMM",
    "ACM SIGOPS": "SIGOPS",
    "ACM SIGACT": "SIGACT",
    "ACM SIGART": "SIGART",
    "ACM SIGMOD": "SIGMOD",
    "ACM Transactions on Intelligent Systems and Technology (TIST)": "TIST",
    "ACM Transactions on Programming Languages and Systems": "TOPLAS",
    "ACM Trans. Program. Lang. Syst.": "TOPLAS",
    "IEEE Transactions on Pattern Analysis and Machine Intelligence": "TPAMI",
    "IEEE Trans. Pattern Anal. Mach. Intell.": "TPAMI",
    "IEEE Transactions on Software Engineering": "TSE",
    "IEEE Trans. Software Eng.": "TSE",
    "IEEE Transactions on Computers": "TC",
    "IEEE Trans. Computers": "TC",
    "IEEE Transactions on Dependable and Secure Computing": "TDSC",
    "IEEE Trans. Dependable Sec. Comput.": "TDSC",
    "USENIX Security Symposium": "USENIX Security",
    "USENIX Security": "USENIX Security",
    "USENIX Network and Distributed System Security Symposium": "NDSS",
    "USENIX Symposium on Operating Systems Design and Implementation": "OSDI",
    "ACM SIGMOD-SIGACT-SIGART": "PODS",
    "ACM SIGMOD-SIGACT-SIGAI": "PODS",
    "ACM SIGACT-SIGMOD-SIGART": "PODS",
    "ACM SIGACT-SIGMOD": "PODS",
    "ACM SIGMOD Record": "SIGMOD Record",
    "SIGMOD Rec.": "SIGMOD Record",
    "ACM SIGPLAN Conference on Programming Language Design and Implementation": "PLDI",
    "Symposium on Operating Systems Design and Implementation": "OSDI",
    "Symposium on Operating Systems Principles": "SOSP",
    "Principles of Distributed Computing": "PODC",
    "Network and Distributed System Security Symposium": "NDSS",
    "IEEE Symposium on Security and Privacy": "IEEE S&P",
    "Journal of Computer and System Sciences": "J. Comput. Syst. Sci.",
    "Proceedings of the ACM on Management of Data": "Proc. ACM Manag. Data",
    "ACM Manag. Data": "Proc. ACM Manag. Data",
    "Lecture Notes in Computer Science": "LNCS",
    "Lecture Notes in Artificial Intelligence": "LNAI",
    "Theoretical Computer Science": "Theor. Comput. Sci.",
    "Electronic Notes in Theoretical Computer Science": "ENTCS",
    "Innovations in Theoretical Computer Science": "ITCS",
    "J. Mach. Learn. Res.": "JMLR",
    "Journal of Intelligent Information Systems": "J. Intell. Inf. Syst.",
    "Data & Knowledge Engineering": "Data Knowl. Eng.",
    "Distributed and Parallel Databases": "Distrib. Parallel Databases",
    "Foundations and Trends in Databases": "Found. Trends Databases",
    "Foundations and Trends in Machine Learning": "Found. Trends Mach. Learn.",
    "Future Generation Computer Systems": "FGCS",
    "Scientific and Statistical Database Management": "SSDBM",
    "Database and Expert Systems Applications": "DEXA",
    "Information and Software Technology": "IST",
    "Synthesis Lectures on Data Management": "Synth. Lect. Data Manag.",
    "Advances in Databases and Information Systems": "ADBIS",
    "Advances in Database and Information Systems": "ADBIS",
    "ACM SIGSOFT Software Engineering Notes": "ACM SIGSOFT Softw. Eng. Notes",
    "ACM SIGLOG News": "ACM SIGLOG News",
    "ACM SIGARCH Computer Architecture News": "ACM SIGARCH Comput. Archit. News",
    "ACM Transactions on Computational Logic": "TOCL",
    "ACM Trans. Comput. Log.": "TOCL",
    "ACM Transactions on Information Systems": "TOIS",
    "ACM Transactions on Internet Technology": "TOIT",
    "ACM Trans. Internet Techn.": "TOIT",
    "ACM Transactions on Software Engineering and Methodology": "TOSEM",
    "ACM Transactions on Storage": "ACM Trans. Storage",
    "ACM Transactions on Computer Systems": "TOCS",
    "ACM Trans. Comput. Syst.": "TOCS",
    "ACM Transactions on Algorithms": "TALG",
    "ACM Transactions on Intelligent Systems and Technology": "TIST",
    "ACM Trans. Intell. Syst. Technol.": "TIST",
    "ACM Transactions on Information and System Security": "TISSEC",
    "ACM Journal of Data and Information Quality": "JDIQ",
    "ACM J. Data Inf. Qual.": "JDIQ",
    "Journal of Visual Languages and Computing": "J. Vis. Lang. Comput.",
    "New Generation Computing": "New Gen. Comput.",
    "SIAM Journal on Computing": "SIAM J. Comput.",
    "Journal of Logic Programming": "J. Log. Program.",
    "Theory of Computing Systems": "Theory Comput. Syst.",
    "Concurrency and Computation": "Concurrency Comput. Pract. Exp.",
    "IBM Systems Journal": "IBM Syst. J.",
    "IEEE Intelligent Systems": "IEEE Intell. Syst.",
    "Information and Computation": "Inf. Comput.",
    "Information Processing Letters": "Inf. Process. Lett.",
    "Journal of Parallel and Distributed Computing": "J. Parallel Distrib. Comput.",
    "Science of Computer Programming": "Sci. Comput. Program.",
    "Software: Practice and Experience": "Softw. Pract. Exp.",
    "Software - Practice and Experience": "Softw. Pract. Exp.",
    "Journal of Grid Computing": "J. Grid Comput.",
    "IEEE Signal Processing Magazine": "IEEE Signal Process. Mag.",
    "Proceedings of the IEEE": "Proc. IEEE",
    "Nucleic Acids Research": "Nucleic Acids Res.",
    "Computing in Science": "Comput. Sci. Eng.",
    "Logical Methods in Computer Science": "Log. Methods Comput. Sci.",
    "Discrete and Computational Geometry": "Discrete Comput. Geom.",
    "Journal of Information and Data Management": "J. Inf. Data Manag.",
    "Statistical Methods in Medical Research": "Stat. Methods Med. Res.",
    "IEEE Transactions on Visualization and Computer Graphics": "TVCG",
    "IEEE Trans. Vis. Comput. Graph.": "TVCG",
    "IEEE Transactions on Parallel and Distributed Systems": "TPDS",
    "IEEE Transactions on Information Theory": "TIT",
    "Information Theory, IEEE Transactions on": "TIT",
    "IEEE Transactions on Knowledge Discovery from Data": "TKDD",
    "Pattern Analysis and Machine Intelligence": "TPAMI",
    "Computers, IEEE Transactions on": "TC",
    "Software Engineering, IEEE Transactions on": "TSE",
    "Acta Informatica": "Acta Inform.",
    "The Computer Journal": "Comput. J.",
    "Journal of Artificial Intelligence Research": "JAIR",
    "Expert Systems with Applications": "Expert Syst. Appl.",
    "IEEE Conference on Big Data": "IEEE Big Data",
    "International Conference on Big Data": "IEEE Big Data",
    "International Conference on Very Large Databases": "VLDB",
    "Very Large Data Bases": "VLDB",
    "VLDB": "VLDB",
    "PVLDB": "PVLDB",
    "Computer Aided Verification": "CAV",
    "Automata, Languages and Programming": "ICALP",
    "Automata, Languages, and Programming": "ICALP",
    "ACM Symposium on Cloud Computing": "SoCC",
    "Symposium on Cloud Computing": "SoCC",
    "IEEE/ACM International Conference on Software Engineering": "ICSE",
    "International Conference on Software Engineering": "ICSE",
    "International Conference on Automated Software Engineering": "ASE",
    "Automated Software Engineering": "ASE",
    "Foundations of Software Engineering": "FSE",
    "Empirical Methods in Natural Language Processing": "EMNLP",
    "Annual Meeting of the Association for Computational Linguistics": "ACL",
    "Artificial Intelligence and Statistics": "AISTATS",
    "World Wide Web Conference": "WWW",
    "Principles of Programming Languages": "POPL",
    "Database Programming Languages": "DBPL",
    "Logic Programming and Nonmonotonic Reasoning": "LPNMR",
    "Practical Aspects of Declarative Languages": "PADL",
    "Theory and Practice of Logic Programming": "TPLP",
    "Deductive and Object-Oriented Databases": "DOOD",
    "Cooperative Information Systems": "CoopIS",
    "Parallel and Distributed Information Systems": "PDIS",
    "International Conference on Information Systems": "ICIS",
    "Advanced Information Systems Engineering": "CAiSE",
    "Information Systems and Management of Data": "CISMOD",
    "Advances in Geographic Information Systems": "ACM-GIS",
    "Workshop on Information Quality in Information Systems": "IQIS",
    "International Conference on Knowledge Discovery and Data Mining": "SIGKDD",
    "IEEE International Conference on Data Engineering": "ICDE",
    "International Conference on Data Engineering": "ICDE",
    "Data Engineering": "IEEE Data Eng. Bull.",
    "ACM-SIAM Symposium on Discrete Algorithms": "SODA",
    "International Conference on High Performance Computing": "HPC",
    "Symposium on Logic in Computer Science": "LICS",
    "Symposium on Foundations of Computer Science": "FOCS",
    "Conference on Learning Theory": "COLT",
    "Advances in Cryptology": "CRYPTO",
    "Networked Systems Design and Implementation": "NSDI",
    "NSDI": "NSDI",
    "Data Management on New Hardware": "DaMoN",
    "Temporal Representation and Reasoning": "TIME",
    "Answer Set Programming": "ASP",
    "Conference on Concurrency Theory": "CONCUR",
    "International Conference on Distributed Computing Systems": "ICDCS",
    "International Conference on Cloud Computing Technology and Science": "CloudCom",
    "International Conference on Mining Software Repositories": "MSR",
    "International Symposium on Software Testing and Analysis": "ISSTA",
    "Annual Conference on Computer Science Logic": "CSL",
    "Mathematical Foundations of Computer Science": "MFCS",
    "International Conference on Distributed and Event-based Systems": "DEBS",
    "European Signal Processing Conference": "EUSIPCO",
    "Hawaii International Conference on System Sciences": "HICSS",
    "Workshop on the Web and Databases": "WebDB",
    "Conference on AI, Ethics, and Society": "AIES",
    "Data Engineering,": "ICDE",
    "Data Engineering (ICDE)": "ICDE",
    "Data Engineering Workshop": "ICDEW",
    "IEEE Data Engineering": "IEEE Data Eng. Bull.",
    "Technical Committee on Data Engineering": "IEEE Data Eng. Bull.",
    "Knowledge & Data Engineering": "TKDE",
    "ACM Transactions on Knowledge Discovery from Data": "TKDD",
    "TKDD": "TKDD",
    "PKDD": "PKDD",
    "ICDEW": "ICDEW",
    "ICDE Workshops": "ICDEW",
    "ACM SIGKDD Explorations Newsletter": "ACM SIGKDD Explor. Newsl.",
    "SIGKDD Explor.": "ACM SIGKDD Explor. Newsl.",
    "Proc. VLDB Endow": "PVLDB",
    "Information Systems": "Inf. Syst.",
    "Information & Knowledge Management": "CIKM",
    "Logics for databases and information systems": "Logics for databases and information systems",
    "Computer Science and Information Systems": "Computer Science and Information Systems",
    "Seminal Contributions to Information Systems Engineering": "Seminal Contributions to Information Systems Engineering",
    "Web Information Systems Engineering": "WISE",
    "Machine Learning and Knowledge Discovery in Databases": "ECML PKDD",
    "ECML PKDD": "ECML PKDD",
    "ECML": "ECML",
    "ACM SIGCOMM Computer Communication Review": "ACM SIGCOMM Comput. Commun. Rev.",
    "ACM SIGOPS Operating Systems Review": "ACM SIGOPS Oper. Syst. Rev.",
    "ACM SIGACT News": "ACM SIGACT News",
    "Certified Programs and Proofs": "CPP",
    "CPP": "CPP",
    "Provenance and Annotation of Data and Processes": "IPAW",
    "Journal of Data and Information Quality": "JDIQ",
    "Journal of the American Statistical Association": "JASA",
    "Information Sciences": "Inf. Sci.",
}

def _normalize_name(name):
    """Strip braces, escapes and extra whitespace so that '{VLDB}' matches 'VLDB'.
    :param name: a venue name
    :returns: the name, lowercased and ready for substring matching
    """
    return re.sub(r"\s+", " ", name.replace("\\", "").replace("{", "").replace("}", "")).strip().lower()


# Longest keys first: a specific venue name must win over a generic key that
# happens to be a substring of it (e.g. "SIGMOD" inside "ACM SIGMOD-SIGACT-SIGART
# Symposium on Principles of Database Systems", which is PODS).
sorted_shortcuts = sorted(
    ((_normalize_name(key), shortcut) for key, shortcut in name_shortcuts.items()),
    key=lambda pair: len(pair[0]),
    reverse=True,
)


def fixConfJournal(record, fieldname):
    if fieldname in record:
        value = _normalize_name(record[fieldname])
        for lname, shortcut in sorted_shortcuts:
            if lname in value:
                record[fieldname] = shortcut
                break


def customizations(record):
    """Use some functions delivered by the library
    :param record: a record
    :returns: -- customized record
    """
    record = bibtexparser.customization.type(record)
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
    # if the user wants to overwrite the input file then set output to some
    # dummy filename
    if opt['overwrite'] and opt['input']:
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
    parser.add_argument("-O", '--overwrite', action='store_true', default=False, help="Overwrite input file (inplace)")
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

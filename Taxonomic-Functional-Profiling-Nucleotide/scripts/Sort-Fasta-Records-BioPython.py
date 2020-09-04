import argparse
import logging
import re
from Bio import SeqIO

def get_args():
    """
    Get arguments from command line with argparse.
    """
    parser = argparse.ArgumentParser(
        prog='Sort-Fasta-Records-Biopython.py',
        description="""Sort all entries in a fasta file by order of record name.""")

    parser.add_argument("-f", "--fasta",
                        required=True,
                        help="The FASTA file to sort.")
                        
    parser.add_argument("-o", "--outfile",
                        required=True,
                        help="The name of the output FASTA file (example: output.fasta).")
                        
    parser.add_argument("-l", "--logfile",
                        required=True,
                        help="The name of the log file to write.")

    return parser.parse_args()

def setup_logging(logfile):
    # set up logging to file
    logging.basicConfig(filename=logfile,
                        format="%(levelname)s: %(asctime)s: %(message)s",
                        datefmt='%d-%b-%y %H:%M:%S',
                        level=logging.DEBUG)

def index_fasta(f):
    """
    Use SeqIO to index the fasta file (f), which may be too big
    to parse into a list. Returns a dictionary-like structure,
    with seq names as keys and seqs as values.

    :param f: path to fasta file
    :return: dictionary-like structure of fasta records
    """
    logging.info("index_fasta: Beginning to index fasta file.")
    records = SeqIO.index(f, "fasta")
    logging.info("index_fasta: Found {:,} records.".format(len(records)))
    logging.info("index_fasta: Completed indexing.")

    return records

def sort_records(records):
    """
    Returns a sorted list of the sequence names in fasta.

    :param records: records obtained from index_fasta
    :return: list of sorted sequence names
    """
    logging.info("sort_records: Beginning sequence name sorting.")
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    ordered_names = sorted(list(records), key = alphanum_key)
    logging.info("sort_records: Completed sorting.")
    #for n in ordered_names:
    #    print("{:,}".format(int(n.split('/')[1])))
    return ordered_names

def write_records(records, ordered_names, outfile):
    """
    Write output fasta.
    :param records: dictionary-like structure from index_fasta
    :param ordered_names: list of sequence names, in sorted order
    :param outfile: name of output file to write
    :return: None
    """
    logging.info("write_records: Beginning to write fasta file.")
    rec_list = []
    rec_count = int(1)
    with open(outfile, 'a') as fhout:
        for n in ordered_names:
            rec_list.append(records[n].format("fasta"))
            if len(rec_list) > 50000:
                fhout.write("".join(rec_list))
                rec_list = []
            rec_count += 1
        fhout.write("".join(rec_list))
            
    logging.info("write_records: Completed writing.")


def main():
    args = get_args()
    setup_logging(args.logfile)
    records = index_fasta(args.fasta)
    ordered_names = sort_records(records)
    write_records(records, ordered_names, args.outfile)

if __name__ == '__main__':
    main()

import argparse
import logging
from Bio import SeqIO

def get_args():
    """
    Get arguments from command line with argparse.
    """
    parser = argparse.ArgumentParser(
        prog='Sort-Fasta-Records-by-SAM-BioPython.py',
        description="""Sort all entries in a fasta file by order of a read names text file.""")

    parser.add_argument("-f", "--fasta",
                        required=True,
                        help="The FASTA file to sort.")

    parser.add_argument("-r", "--reads",
                        required=True,
                        help="The reads file to sort by.")

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
    Use SeqIO to index the fasta file (f). Returns a
    dictionary-like structure, with seq names as keys and
    seqs as values.

    :param f: path to fasta file
    :return records: dictionary-like structure of fasta records
    """
    logging.info("index_fasta: Beginning to index fasta file.")
    records = SeqIO.index(f, "fasta")
    logging.info("index_fasta: Found {:,} records.".format(len(records)))
    logging.info("index_fasta: Completed indexing.\n")

    return records

def write_records(records, infile, outfile):
    """
    Write output fasta.
    :param records: dictionary-like structure from index_fasta
    :param infile: read names text file
    :param outfile: name of output file to write
    :return: None
    """
    logging.info("write_records: Writing new sorted fasta file.")
    rec_count = int(0)
    with open(infile, 'r') as fh_in, open(outfile, 'a') as fh_out:
        for line in fh_in:
            rec_count += 1
            if line.strip() in records:
                fh_out.write(records[line.strip()].format("fasta"))
            else:
                logging.warning("write_records: Read name from SAM not found in fasta: {}.".format(line.strip()))
            if rec_count % 10000 == 0:
                logging.info("write_records: Wrote {:,} records.".format(rec_count))
            
    logging.info("write_records: Completed writing.")

def main():
    args = get_args()
    setup_logging(args.logfile)
    records = index_fasta(args.fasta)
    write_records(records, args.reads, args.outfile)

if __name__ == '__main__':
    main()

import argparse
import logging
import re
from Bio import SeqIO

def get_args():
    """
    Get arguments from command line with argparse.
    """
    parser = argparse.ArgumentParser(
        prog='Parse-SAM.py',
        description="""Get ordered unique read names in SAM file.""")

    parser.add_argument("-s", "--sam",
                        required=True,
                        help="The SAM file to sort by.")

    parser.add_argument("-o", "--outfile",
                        required=True,
                        help="The name of the output reads file (example: output.fasta).")
                        
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

def parse_sam(sam, outfile):
    """
    Simply read the sorted SAM file line by line to obtain
    all unique read names (qnames). This list will be used to
    write the reads fasta in the order of the SAM, and only
    including reads with alignments.

    :param s: path to SAM file
    :param outfile: output file name
    :return: list of read names
    """
    logging.info("parse_sam: Beginning SAM parsing.")
    lcnt = int(0)
    unique_reads = set()
    with open(sam, 'r') as fh_in, open(outfile, 'a') as fh_out:
        for line in fh_in:
            if not line.startswith('@'):
                lcnt += 1
                if lcnt % 50000 == 0:
                    logging.info("parse_sam: processed {:,} alignments...".format(lcnt))
                if line.split('\t')[0] not in unique_reads:
                    unique_reads.add(line.split('\t')[0])
                    fh_out.write("{}\n".format(line.split('\t')[0]))
    logging.info("parse_sam: Found {:,} unique read names in SAM file.".format(len(unique_reads)))

def main():
    args = get_args()
    setup_logging(args.logfile)
    parse_sam(args.sam, args.outfile)

if __name__ == '__main__':
    main()

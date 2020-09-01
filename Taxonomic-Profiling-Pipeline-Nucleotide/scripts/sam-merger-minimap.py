import argparse
import logging

def get_args():
    """
    Get arguments from command line with argparse.
    """
    parser = argparse.ArgumentParser(
        prog='sam-merger.py',
        description="""Merge a series of SAM format files from a chunked alignment pipeline.""")

    parser.add_argument("-i", "--infiles",
                        required=True,
                        nargs='+',
                        help="The SAM files to merge (include all file names "
                             "separated by spaces).")
    parser.add_argument("-o", "--outfile",
                        required=True,
                        help="The name of the output file (example: Merged.sam).")

    parser.add_argument("-l", "--logfile",
                        required=True,
                        help="The name of the log file to write.")

    return parser.parse_args()

def add_skeleton_header(outfile):
    """
    Writes a false @PG header to SAM to allow compatibility
    with sam2rma converter for MEGAN. Uses minimap2 header from
    the workflow.

    :param outfile: name of output SAM file to write to
    """
    with open(outfile, 'a') as fhout:
        fhout.write("@PG\tID:minimap2\tPN:minimap2\tVN:2.17-r941\t"
                    "CL:minimap2 -a --eqx -k 19 -w 10 -g 5000 -r 2000 "
                    "--lj-min-ratio 0.5 -A 2 -B 5 -O 5,56 -E 4,1 -z 400,50 -t 24 DATABASE FASTA\n")
    logging.info("Added sham @PG header to output SAM.")

def write_all_sams(samlist, outfile):
    """
    Writes all lines of SAM files included in list to output file,
    while excluding any lines with headers (start with @). Filters
    out CIGAR strings with illegal characters and omits row.
    
    :param samlist: list of SAM file names
    :param outfile: name of output SAM file to write to
    :return alncount: count of all alignments in SAM
    """
    alncount = int(0)
    for infile in samlist:
        with open(infile, 'r') as fhin, open(outfile, 'a') as fhout:
            for line in fhin:
                if not line.startswith("@") and len(line.split()) > 5:
                    fhout.write(line)
                    alncount += 1
        logging.info("Finished adding SAM: {}".format(infile))
    return alncount

def setup_logging(logfile):
    # set up logging to file
    logging.basicConfig(filename=logfile,
                        format="%(levelname)s: %(asctime)s: %(message)s",
                        datefmt='%d-%b-%y %H:%M:%S',
                        level=logging.DEBUG)

def main():
    args = get_args()
    setup_logging(args.logfile)
    logging.info("Starting SAM merge.")
    add_skeleton_header(args.outfile)
    alncount = write_all_sams(args.infiles, args.outfile)
    logging.info("Found {:,} total read alignments.".format(alncount))

if __name__ == '__main__':
    main()

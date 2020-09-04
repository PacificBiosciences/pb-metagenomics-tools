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

def good_cigar(legal, cigar):
    status = True
    for c in cigar:
        if c.isdigit() or c in legal:
            pass
        else:
            status = False
    return status

def write_header_sam(infile, outfile, legal):
    """
    Writes all lines of SAM file, including headers,
    to the output file. Filters out CIGAR strings with
    illegal characters and omits row.
    
    :param infile: name of first SAM file in series
    :param outfile: name of output file to write contents in
    :param legal: list of legal characters for CIGAR strings
    :return goodcount: count of alignments with valid CIGAR
    :return badcount: count of excluded alignments with invalid CIGAR
    """
    goodcount, badcount = int(0), int(0)
    with open(infile, 'r') as fhin, open(outfile, 'a') as fhout:
        for line in fhin:
            if line.startswith("@"):
                fhout.write(line)
            if not line.startswith("@") and len(line.split()) > 5:
                if good_cigar(legal, line.split()[5]):
                    goodcount += 1
                    fhout.write(line)
                else:
                    badcount+=1
    logging.info("Finished adding SAM: {}".format(infile))
    return goodcount, badcount
                            
def write_remainder_sams(samlist, outfile, legal):
    """
    Writes all lines of SAM files included in list to output file,
    while excluding any lines with headers (start with @). Filters
    out CIGAR strings with illegal characters and omits row.
    
    :param samlist: list of SAM file names
    :param outfile: name of output file to write contents in
    :param legal: list of legal characters for CIGAR strings
    :return goodcount: count of alignments with valid CIGAR
    :return badcount: count of excluded alignments with invalid CIGAR
    """
    goodcount, badcount = int(0), int(0)
    for infile in samlist:
        with open(infile, 'r') as fhin, open(outfile, 'a') as fhout:
            for line in fhin:
                if not line.startswith("@") and len(line.split()) > 5:
                    if good_cigar(legal, line.split()[5]):
                        goodcount += 1
                        fhout.write(line)
                    else:
                        badcount += 1
        logging.info("Finished adding SAM: {}".format(infile))
    return goodcount, badcount
    
def tally_counts(g1, g2, b1, b2):
    total = g1+g2+b1+b2
    pgood = round(((g1+g2) / float(total)) * 100, 5)
    pbad = round(((b1+b2) / float(total)) * 100, 5)
    logging.info("Found {:,} total read alignments.".format(total))
    logging.info("Found {:,} read alignments ({}%) contained valid CIGAR strings.".format(g1+g2, pgood))
    logging.info("Found {:,} read alignments ({}%) contained illegal CIGAR strings.".format(b1+b2, pbad))

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
    legal = ["M", "I", "D", "N", "S", "H", "P", "=", "X"]
    g1, b1 = write_header_sam(args.infiles[0], args.outfile, legal)
    g2, b2 = write_remainder_sams(args.infiles[1:], args.outfile, legal)
    tally_counts(g1, g2, b1, b2)

if __name__ == '__main__':
    main()

import argparse
import os
def get_args():
    """
    Get arguments from command line with argparse.
    """
    parser = argparse.ArgumentParser(
        prog='CheckM-to-batch-GTDB.py',
        description="""Screen o2 format from CheckM to provide batch input file to GTDB.""")

    parser.add_argument("-i", "--infile",
                        required=True,
                        help="The o2 format summary file from CheckM.")
    parser.add_argument("-c", "--completeness",
                        required=False,
                        type=float,
                        default=60.0,
                        help="The minimum threshold for completeness (integer; a percent).")
    parser.add_argument("-m", "--contamination",
                        required=False,
                        type=float,
                        default=10.0,
                        help="The maximum threshold for contamination (integer; a percent).")
    parser.add_argument("-g", "--contigs",
                        required=False,
                        type=float,
                        default=10.0,
                        help="The maximum number of contigs allowed in a genome bin (integer).")
    parser.add_argument("-p", "--binpath",
                        required=True,
                        help="The path to the bins (do not include final / in path).")
    parser.add_argument("-o", "--outfile",
                        required=True,
                        help="The name of the output file.")
    parser.add_argument("-l", "--logfile",
                        required=True,
                        help="The name of the log file.")

    return parser.parse_args()

def parse_summary(infile, completeness, contamination, contigs, binpath, outfile):
    """
    Screens summary file to identify bins with particular thresholds
    of completeness, contamination, and contigs.

    :param infile: full path to o2 format summary file from CheckM
    :param completeness: minimum threshold for completeness
    :param contamination: maximum threshold for contamination
    :param contigs: maximum number of contigs allowed in a genome bin
    :return:
    """
    failed, passed = [], []
    with open(infile, 'r') as fhin, open(outfile, 'a') as fhout:
        next(fhin)
        for line in fhin:
            if len(line.split('\t')) > 12:
                cols = line.split('\t')
                if float(cols[5]) >= completeness \
                        and float(cols[6]) <= contamination \
                        and float(cols[11]) <= contigs:
                    fpath = os.path.join(os.getcwd(), binpath, cols[0]+'.fa')
                    if not os.path.isfile(fpath):
                        raise ValueError("{} is NOT valid!".format(fpath))
                    else:
                        print("{} is valid!".format(fpath))
                    fhout.write("{0}\t{1}\n".format(fpath, cols[0]))
                    passed.append("PASSED\t{}\t{}\t{}\t{}\t{}\t{}\n".format(cols[0], cols[5], cols[6],
                                                                          cols[7], cols[8], cols[11]))
                else:
                    failed.append("FAILED\t{}\t{}\t{}\t{}\t{}\t{}\n".format(cols[0], cols[5], cols[6],
                                                                          cols[7], cols[8], cols[11]))
    return passed, failed

def write_log(logfile, passed, failed):
    with open(logfile, 'a') as fh:
        fh.write("Filter\tBin\tCompletenes\tContamination\tStrainHeterogeneity\tGenomeSize\tContigs\n")
        for p in passed:
            fh.write(p)
        for f in failed:
            fh.write(f)

def main():
    args = get_args()
    passed, failed = parse_summary(args.infile, args.completeness, args.contamination,
                  args.contigs, args.binpath, args.outfile)
    write_log(args.logfile, passed, failed)

if __name__ == '__main__':
    main()

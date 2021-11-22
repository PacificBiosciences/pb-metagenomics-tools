import argparse
import os

def get_args():
    """
    Get arguments from command line with argparse.
    """
    parser = argparse.ArgumentParser(
        prog='CheckBins.py',
        description="""Add circular contigs to bins.""")

    parser.add_argument("-f", "--full",
                        required=True,
                        help="Full path to the input tsv file for DAS_Tool.")
    parser.add_argument("-l", "--lincirc",
                        required=True,
                        help="Full path to the input tsv file for DAS_Tool.")
    parser.add_argument("-o", "--outfile",
                        required=True,
                        help="Name of output completion file.")
    return parser.parse_args()

def evaluate_bins(full, lincirc, outfile):

    if os.stat(full).st_size == 0 and os.stat(lincirc).st_size == 0:
        raise ValueError("\n\nFiles {} and {} are both empty.\nThis means no bins were produced "
                         "by MetaBat2.\nCheck the assembly or assembly graph to ensure high-quality "
                         "contigs are present.\n".format(full, lincirc))

    elif os.stat(full).st_size == 0 and os.stat(lincirc).st_size > 0:
        bins = set()
        with open(lincirc, 'r') as fh:
            for line in fh:
                bins.add(line.split('\t')[-1])
        lins = [x for x in list(bins) if x.split('.')[1] == "lin"]
        circs = [x for x in list(bins) if x.split('.')[1] == "circ"]

        if len(circs) > 0 and len(lins) == 0:
            print("\nWARNING: Only circular contigs were binned (n={} bins); these\n"
                  "\tcould represent plasmid or viral sequences.\n"
                  "\tDAS_Tool may fail!\n".format(len(circs)))
        elif len(circs) == 0 and len(lins) > 0:
            print("\nWARNING: Bins were only found for a subset of linear contigs (n={} bins).\n"
                  "\tThis behavior is unexpected.\n".format(len(lins)))
        elif len(circs) > 0 and len(lins) > 0:
            print("\nWARNING: No bins were recovered for the full contig set,\n"
                  "\tbut circular contig bins (n={} bins) and\n"
                  "\tlinear contig bins (n={} bins) were found.\n"
                  "\tThis behavior is unexpected.\n".format(len(circs), len(lins)))

    elif os.stat(full).st_size > 0 and os.stat(lincirc).st_size == 0:
        print("\nWARNING: Bins were only found for the full set of contigs.\n"
              "\tNo circular contig bins or linear subset contig bins were found.\n"
              "\tThis behavior is unexpected.\n")

    elif os.stat(full).st_size > 0 and os.stat(lincirc).st_size > 0:
        print("\nBins were found for both binning strategies.\n")

    with open(outfile, 'a') as fh:
        fh.write("Bin evaluation completed.")

def main():
    args = get_args()
    evaluate_bins(args.full, args.lincirc, args.outfile)

if __name__ == '__main__':
    main()


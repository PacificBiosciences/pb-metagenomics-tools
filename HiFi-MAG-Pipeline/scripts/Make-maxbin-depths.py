import argparse
import os

def get_args():
    """
    Get arguments from command line with argparse.
    """
    parser = argparse.ArgumentParser(
        prog='Make-maxbin-depths.py',
        description="""Filter JGI depths for maxbin.""")

    parser.add_argument("-i", "--infile",
                        required=True,
                        help="Path to JGI depth file.")
    parser.add_argument("-o", "--outfile",
                        required=True,
                        help="Name of output depth file.")
    return parser.parse_args()

def write_new_depth_file(input_depth_file, output_depth_file):
    """
    contigName      contigLen       totalAvgDepth   sludge.bam      sludge.bam-var
    s0.ctg000001c   4.13709e+06     61.7612 61.7612 103.936
    s1.ctg000002c   2.23849e+06     14.3086 14.3086 33.5774
    s2.ctg000003l   40246   10.6046 10.6046 38.4902
    s3.ctg000004l   461151  4.44724 4.44724 3.09768
    s4.ctg000005l   516089  30.5501 30.5501 65.15
    s5.ctg000006l   1.6986e+06      8.46604 8.46604 13.8984
    s2.ctg000007l   24711   0.643378        0.643378        0.229328
    s6.ctg000008l   31810   35.0132 35.0132 468.885
    s7.ctg000009c   3.24454e+06     200.377 200.377 1599.71
    """
    if os.path.exists(output_depth_file):
        print("Removing existing version of file.")
        os.remove(output_depth_file)

    with open(input_depth_file, 'r') as fh_in, open(output_depth_file, 'a') as fh_out:
        kept_count = int(0)
        for line in fh_in:
            if line.startswith("contigName"):
                pass
            else:
                fh_out.write("{}\t{}\n".format(line.split('\t')[0], line.split('\t')[2]))
                kept_count += 1
        print("Parsed {:,} contigs".format(kept_count))

def main():
    args = get_args()
    write_new_depth_file(args.infile, args.outfile)

if __name__ == '__main__':
    main()


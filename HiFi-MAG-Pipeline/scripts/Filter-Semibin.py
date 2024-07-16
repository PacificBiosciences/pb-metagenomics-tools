import argparse
import os
import shutil

def get_args():
    """
    Get arguments from command line with argparse.
    """
    parser = argparse.ArgumentParser(
        prog='Filter-SemiBin.py',
        description="""Identify any superbins (>100Mb) from semibin2 and move to a separate directory.""")
    parser.add_argument("-i", "--in_dir",
                        required=True,
                        help="The full path to the semibin2 bins directory.")
    parser.add_argument("-o", "--out_dir",
                        required=True,
                        help="The full path to the output directory.")
    parser.add_argument("-f", "--outfile",
                        required=True,
                        help="Name of output file to write.")

    return parser.parse_args()

def make_dir(out_dir):
    os.makedirs(out_dir, exist_ok=True)

def filter_bin_files(in_dir, out_dir):
    mv_count = 0
    print("filter_bin_files: getting files")
    os.chdir(in_dir)
    fasta_files = [f for f in os.listdir('.') if f.endswith((".fa", ".fasta"))]
    print("filter_bin_files: removing large (>100Mb) files")
    for f in fasta_files:
        if os.path.getsize(f) >= 100000000:
            print("\tMoved file {}: {:,} bytes".format(f, os.path.getsize(f)))
            mv_count += 1
            shutil.move(f, os.path.join(out_dir, f))
    print("filter_bin_files: Identified {} super bins".format(mv_count))

    return mv_count

def write_outfile(outfile, mv_count, out_dir):
    print("write_outfile: Writing output file.")
    with open(outfile, 'w') as fh:
        fh.write("Identified {} super bins\nFile(s) located in: {}".format(mv_count, out_dir))

def main():
    args = get_args()
    make_dir(args.out_dir)
    mv_count = filter_bin_files(args.in_dir, args.out_dir)
    write_outfile(args.outfile, mv_count, args.out_dir)

if __name__ == '__main__':
    main()
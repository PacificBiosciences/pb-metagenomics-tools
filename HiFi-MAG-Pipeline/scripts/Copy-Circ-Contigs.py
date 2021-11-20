import argparse
import os
from Bio import SeqIO

def get_args():
    """
    Get arguments from command line with argparse.
    """
    parser = argparse.ArgumentParser(
        prog='Copy-Circ-Contigs.py',
        description="""Add circular contigs to bins.""")

    parser.add_argument("-f", "--fasta",
                        required=True,
                        help="Full path to the input fasta file.")
    parser.add_argument("-s", "--sample",
                        required=True,
                        help="Name of sample.")
    parser.add_argument("-o1", "--outdir",
                        required=True,
                        help="Name of output directory.")
    parser.add_argument("-o2", "--outfile",
                        required=True,
                        help="Name of output completion file.")
    return parser.parse_args()

def write_bins(fasta, sample, outdir):
    """
    outdir = directory("3-metabat-bins/{sample}/")
    sample = sample
    /3-metabat-bins/SAMPLE/SAMPLE_bin.1.fa
    """
    bin_count = int(1)
    for rec in SeqIO.parse(fasta, "fasta"):
        outname = os.path.join(outdir, "{}_bin.circ.{}.fa".format(sample, bin_count))
        with open(outname, 'a') as fh:
            fh.write(rec.format("fasta"))
        bin_count += 1

def main():
    args = get_args()
    if os.stat(args.fasta).st_size == 0:
        pass
    else:
        write_bins(args.fasta, args.sample, args.outdir)
    with open(args.outfile, 'a') as fh:
        fh.write("Completed.")

if __name__ == '__main__':
    main()


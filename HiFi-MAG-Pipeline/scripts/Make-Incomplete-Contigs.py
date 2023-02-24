import argparse
import os
import shutil
from Bio import SeqIO

def get_args():
    """
    Get arguments from command line with argparse.
    """
    parser = argparse.ArgumentParser(
        prog='Make-Incomplete-Contigs.py',
        description="""Identify long complete contigs from checkm2 scores.""")
    parser.add_argument("-i", "--input_fasta",
                        required=True,
                        help="The input contigs fasta file.")
    parser.add_argument("-p", "--passed_bins",
                        required=True,
                        help="Name of file with list of passed bins.")
    parser.add_argument("-f", "--output_fasta",
                        required=True,
                        help="Name of output contigs fasta file.")
    parser.add_argument("-d", "--fastadir",
                        required=True,
                        help="Name of directory with long bin fastas.")
    parser.add_argument("-o", "--outdir",
                        required=True,
                        help="Name of output directory to copy passed long bins.")
    return parser.parse_args()

def make_outdir(outdir):
    if not os.path.exists(outdir):
        os.makedirs(outdir, exist_ok=True)

def get_complete_bins(passed_bins):
    """
    s4.ctg000005c	complete.1
    s8.ctg000009c	complete.3
    s9.ctg000010c	complete.4
    """
    print("get_complete_bins: Gathering names of complete contigs.")
    with open(passed_bins, 'r') as fh:
        complete_contigs = [line.split('\t')[0] for line in fh]
    with open(passed_bins, 'r') as fh:
        complete_bin_names = [line.strip().split('\t')[1] for line in fh]
    print("get_complete_bins: Found {} complete contigs.".format(len(complete_contigs)))
    return complete_contigs, complete_bin_names

def write_output_contig_fasta(input_fasta, complete_contigs, output_fasta):
    print("write_output_contig_fasta: Writing output fasta file.")
    recs, incomplete_count = 0, 0
    if os.path.exists(output_fasta):
        os.remove(output_fasta)
    with open(output_fasta, 'a') as fh:
        for rec in SeqIO.parse(input_fasta, "fasta"):
            recs += 1
            if rec.id not in complete_contigs:
                incomplete_count += 1
                fh.write(rec.format("fasta"))
    print("write_output_contig_fasta: Found {:,} contigs in input fasta file.".format(recs))
    print("write_output_contig_fasta: Wrote {:,} contigs to output fasta file.".format(incomplete_count))

def write_long_bins(fastadir, outdir, complete_bin_names):
    """
    Write passed long bins to output directory.
    """
    print("write_long_bins: Writing passed long bin files.")
    bin_count = 0
    if complete_bin_names:
        for bin in complete_bin_names:
            shutil.copy(os.path.join(fastadir, "{}.fa".format(bin)), outdir)
            bin_count += 1
        print("write_long_bins: Wrote {:,} passed long bin files.".format(bin_count))
    else:
        print("write_long_bins: No long bin files passed filters, skipping copy.".format(bin_count))

def main():
    args = get_args()
    make_outdir(args.outdir)
    complete_contigs, complete_bin_names = get_complete_bins(args.passed_bins)
    write_output_contig_fasta(args.input_fasta, complete_contigs, args.output_fasta)
    write_long_bins(args.fastadir, args.outdir, complete_bin_names)

if __name__ == '__main__':
    main()



import argparse
import os
import shutil
import pandas as pd

def get_args():
    """
    Get arguments from command line with argparse.
    """
    parser = argparse.ArgumentParser(
        prog='Copy-consolidated-bins.py',
        description="""Copy consolidated bins to final directory.""")
    parser.add_argument("-t", "--tsv",
                        required=True,
                        help="Name of consolidated summary tsv.")
    parser.add_argument("-i1", "--indir1",
                        required=True,
                        help="The path to directory containing fasta files for bins1.")
    parser.add_argument("-i2", "--indir2",
                        required=True,
                        help="The path to directory containing fasta files for bins1.")
    parser.add_argument("-c", "--consolidation_method",
                        required=True,
                        choices=["unify", "bins1", "bins2"],
                        help="Strategy to select mixed bins. See documentation.")
    parser.add_argument("-o", "--outdir",
                        required=True,
                        help="Path of directory to write output files.")
    parser.add_argument("-e", "--extension",
                        required=False,
                        default="fa",
                        help="Fasta extension to use for final fasta files.")
    parser.add_argument("-l1", "--label1",
                        required=False,
                        default="bins1",
                        help="Prefix to use for final fasta files.")
    parser.add_argument("-l2", "--label2",
                        required=False,
                        default="bins2",
                        help="Fasta extension to use for final fasta files.")
    return parser.parse_args()

def make_outdir(outdir):
    if not os.path.exists(outdir):
        os.makedirs(outdir, exist_ok=True)

def identify_bin_sources(f, consolidation_method):
    """
    Make dataframe from SAMPLE_unified.comparison_summary.txt file and
    identify correct bin sources across assignment categories.
    """
    df = pd.read_csv(f, sep='\t')

    unique1 = df[(df["bin1_category"] == "Unique")]["bin1_name"].to_list()
    unique2 = df[(df["bin2_category"] == "Unique")]["bin2_name"].to_list()
    identical = df[(df["bin1_category"] == "Identical")]["bin1_name"].to_list()
    superset1 = df[(df["bin1_category"] == "Superset")]["bin1_name"].to_list()
    superset2 = df[(df["bin2_category"] == "Superset")]["bin2_name"].to_list()

    if consolidation_method == "bins1":
        mixed1 = df[(df["bin1_category"] == "Mixed-HS")
                    | (df["bin1_category"] == "Mixed-MS")
                    | (df["bin1_category"] == "Mixed-LS")]["bin1_name"].to_list()
        mixed2 = []

    elif consolidation_method == "bins2":
        mixed1 = []
        mixed2 = df[(df["bin2_category"] == "Mixed-HS")
                    | (df["bin2_category"] == "Mixed-MS")
                    | (df["bin2_category"] == "Mixed-LS")]["bin2_name"].to_list()

    elif consolidation_method == "unify":
        mixed1, mixed2 = [], []
        filtered_dict = df[(df["bin1_category"] == "Mixed-HS")
                           | (df["bin1_category"] == "Mixed-MS")
                           | (df["bin1_category"] == "Mixed-LS")].to_dict(orient="index")

        for k, v in filtered_dict.items():
            if v["bin1_completeness"] >= v["bin2_completeness"]:
                mixed1.append(v["bin1_name"])
            elif v["bin1_completeness"] < v["bin2_completeness"]:
                mixed2.append(v["bin2_name"])

    print("Identical = {}".format(len(identical)))
    print("Superset1 = {}".format(len(superset1)))
    print("Superset2 = {}".format(len(superset2)))
    print("Mixed1 = {}".format(len(mixed1)))
    print("Mixed2 = {}".format(len(mixed2)))
    print("Unique1 = {}".format(len(unique1)))
    print("Unique2 = {}".format(len(unique2)))

    bins1_names = identical + superset1 + mixed1 + unique1
    bins2_names = superset2 + mixed2 + unique2

    return bins1_names, bins2_names

def write_bins(bin_names, bin_dir, outdir, new_ext, label):
    """
    Write bins to output directory.
    """
    print("write_bins: Writing final bin files.")
    bin_cnt = 0
    if bin_names:
        if os.path.exists(os.path.join(bin_dir, "{}.fa".format(bin_names[0]))):
            old_ext = "fa"
        elif os.path.exists(os.path.join(bin_dir, "{}.fasta".format(bin_names[0]))):
            old_ext = "fasta"
        elif os.path.exists(os.path.join(bin_dir, "{}.fna".format(bin_names[0]))):
            old_ext = "fna"
        else:
            raise ValueError("Unrecognized file extension - only .fa, .fna, and .fasta are accepted.")

        for b in bin_names:
            shutil.copy(os.path.join(bin_dir, "{}.{}".format(b, old_ext)),
                        os.path.join(outdir, "{}_{}.{}".format(label, b, new_ext)))
            bin_cnt += 1
        print("write_bins: Wrote {:,} bin files.".format(bin_cnt))
    else:
        print("write_bins: No bins?.".format(bin_cnt))

def main():
    args = get_args()
    make_outdir(args.outdir)
    bins1_names, bins2_names = identify_bin_sources(args.tsv, args.consolidation_method)
    write_bins(bins1_names, args.indir1, args.outdir, args.extension, args.label1)
    write_bins(bins2_names, args.indir2, args.outdir, args.extension, args.label2)

if __name__ == '__main__':
    main()



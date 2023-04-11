import argparse
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def get_args():
    """
    Get arguments from command line with argparse.
    """
    parser = argparse.ArgumentParser(
        prog='Filter-Complete-Contigs.py',
        description="""Identify long complete contigs from checkm2 scores.""")
    parser.add_argument("-i", "--input_fasta",
                        required=True,
                        help="The input contigs fasta file.")
    parser.add_argument("-c", "--checkm",
                        required=True,
                        help="The checkm2 quality_report.tsv file.")
    parser.add_argument("-b", "--bins_contigs",
                        required=True,
                        help="Name of output file with bin number/contig names.")
    parser.add_argument("-l", "--length",
                        required=False,
                        type=int,
                        default=500000,
                        help="Minimum length of contigs.")
    parser.add_argument("-m", "--min_completeness",
                        required=False,
                        type=int,
                        default=93,
                        help="Minimum completeness score to select a contig.")
    parser.add_argument("-p", "--passed_bins",
                        required=True,
                        help="Name of output file with list of passed bins.")
    parser.add_argument("-p1", "--plot_scatter",
                        required=True,
                        help="Name of output scatterplot.")
    parser.add_argument("-p2", "--plot_histo",
                        required=True,
                        help="Name of output histogram.")

    return parser.parse_args()


def make_checkm_df(checkm):
    """
    Convert checkm2 quality_report.tsv file into pandas dataframe.
    """
    print("make_checkm_df: Making checkm2 dataframe.")
    return pd.read_csv(checkm, sep='\t')

def get_complete_bins(df, min_completeness):
    """
    Filter checkm2 dataframe to obtain a list of names of all bins with > minimum completeness value.
    Why is the default completeness 93? In binny they have it set it to 92.5, so some precendent.
    """
    print("get_complete_bins: Identifying bins with completeness > {}.".format(min_completeness))
    return df[(df['Completeness'] >= min_completeness)]['Name'].tolist()

def scatter_size_completeness(df, plot_scatter, min_completeness):
    """
    Create seaborn scatterplot of contig size vs. completeness.
    """
    print("scatter_size_completeness: Making scatterplot.")
    plt.figure(figsize=(10,10))
    ax = sns.scatterplot(x="Genome_Size", y="Completeness", data=df, hue=df["Completeness"], s=100, palette="PuOr",
                         alpha=0.6, edgecolor="black", linewidth=1)
    plt.title("Contig Size vs. Completeness", fontsize=16)
    ax.set_xlabel("Contig Size (Mb)", fontsize=16)
    ax.set_ylabel("Percent Completeness (CheckM2)", fontsize=16)
    ax.tick_params(labelsize=14)
    plt.axhline(y=min_completeness, color='black', linestyle='--')
    ax.figure.savefig(plot_scatter, bbox_inches='tight')
    plt.close()

def histo_completeness(df, plot_histo, min_completeness):
    """
    Create seaborn histogram of completeness scores.
    """
    print("histo_completeness: Making histogram.")
    fig, ax = plt.subplots(figsize=(10, 8))
    if df.shape[0] <= 1 or df.shape[0]*100 == df['Completeness'].sum():
        sns.histplot(data=df, x='Completeness')
    else:
        sns.histplot(data=df, x='Completeness', binwidth=1)
    plt.title("Completeness Scores", fontsize=16)
    ax.set_ylabel("Count", fontsize=16)
    ax.set_xlabel("Percent Completeness (CheckM2)", fontsize=16)
    ax.tick_params(labelsize=14)
    plt.axvline(x=min_completeness, color='black', linestyle='--')
    ax.figure.savefig(plot_histo, bbox_inches='tight')
    plt.close()

def make_bin_contig_dict(bins_contigs, bin_list, passed_bins):
    """
    Format of file is as follows:
    tempbin_1	s0.ctg000003l
    tempbin_2	s0.ctg000006l
    tempbin_3	s7.ctg000012l
    ...

    bin_contig_dict:
    [s0.ctg000003l] = tempbin_1
    [s0.ctg000006l] = tempbin_2
    """
    print("make_bin_contig_dict: Making bin-contig dictionary.")
    bin_contig_dict = {}
    with open(bins_contigs, 'r') as fh:
        for line in fh:
            if line.split('\t')[0] in bin_list:
                bin_contig_dict[line.strip().split('\t')[1]] = line.split('\t')[0]
                
    with open(passed_bins, 'a') as fh:
        for k,v in bin_contig_dict.items():
            fh.write("{}\t{}\n".format(k, v))

def main():
    args = get_args()
    df = make_checkm_df(args.checkm)
    bin_list = get_complete_bins(df, args.min_completeness)
    print("get_complete_bins: {:,} bins passed.".format(len(bin_list)))
    scatter_size_completeness(df, args.plot_scatter, args.min_completeness)
    histo_completeness(df, args.plot_histo, args.min_completeness)
    make_bin_contig_dict(args.bins_contigs, bin_list, args.passed_bins)
    print("\nFinished.")

if __name__ == '__main__':
    main()



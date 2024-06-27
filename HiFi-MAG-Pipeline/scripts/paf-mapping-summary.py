import argparse
import os
import pysam
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def get_args():
    """
    Get arguments from command line with argparse.
    """
    parser = argparse.ArgumentParser(
        prog='paf-mapping-summary.py',
        description="""Summarize mapped read counts in a PAF from minimap2.""")
    parser.add_argument("-p", "--paf",
                        required=True,
                        help="A PAF file resulting from minimap2.")
    parser.add_argument("-r", "--reads_fasta",
                        required=True,
                        help="Fasta file with the HiFi reads used for mapping.")
    parser.add_argument("-c", "--contig_list",
                        required=True,
                        help="Optional file containing contig names to search for (format: one contig per line).")
    parser.add_argument("-o1", "--out_plot",
                        required=True,
                        help="Name of output figure.")
    parser.add_argument("-o2", "--out_table",
                        required=True,
                        help="Name of output table.")
    parser.add_argument("-x", "--count",
                        required=False,
                        default=None,
                        help="Read number to skip fasta counting.")
    return parser.parse_args()

def get_paf_df(f):
    df = pd.read_csv(f, sep='\t', usecols=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                     names=['query_name', 'query_length', 'query_start', 'query_end',
                            'strand', 'target_name', 'target_length', 'target_start',
                            'target_end', 'matched_bases', 'total_bases', 'quality', 'aln_type'],
                     header=None)
    df['perc_identity'] = round((df['matched_bases'] / df['total_bases'] * 100), 1)
    df['perc_read_aligned'] = round(((df['query_end'] - df['query_start']) / df['query_length'] * 100), 1)
    return df

def get_paf_df_lite(f):
    print('\nget_paf_df_lite: reading paf file')
    df = pd.read_csv(f, sep='\t', usecols=[0, 1, 2, 3, 5, 9, 10, 12],
                     names=['query_name', 'query_length', 'query_start', 'query_end',
                            'target_name', 'matched_bases', 'total_bases', 'aln_type'],
                     header=None)
    df['perc_identity'] = round((df['matched_bases'] / df['total_bases'] * 100), 1)
    df['perc_read_aligned'] = round(((df['query_end'] - df['query_start']) / df['query_length'] * 100), 1)
    return df

def get_read_count(reads_fasta):
    print('get_read_count: reading fasta file')
    read_count = 0
#    with open(reads_fasta, 'r') as fh:
#        for line in fh:
#            if line.startswith('>'):
#                read_count += 1
    with pysam.FastxFile(reads_fasta) as fh:
        for entry in fh:
            read_count += 1
            if read_count % 200000 == 0:
                print("\t{:,} reads".format(read_count))
    print("\t{:,} reads".format(read_count))
    return read_count

def get_contig_names(contig_list):
    print('get_contig_names: gathering MAG contig names')
    with open(contig_list, 'r') as fh:
        contig_names = [line.strip() for line in fh]
    return contig_names

def make_percent(reads, total_reads):
    return round(((reads / total_reads) * 100), 1)

def count_mapped_reads(df, read_count, contig_names):
    print('count_mapped_reads: summarizing mappings')
    print("\nTotal reads used for mapping:\n\t{:,}".format(read_count))
    print("Total alignments:\n\t{:,}".format(df.shape[0]))
    print("Total reads mapped:\n\t{:,}\n".format(len(df['query_name'].unique())))

    # remove multiple entries for a read, keeping the one with the longest aln length
    df = df.sort_values('perc_read_aligned', ascending=False).drop_duplicates('query_name').sort_index()

    # create dict to store percent values for table and figure
    mapping_dict = {}
    mapping_dict["percent_ID"] = ["90%", "95%", "99%"]
    mapping_dict["contigs"] = [make_percent(df[(df['perc_read_aligned'] >= 90) & (df['perc_identity'] >= 90) &
                                               (df['aln_type'] == "tp:A:P")].shape[0], read_count)]
    mapping_dict["contigs"].append(make_percent(df[(df['perc_read_aligned'] >= 90) & (df['perc_identity'] >= 95) &
                                                   (df['aln_type'] == "tp:A:P")].shape[0], read_count))
    mapping_dict["contigs"].append(make_percent(df[(df['perc_read_aligned'] >= 90) & (df['perc_identity'] >= 99) &
                                                   (df['aln_type'] == "tp:A:P")].shape[0], read_count))
    mapping_dict["mags"] = [make_percent(df[(df["target_name"].isin(contig_names)) &
                                            (df['perc_read_aligned'] >= 90) & (df['perc_identity'] >= 90) &
                                            (df['aln_type'] == "tp:A:P")].shape[0], read_count)]
    mapping_dict["mags"].append(make_percent(df[(df["target_name"].isin(contig_names)) &
                                                (df['perc_read_aligned'] >= 90) & (df['perc_identity'] >= 95) &
                                                (df['aln_type'] == "tp:A:P")].shape[0], read_count))
    mapping_dict["mags"].append(make_percent(df[(df["target_name"].isin(contig_names)) &
                                                (df['perc_read_aligned'] >= 90) & (df['perc_identity'] >= 99) &
                                                (df['aln_type'] == "tp:A:P")].shape[0], read_count))

    return pd.DataFrame.from_dict(mapping_dict)

def make_palette(hex_code):
    return sns.color_palette(sns.light_palette(hex_code, input='rgb', as_cmap=False, n_colors=6).as_hex()[1:] +
                             sns.dark_palette(hex_code, input='rgb', as_cmap=False, n_colors=6).as_hex()[-2:0:-1])

def plot_mapped(df_plot, out_plot):
    print('\nplot_mapped: plotting figure')
    if os.path.exists(out_plot):
        os.remove(out_plot)

    pb_blue = make_palette("#1383C6")
    pb_green = make_palette("#009D4E")

    ax = df_plot.plot.bar(stacked=False, figsize=(6, 7), width=0.7, color=[pb_green[3], pb_blue[4]],
                          fontsize='x-large', edgecolor='black', linewidth=0.5, ylim=(0, 105))
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, ["Contigs", "MAGs"], bbox_to_anchor=(1, 0.99),
              fontsize='large', ncol=1, labelspacing=0.3)
    ax.set_xticklabels(df_plot['percent_ID'], rotation=0, ha='center', fontsize='x-large')
    for x, y in enumerate(df_plot["contigs"]):
        ax.annotate("{:,}".format(y), (x - 0.175, y + (0.02 * df_plot["contigs"].max())),
                    ha='center', color="black", fontweight="regular", fontsize='large')
    for x, y in enumerate(df_plot["mags"]):
        ax.annotate("{:,}".format(y), (x + 0.175, y + (0.02 * df_plot["mags"].max())),
                    ha='center', color="black", fontweight="regular", fontsize='large')
    ax.set_xlabel("Minimum percent ID threshold", fontsize="x-large")
    ax.set_ylabel("Percent reads mapped (%)", fontsize="x-large")
    ax.figure.savefig("{}".format(out_plot))
    plt.close()

def write_table(df_plot, out_table):
    if os.path.exists(out_table):
        os.remove(out_table)
    df_plot.to_csv("{}".format(out_table), index=False, sep='\t')

def main():
    args = get_args()
    df = get_paf_df_lite(args.paf)
    if args.count is None:
        read_count = get_read_count(args.reads_fasta)
    else:
        read_count = int(args.count)
    contig_names = get_contig_names(args.contig_list)
    df_plot = count_mapped_reads(df, read_count, contig_names)
    print(df_plot)
    plot_mapped(df_plot, args.out_plot)
    write_table(df_plot, args.out_table)

if __name__ == '__main__':
    main()



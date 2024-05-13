import argparse
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def get_args():
    """
    Get arguments from command line with argparse.
    """
    parser = argparse.ArgumentParser(
        prog='Plot-Qualities.py',
        description="""Make informative figures from pre- and post-filtered bins.""")
    parser.add_argument("-i1", "--input_tsv1",
                        required=True,
                        help="The filtered checkm2 quality tsv file 1.")
    parser.add_argument("-i2", "--input_tsv2",
                        required=True,
                        help="The filtered checkm2 quality tsv file 2.")
    parser.add_argument("-o1", "--output1",
                        required=True,
                        help="The name of output figure 1.")
    parser.add_argument("-o2", "--output2",
                        required=True,
                        help="The name of output figure 2.")
    parser.add_argument("-o3", "--output3",
                        required=True,
                        help="The name of output figure 3.")
    parser.add_argument("-o4", "--output4",
                        required=True,
                        help="The name of output figure 4.")
    parser.add_argument("-l1", "--label1",
                        required=False,
                        default="bins1",
                        help="Name to use for bins1.")
    parser.add_argument("-l2", "--label2",
                        required=False,
                        default="bins2",
                        help="Name to use for bins2.")
    return parser.parse_args()

def make_palette(hex_code):
    return sns.color_palette(sns.light_palette(hex_code, input='rgb', as_cmap=False, n_colors=6).as_hex()[1:] +
                             sns.dark_palette(hex_code, input='rgb', as_cmap=False, n_colors=6).as_hex()[-2:0:-1])

def make_tsv_df(tsv):
    print("make_tsv_df: making dataframe for: {}".format(tsv))
    return pd.read_csv(tsv, sep='\t')

def mod_tsv_df(df_tsv1, df_tsv2, label1, label2):
    print("mod_tsv_df: modifying dataframes...")
    df_tsv1['bin'] = df_tsv1["bin1_name"]
    df_tsv1['completeness'] = df_tsv1["bin1_completeness"]
    df_tsv1['contamination'] = df_tsv1["bin1_contamination"]
    df_tsv1['contigs'] = df_tsv1["bin1_contig_number"]
    df_tsv1['category'] = df_tsv1["bin1_category"]
    df_tsv1['size'] = df_tsv1["bin1_size"]
    df_tsv1['method'] = label1
    df_temp1 = df_tsv1[['bin', 'completeness', 'contamination', 'contigs', 'size', 'category', 'method']]

    df_tsv2['bin'] = df_tsv2["bin2_name"]
    df_tsv2['completeness'] = df_tsv2["bin2_completeness"]
    df_tsv2['contamination'] = df_tsv2["bin2_contamination"]
    df_tsv2['contigs'] = df_tsv2["bin2_contig_number"]
    df_tsv2['category'] = df_tsv2["bin2_category"]
    df_tsv2['size'] = df_tsv2["bin2_size"]
    df_tsv2['method'] = label2
    df_temp2 = df_tsv2[['bin', 'completeness', 'contamination', 'contigs', 'size', 'category', 'method']]

    df_mod = pd.concat([df_temp1, df_temp2], axis=0)

    return df_mod

def make_plot(df, y, title, label1, label2, output, col1, col2):
    print("make_plot: {}".format(title))
    plt.figure(figsize=(12,6))
    ax = sns.boxplot(data=df, x='category', y=y, hue="method", showfliers=False, linewidth=1.25,
                     order=["Identical", "Superset", "Subset", "Mixed-HS", "Mixed-MS", "Mixed-LS", "Unique"],
                     palette=[col1, col2])
    ax.set(xlabel='', ylabel='')
    plt.title(title, size='x-large')
    ax.set_ylabel(title, fontsize="x-large")
    ax.set_xticklabels(["Identical", "Superset", "Subset", "Mixed-HS", "Mixed-MS", "Mixed-LS", "Unique"],
                       rotation=0, ha='center', fontsize='x-large')
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, bbox_to_anchor=(1,0.99),
              fontsize='large', ncol=1, labelspacing=0.3)
    ax.figure.savefig("{}".format(output), bbox_inches='tight')
    plt.close()

def main():
    args = get_args()
    pb_magenta = make_palette("#DF1995")
    pb_teal = make_palette("#009CA2")
    pb_blue = make_palette("#1383C6")
    pb_orange = make_palette("#E16A2C")
    pb_green = make_palette("#009D4E")
    pb_purple = make_palette("#5F249F")

    df_tsv1 = make_tsv_df(args.input_tsv1)
    df_tsv2 = make_tsv_df(args.input_tsv2)
    df_mod = mod_tsv_df(df_tsv1, df_tsv2, args.label1, args.label2)
    make_plot(df_mod, "completeness", "Completeness (%)", args.label1, args.label2, args.output1, pb_teal[1], pb_blue[5])
    make_plot(df_mod, "contamination", "Contamination (%)", args.label1, args.label2, args.output2, pb_teal[1], pb_blue[5])
    make_plot(df_mod, "contigs", "Number of contigs", args.label1, args.label2, args.output3, pb_teal[1], pb_blue[5])
    make_plot(df_mod, "size", "Genome size", args.label1, args.label2, args.output4, pb_teal[1], pb_blue[5])

if __name__ == '__main__':
    main()


import argparse
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def get_args():
    """
    Get arguments from command line with argparse.
    """
    parser = argparse.ArgumentParser(
        prog='Plot-Main.py',
        description="""Make informative figures from pre- and post-filtered bins.""")
    parser.add_argument("-i1", "--input_tsv1",
                        required=True,
                        help="The filtered checkm2 quality tsv file 1.")
    parser.add_argument("-i2", "--input_tsv2",
                        required=True,
                        help="The filtered checkm2 quality tsv file 2.")
    parser.add_argument("-o1", "--output1",
                        required=True,
                        help="The name of the output file (a table).")
    parser.add_argument("-o2", "--output2",
                        required=True,
                        help="The name of the output file (a figure).")
    parser.add_argument("-l1", "--label1",
                        required=False,
                        default="bins1",
                        help="Name to use for bins1.")
    parser.add_argument("-l2", "--label2",
                        required=False,
                        default="bins2",
                        help="Name to use for bins2.")
    return parser.parse_args()

def get_bin_category_counts(tsv1, tsv2, outname, label1, label2):
    cat_count_dict = {}

    df1 = pd.read_csv(tsv1, sep='\t')
    df2 = pd.read_csv(tsv2, sep='\t')

    cat_count_dict[label1] = {"Total": df1.shape[0],
                               "Identical": df1[(df1["bin1_category"] == "Identical")].shape[0],
                               "Superset": df1[(df1["bin1_category"] == "Superset")].shape[0],
                               "Subset": df1[(df1["bin1_category"] == "Subset")].shape[0],
                               "Mixed-HS": df1[(df1["bin1_category"] == "Mixed-HS")].shape[0],
                               "Mixed-MS": df1[(df1["bin1_category"] == "Mixed-MS")].shape[0],
                               "Mixed-LS": df1[(df1["bin1_category"] == "Mixed-LS")].shape[0],
                               "Unique": df1[(df1["bin1_category"] == "Unique")].shape[0]}

    cat_count_dict[label2] = {"Total": df2.shape[0],
                               "Identical": df2[(df2["bin2_category"] == "Identical")].shape[0],
                               "Superset": df2[(df2["bin2_category"] == "Superset")].shape[0],
                               "Subset": df2[(df2["bin2_category"] == "Subset")].shape[0],
                               "Mixed-HS": df2[(df2["bin2_category"] == "Mixed-HS")].shape[0],
                               "Mixed-MS": df2[(df2["bin2_category"] == "Mixed-MS")].shape[0],
                               "Mixed-LS": df2[(df2["bin2_category"] == "Mixed-LS")].shape[0],
                               "Unique": df2[(df2["bin2_category"] == "Unique")].shape[0]}

    df_cat_count = pd.DataFrame.from_dict(cat_count_dict, orient='index')
    df_cat_count.to_csv(outname, sep='\t', index=True)

    return df_cat_count

def create_plot(df_cat_count, output, label1, label2):
    ax = df_cat_count[['Identical', 'Superset', 'Subset', 'Mixed-HS', 'Mixed-MS', 'Mixed-LS', 'Unique']].plot.bar(
        stacked=True, width=0.7, color=sns.color_palette("Spectral_r", 7), fontsize='x-large', edgecolor='black',
        linewidth=0.5, figsize=(5,10), ylim=(0, (1.1 * df_cat_count["Total"].max())))

    # for vertical plot, we need to reverse the legend labels, start by getting these objects
    handles, labels = ax.get_legend_handles_labels()

    # add reversed(handles) and reversed(labels) to the legend arguments
    # this controls the placement of the legend (bbox_to_anchor), as well as font (fontsize),
    # number of columns for labels (ncol), and spacing (labelspacing)
    ax.legend(reversed(handles), reversed(labels), bbox_to_anchor=(1, 0.99),
              fontsize='x-large', ncol=1, labelspacing=0.3)

    for x, y in enumerate(df_cat_count["Total"]):
        ax.annotate("{:,}".format(y), (x, y + (0.02 * df_cat_count["Total"].max())),
                    ha='center', color="black", fontsize='x-large')
    ax.set_ylabel("Total Bins", fontsize="xx-large")
    ax.set_xticklabels([label1, label2], rotation=45, ha='center', fontsize='xx-large')

    ax.figure.savefig("{}".format(output), bbox_inches='tight')

    plt.close()

def main():
    args = get_args()
    df_cat_count = get_bin_category_counts(args.input_tsv1, args.input_tsv2, args.output1, args.label1, args.label2)
    create_plot(df_cat_count, args.output2, args.label1, args.label2)

if __name__ == '__main__':
    main()


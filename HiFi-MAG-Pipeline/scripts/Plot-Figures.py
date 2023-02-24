import argparse
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def get_args():
    """
    Get arguments from command line with argparse.
    """
    parser = argparse.ArgumentParser(
        prog='Plot-Figures.py',
        description="""Make informative figures from pre- and post-filtered bins.""")
    parser.add_argument("-i1", "--checkm_eval",
                        required=True,
                        help="The SAMPLE.quality_report.tsv file from checkm2.")
    parser.add_argument("-i2", "--mag_eval",
                        required=True,
                        help="The SAMPLE.HiFi_MAG.summary.txt file from the pipeline.")
    parser.add_argument("-l", "--label",
                        required=True,
                        help="A label for the plot.")
    parser.add_argument("-c1", "--completeness",
                        type=float,
                        required=True,
                        help="The name of the output file (a plot).")
    parser.add_argument("-c2", "--contamination",
                        type=float,
                        required=True,
                        help="The name of the output file (a plot).")
    parser.add_argument("-o1", "--output1",
                        required=True,
                        help="The name of the output file (a plot).")
    parser.add_argument("-o2", "--output2",
                        required=True,
                        help="The name of the output file (a plot).")
    parser.add_argument("-o3", "--output3",
                        required=True,
                        help="The name of the output file (a plot).")
    return parser.parse_args()

def get_df(f):
    """
    Convert file into pandas dataframe.
    """
    print("get_df: Making pandas dataframe.")
    return pd.read_csv(f, sep='\t')

def create_unfiltered_joint_scatter(df, output):
    """
    :param df: pandas dataframe
    :param output: figure output name (str)
    """
    sns.jointplot(data=df, x='Completeness', y='Contamination', s=40, alpha=0.7, edgecolor="black", linewidth=0.4,
                  hue=df["Status"], xlim=(-2,102), ylim=(-2,102), marginal_ticks=True)
    plt.savefig("{}".format(output))
    plt.close()

def create_scatter_completeness_contamination_contigs(df, label, output, completeness, contamination):
    """
    Set some reasonable bounds for the plot and make the figure.

    :param df: pandas dataframe
    :param label: sample name (str)
    :param output: figure output name (str)
    :param completeness: min completeness (int)
    :param contamination: max completeness (int)
    """
    if completeness > 90:
        completeness = 70
    if contamination < 10:
        contamination = 10
    plt.figure(figsize=(7,6))
    ax = sns.scatterplot(x="Completeness", y="Contamination", data=df, hue=df["Contig_Number"], palette="viridis_r",
                         s=100, alpha=0.8, edgecolor="black", linewidth=1, legend="full")
    ax.set(xlim=((completeness-2),102))
    ax.set(ylim=(-0.5,(contamination+0.5)))
    plt.title("MAG Completeness vs. Contamination: {}".format(label))
    ylabels = ['{:,.0f}'.format(x) for x in ax.get_yticks()]
    ax.set_axisbelow(True)
    ax.yaxis.grid(color='lightgray', linestyle='solid')
    ax.xaxis.grid(color='lightgray', linestyle='solid')
    ax.set_yticklabels(ylabels, size = 10)
    ax.set_xticklabels(ax.get_xticks(), size = 10)
    handles, labels = ax.get_legend_handles_labels()
    for h in handles:
        h.set_alpha(0.8)
    ax.legend(fontsize = 12, bbox_to_anchor= (1.03, 1), title="Contigs", title_fontsize = 12,
              shadow = True, facecolor = 'white', markerscale=2)
    ax.figure.savefig("{}".format(output), bbox_inches='tight')
    plt.close()

def create_scatter_genomesize_depth(df, label, output):
    """
    :param df: pandas dataframe
    :param label: sample name (str)
    :param output: figure output name (str)
    """
    plt.figure(figsize=(7, 6))
    ax = sns.scatterplot(x="Genome_Size", y="Avg_Depth", data=df, hue=df["GC_Content"], palette="inferno",
                         s=100, alpha=0.7, edgecolor="black", linewidth=1)
    plt.title("MAG Size (Mb) vs. Depth of Coverage: {}".format(label))
    ylabels = ['{:,.0f}'.format(x) for x in ax.get_yticks()]
    ax.set_axisbelow(True)
    xlabels = [round((float(x)/1000000), 2) for x in ax.get_xticks()]
    ax.yaxis.grid(color='lightgray', linestyle='solid')
    ax.xaxis.grid(color='lightgray', linestyle='solid')
    ax.set_yticklabels(ylabels, size=10)
    ax.set_xticklabels(xlabels, size=10)
    handles, labels = ax.get_legend_handles_labels()
    for h in handles:
        h.set_alpha(0.7)
    ax.legend(fontsize = 12, bbox_to_anchor= (1.03, 1), title="Percent GC", title_fontsize = 12,
              shadow = True, facecolor = 'white', markerscale=2)
    ax.figure.savefig("{}".format(output))
    plt.close()

def main():
    args = get_args()
    df_checkm2 = get_df(args.checkm_eval)
    df_mags = get_df(args.mag_eval)
    create_unfiltered_joint_scatter(df_checkm2, args.output1)
    create_scatter_completeness_contamination_contigs(df_mags, args.label, args.output2, args.completeness, args.contamination)
    create_scatter_genomesize_depth(df_mags, args.label, args.output3)

if __name__ == '__main__':
    main()


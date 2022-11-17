import argparse
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def get_args():
    """
    Get arguments from command line with argparse.
    """
    parser = argparse.ArgumentParser(
        prog='Summary-Plots.py',
        description="""Make high-quality plots with MAG information.""")

    parser.add_argument("-i", "--input",
                        required=True,
                        help="The summary file from the pipeline.")
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
    return parser.parse_args()

def create_scatter_completeness_contamination_contigs(df, label, output, completeness, contamination):
    plt.figure(figsize=(7,6))
    ax = sns.scatterplot(x="BinCompleteness", y="BinContamination", data=df, hue=df["NumberContigs"], palette="viridis_r", s=100,
                         alpha=0.9, edgecolor="black", linewidth=1)
    ax.set(xlim=((completeness-2),102))
    ax.set(ylim=(-0.5,(contamination+0.5)))
    plt.title("MAG Completeness vs. Contamination: {}".format(label))
    ylabels = ['{:,.0f}'.format(x) for x in ax.get_yticks()]
    ax.set_axisbelow(True)
    ax.yaxis.grid(color='lightgray', linestyle='solid')
    ax.xaxis.grid(color='lightgray', linestyle='solid')
    ax.set_yticklabels(ylabels, size = 10)
    ax.set_xticklabels(ax.get_xticks(), size = 10)
    ax.legend(fontsize = 12, bbox_to_anchor= (1.03, 1),title="Contigs", title_fontsize = 12,
              shadow = True, facecolor = 'white', markerscale=2)
    ax.figure.savefig("{}".format(output), bbox_inches='tight')
    plt.close()

def create_scatter_genomesize_depth(df, label, output):
    plt.figure(figsize=(7, 6))
    # ax = df.plot.scatter(x="Genome Size", y="Depth",  c="Half")
    ax = sns.scatterplot(x="BinGenomeSize", y="AverageDepth", data=df, s=100,
                         alpha=0.8, edgecolor="black", linewidth=1)
    plt.title("MAG Size (Mb) vs. Depth of Coverage: {}".format(label))
    ylabels = ['{:,.0f}'.format(x) for x in ax.get_yticks()]
    ax.set_axisbelow(True)
    xlabels = [round((float(x)/1000000), 2) for x in ax.get_xticks()]
    ax.yaxis.grid(color='lightgray', linestyle='solid')
    ax.xaxis.grid(color='lightgray', linestyle='solid')
    ax.set_yticklabels(ylabels, size=10)
    ax.set_xticklabels(xlabels, size=10)
    ax.figure.savefig("{}".format(output))
    plt.close()

def main():
    args = get_args()
    df = pd.read_csv(args.input, sep='\t')
    create_scatter_completeness_contamination_contigs(df, args.label, args.output1, args.completeness, args.contamination)
    create_scatter_genomesize_depth(df, args.label, args.output2)

if __name__ == '__main__':
    main()


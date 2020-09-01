import argparse
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def get_args():
    """
    Get arguments from command line with argparse.
    """
    parser = argparse.ArgumentParser(
        prog='Metabat-Plot.py',
        description="""Plot bin information from MetaBAT2.""")

    parser.add_argument("-i", "--input",
                        required=True,
                        help="The o2 format summary file from CheckM.")
    parser.add_argument("-l", "--label",
                        required=True,
                        help="A label for the plot.")
    parser.add_argument("-o1", "--output1",
                        required=True,
                        help="The name of the output file (a plot).")
    parser.add_argument("-o2", "--output2",
                        required=True,
                        help="The name of the output file (a plot).")
    parser.add_argument("-o3", "--output3",
                        required=True,
                        help="The name of the output file (a plot).")
    parser.add_argument("-o4", "--output4",
                        required=True,
                        help="The name of the output file (a plot).")
    parser.add_argument("-o5", "--output5",
                        required=True,
                        help="The name of the output file (a plot).")
    parser.add_argument("-o6", "--output6",
                        required=True,
                        help="The name of the output file (a plot).")

    return parser.parse_args()


def create_unfiltered_joint_scatter(df, output):
    sns.jointplot(df['Completeness'], df['Contamination'], s=50, alpha=0.7)
    plt.savefig("{}".format(output))
    plt.close()

def create_unfiltered_scatter_bins(df, label, output):
    ax = df.plot.scatter(x='Completeness', y='Contamination', s=40, alpha=0.9)
    for i, txt in enumerate(df['Bin Id']):
        ax.annotate("{}".format(txt.replace(label+"_", "")), (df['Completeness'].iat[i], df['Contamination'].iat[i]),
                    xytext=(df['Completeness'].iat[i] + 0.15, df['Contamination'].iat[i] + 0.15),
                    fontsize=5)
    plt.xlabel('Genome Completeness')
    plt.ylabel('Genome Contamination')
    plt.title("Unfiltered Genome Bins: {}\n(labeled by bin name)".format(label))
    plt.savefig("{}".format(output))
    plt.close()
    
def create_unfiltered_scatter_contigs(df, label, output):
    ax = df.plot.scatter(x='Completeness', y='Contamination', s=40, alpha=0.9)
    for i, txt in enumerate(df['# contigs']):
        ax.annotate(txt, (df['Completeness'].iat[i], df['Contamination'].iat[i]),
                    xytext=(df['Completeness'].iat[i] + 0.15, df['Contamination'].iat[i] + 0.15),
                    fontsize=5)
    plt.xlabel('Genome Completeness')
    plt.ylabel('Genome Contamination')
    plt.title("Unfiltered Genome Bins: {}\n(labeled with numbers of contigs in bins)".format(label))
    plt.savefig("{}".format(output))
    plt.close()

def create_filtered_scatter(df, label, output):
    ax = df.plot.scatter(x='Completeness', y='Contamination', s=40, alpha=0.9)
    plt.xlabel('Genome Completeness')
    plt.ylabel('Genome Contamination')
    plt.title("Filtered Genome Bins: {}".format(label))
    plt.savefig("{}".format(output))
    plt.close()

def create_filtered_scatter_contigs(df, label, output):
    ax = df.plot.scatter(x='Completeness', y='Contamination', s=40, alpha=0.9)
    for i, txt in enumerate(df['# contigs']):
        ax.annotate(txt, (df['Completeness'].iat[i], df['Contamination'].iat[i]),
                    xytext=(df['Completeness'].iat[i] + 0.1, df['Contamination'].iat[i] + 0.15),
                    fontsize=6)
    plt.xlabel('Genome Completeness')
    plt.ylabel('Genome Contamination')
    plt.title("Filtered Genome Bins: {}\n(labeled with numbers of contigs in bins)".format(label))
    plt.savefig("{}".format(output))
    plt.close()

def create_filtered_scatter_bins(df, label, output):
    ax = df.plot.scatter(x='Completeness', y='Contamination', s=40, alpha=0.9)
    for i, txt in enumerate(df['Bin Id']):
        ax.annotate("{}".format(txt.replace(label+"_", "")), (df['Completeness'].iat[i], df['Contamination'].iat[i]),
                    xytext=(df['Completeness'].iat[i] + 0.1, df['Contamination'].iat[i] + 0.12),
                    fontsize=5)
    plt.xlabel('Genome Completeness')
    plt.ylabel('Genome Contamination')
    plt.title("Filtered Genome Bins: {}\n(labeled by bin name)".format(label))
    plt.savefig("{}".format(output))
    plt.close()


def main():
    args = get_args()
    df = pd.read_csv(args.input, sep='\t')
    scatfilt = (df['Completeness'] >= 70) & (df['Contamination'] <= 10) & (df['# contigs'] < 10)
    filt = df[scatfilt]
    create_unfiltered_joint_scatter(df, args.output1)
    create_unfiltered_scatter_contigs(df, args.label, args.output2)
    create_unfiltered_scatter_bins(df, args.label, args.output3)
    create_filtered_scatter(filt, args.label, args.output4)
    create_filtered_scatter_contigs(filt, args.label, args.output5)
    create_filtered_scatter_bins(filt, args.label, args.output6)

if __name__ == '__main__':
    main()


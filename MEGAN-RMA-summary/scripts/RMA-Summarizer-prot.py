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
        prog='RMA-class-join.py',
        description="""Summarize read assignments obtained from MEGAN RMA files.""")

    parser.add_argument("-c", "--counts",
                        required=True,
                        nargs='+',
                        help="The complete set of read count files.")
    parser.add_argument("-s", "--summaries",
                        required=True,
                        nargs='+',
                        help="The complete set of absolute summary count files.")
    parser.add_argument("-r", "--rcfile",
                        required=True,
                        help="The read count summary for the fasta file(s).")
    parser.add_argument("-o", "--outname",
                        required=True,
                        help="Name of output file.")
    parser.add_argument("-p", "--outdir",
                        required=True,
                        help="Output directory path to write output files.")
    return parser.parse_args()

def make_df(f):
    """
    Read in dataframe using read and count as column headers, return dataframe.
    """
    df = pd.read_csv(f, sep = '\t', names = ['read', 'annotation'], header = None)
    return df

def summarize_read_counts(df):
    count_dist = sorted(df['read'].value_counts().values)
    avg_annotation_per_read = round(sum(count_dist)/len(count_dist), 1)
    total_unique_reads = len(count_dist)
    return count_dist, avg_annotation_per_read, total_unique_reads

def make_annotations_dict(counts):
    annotations_dict = {}
    samplereads_dict = {"Combined_Functional":{}, "Combined_Taxonomic":{}}
    functional_dbs = ['EC', 'EGGNOG', 'INTERPRO2GO', 'SEED']
    taxonomic_dbs = ['GTDB', 'NCBI', 'NCBIbac']

    for f in counts:
        database = f.split('/')[-1].split('.')[1]
        if database not in annotations_dict:
            annotations_dict[database] = {}

        df = make_df(f)
        count_dist, avg_annotation_per_read, total_unique_reads = summarize_read_counts(df)

        sample = f.split('/')[-1].split('.')[0]

        if sample not in samplereads_dict["Combined_Functional"]:
            samplereads_dict["Combined_Functional"][sample] = set()
        if sample not in samplereads_dict["Combined_Taxonomic"]:
            samplereads_dict["Combined_Taxonomic"][sample] = set()

        if database in functional_dbs:
            samplereads_dict["Combined_Functional"][sample].update(df['read'].unique())
        elif database in taxonomic_dbs:
            samplereads_dict["Combined_Taxonomic"][sample].update(df['read'].unique())

        annotations_dict[database][sample] = {'count_dist':count_dist,
                                         'avg_annotation_per_read':avg_annotation_per_read,
                                         'total_unique_reads':total_unique_reads}
    # Add dummy key, vals for Combined_Functional and Combined_Taxonomic
    for db, dict in samplereads_dict.items():
        annotations_dict[db] = {}
        for sample, readset in dict.items():
            annotations_dict[db][sample] = {'total_unique_reads':len(readset),
                                            'count_dist':0,
                                            'avg_annotation_per_read':0,
                                            'classes':0,
                                            'total_assignments':0}
    return annotations_dict

def add_summary_info(annotations_dict, samples, summaries):
    for f in summaries:
        database = f.split('/')[-1].split('.')[1]
        df = pd.read_csv(f, sep='\t')
        for sample in samples:
            print("{}, {}".format(sample, df[sample].sum()))
            annotations_dict[database][sample]['classes'] = (df[sample] != 0).sum()
            annotations_dict[database][sample]['total_assignments'] = df[sample].sum()
    return annotations_dict
            
def add_normalization_info(annotations_dict, samples, rcfile):
    normalization_dict = {}
    read_counts_list = []
    with open(rcfile, 'r') as fh:
        for line in fh:
            sample = line.strip().split()[0]
            count = int(line.strip().split()[1])
            if sample not in normalization_dict:
                normalization_dict[sample] = {}
            normalization_dict[sample]['read_count'] = count
            read_counts_list.append(count)
    read_counts_list.sort()
    for sample in samples:
        normalization_dict[sample]['normalization'] = round(float(read_counts_list[0])/float(normalization_dict[sample]['read_count']), 3)
    #print(normalization_dict)
    return normalization_dict

def plot_histograms(dbs, samples, annotations_dict, outdir):
    exceptions = ["GTDB", "NCBI", "NCBIbac", "Combined_Functional", "Combined_Taxonomic"]
    for db in dbs:
        if db in exceptions:
            pass
        else:
            for sample in samples:
                #fig, ax = plt.subplots(figsize=(10, 8))
                sns.histplot(x=annotations_dict[db][sample]['count_dist'],
                             bins = list(range(1,annotations_dict[db][sample]['count_dist'][-1],1)),
                             linewidth=0.75, edgecolor=".2")
                plt.xlabel('Annotations per Read')
                plt.xticks(list(range(1,annotations_dict[db][sample]['count_dist'][-1],1)))
                plt.ylabel('Count')
                plt.title("Sample {}; Database: {}".format(sample, db))
                #plt.show()
                fpath = os.path.join(os.getcwd(), outdir, "Plots-Samples")
                if not os.path.exists(fpath):
                    os.mkdir(fpath)
                plt.savefig(os.path.join(fpath, "{}.{}.histo.prot.pdf".format(sample, db)))
                plt.close()

def write_main_output(samples, annotations_dict, normalization_dict, outname):
    """
    Write tab-delimited text file.
    """
    with open(outname, 'a') as fh:
        fh.write("Category\tDatabase\t{}\n".format('\t'.join(samples)))

        dbs = ['Combined_Functional', 'EC', 'EGGNOG', 'INTERPRO2GO', 'SEED', 'Combined_Taxonomic', 'GTDB', 'NCBI', 'NCBIbac']

        for db in dbs:
            reads_assigned = ["{:,}".format(annotations_dict[db][s]['total_unique_reads']) for s in samples]
            fh.write("{}\t{}\t{}\n".format("Total reads assigned", db, '\t'.join(reads_assigned)))

        for db in dbs:
            percent_assigned = ["{}".format(round(float(annotations_dict[db][s]['total_unique_reads']) /
                                      float(normalization_dict[s]['read_count']) * 100, 1)) for s in samples]
            fh.write("{}\t{}\t{}\n".format("Percent reads assigned", db, '\t'.join(percent_assigned)))

        for db in dbs:
            classes = ["{:,}".format(annotations_dict[db][s]['classes']) for s in samples]
            if db == "Combined_Functional" or db == "Combined_Taxonomic":
                pass
            else:
                fh.write("{}\t{}\t{}\n".format("Number of unique classes", db, '\t'.join(classes)))

        for db in dbs:
            assignments = ["{:,}".format(int(annotations_dict[db][s]['total_assignments'])) for s in samples]
            if db == "Combined_Functional" or db == "Combined_Taxonomic":
                pass
            else:
                fh.write("{}\t{}\t{}\n".format("Total assignments to classes", db, '\t'.join(assignments)))

        for db in dbs:
            avg_per_read = [str(annotations_dict[db][s]['avg_annotation_per_read']) for s in samples]
            if db == "Combined_Functional" or db == "Combined_Taxonomic" or db == "GTDB" or db == "NCBI":
                pass
            else:
                fh.write("{}\t{}\t{}\n".format("Average annotations per read", db, '\t'.join(avg_per_read)))

def convert_to_df_and_plot(dict, cols, y, title, outname):
    df = pd.DataFrame(dict)
    sns.barplot(x=cols[0], y=cols[1], hue=cols[2], data=df, linewidth=1, edgecolor=".2", palette="viridis")
    plt.xlabel('Sample')
    plt.ylabel(y)
    if cols[1] == "Percent_Reads_Assigned":
        plt.ylim(0, 110)
    #plt.legend(bbox_to_anchor=(1.01, 1), borderaxespad=0)
    #plt.tight_layout()
    plt.title(title)
    #plt.show()
    plt.savefig(outname)
    plt.close()


def make_plot_dicts(samples, annotations_dict, normalization_dict, outdir):
    # sample reads_assigned database (functional)
    # sample reads_assigned database (taxonomic)
    # sample percent_assigned database (functional)
    # sample percent_assigned database (taxonomic)
    # sample classes database (functional)
    # sample classes database (taxonomic)
    # sample avg_annotations database (functional)

    func_dbs = ['Combined_Functional', 'EC', 'EGGNOG', 'INTERPRO2GO', 'SEED']
    tax_dbs = ['Combined_Taxonomic', 'GTDB', 'NCBI', 'NCBIbac']


    func_read_dict = {'Sample':[], 'Total_Reads_Assigned':[], 'Database':[]}
    for s in samples:
        for db in func_dbs:
            func_read_dict['Sample'].append(s)
            func_read_dict['Total_Reads_Assigned'].append(annotations_dict[db][s]['total_unique_reads'])
            func_read_dict['Database'].append(db)

    tax_read_dict = {'Sample':[], 'Total_Reads_Assigned':[], 'Database':[]}
    for s in samples:
        for db in tax_dbs:
            tax_read_dict['Sample'].append(s)
            tax_read_dict['Total_Reads_Assigned'].append(annotations_dict[db][s]['total_unique_reads'])
            tax_read_dict['Database'].append(db)

    func_perc_dict = {'Sample':[], 'Percent_Reads_Assigned':[], 'Database':[]}
    for s in samples:
        for db in func_dbs:
            func_perc_dict['Sample'].append(s)
            func_perc_dict['Percent_Reads_Assigned'].append(round(float(annotations_dict[db][s]['total_unique_reads'])/
                                                                   float(normalization_dict[s]['read_count']) * 100, 1))
            func_perc_dict['Database'].append(db)

    tax_perc_dict = {'Sample':[], 'Percent_Reads_Assigned':[], 'Database':[]}
    for s in samples:
        for db in tax_dbs:
            tax_perc_dict['Sample'].append(s)
            tax_perc_dict['Percent_Reads_Assigned'].append(round(float(annotations_dict[db][s]['total_unique_reads'])/
                                                                   float(normalization_dict[s]['read_count']) * 100, 1))
            tax_perc_dict['Database'].append(db)

    func_class_dict = {'Sample':[], 'Classes':[], 'Database':[]}
    for s in samples:
        for db in func_dbs:
            if db != "Combined_Functional":
                func_class_dict['Sample'].append(s)
                func_class_dict['Classes'].append(annotations_dict[db][s]['classes'])
                func_class_dict['Database'].append(db)

    tax_class_dict = {'Sample':[], 'Classes':[], 'Database':[]}
    for s in samples:
        for db in tax_dbs:
            if db != "Combined_Taxonomic":
                tax_class_dict['Sample'].append(s)
                tax_class_dict['Classes'].append(annotations_dict[db][s]['classes'])
                tax_class_dict['Database'].append(db)

    func_annot_dict = {'Sample':[], 'Average_Annotations_per_Read':[], 'Database':[]}
    for s in samples:
        for db in func_dbs:
            if db != "Combined_Functional":
                func_annot_dict['Sample'].append(s)
                func_annot_dict['Average_Annotations_per_Read'].append(annotations_dict[db][s]['avg_annotation_per_read'])
                func_annot_dict['Database'].append(db)

    #return func_read_dict, tax_read_dict, func_perc_dict, tax_perc_dict, func_class_dict, tax_class_dict, func_annot_dict
    #convert_to_df_and_plot(dict, cols, y, title, outname):
    fpath = os.path.join(os.getcwd(), outdir, "Plots-Summaries")
    if not os.path.exists(fpath):
        os.mkdir(fpath)

    convert_to_df_and_plot(func_read_dict, ['Sample', 'Total_Reads_Assigned', 'Database'],
                           "Reads", "Total Reads Assigned to Functional Databases",
                           os.path.join(fpath, "SummaryPlot-Functional_Total_Reads_Assigned.prot.pdf"))
    convert_to_df_and_plot(tax_read_dict, ['Sample', 'Total_Reads_Assigned', 'Database'],
                           "Reads", "Total Reads Assigned to Taxonomic Databases",
                           os.path.join(fpath, "SummaryPlot-Taxonomic_Total_Reads_Assigned.prot.pdf"))

    convert_to_df_and_plot(func_perc_dict, ['Sample', 'Percent_Reads_Assigned', 'Database'],
                           "Percent Reads", "Percent Reads Assigned to Functional Databases",
                           os.path.join(fpath, "SummaryPlot-Functional_Percent_Reads_Assigned.prot.pdf"))
    convert_to_df_and_plot(tax_perc_dict, ['Sample', 'Percent_Reads_Assigned', 'Database'],
                           "Percent Reads", "Percent Reads Assigned to Taxonomic Databases",
                           os.path.join(fpath, "SummaryPlot-Taxonomic_Percent_Reads_Assigned.prot.pdf"))

    convert_to_df_and_plot(func_class_dict, ['Sample', 'Classes', 'Database'],
                           "Count", "Classes Represented in Functional Databases",
                           os.path.join(fpath, "SummaryPlot-Functional_Classes_Assigned.prot.pdf"))
    convert_to_df_and_plot(tax_class_dict, ['Sample', 'Classes', 'Database'],
                           "Count", "Classes Represented in  Taxonomic Databases",
                           os.path.join(fpath, "SummaryPlot-Taxonomic_Classes_Assigned.prot.pdf"))

    convert_to_df_and_plot(func_annot_dict, ['Sample', 'Average_Annotations_per_Read', 'Database'],
                           "Count", "Average Annotations per Read from Functional Databases",
                           os.path.join(fpath, "SummaryPlot-Functional_Average_Annotations_Assigned.prot.pdf"))

def normalize_count_summaries(summaries, normalization_dict, samples, outdir):
    for f in summaries:
        db = f.split('/')[-1].split('.')[1]
        df = pd.read_csv(f, sep='\t')
        for s in samples:
            df[s] = (df[s] * normalization_dict[s]['normalization']).round(1)
        output = os.path.join(outdir, "Normalized.{}.counts.prot.txt".format(db))
        df.to_csv(output, index=False, sep='\t')

def main():
    args = get_args()
    annotations_dict = make_annotations_dict(args.counts)
    dbs = sorted(annotations_dict.keys())
    samples = sorted(annotations_dict[dbs[0]].keys())
    annotations_dict = add_summary_info(annotations_dict, samples, args.summaries)
    normalization_dict = add_normalization_info(annotations_dict, samples, args.rcfile)
    plot_histograms(dbs, samples, annotations_dict, args.outdir)
    write_main_output(samples, annotations_dict, normalization_dict, args.outname)
    make_plot_dicts(samples, annotations_dict, normalization_dict, args.outdir)
    normalize_count_summaries(args.summaries, normalization_dict, samples, args.outdir)

if __name__ == '__main__':
    main()



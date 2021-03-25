import argparse
import os
import ete3
import pandas as pd
from ete3 import NCBITaxa

def get_args():
    """
    Get arguments from command line with argparse.
    """
    parser = argparse.ArgumentParser(
        prog='Convert_metaphlan3_mpa_to_kreport.py',
        description="""Convert a MetaPhlAn3 mpa file into kreport (kraken) output format. 
        Note that differences in taxonomy may cause a negative level count for some 
        higher taxa.""")

    parser.add_argument("-i", "--input",
                        required=True,
                        help="A mpa file obtained from MetaPhlAn3.")
    parser.add_argument("-l", "--label",
                        required=True,
                        help="A prefix that will help name the output files.")
    parser.add_argument("-r", "--readcount",
                        required=True,
                        type=int,
                        help="The total number of reads.")
    parser.add_argument("-m", "--mappedreads",
                        required=True,
                        type=int,
                        help="The total number of reads that were mapped by bowtie2.")
    parser.add_argument("--update",
                        required=False,
                        action='store_true',
                        help="Including this flag will cause NCBITaxa to update the taxonomy database.")

    return parser.parse_args()

def activate_ncbi(update=False):
    print("\nActivating NCBI taxonomy database...")
    ncbi = NCBITaxa()
    if update is True:
        print("\tUpdating database...")
        ncbi.update_taxonomy_database()
    return ncbi

def create_df(infile, mappedreads):
    print("\nReading in MetaPhlAn3 mpa file...")
    df = pd.read_csv(infile, sep='\t',
                     names=['clade_name', 'NCBI_tax_id_lineage', 'relative_abundance', 'additional_species'],
                     header=None, comment='#')
    df["taxid"] = df["NCBI_tax_id_lineage"].str.split('|').str[-1]
    df["Count"] = (df["relative_abundance"] * 0.01) * mappedreads
    df = df.round({'Count': 1})
    return df

def get_taxon_dict(ncbi, df):
    print("Translating taxon names...")
    taxon_dict = {}
    for taxid in list(df['taxid'].unique()):
        if taxid != 0:
            taxon_dict[ncbi.get_taxid_translator([int(taxid)])[int(taxid)]] = {'taxid': int(taxid)}
    return taxon_dict

def add_ranks(ncbi, k, v):
    lineage = ncbi.get_lineage(v['taxid'])
    taxid_to_rank_dict = ncbi.get_rank(lineage)
    taxid_to_names_dict = ncbi.get_taxid_translator(lineage)
    ranks = ['superkingdom', 'kingdom', 'clade', 'phylum', 'class', 'order', 'family', 'genus', 'species', 'strain']
    temp_dict = {}
    for taxid in lineage:
        if taxid_to_rank_dict[taxid] in ranks:
            temp_dict[taxid_to_rank_dict[taxid]] = {'taxid': taxid, 'name': taxid_to_names_dict[taxid]}
    for r in ranks:
        if r not in temp_dict:
            temp_dict[r] = {'taxid': 'NA', 'name': 'NA'}
    return temp_dict

def write_intermediate_output(taxon_dict, output, label):
    with open(output, 'a') as fh:
        fh.write("{0}\t{1}\t{2}\t{3}\t{4}\t{5}"
                 "\t{6}\t{7}\t{8}\t{9}\t{10}\t{11}\n".format('Taxon', 'Count', 'superkingdom',
                                                     'kingdom', 'clade', 'phylum', 'class',
                                                     'order', 'family', 'genus', 'species', 'strain'))
        for k, v in taxon_dict.items():
            fh.write("{0}\t{1}\t{2}\t{3}\t{4}\t{5}"
                     "\t{6}\t{7}\t{8}\t{9}\t{10}\t{11}\n".format(k, v['Count'], v['superkingdom'][label],
                                                           v['kingdom'][label], v['clade'][label],
                                                           v['phylum'][label], v['class'][label],
                                                           v['order'][label], v['family'][label],
                                                           v['genus'][label], v['species'][label],
                                                           v['strain'][label]))

def make_lineage_dict(infile):
    print("\nReading intermediate ranks file...")
    lineage_dict = {}
    with open(infile, 'r') as fh:
        next(fh)
        for line in fh:
            parts = line.strip().split('\t')
            badnames = ["k__NA", "p__NA", "c__NA", "o__NA", "f__NA", "g__NA", "s__NA", "ss__NA"]
            relabeled = ["k__{}".format(parts[2]), "p__{}".format(parts[5]),
                         "c__{}".format(parts[6]), "o__{}".format(parts[7]),
                         "f__{}".format(parts[8]), "g__{}".format(parts[9]),
                         "s__{}".format(parts[10]), "ss__{}".format(parts[11])]
            lineage = "|".join([l for l in relabeled if l not in badnames])
            if lineage:
                lineage_dict[lineage] = {'level_count': '-', 'cumulative_count': int(parts[1])}
    return lineage_dict

def fill_out_lineages(lineage_dict):
    print("Filling out lineage gaps...")
    expanded_dict = {k: v for (k, v) in lineage_dict.items()}
    for k, v in lineage_dict.items():
        expanded_dict[k] = v
        label = ""
        for i in k.split('|'):
            label += i
            if label not in expanded_dict:
                expanded_dict[label] = {'level_count': '-', 'cumulative_count': int(0)}
            label += "|"
    return expanded_dict

def write_mpa(expanded_dict, outname):
    print("Writing mpa output file...")
    # mpa is 2 columns: full_lineage + cumulative_count
    with open(outname, 'a') as fh:
        for k, v in sorted(expanded_dict.items()):
            fh.write("{}\t{}\n".format(k.replace(" ","_"), v['cumulative_count']))

def write_intermediate_kreport(expanded_dict, outname, reads, ncbi):
    print("Writing intermediate kreport file...")
    # headers for kreport
    # proportion + cumulative_count + level_count + rank + taxid + name
    with open(outname, 'a') as fh:
        for k, v in sorted(expanded_dict.items()):
            indent_rules = {"K":"", "P":"  ", "C":"    ",
                            "O":"      ", "F":"        ",
                            "G":"          ", "S":"            ",
                            "SS":"              "}
            if '|' in k:
                rank = k.split('|')[-1].split('__')[0].upper()
                name = k.split('|')[-1].split('__')[-1]
            else:
                rank = k.split('_')[0].upper()
                name = k.split('_')[-1]
            taxid = ncbi.get_name_translator([name])[name][0]
            row_data = [round((float(v['cumulative_count'])/float(reads))*100, 2), v['cumulative_count'], v['level_count'], rank, taxid, k.replace(" ","_")]
            row_string = "\t".join([str(i) for i in row_data])
            fh.write("{}\n".format(row_string))

def calculate_level_counts(infile):
    ranks = ["K", "P", "C", "O", "F", "G", "S"]
    rows = []
    with open(infile, 'r') as fh:
        for line in fh:
            cols = [l.strip() for l in line.strip().split('\t')]
            rows.append(cols)
    for r in rows:
        r[1] = int(r[1])
        if r[3] == 'S':
            r[2] = r[1]
        else:
            r[2] = int(0)
    for i, rank in enumerate(ranks[::-1]):
        if rank == 'S':
            pass
        else:
            for row in rows:
                if row[3] == rank:
                    #print(row[3], row[-1])
                    #nested = [r for r in rows if r[-1].startswith(row[-1]) and r[-1] != row[-1] and r[3] == ranks[::-1][i-1]]
                    #for n in nested:
                        #print('\t', n[3], n[-1])
                    if row[1] == int(0):
                        row[1] = sum([r[1] for r in rows if r[-1].startswith(row[-1]) and r[-1] != row[-1] and r[3] == ranks[::-1][i-1]])
                    subcount = sum([r[2] for r in rows if r[-1].startswith(row[-1]) and r[-1] != row[-1]])
                    if subcount == int(0):
                        row[2] = int(0)
                    else:
                        row[2] = row[1] - subcount
    return rows

def write_kreport(rows, outname):
    print("Writing kreport output file...")
    # headers for kreport
    # proportion + cumulative_count + level_count + rank + taxid + name
    with open(outname, 'a') as fh:
        indent_rules = {"K":"", "P":"  ", "C":"    ",
                        "O":"      ", "F":"        ",
                        "G":"          ", "S":"            ",
                        "SS":"              "}
        for row in rows:
            if '|' in row[-1]:
                name = row[-1].split('|')[-1].split('__')[-1]
            else:
                name = row[-1].split('_')[-1]
            name = indent_rules[row[3]] + name
            if row[3] == "SS":
                row[3] = "S1"
            new_row = [row[0], row[1], row[2], row[3], row[4], name.replace("_", " ")]
            row_string = "\t".join([str(i) for i in new_row])
            fh.write("{}\n".format(row_string))

def main():
    args = get_args()
    ncbi = activate_ncbi(args.update)
    df = create_df(args.input, args.mappedreads)
    taxon_dict = get_taxon_dict(ncbi, df)
    print("Getting lineage information for all taxa...")
    for k, v in taxon_dict.items():
        # add lineage ranks and names
        v.update(add_ranks(ncbi, k, v))
        # add read counts
        v['Count'] = int((df.loc[df['taxid'] == str(v['taxid'])])['Count'])
    write_intermediate_output(taxon_dict, "{}.intermediate.names.txt".format(args.label), 'name')
    lineage_dict = make_lineage_dict("{}.intermediate.names.txt".format(args.label))
    os.remove("{}.intermediate.names.txt".format(args.label))
    expanded_dict = fill_out_lineages(lineage_dict)
    #write_mpa(expanded_dict, "{}.metaphlan-mpa.mpa.txt".format(args.label))
    write_intermediate_kreport(expanded_dict, "{}.intermediate.kreport.txt".format(args.label), args.readcount, ncbi)
    rows = calculate_level_counts("{}.intermediate.kreport.txt".format(args.label))
    write_kreport(rows, "{}.kreport.txt".format(args.label))
    os.remove("{}.intermediate.kreport.txt".format(args.label))
    print("\nDone!\n")

if __name__ == '__main__':
    main()

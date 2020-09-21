import argparse
import logging
import os
import shutil
import gzip
from Bio import SeqIO

def get_args():
    """
    Get arguments from command line with argparse.
    """
    parser = argparse.ArgumentParser(
        prog='Sort-Fasta-Records-Biopython.py',
        description="""Sort all entries in a fasta file by order of record name.""")

    parser.add_argument("-d", "--depth",
                        required=True,
                        help="The depth file produced by metabat2.")

    parser.add_argument("-b", "--batch",
                        required=True,
                        help="The batch file produced for gtdb-tk.")

    parser.add_argument("-c", "--checkm",
                        required=True,
                        help="The simple format checkm summary file.")

    parser.add_argument("-g", "--gtdb_dir",
                        required=True,
                        help="The path to the /classify directory produced by GTDB.")

    parser.add_argument("-j", "--gtdb_db",
                        required=True,
                        help="The path to the database for GTDB.")

    parser.add_argument("-o", "--outfile",
                        required=True,
                        help="The name of the output summary file.")

    parser.add_argument("-s", "--outdir",
                        required=True,
                        help="The name of the output directory.")

    parser.add_argument("-l", "--logfile",
                        required=True,
                        help="The name of the log file to write.")

    return parser.parse_args()

def setup_logging(logfile):
    # set up logging to file
    logging.basicConfig(filename=logfile,
                        format="%(levelname)s: %(asctime)s: %(message)s",
                        datefmt='%d-%b-%y %H:%M:%S',
                        level=logging.DEBUG)

def depth_to_dict(depth):
    """
    depth contains 5 cols:
    contigName	contigLen	totalAvgDepth	Sample.bam	Sample.bam-var
    Will enter [contigName] = {contigLen:int, totalAvgDepth:float}
    for each contig available in depth.

    :param depth: full path to depth file
    :return depth_dict: dict of dicts described above
    """
    logging.info("Parsing depth file.")
    depth_dict = {}
    with open(depth, 'r') as fh:
        #skip header
        next(fh)
        for line in fh:
            parts = line.strip().split('\t')
            depth_dict[parts[0]] = {"contigLen": int(float(parts[1])),
                                    "totalAvgDepth": int(float(parts[2]))}
            logging.info("{} = contigLen: {}; totalAvgDepth: {}"
                         .format(parts[0], int(float(parts[1])), int(float(parts[2]))))
    return depth_dict

def batch_to_dict(batch):
    """
    Batch file contains two columns:
    FULL/PATH/TO/SAMPLE_bin.13.fa	SAMPLE_bin.13
    Create a dict with [sample_bin_name] = ["Tigname1", "Tigname2"]

    :param batch: full path to batch file
    :return batch_dict: dict described above
    :return bin_list: list of bin names
    """
    logging.info("Parsing batch file.")
    batch_dict, batch_paths, bin_list = {}, {}, []
    with open(batch, 'r') as fh:
        for line in fh:
            parts = line.strip().split('\t')
            records = SeqIO.index(parts[0], "fasta")
            tigs = sorted(list(records))
            batch_dict[parts[1]] = tigs
            bin_list.append(parts[1])
            logging.info("{} = {}.".format(parts[1], ", ".join(tigs)))
            batch_paths[parts[1]] = parts[0]
    return batch_dict, bin_list, batch_paths

def checkmsimple_to_dict(checkm, bin_list):
    """
    checkm simple is a tab-delimited file with 6 columns:
    Filter	Bin	Completenes	Contamination	StrainHeterogeneity	GenomeSize	Contigs
    Create a dictionary where [Bin] = {Completenes:val, Contamination:val,
    StrainHeterogeneity:val, GenomeSize:val, Contigs:val}

    :param checkm: full path to simplified checkm summary file
    :param bin_list: list of bin names (which passed filtering)
    :return checkm_dict: dict described above
    """
    logging.info("Parsing checkm simple file.")
    checkm_dict = {}
    with open(checkm, 'r') as fh:
        #skip header
        next(fh)
        for line in fh:
            parts = line.strip().split('\t')
            if parts[1] in bin_list:
                checkm_dict[parts[1]] = {"Completeness": parts[2],
                                         "Contamination": parts[3],
                                         "StrainHeterogeneity": parts[4],
                                         "GenomeSize": parts[5],
                                         "Contigs": parts[6]}
            logging.info("{} = Completeness: {}, "
                         "Contamination: {}, "
                         "StrainHeterogeneity: {}, "
                         "GenomeSize: {}, "
                         "Contigs: {}".format(parts[1], parts[2], parts[3],
                                              parts[4], parts[5], parts[6]))
    return checkm_dict

def gtdb_to_dict(gtd_dir, home):
    """
    0)user_genome 1)classification 2)fastani_reference 3)fastani_reference_radius 4)fastani_taxonomy
    5)fastani_ani 6)fastani_af 7)closest_placement_reference 8)closest_placement_radius
    9)closest_placement_taxonomy 10)closest_placement_ani 11)closest_placement_af 12)pplacer_taxonomy
    13)classification_method 14)note 15)other_related_references(genome_id,species_name,radius,ANI,AF)
    16)aa_percent 17)translation_table 18)red_value 19)warnings
    :param gtd_dir: directory containing the *.summary.tsv files to parse (bacteria and/or archaea)
    :param home: initial working directory
    :return:
    """
    gtdb_dict = {}
    os.chdir(gtd_dir)
    summaries = [f for f in os.listdir('.') if f.endswith('.summary.tsv')]
    for s in summaries:
        logging.info("Parsing gtdb summary file: {}.".format(s))
        with open(s, 'r') as fh:
            next(fh)
            for line in fh:
                parts = line.strip().split('\t')
                gtdb_dict[parts[0]] = {"Species": parts[1].split(';')[-1],
                                       "Taxonomy": parts[1],
                                       "ReferenceGenome": parts[2],
                                       "AvgNucleotideIdentity": parts[5],
                                       "ClassificationMethod": parts[13],
                                       "other_related_references": parts[15],
                                       "GTDB_warnings": parts[19]}
    os.chdir(home)
    return gtdb_dict

def write_summary(depth_dict, batch_dict, gtdb_dict, checkm_dict, bin_list, outfile):
    logging.info("Writing summary file: {}.".format(outfile))
    with open(outfile, 'a') as fh:
        fh.write("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\t{10}"
                 "\t{11}\t{12}\t{13}\t{14}\t{15}\n".format("BinName",
                                                           "NumberContigs",
                                                           "Content",
                                                           "ContigLengths",
                                                           "ContigDepths",
                                                           "BinCompleteness",
                                                           "BinContamination",
                                                           "BinStrainHeterogeneity",
                                                           "BinGenomeSize",
                                                           "GTDB_Species",
                                                           "GTDB_Taxonomy",
                                                           "ReferenceGenome",
                                                           "AvgNucleotideIdentity",
                                                           "ClassificationMethod",
                                                           "other_related_references(genome_id,species_name,radius,ANI,AF)",
                                                           "GTDB_warnings"))
        for bin in bin_list:
            #learned the hard way that some bins get filtered out using GTDB
            #it isn't a guarantee they will be in the gtdb_dict
            if bin in gtdb_dict:
                fh.write("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\t{10}"
                         "\t{11}\t{12}\t{13}\t{14}\t{15}\n".format(bin,
                                                                   checkm_dict[bin]["Contigs"],
                                                                   ", ".join(batch_dict[bin]),
                                                                   ", ".join([str(depth_dict[contig]["contigLen"]) for contig in batch_dict[bin]]),
                                                                   ", ".join([str(depth_dict[contig]["totalAvgDepth"]) for contig in batch_dict[bin]]),
                                                                   checkm_dict[bin]["Completeness"],
                                                                   checkm_dict[bin]["Contamination"],
                                                                   checkm_dict[bin]["StrainHeterogeneity"],
                                                                   checkm_dict[bin]["GenomeSize"],
                                                                   gtdb_dict[bin]["Species"],
                                                                   gtdb_dict[bin]["Taxonomy"],
                                                                   gtdb_dict[bin]["ReferenceGenome"],
                                                                   gtdb_dict[bin]["AvgNucleotideIdentity"],
                                                                   gtdb_dict[bin]["ClassificationMethod"],
                                                                   gtdb_dict[bin]["other_related_references"],
                                                                   gtdb_dict[bin]["GTDB_warnings"]))
            else:
                fh.write("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\tNA\tNA"
                         "\tNA\tNA\tNA\tNA\tNA\n".format(bin, checkm_dict[bin]["Contigs"],
                                                         ", ".join(batch_dict[bin]),
                                                         ", ".join([str(depth_dict[contig]["contigLen"]) for contig in batch_dict[bin]]),
                                                         ", ".join([str(depth_dict[contig]["totalAvgDepth"]) for contig in batch_dict[bin]]),
                                                         checkm_dict[bin]["Completeness"],
                                                         checkm_dict[bin]["Contamination"],
                                                         checkm_dict[bin]["StrainHeterogeneity"],
                                                         checkm_dict[bin]["GenomeSize"]))


def make_target_query_pairs(bin_list, batch_paths, gtdb_dict, gtdb_db, home, outdir):
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    os.chdir(outdir)
    for bin in bin_list:
        bindir = os.path.join(os.getcwd(), bin)
        logging.info("Writing paired files to: {}.".format(bindir))
        if not os.path.exists(bindir):
            os.mkdir(bindir)
        dest1 = os.path.join(bindir, "{}.fa".format(bin))
        logging.info("Copying target file: {}.".format(batch_paths[bin]))
        shutil.copyfile(batch_paths[bin], dest1)

        fzip = os.path.join(gtdb_db, "fastani", "database", "{}_genomic.fna.gz".format(gtdb_dict[bin]["ReferenceGenome"]))
        dest2 = os.path.join(bindir, "{}.fa".format(gtdb_dict[bin]["ReferenceGenome"]))
        if os.path.isfile(fzip):
            with gzip.open(fzip, 'rb') as fhin:
                with open(dest2, 'wb') as fhout:
                    shutil.copyfileobj(fhin, fhout)
            #shutil.copyfile(fzip, dest2)
            logging.info("Copying and decompressing query file: {}.".format(fzip))
        else:
            logging.info("Unable to find query file: {}.".format(fzip))
    os.chdir(home)

def main():
    args = get_args()
    setup_logging(args.logfile)
    home = os.getcwd()
    depth_dict = depth_to_dict(args.depth)
    batch_dict, bin_list, batch_paths = batch_to_dict(args.batch)
    checkm_dict = checkmsimple_to_dict(args.checkm, bin_list)
    gtdb_dict= gtdb_to_dict(args.gtdb_dir, home)
    write_summary(depth_dict, batch_dict, gtdb_dict, checkm_dict, bin_list, args.outfile)
    make_target_query_pairs(bin_list, batch_paths, gtdb_dict, args.gtdb_db, home, args.outdir)
    
if __name__ == '__main__':
    main()

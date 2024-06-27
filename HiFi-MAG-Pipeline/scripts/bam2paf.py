import argparse
import pysam
import os

def get_args():
    """
    Get arguments from command line with argparse.
    """
    parser = argparse.ArgumentParser(
        prog='bam2paf.py',
        description="""Convert an aligned bam from minimap2 into paf.""")
    parser.add_argument("-i", "--input_bam",
                        required=True,
                        help="Path to bam file.")
    parser.add_argument("-o", "--out_paf",
                        required=True,
                        help="Name of output paf file to write.")
    return parser.parse_args()

def get_bam_object(input_bam):
    print("get_bam_object: Getting pysam bam object.")
    return pysam.AlignmentFile(input_bam, 'rb', check_sq=False)

def bam2paf(bam, out_paf):
    if os.path.exists(out_paf):
        os.remove(out_paf)

    print("bam2paf: Converting bam to paf...")
    entries = 0
    with open(out_paf, 'a') as fh:
        for read in bam:
            # simple progress tracking
            entries += 1
            if entries % 100000 == 0:
                print("\t{:,} entries".format(entries))
            # get orientation
            if read.is_reverse is True:
                strand = '-'
            else:
                strand = '+'
            # see if tp tag is present
            try:
                aln_type = "tp:A:{}".format(read.get_tag('tp'))
            except:
                aln_type = ""
            # write paf format
            fh.write("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t"
                     "{6}\t{7}\t{8}\t{9}\t{10}\t{11}\t"
                     "{12}\n".format(read.query_name, read.query_length, read.query_alignment_start,
                                     read.query_alignment_end, strand, read.reference_name,
                                     read.reference_length, read.reference_start, read.reference_end,
                                     read.get_cigar_stats()[0][0], read.query_alignment_length,
                                     read.mapping_quality, aln_type))
    print("bam2paf: Wrote {:,} entries".format(entries))

def main():
    args = get_args()
    bam = get_bam_object(args.input_bam)
    bam2paf(bam, args.out_paf)

if __name__ == '__main__':
    main()



# pb-metagenomics-scripts

Welcome! This repository contains a variety of scripts that are useful for metagenomics work. The scripts are listed by topic, with detailed usage instructions provided below.

## Contents <a name="TOP"></a>

**Converting output file formats for taxonomic profilers:**

+ [Convert_kreport_to_mpa.py](#ckm): Convert any kraken report (kreport) file into metaphlan (mpa) format.
+ [Convert_MEGAN-RMA-NCBI-c2c_to_kreport-mpa.py](#mckm): Convert taxonomic counts from MEGAN6 into kraken report (kreport) and metaphlan (mpa) formats.
+ [Convert_metamaps-KRONA_to_kreport-mpa.py](#mkkm): Convert the output of Metamaps into kraken report (kreport) and metaphlan (mpa) formats.
+ [Convert_metaphlan3_mpa_to_kreport](#mmkr): Convert the output of MetaPhlAn3 into kraken report (kreport) format.

---------------

## Convert_kreport_to_mpa.py <a name="ckm"></a>

This is a general use script that will convert any kraken report (kreport) file into metaphlan (mpa) format. Programs that output kreport formats include [Kraken](https://github.com/DerrickWood/kraken2), [Bracken](https://github.com/jenniferlu717/Bracken/), [Centrifuge](https://ccb.jhu.edu/software/centrifuge/manual.shtml), and [mmseqs2](https://github.com/soedinglab/MMseqs2). This script was primarily intended for use with `mmseqs2`. 

This script requires `python 3.7` and the python packages `ete3` and `pandas`. 

Output file is written to working directory (`label.mpa.txt`).

#### Basic Usage:

```
python Convert_kreport_to_mpa.py -i <kreport file> -f <choice> -l <label string>
```

#### Argument Explanations:

##### `-i <path-to-file>` or `--input <path-to-file>`

> **Required**: The kreport file name or the path to a kreport file.

##### `-f <choice>` or `--format <choice>`

> **Required**: The format of the kreport ranks. Choices = *kraken, mmseqs*.
> kraken format displays ranks as single characters: K, P, C, O, F, G, S, S1, etc.
> mmseqs format displays ranks as words: kingdom, phylum, class, etc.

##### `-l <string>` or `--label <string>`

> **Required**: A label used to name the output file: label.mpa.txt.

##### `--update`

> **Optional**: If this flag is provided, ete3 will update the local NCBI taxonomy database before using it to perform the format conversion.


#### Example Usage:

```
python Convert_kreport_to_mpa.py -i Sample1_mmseqs2_report.txt -f mmseqs -l Sample1
```

#### Example Input File Contents:

**kraken format ranks:**
```
99.94	1961144	0	D	2	    Bacteria
48.79	957327	0	D1	1783272	      Terrabacteria group
46.63	915081	0	P	1239	        Firmicutes
28.82	565455	0	C	186801	          Clostridia
28.80	565192	0	O	186802	            Clostridiales
20.07	393748	0	F	541000	              Ruminococcaceae
19.91	390707	0	G	216851	                Faecalibacterium
19.91	390707	390707	S	853	                  Faecalibacterium prausnitzii
0.15	2934	0	G	946234	                Flavonifractor
0.15	2934	2934	S	292800	                  Flavonifractor plautii
0.00	84	0	G	1905344	                Ruthenibacterium
0.00	84	84	S	1550024	                  Ruthenibacterium lactatiformans
0.00	22	0	G	253238	                Ethanoligenens
0.00	22	22	S	253239	                  Ethanoligenens harbinense
5.65	110871	0	F	186803	              Lachnospiraceae
5.41	106128	0	G	841	                Roseburia
5.22	102374	102374	S	301301	                  Roseburia hominis
0.19	3753	3753	S	166486	                  Roseburia intestinalis
```

**mmseqs format ranks:**
```
0.0031	61	61	no rank	0	unclassified
99.9969	1978505	251569	no rank	1	root
87.2821	1726933	311	no rank	131567	  cellular organisms
86.7817	1717034	157371	superkingdom	2	    Bacteria
36.5627	723417	3797	clade	1783272	      Terrabacteria group
34.7785	688115	19991	phylum	1239	        Firmicutes
27.4589	543293	38825	class	186801	          Clostridia
25.4966	504468	74286	order	186802	            Clostridiales
16.6688	329803	28579	family	541000	              Ruminococcaceae
15.2237	301210	290530	genus	216851	                Faecalibacterium
0.3679	7279	633	no rank	2646395	                  unclassified Faecalibacterium
0.3253	6436	6436	species	2292234	                    Faecalibacterium sp. AF28-13AC
0.0100	198	198	species	2293109	                    Faecalibacterium sp. OF04-11AC
0.0006	11	11	species	1971605	                    Faecalibacterium sp.
0.0001	1	1	species	2302957	                    Faecalibacterium sp. AM43-5AT
0.1650	3265	3252	species	853	                  Faecalibacterium prausnitzii
0.0003	5	5	strain	411483	                    Faecalibacterium prausnitzii A2-165
0.0003	5	5	strain	411485	                    Faecalibacterium prausnitzii M21/2
0.0002	3	3	strain	718252	                    Faecalibacterium prausnitzii L2-6
0.0069	136	0	no rank	259314	                  environmental samples
0.0068	135	135	species	259315	                    uncultured Faecalibacterium sp.
0.0001	1	1	species	1262898	                    Faecalibacterium sp. CAG:82
0.0004	8	1	genus	292632	                Subdoligranulum
0.0003	6	0	no rank	2685293	                  unclassified Subdoligranulum
0.0003	6	6	species	2779354	                    Subdoligranulum sp. DSM 109015
0.0001	1	0	species	214851	                  Subdoligranulum variabile
0.0001	1	1	strain	411471	                    Subdoligranulum variabile DSM 15176
0.0002	3	0	genus	946234	                Flavonifractor
0.0002	3	3	species	292800	                  Flavonifractor plautii
```


#### Example Output File Contents:

This is the result of converting the mmseqs format example above:
```
k__Bacteria|p__Firmicutes|c__Clostridia|o__Eubacteriales|f__Oscillospiraceae|g__Faecalibacterium	301210
k__Bacteria|p__Firmicutes|c__Clostridia|o__Eubacteriales|f__Oscillospiraceae|g__Faecalibacterium|s__Faecalibacterium_sp._AF28-13AC	6436
k__Bacteria|p__Firmicutes|c__Clostridia|o__Eubacteriales|f__Oscillospiraceae|g__Faecalibacterium|s__Faecalibacterium_sp._OF04-11AC	198
k__Bacteria|p__Firmicutes|c__Clostridia|o__Eubacteriales|f__Oscillospiraceae|g__Faecalibacterium|s__Faecalibacterium_sp.	11
k__Bacteria|p__Firmicutes|c__Clostridia|o__Eubacteriales|f__Oscillospiraceae|g__Faecalibacterium|s__Faecalibacterium_sp._AM43-5AT	1
k__Bacteria|p__Firmicutes|c__Clostridia|o__Eubacteriales|f__Oscillospiraceae|g__Faecalibacterium|s__Faecalibacterium_prausnitzii	3265
k__Bacteria|p__Firmicutes|c__Clostridia|o__Eubacteriales|f__Oscillospiraceae|g__Faecalibacterium|s__Faecalibacterium_prausnitzii|ss__Faecalibacterium_prausnitzii_A2-165	5
k__Bacteria|p__Firmicutes|c__Clostridia|o__Eubacteriales|f__Oscillospiraceae|g__Faecalibacterium|s__Faecalibacterium_prausnitzii|ss__Faecalibacterium_prausnitzii_M21/2	5
k__Bacteria|p__Firmicutes|c__Clostridia|o__Eubacteriales|f__Oscillospiraceae|g__Faecalibacterium|s__Faecalibacterium_prausnitzii|ss__Faecalibacterium_prausnitzii_L2-6	3
k__Bacteria|p__Firmicutes|c__Clostridia|o__Eubacteriales|f__Oscillospiraceae|g__Faecalibacterium|s__uncultured_Faecalibacterium_sp.	135
k__Bacteria|p__Firmicutes|c__Clostridia|o__Eubacteriales|f__Oscillospiraceae|g__Faecalibacterium|s__Faecalibacterium_sp._CAG:82	1
k__Bacteria|p__Firmicutes|c__Clostridia|o__Eubacteriales|f__Oscillospiraceae|g__Subdoligranulum	8
k__Bacteria|p__Firmicutes|c__Clostridia|o__Eubacteriales|f__Oscillospiraceae|g__Subdoligranulum|s__Subdoligranulum_sp._DSM_109015	6
k__Bacteria|p__Firmicutes|c__Clostridia|o__Eubacteriales|f__Oscillospiraceae|g__Subdoligranulum|s__Subdoligranulum_variabile	1
k__Bacteria|p__Firmicutes|c__Clostridia|o__Eubacteriales|f__Oscillospiraceae|g__Subdoligranulum|s__Subdoligranulum_variabile|ss__Subdoligranulum_variabile_DSM_15176	1
k__Bacteria|p__Firmicutes|c__Clostridia|o__Eubacteriales|f__Oscillospiraceae|g__Flavonifractor	3
k__Bacteria|p__Firmicutes|c__Clostridia|o__Eubacteriales|f__Oscillospiraceae|g__Flavonifractor|s__Flavonifractor_plautii	3
```


[Back to top](#TOP)

---------------

## Convert_MEGAN-RMA-NCBI-c2c_to_kreport-mpa.py <a name="mckm"></a>

This script can be used to convert an NCBI class2count (c2c) file obtained through MEGAN6  into kraken report (kreport) and metaphlan (mpa) formats. To obtain this c2c file, you can run MEGAN's `rma2info` program on a MEGAN read-count RMA file:

```
rma2info -i input.RMA -o NCBI.c2c.txt -c2c Taxonomy -n -r
```

Note that complete pipelines for aligning HiFi reads, annotation with MEGAN, and producing outputs files (including kreport and mpa files) are already available: [Taxonomic-Functional-Profiling-Protein](https://github.com/PacificBiosciences/pb-metagenomics-tools/tree/master/Taxonomic-Functional-Profiling-Protein), [Taxonomic-Profiling-Nucleotide](https://github.com/PacificBiosciences/pb-metagenomics-tools/tree/master/Taxonomic-Profiling-Nucleotide), and [MEGAN-RMA-summary](https://github.com/PacificBiosciences/pb-metagenomics-tools/tree/master/MEGAN-RMA-summary).

This script requires `python 3.7` and the python packages `ete3` and `pandas`. 

Output files are written to working directory (`label.megan-c2c.mpa.txt`, `label.megan-c2c.kreport.txt`, `label.intermediate.names.txt`, and `label.intermediate.taxid.txt`).

#### Basic Usage:

```
python Convert_MEGAN-RMA-NCBI-c2c_to_kreport-mpa.py -i <c2c file> -c <choice> -l <label string> -r <int>
```

#### Argument Explanations:

##### `-i <path-to-file>` or `--input <path-to-file>`

> **Required**: The MEGAN c2c file name or the path to a MEGAN c2c file.

##### `-c <choice>` or `--columns <choice>`

> **Required**: Whether the c2c file contains two columns (taxon, count) or three columns (rank, taxon, count).

##### `-l <string>` or `--label <string>`

> **Required**: A label used as a prefix to name the output files.

##### `-r <int>` or `--readcount <int>`

> **Required**: The total number of reads that were used for alignment (e.g. the number of starting reads).

##### `--update`

> **Optional**: If this flag is provided, ete3 will update the local NCBI taxonomy database before using it to perform the format conversion.

#### Example Usage:

```
python Convert_MEGAN-RMA-NCBI-c2c_to_kreport-mpa.py -i Sample1.NCBI.c2c.txt -c three -l Sample1 -r 1802756
```

#### Example Input File Contents:

This is an example of the three-column input c2c format.
```
-	NCBI	4996.0
D	Bacteria	225516.0
-	Opisthokonta	202.0
-	saccharomyceta	421.0
O	Bifidobacteriales	190.0
G	Bifidobacterium	15247.0
K	Fungi	37.0
S	Bifidobacterium adolescentis	13216.0
G	Faecalibacterium	171669.0
G	Veillonella	185265.0
P	Ascomycota	5.0
C	Saccharomycetes	1.0
O	Saccharomycetales	342.0
F	Saccharomycetaceae	172.0
-	Dikarya	105.0
F	Enterobacteriaceae	87430.0
O	Bacteroidales	61390.0
F	Prevotellaceae	1339.0
F	Lactobacillaceae	179.0
```

And this is the two-column c2c format:
```
NCBI	4996.0
Bacteria	225516.0
Opisthokonta	202.0
saccharomyceta	421.0
Bifidobacteriales	190.0
Bifidobacterium	15247.0
Fungi	37.0
Bifidobacterium adolescentis	13216.0
Faecalibacterium	171669.0
Veillonella	185265.0
Ascomycota	5.0
Saccharomycetes	1.0
Saccharomycetales	342.0
Saccharomycetaceae	172.0
Dikarya	105.0
Enterobacteriaceae	87430.0
Bacteroidales	61390.0
Prevotellaceae	1339.0
Lactobacillaceae	179.0
```


#### Example Output File Contents:

Output mpa format:
```
k__Bacteria	1372876
k__Bacteria|p__Actinobacteria	31647
k__Bacteria|p__Actinobacteria|c__Actinomycetia	29905
k__Bacteria|p__Actinobacteria|c__Actinomycetia|o__Bifidobacteriales	29905
k__Bacteria|p__Actinobacteria|c__Actinomycetia|o__Bifidobacteriales|f__Bifidobacteriaceae	29715
k__Bacteria|p__Actinobacteria|c__Actinomycetia|o__Bifidobacteriales|f__Bifidobacteriaceae|g__Bifidobacterium	28463
k__Bacteria|p__Actinobacteria|c__Actinomycetia|o__Bifidobacteriales|f__Bifidobacteriaceae|g__Bifidobacterium|s__Bifidobacterium_adolescentis	13216
k__Bacteria|p__Bacteroidetes	453571
k__Bacteria|p__Bacteroidetes|c__Bacteroidia	434294
k__Bacteria|p__Bacteroidetes|c__Bacteroidia|o__Bacteroidales	432333
k__Bacteria|p__Bacteroidetes|c__Bacteroidia|o__Bacteroidales|f__Bacteroidaceae	274659
k__Bacteria|p__Bacteroidetes|c__Bacteroidia|o__Bacteroidales|f__Bacteroidaceae|g__Bacteroides	273975
k__Bacteria|p__Bacteroidetes|c__Bacteroidia|o__Bacteroidales|f__Bacteroidaceae|g__Bacteroides|s__Bacteroides_fragilis	119761
```

Output kreport format:
```
69.38	1372876	27968	K	2	Bacteria
1.6	31647	1742	P	201174	  Actinobacteria
1.51	29905	0	C	1760	    Actinomycetia
1.51	29905	190	O	85004	      Bifidobacteriales
1.5	29715	1252	F	31953	        Bifidobacteriaceae
1.44	28463	15247	G	1678	          Bifidobacterium
0.67	13216	13216	S	1680	          Bifidobacterium adolescentis
22.92	453571	19277	P	976	  Bacteroidetes
21.95	434294	1961	C	200643	    Bacteroidia
21.85	432333	61390	O	171549	      Bacteroidales
13.88	274659	684	F	815	        Bacteroidaceae
13.85	273975	154214	G	816	          Bacteroides
6.05	119761	119761	S	817	          Bacteroides fragilis
```


[Back to top](#TOP)

---------------

## Convert_metamaps-KRONA_to_kreport-mpa.py <a name="mkkm"></a>

Metamaps is a metagenomics taxonomic profiler that was designed to be used with long reads. Currently, metamaps does not provide the option for kraken report (kreport) or metaphlan (mpa) formats. This script can be used to convert the KRONA output file from metamaps into kraken report (kreport) and metaphlan (mpa) formats. The krona file should have an extension that looks like `EM.reads2Taxon.krona`, and it is produced after running the `metamaps classify` module.

This script requires `python 3.7` and the python packages `ete3` and `pandas`. 

Output files are written to working directory (`label.metamaps-krona.mpa.txt`, `label.metamaps-krona.kreport.txt`, `label.intermediate.names.txt`, and `label.intermediate.taxid.txt`).

#### Basic Usage:

```
python Convert_metamaps-KRONA_to_kreport-mpa.py -i <krona file> -l <label string> -r <int>
```

#### Argument Explanations:

##### `-i <path-to-file>` or `--input <path-to-file>`

> **Required**: The `EM.reads2Taxon.krona` file name or the path to a `EM.reads2Taxon.krona` file.

##### `-l <string>` or `--label <string>`

> **Required**: A label used as a prefix to name the output files.

##### `-r <int>` or `--readcount <int>`

> **Required**: The total number of reads that were used for alignment (e.g. the number of starting reads).

##### `--update`

> **Optional**: If this flag is provided, ete3 will update the local NCBI taxonomy database before using it to perform the format conversion.

#### Example Usage:

```
python Convert_metamaps-KRONA_to_kreport-mpa.py -i Sample1.EM.reads2Taxon.krona -l Sample1 -r 1802756
```

#### Example Input File Contents:

Contents of the krona file (`EM.reads2Taxon.krona`), in which each read is assigned a taxon ID.
```
m64015_200911_223407/89456948/ccs	479436	1
m64015_200911_223407/96600344/ccs	76859	0.922311
m64015_200911_223407/103549548/ccs	817	0.39539
m64015_200911_223407/110561518/ccs	481805	1
m64015_200911_223407/124914168/ccs	195	0.717489
m64015_200911_223407/132253047/ccs	585394	1
m64015_200911_223407/139724371/ccs	566546	0.393522
m64015_200911_223407/8258180/ccs	817	0.548123
m64015_200911_223407/147325811/ccs	817	0.278916
m64015_200911_223407/155322615/ccs	536056	0.592172
m64015_200911_223407/163512428/ccs	469607	1
m64015_200911_223407/16254895/ccs	272559	0.665483
m64015_200911_223407/31654330/ccs	585394	1
m64015_200911_223407/39127347/ccs	817	0.559924
m64015_200911_223407/46598682/ccs	817	0.491624
m64015_200911_223407/61147908/ccs	349741	0.772543
```

#### Example Output File Contents:

Output mpa format:
```
k__Bacteria	1372876
k__Bacteria|p__Actinobacteria	31647
k__Bacteria|p__Actinobacteria|c__Actinomycetia	29905
k__Bacteria|p__Actinobacteria|c__Actinomycetia|o__Bifidobacteriales	29905
k__Bacteria|p__Actinobacteria|c__Actinomycetia|o__Bifidobacteriales|f__Bifidobacteriaceae	29715
k__Bacteria|p__Actinobacteria|c__Actinomycetia|o__Bifidobacteriales|f__Bifidobacteriaceae|g__Bifidobacterium	28463
k__Bacteria|p__Actinobacteria|c__Actinomycetia|o__Bifidobacteriales|f__Bifidobacteriaceae|g__Bifidobacterium|s__Bifidobacterium_adolescentis	13216
k__Bacteria|p__Bacteroidetes	453571
k__Bacteria|p__Bacteroidetes|c__Bacteroidia	434294
k__Bacteria|p__Bacteroidetes|c__Bacteroidia|o__Bacteroidales	432333
k__Bacteria|p__Bacteroidetes|c__Bacteroidia|o__Bacteroidales|f__Bacteroidaceae	274659
k__Bacteria|p__Bacteroidetes|c__Bacteroidia|o__Bacteroidales|f__Bacteroidaceae|g__Bacteroides	273975
k__Bacteria|p__Bacteroidetes|c__Bacteroidia|o__Bacteroidales|f__Bacteroidaceae|g__Bacteroides|s__Bacteroides_fragilis	119761
```

Output kreport format:
```
69.38	1372876	27968	K	2	Bacteria
1.6	31647	1742	P	201174	  Actinobacteria
1.51	29905	0	C	1760	    Actinomycetia
1.51	29905	190	O	85004	      Bifidobacteriales
1.5	29715	1252	F	31953	        Bifidobacteriaceae
1.44	28463	15247	G	1678	          Bifidobacterium
0.67	13216	13216	S	1680	          Bifidobacterium adolescentis
22.92	453571	19277	P	976	  Bacteroidetes
21.95	434294	1961	C	200643	    Bacteroidia
21.85	432333	61390	O	171549	      Bacteroidales
13.88	274659	684	F	815	        Bacteroidaceae
13.85	273975	154214	G	816	          Bacteroides
6.05	119761	119761	S	817	          Bacteroides fragilis
```

[Back to top](#TOP)


---------------

## Convert_metaphlan3_mpa_to_kreport.py <a name="mmkr"></a>

MetaPhlAn3 is a short-read metagenomics taxonomic profiler. It outputs the metaphlan (mpa) format, but not a kraken report. This script can be used to convert the mpa output file from MetaPhlAn3 into a kraken report (kreport) format. Because the mpa format from MetaPhlAn3 provides proportions rather than absolute read counts, the proportions are converted into estimated read counts based on the number of reads that were successfully aligned (from the bowtie2 step). The number of starting reads must also be provided, so the percentages of reads calculated in the kraken report are accurate.

Note that differences in mpa and NCBI taxonomy may provide some inaccurate **level** counts for higher taxa in the kraken report (occasionally a negative number), but the **cumulative** counts will always be accurate.

This script requires `python 3.7` and the python packages `ete3` and `pandas`. 

Output files are written to working directory (`label.metamaps-krona.mpa.txt`, `label.metamaps-krona.kreport.txt`, `label.intermediate.names.txt`, and `label.intermediate.taxid.txt`).

#### Basic Usage:

```
python Convert_metaphlan3_mpa_to_kreport.py -i <mpa file> -l <label string> -r <int> -m <int>
```

#### Argument Explanations:

##### `-i <path-to-file>` or `--input <path-to-file>`

> **Required**: The map file name or the path to an mpa file.

##### `-l <string>` or `--label <string>`

> **Required**: A label used as a prefix to name the output files.

##### `-r <int>` or `--readcount <int>`

> **Required**: The total number of reads that were used for alignment (e.g. the number of starting reads).

##### `-m <int>` or `--mappedreads <int>`

> **Required**: The total number of unique reads that were successfully aligned (e.g. the number of unique reads with alignments from bowtie2). This number will always be less than the `readcount` value provided.

##### `--update`

> **Optional**: If this flag is provided, ete3 will update the local NCBI taxonomy database before using it to perform the format conversion.

#### Example Usage:

```
python Convert_metaphlan3_mpa_to_kreport.py -i Sample1-profiled_metagenome.mpa.txt -l Sample1 -r 1802756 -m 1407360
```

#### Example Input File Contents:

The mpa format resulting from MetaPhlAn3:

```
#mpa_v30_CHOCOPhlAn_201901
#/home/dportik/.conda/envs/mpa/bin/metaphlan STD.sam --nproc 12 --input_type sam --nreads 1978852 -o STD-profiled_metagenome.txt --index mpa_v30_CHOCOPhlAn_201901 --bowtie2db /dept/appslab/datasets/dp_metaphlan
#SampleID	Metaphlan_Analysis
#clade_name	NCBI_tax_id	relative_abundance	additional_species
k__Bacteria	2	99.70225	
k__Eukaryota	2759	0.21428	
k__Archaea	2157	0.08347	
k__Bacteria|p__Firmicutes	2|1239	39.83772	
k__Bacteria|p__Proteobacteria	2|1224	27.76134	
k__Bacteria|p__Bacteroidetes	2|976	20.19486	
k__Bacteria|p__Fusobacteria	2|32066	6.92886	
k__Bacteria|p__Actinobacteria	2|201174	2.86286	
k__Bacteria|p__Verrucomicrobia	2|74201	2.09383	
k__Eukaryota|p__Ascomycota	2759|4890	0.21428	
k__Archaea|p__Euryarchaeota	2157|28890	0.08347	
k__Bacteria|p__Planctomycetes	2|203682	0.01992	
k__Bacteria|p__Chloroflexi	2|200795	0.00285	
k__Bacteria|p__Proteobacteria|c__Gammaproteobacteria	2|1224|1236	27.76134	
k__Bacteria|p__Firmicutes|c__Clostridia	2|1239|186801	23.12792	
k__Bacteria|p__Bacteroidetes|c__Bacteroidia	2|976|200643	20.19486	
```

#### Example Output File Contents:

The kreport output file:
```
0.02	437	0	K	2157	Archaea
0.02	437	0	P	28890	  Euryarchaeota
0.02	437	0	C	183925	    Methanobacteria
0.02	437	0	O	2158	      Methanobacteriales
0.02	437	0	F	2159	        Methanobacteriaceae
0.02	437	0	G	2172	          Methanobrevibacter
0.02	437	437	S	2173	            Methanobrevibacter smithii
26.43	523105	3	K	2	Bacteria
0.76	15020	1	P	201174	  Actinobacteria
0.53	10487	0	C	1760	    Actinomycetia
0.53	10487	0	O	85004	      Bifidobacteriales
0.53	10487	0	F	31953	        Bifidobacteriaceae
0.06	1127	0	G	240233	          Aeriscardovia
0.06	1127	1127	S	218139	            Aeriscardovia aeriphila
0.47	9360	1	G	1678	          Bifidobacterium
0.47	9217	9217	S	1680	            Bifidobacterium adolescentis
0.01	128	128	S	1686	            Bifidobacterium catenulatum
0.0	14	14	S	28026	            Bifidobacterium pseudocatenulatum
```

[Back to top](#TOP)

---------------

### DISCLAIMER
THIS WEBSITE AND CONTENT AND ALL SITE-RELATED SERVICES, INCLUDING ANY DATA, ARE PROVIDED "AS IS," WITH ALL FAULTS, WITH NO REPRESENTATIONS OR WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, ANY WARRANTIES OF MERCHANTABILITY, SATISFACTORY QUALITY, NON-INFRINGEMENT OR FITNESS FOR A PARTICULAR PURPOSE. YOU ASSUME TOTAL RESPONSIBILITY AND RISK FOR YOUR USE OF THIS SITE, ALL SITE-RELATED SERVICES, AND ANY THIRD PARTY WEBSITES OR APPLICATIONS. NO ORAL OR WRITTEN INFORMATION OR ADVICE SHALL CREATE A WARRANTY OF ANY KIND. ANY REFERENCES TO SPECIFIC PRODUCTS OR SERVICES ON THE WEBSITES DO NOT CONSTITUTE OR IMPLY A RECOMMENDATION OR ENDORSEMENT BY PACIFIC BIOSCIENCES.

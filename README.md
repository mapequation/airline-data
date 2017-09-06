
# Airline data

Scripts to automatically download and preprocess airline data for Infomap

Using _Airline Origin and Destination Survey (DB1B)_ from [Bureau of Transportation Statistics (transtats.bts.gov)](https://www.transtats.bts.gov/databases.asp?Mode_ID=1&Mode_Desc=Aviation&Subject_ID2=0):

>Origin and Destination Survey (DB1B) is a 10% sample of airline tickets from reporting carriers. Data includes origin, destination and other itinerary details of passengers transported.

## Install
Run
```bash
make install
```
to install required python and node.js dependencies


## Download

Prezipped data can be downloaded from:
```
https://transtats.bts.gov/PREZIP/Origin_and_Destination_Survey_DB1BCoupon_{year}_{quarter}.zip
```
where `{year}` is substituted to a year `1993-2017` and `{quarter}` to an integer `1-4`.

Selected data is stored temporarily at https://transtats.bts.gov/ftproot/TranStatsData/.

Automatically download, extract, rename and clean data with `download.js`:

```
  Usage: download [options]


  Options:

    -V, --version             output the version number
    -y, --year <years>        Select years from 1993-2017 (e.g. -y 1995..2000,2010,2015)
    -q, --quarter <quarters>  Select quarters from 1-4 (e.g. -q 1,4. Default 1..4)
    -f, --force               Force overwrite even if file exist
    -m, --minimal             Download minimal number of data columns
    -t, --type <type>         Type of data, one of Coupon or Market, default Coupon
    -d, --debug               Run test
    -h, --help                output usage information
```

### Example

```bash
node download.js --year 2010..2016
```
to download data for selected years, one file per quarter. The extracted files are renamed according to year, quarter and type, and the content is fixed (removing trailing commas).


## Generate paths

Pathways are formed by multiple source-desitionation pairs per itinerary id. Sample frequencies of path lengths:
```bash
cat 341756927_T_DB1B_MARKET_2017_1.csv | cut -d, -f1 | sort -n | uniq -c | tr -s ' ' | cut -d' ' -f2 | sort -nr | uniq -c

   3 9
  12 8
   9 7
 154 6
 319 5
10437 4
21259 3
2251776 2
1254842 1
```

```bash
341756927_T_DB1B_COUPON_2017_1.csv
   1 14
   1 13
   9 12
  21 11
  84 10
 213 9
 958 8
3203 7
32452 6
60448 5
904186 4
285497 3
1717666 2
534072 1
```

Generate paths with `make_paths.py`:

```
usage: make_paths.py [-h] input

Make paths from csv data.

positional arguments:
  input       input csv file

optional arguments:
  -h, --help  show this help message and exit
```

### Example
```bash
python make_paths.py data/2011_1_Coupon.csv
python make_paths.py data/2011_2_Coupon.csv
python make_paths.py data/2011_3_Coupon.csv
python make_paths.py data/2011_4_Coupon.csv
```


## Generate state networks of different order from paths data

Generate ngrams in state format from paths data with `paths_to_states.py`:

```
usage: paths_to_states.py [-h] [-o ORDER] -y YEAR -q QUARTER
                          [-c COUNT_THRESHOLD]
                          [input]

Paths to states format.

positional arguments:
  input                 optional input paths file to use instead of from args

optional arguments:
  -h, --help            show this help message and exit
  -o ORDER, --order ORDER
                        markov order (default: 1)
  -y YEAR, --year YEAR  year
  -q QUARTER, --quarter QUARTER
                        quarter (1-4), use multiple times for many quarters
  -c COUNT_THRESHOLD, --count-threshold COUNT_THRESHOLD
                        Ignore paths with count less than this threshold
                        (default: 2)
```

The input filenames are inferred from the `year` and `quarter` arguments, assuming they are generated before (see above).

### Example
```
python paths_to_states.py -y 2011 -q1 -o2
python paths_to_states.py -y 2011 -q2 -o2
python paths_to_states.py -y 2011 -q3 -o2
python paths_to_states.py -y 2011 -q4 -o2
python paths_to_states.py -y 2011 -q1 -q2 -o2
python paths_to_states.py -y 2011 -q3 -q4 -o2
python paths_to_states.py -y 2011 -q1 -q2 -q3 -q4 -o2
```

## Generate multilayer state networks from individual state networks

Multiple individual state networks can be combined to a multilayer network with `states_to_multilayer_states.py`:
```
usage: states_to_multilayer_states.py [-h] [-r RELAX_RATE]
                                      input [input ...] output

Join states to multilayer states

positional arguments:
  input                 input states files
  output                output filename

optional arguments:
  -h, --help            show this help message and exit
  -r RELAX_RATE, --relax-rate RELAX_RATE
                        Multilayer relax rate
```

### Example
Run
```
python states_to_multilayer_states.py data/2011_12_states_2.net data/2011_34_states_2.net data/2011_12_34_states_2.net
```
to generate a multilayer network with two layers from quarters 1-2 and 3-4 respectively.

Run
```
python states_to_multilayer_states.py data/2011_1_states_2.net data/2011_2_states_2.net data/2011_3_states_2.net data/2011_4_states_2.net data/2011_1_2_3_4_states_2.net
```
to generate a multilayer network with a layer for each quarter.


## Statistics

Run
```bash
python statistics.py clusterfile.clu
```
to calculate and print module perplexity and module assignments etc.


## Other

Metadata on airports available from "Master Coordinate" in [Aviation Support Tables](https://www.transtats.bts.gov/Tables.asp?DB_ID=595#)

Links on filtering the DB1B dataset:
* http://catsr.ite.gmu.edu/SYST660/BigDataAnalysisInAviation_DB1B.pdf
* http://leea.recherche.enac.fr/Steve%20Lawford/projects/fares.pdf


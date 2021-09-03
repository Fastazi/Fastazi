# Fastazi

Comparison between Test Case Selection, Test Case Prioritization and their combination.

This is the results and replication package for the paper titled 
*Comparing and Combining File-based Selection and Similarity-based Prioritization towards Regression Test Orchestration*, submitted to ICSE22.
**Please do not fork this repository or otherwise attempt to modify
its contents before the paper is peer-reviewed and published.**

Utilizes 
[Ekstazi](http://ekstazi.org) for selection and 
[FAST](https://github.com/icse18-FAST/FAST) for prioritization.
Utilizes [Defects4J](https://github.com/rjust/defects4j) for experiment subjects.

## Repository contents

* The `results` directory contains spreadsheets and figures with the data utilized in the paper. 
These were the results of our experiments with the tool.
* The `scripts` directory contains shell scripts that automate the execution of experiments.
* The `metrics` directory is where the output of the experiments are located after execution.
* The `tools` directory contains:
  * Modified source code for FAST in Python;
  * The JARs for the Ekstazi Maven and Ant plugins;
  * Additional Python scripts needed for running the experiments.
* `Dockerfile` and `docker-compose.yml` files to streamline the experiments using Docker.

## Running the experiments

Our experiments were run on the following setup:
* Host computer: Mac mini (2018)
  * OS: macOS 11.4
  * CPU: 3.2 GHz 6-Core Intel Core i7
  * Memory: 32 GB 2667 MHz DDR4
  * Storage: 512GB SSD
* Docker engine: v20.10.6
  * Image: Ubuntu 20.04 LTS
  * Available CPU: 12 cores
  * Available memory: 8GB
  * Available swap: 2GB

### 1. Clone the repository

```bash
git clone [url]
cd fastazi
```

The easiest way to run the experiments is using Docker.
To do so, follow the steps in section 2, then skip to section 4.
Otherwise, follow the steps in section 3 to install the
required dependencies without Docker.

### 2. Setup using Docker

#### 2.1 Installing Docker

Please follow the [Docker Engine installation instructions](https://docs.docker.com/engine/install/)
from the Docker website according to your operating system.

#### 2.2. Create the Docker image
```bash
docker build -t fastazi_img --rm .
```
This will create a Docker image named `fastazi_img`, 
which runs Ubuntu 20.04 LTS and has all the necessary 
Linux, Python and Java dependencies installed as well 
as Defects4J.

See `Dockerfile` for the full contents of this image. 
This image will be made publicly available through Docker 
Hub after the paper is published.

#### 2.3. Run the Docker container
```bash
docker compose run fastazi
```
This creates a Docker container from `fastazi_img` that has
access to the `scripts`, `tools` and `metrics` directories.

Upon completion, your terminal will be running Bash within
the container at the `/home/fastazi/` path.

### 3. Manual setup



### 4. Run the experiments
To run the experiments for all available subjects using their
recommended versions (replicating the results from the paper), run:
```bash
./scripts/run_multiple.sh
```

To run experiments for individual subjects, run
```bash
./scripts/run_fastazi.sh [min_ver] [max_ver] [subject] [build]
```
* `min_ver` is the first version of the subject to be used.
* `max_ver` is the last version of the subject to be used.
* `subject` is the subject for the experiment.
* `build` determines whether compilation will use Maven or Ant.

For more information about these parameters, see the table 
under **Experiment Subjects**.


## Experiment Subjects
The following table contains our suggested parameters for the subjects:

| Project | Build | Min. ver | Max. ver | Skipped |
--- | --- | --- | --- | ---
Chart | ant | 1 | 26 | - |
Cli | mvn | 11 | 40 | - |
Closure | ant | 4 | 176 | 21,63,93,137,146 |
Codec | mvn | 11 | 18 | - |
Collections | mvn | 25 | 28 | - |
Compress | mvn | 9 | 47 | - |
Gson | mvn | 1 | 18 | - |
Jsoup | mvn | 1 | 93 | - |
JxPath | mvn | 19 | 22 | - |
Lang | mvn | 14 | 41 | - |
Math | mvn | 5 | 104 | - |
Time | mvn | 3 | 26 | 21 |

A few observations about the Defects4J subjects:
* We did not use `JacksonCore`, `JacksonDatabind`, `JacksonXml` 
and `Mockito` due to issues compiling these projects with Java 1.8.0.
* Similarly, in some projects we omitted certain
versions for some possible reasons:
  *  they either used a different build system, 
  *  or had compilation issues with Java 1.8.0, 
  *  or were marked as deprecated in the Defects4J documentation, 
  *  or there were no detected changes from the previous version.
* There were also some cases where either Ekstazi or FAST failed
to run in a certain version. In most of these cases, there was an
encoding error issue in one of the source files that was fixed in
the subsequent version. Nevertheless, these versions were omitted
from the experiment.
* On `Chart`, `Closure`, `Lang`, `Math` and `Time`, the Defects4J
versions are in *reverse chronological order*. That is, version 1
is the newest commit.
Naturally, for a regression testing experiment, it is necessary
for changes to be considered in chronological order.
Therefore, we reverse the numerical order of these projects
(e.g. Chart is processed from 26 to 1), so the results are
in chronological order.

## Results description and legend

Within the `results` and `metrics` directories, you will find files 
following this pattern for each experiment subject:

* `avg.csv`: Reports average results over the 30 repetitions for each 
  software version and test suite.
* `raw.csv`: Reports the individual results for each of the 30 repetitions
  for each software version and test suite.
* `budget_all.csv`: Provides results considering budget, with 100% defined
  as the size of the entire test suite.
* `budget_selected.csv`: Provides results considering budget, with 100% defined
  as the size of the test suite selected by Ekstazi on each version.
* `time.csv`: Shows the time taken by each step of the approaches on each
  software version.
* `time_avg.csv`: Averages of the time taken by each step of the approaches across
  all software versions.

The metrics reported in these tables are:
* `Test count`: The number of tests in a particular version of the test suite.
* `APFD`: The non-normalized APFD result.
* `APFDf`: APFD normalized according to the full test suite size (used in the paper).
* `TTFF`: The non-normalized TTFF result.
* `pTTFF`: TTFF normalized according to the full test suite size (used in the paper).
* `Misses`: The number of times, out of the 30 repetitions, that the test suite was unable to detect the fault.
* `Hit`: 1 if the fault was detected in all 30 repetitions; 0 otherwise.
* `Misses`: The number of times, out of the 30 repetitions, that the test suite was able to detect the fault.

The test suites compared in these tables are:
* `Ekstazi+random`: 30 permutations of the test suite selected by Ekstazi.
* `FAST-pw`: 30 prioritizations of the test suite using FAST-pw.
* `Fastazi-S`: The sequential version of Fastazi (used in the paper).
* `Fastazi-P`: The parallel version of Fastazi (briefly described in the paper).
* `Random`: 30 permutations of the entire test suite.

## References from the paper to this repository

Throughout the paper, the † symbol is used to indicate when additional information 
can be found in this repository. This list serves to guide a reader from certain
parts of the paper to the relevant piece of data.

* In the paper, the sequential version of Fastazi (`Fastazi-S`) is used primarily. 
  In this repository, results from the parallel version are found under the name `Fastazi-P`.
* In the paper, TTFF and APFD results are normalized according to the size of the
  full test suite, as a matter of fairness towards the approaches that select test
  cases. In this repository, the normalized versions of the metrics are named `pTTFF`
  and `APFDf`, while the standard names refer to the non-normalized values.
* This repository contains the instructions for preparing a Docker container identical
  to the one used for the experiments.
* The `results` directory contains the full datasets used to generate the plots found
  in the paper.
* The `results` directory also contains the full results of the statistical analysis,
  including the numerical values of the Vargha and Delaney measures.
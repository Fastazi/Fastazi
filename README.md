# Fastazi

Tool for combining Test Case Selection and & Test Case Prioritization.

This is the results and replication package for the paper titled 
*Combining File-based Selection and Similarity-based Prioritization 
for Improved Software Regression Testing*, submitted to ICSE22.
Please do not fork this repository or otherwise attempt to modify
its contents before the paper is peer-reviewed and published.

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
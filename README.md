Artifact for "On the Impact of Test Oracle in Smart Contract Security Testing"
========

# Experiment
This repository is for comparing performance differences across tools under
different test oracles. We compare the performance of three tools: Smartian,
SmarTest, and RLF. We compare the performance of these tools under different
test oracles and analyze the results to understand the impact of test oracles on
the performance of these tools.

# Structure

We run all our experiments in a dockerized environment. In
[docker-setup](./docker-setup), we provide various files required to build the
docker image. The [benchmarks](./benchmarks) directory contains benchmarks we
used for the experiments. In [scripts](./scripts), you can find scripts to run
the experiments and analyze their results.

# Setup

We assume that your system has Docker installed. Also, you should be able to run
the `docker` command without `sudo`. The following command will build the
docker image name 'oracle-artifact', using our [Dockerfile](./Dockerfile).

```
$ ./build.sh
```

Next, check the `MAX_INSTANCE_NUM` configuration parameter in
[scripts/run\_experiment.py](./scripts/run_experiment.py) script, which decides
the number of containers to run in parallel.  Currently, this parameter is set
to 60. Make sure that this parameter value is lower than the number of cores in
your machine.

# Evaluation of the impact of test oracle
To reproduce our experiment, you can run the following script. This script
internally executes `run_experiment.py` to run each tool in the paper.
Here, the script argument specifies the number of repetition for the experiment.

```
$ ./scripts/test_ELSC_compare.sh 40
```

After the above command finishes, you will obtain the `output/result-EL`
directory that contains the raw data. For instance, `Smartian` subdirectory
contains the result of running Smartian that uses its own test oracle.
'Smartian-SmarTest' subdirectory contains the result of running Smartian that
uses SmarTest's test oracle, and so on.

Now, you can parse the experiment results as below.

```
$ python scripts/plot_ELSC_bug.py output/result-EL/Smartian/*
```

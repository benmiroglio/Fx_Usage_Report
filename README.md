# Firefox Public Data

The [Firefox Public Data](https://metrics.mozilla.com/protected/usage-report-demo/dashboard/user-activity) (FxPD) project is a public facing website which tracks various merics over time and helps the general public understand what kind of data is being tracked by Mozilla and how it is used. It is modeled after and evolved out of the [Firefox Hardware Report](https://hardware.metrics.mozilla.com/), which is now included as a part of FxPD. 

This repository contains the code used to pull and process the data for the **User Activity** and **Usage Behavior** subsections of the **Desktop** sections of the report. 

The website itself is generated by the [Ensemble](https://github.com/mozilla/ensemble) and [Ensemble Transposer](https://github.com/mozilla/ensemble-transposer) repos. 

# Data

The data is pulled from Firefox desktop [telemetry](https://wiki.mozilla.org/Telemetry), specifically the [main summary](https://docs.telemetry.mozilla.org/datasets/batch_view/main_summary/reference.html) view of the data. 

The data is on a weekly resolution (one datapoint per week), and includes the metrics below. The metrics are estimated from a 10% sample of the Release, Beta, ESR, and Other channels, and broken down by the top 10 countries and worldwide overall aggregate. The historical data is kept in an S3 bucket as a JSON file. 

This job (the repo) is designed to be run once a week and will produce the data for a single week. It will then update the historical data in the S3 bucket. 

For backfills, this job needs to be run for each week of the backfill. 


#### Metrics

For the list of metrics, see [METRICS.md](METRICS.md). 

#### Data Structure

For a description of the structure of the data output, see [DATAFORMAT.md](DATAFORMAT.md).

# Developing

#### Run the Job

To initiate a test run of this job, you can clone this repo onto an ATMO cluster. First run

	$ pip install py4j --upgrade

from your cluster console to get the latest version of `py4j`.


Next, clone the repo, and from the repo's top-level directory, run:

	$ python usage_report/usage_report.py --date [some date, i.e. 20180201] --no-output

which will aggregate usage statistics from the last 7 days by default. It is recommended when testing to specifiy the `--lag-days` flag to `1` for quicker iterations, i.e

	$ python usage_report/usage_report.py --date 20180201 --lag-days 1 --no-output

*Note: there is currently no output to S3, so testing like this is not a problem. However when testing runs in this way, always make sure to include the flag* `--no-output`

#### Testing

Each metric has it's own set of unit tests. Code to extract a particular metric are found in `.py` files in `usage_report/utils/`, which are integrated in `usage_report/usage_report.py`.

To run these tests, first ensure to install `tox` and `snappy`:

	$ pip install tox
	$ brew install snappy # MacOS only


Once installed, you can simply run

	$ tox

from the repo's top-level directory. This command invokes `pytest` and also runs `flake8` tests on the codebase, which is a style linter.


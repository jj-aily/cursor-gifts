
## Tool installation instructions

* Create a directory, say aws-tool, and copy the script into this directory
* Generate a virtual environment with 'python -m venv .venv'
* Activate the virtual environment with 'source .venv/bin/activate'
* Install the single dependency 'pip install boto3'

## Tool usage instructions

* Use AWS Dashboard to login to AWS
* Click on Access Keys and copy the values in Option 1:

```
export AWS_ACCESS_KEY_ID="<some-key>"
export AWS_SECRET_ACCESS_KEY="<some-secret>"
export AWS_SESSION_TOKEN="<some-token>"
```
* Run the tool following the example below:

```
./list_executions.py --hours 72 --state-machine "arn:aws:states:eu-west-1:730335534205:stateMachine:plai-eu-west-1-pipeline-sm" --region "eu-west-1" --name "sanofi-prod-dataloader-bucket" --key-contains "supply_kpi_parquet"
```



## Steps to arrive at this script using Cursor

* Please generate a command line utility to list all AWS executions in the last 24 hours.  The utility should be written in Python using standard libraries to access Amazon services.
* The only values one can assign to statusFilter are [SUCCEEDED, TIMED_OUT, PENDING_REDRIVE, ABORTED, FAILED, RUNNING].  Modify the code so that the user can provide on the command line which state should be displayed
* Each step function has an execution input in JSON format.  Modify the code to display the execution format pretty printed.
* The execution input contains two attributes: name and key.  Modify the code so that the user can optionally specify an exact match for name that should be used to filter out results and an optional substring that if present in key should also be used to filter out results
* Modify the code so that the user can optionally specify which SSO region to use within AWS

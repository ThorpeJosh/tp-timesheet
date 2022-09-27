# tp-timesheet
Automated submission of TP timesheets

## Usage
This tool is published on pypi so from any terminal with python3 installed run:

``` bash
pip install tp-timesheet
```

Then setup the URL and EMAIL to use for the timesheet submission by running the following:

``` bash
export TP_EMAIL='<TP EMAIL ADDR>'
export TP_URL='<URL OF TIMESHEET>'

# Add these to your ~/*.rc for this to be persistent
```

Then run the tool with the help option to find out additional usage information

``` bash
tp-timesheet --help
```

### Common cli options

``` bash
# submit today
tp-timesheet --start today

# submit for next 5 days
tp-timesheet --start today --count 5

# submit for Mon 3/10/22 to Thursday 6/10/22
tp-timesheet --start '3/10/22' --count 5

# Schedule the form to submit automatically on weekdays
tp-timesheet --automate weekdays

# append '--debug' to any command to get more log messages about what is going on
```

## Development
Install and run tool locally (append `--help` to see how to use it):

```bash
pip install -e .

tp-timesheet ...
```

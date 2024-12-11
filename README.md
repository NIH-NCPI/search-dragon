# search-dragon

**`search-dragon`** Unified API Interface for ontology search APIs.

## Prerequisites

## Package installation

1. **Install the package and dependencies**:
    ```bash
    pip install git+https://github.com/NIH-NCPI/search-dragon.git
    ```
3. **Run a command/action**

   ## Available actions:
   * [run_search](#run_search) <br>

## Commands
### <u>run_search</u> <br>
#### Usage
```bash
run_search -s <search_api> -k <keyword> -o <ontologies>
```
* -s, --search_api
    * Description: APIs to include in the search
    * Choices:
        * `ols`: Gather data with the Ontology Lookup Service API.
        * `all`: Gather data using all available ontology APIs.
    * Required: No
    * default: "all" ? TODO

* -k, --keyword
    * Description: Keyword to search against the APIs
    * Required: No

* -o, --ontologies
    * Description: User preferred Ontologies
    * Default: A default list of approved ontologies is provided. If none are selected, data from all ontologies on this list will be returned.
    * Required: No

## Running the script locally or working on a branch?
1. **Create and activate a virtual environment** (recommended):

[[Click here]](https://realpython.com/python-virtual-environments-a-primer/) for more on virtual environments.

    ```
    # Step 1: cd into the directory to store the venv

    # Step 2: run this code. It will create the virtual env named utils_venv in the current directory.
    python3 -m venv utils_venv

    # Step 3: run this code. It will activate the utils_venv environment
    source utils_venv/bin/activate # On Windows: venv\Scripts\activate

    # You are ready for installations! 
    # If you want to deactivate the venv run:
    deactivate
    ```
2. **Install the package** <br>
    If working on a new feature it is possible to install a package version within
    the remote or local branch
      ```
    # remote
    pip install git+https://github.com/NIH-NCPI/locutus_utilities.git@{branch_name}

    # local
    pip install -e .
    ```
3. **Run commands**<br>
    Run the command from the root of the directory. Checkout data/logs while troubleshooting. 
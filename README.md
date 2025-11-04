# search-dragon

**`search-dragon`** Unified API Interface for ontology search APIs, OLS and UMLS.


## Running the script locally or working on a branch?
1. **Create and/or activate a virtual environment** (recommended):

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
    the remote or local branch <br>
    
    - **Locutus Users** <br>
    1. If testing changes to search-dragon in `locutus` don't forget to deploy a `locutus` branch with the correct `search-dragon` version in the toml file! <br>
    2. Any new env variables created, e.g. api keys, will need to be added to the `locutus` deployment files.

    Installation methods:
      ```bash
    Search-dragon should installed using the following command.
    pip install git+https://github.com/NIH-NCPI/search-dragon.git

    # This install command will ensure the proper version installed. Useful for troubleshooting purposes.
    pip install --force-reinstall --no-cache-dir git+https://github.com/NIH-NCPI/search-dragon.git

    # Installing a specific branch of search-dragon.
    pip install git+https://github.com/NIH-NCPI/search-dragon.git@{branch_name}

    # Use this method for local development. In the root dir of the cloned repo run this command to enact local changes. 
    pip install -e .
    ```

## Dragon Search
Based on a CLI tool from DBT Utilities that Brenda has written, *dragon_search* provides the ability to do basic ontology searches using the same backed functionality that Locutus is currently using, though, adjusted for more general use. 

Some example usages: 
```bash
$ dragon_search -ak "lung|diabetes|heart" -o "HP,HPO,MONDO"
```

By default, the results are passed to the terminal via stdin and are displayed as a rich table. 

If you want to write the results to a file, simply pass a filename for the results: 
```bash
$ dragon_search -ak "HP:0000873|OMIM:616421" -f quick-onto-search.csv
```

When writing results to a file, logging is written to stdout. When writing to a stdout, logging is written to the file, 'logs/search.log'

  ## Notes
  ### API usage
  - OLSSearchAPI
    - MapDragon tested
    <br>
  - OLSSearchAPICode
    - DBT tested. 
    - This url is more reliable for searching on a code(HP:0003045)
    <br>
  - UMLSSearchAPI
    - MapDragon tested
# search-dragon

**`search-dragon`** Unified API Interface for ontology search APIs to be used by the locutus application.


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
    **NOTE** If testing changes to search-dragon in `locutus` don't forget to deploy a `locutus` branch with the correct `search-dragon` version in the requirements.txt file! 
    **NOTE** Any new env variables created, e.g. api keys, will need to be added to the `locutus` deployment files.
      ```
    # remote
    pip install git+https://github.com/NIH-NCPI/search-dragon.git@{branch_name}

    # local
    pip install -e .

    # Locutus should install using the following command.
    pip install git+https://github.com/NIH-NCPI/search-dragon.git

    # A re-install might be required while testing any changes to this repo, use this command to force the reinstall and ensure the latest version.
    pip install --force-reinstall --no-cache-dir git+https://github.com/NIH-NCPI/search-dragon.git
    ```
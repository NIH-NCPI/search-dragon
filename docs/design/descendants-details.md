# Implementation Details for Descendants
## Create New API Search class
Create a new OLS Search class that is a child of the ols code api class and override the following functions: 
- collect_data
- build_url
- harmonize_data

These will be somewhat different from what was necessary for the regular search

Create a reference to the new class inside the [SEARCH_APIS](https://github.com/NIH-NCPI/search-dragon/blob/main/src/search_dragon/search.py#L20) lookup. Be sure to use a reasonably description key. 

## Create a new search function
Create a new function, similar in part to the [do_search](https://github.com/NIH-NCPI/search-dragon/blob/main/src/search_dragon/search.py#L96) function. This will explicitly know to use the class based on the key you defined in the new SEARCH_APIS entry

For now, the output can be similar to the output being written in the existing do_search function, however, maybe rename some of the headers to be more specific to the use case (so parent code instead of keyword, etc)

## Add CLI argument for descendants
Add a new argument, something like --descendants, to the [argument parser](https://github.com/NIH-NCPI/search-dragon/blob/main/src/search_dragon/search.py#L178). This should be one of the [action='store_true'](https://docs.python.org/3/library/argparse.html#action) types. 

you will then need to confirm that was selected to decide whether to do the [regular search](https://github.com/NIH-NCPI/search-dragon/blob/main/src/search_dragon/search.py#L196) or your new search function defined above.

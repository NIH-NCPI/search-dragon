# Search Dragon - Descendants

![status](https://img.shields.io/badge/status-draft-yellow) ![version](https://img.shields.io/badge/version-0.1.0-lightgrey)

| | |
|---|---|
| **Author** | Eric Torstenson |
| **Created** | 2026-05-28 |
| **Updated** | 2026-05-28 |
| **Reviewers** | — |


## 1. Overview

Add new search capability to search dragon to enable pulling down all descendants for a given term from within a hierarchical ontology.


### Goals

- Add new search to application for pulling descendants for a given term
- Add support to OLS and possibly UMLS depending on time


### Non-Goals

- This will only return codes and displays and will not expand linkml enums


## 2. Context & Motivation


### Background

Oaklib's vskit is failing on certain ontologies, which OLS supports. We be moving toward writing our own expansion code that relies on OLS APIs.


### Motivation

There is uncertainty whether the issues we encountered with using vskit could be overcome without a lot of work. OLS has been proven to return the correct codes for some of the required expansions. Without this, there is a real risk that the enumeration expansion will not be able to move forward without a significant amount of effort.


### References

- [OLS Descendants Discovery work](https://docs.google.com/document/d/1bATkZ4Sh-BhR3LXxIrfYJEo2vmvMCn1zIzSQsShJvjU/edit?usp=sharing)
- [Implementation Details](design/descendants-details)


## 3. Scope


### In Scope

- Add new command line argument to the search dragon app to support the new query
- Add new application function to properly dispatch the api execution
- Add functionality to each of the relevant API search models to perform the new search


### Out of Scope

- This only involves code responses, not expansion of enumerations


### Constraints

- Prioritize OLS functionality


### Assumptions

- We are expecting that our expansions can always be handled by OLS or UMLS


## 4. Stakeholders

| Role | Name | Responsibilities |
|---|---|---|
| Developer | Yelena Cox | Add new functionality to the search dragon application |


## 5. Technical Design


### Architecture

Add functionality to the search dragon application to enable searches that return all descendant codes for a given ontological term from a hierarchical ontology using the search APIs currently supported by the application.


#### Components

| Component | Technology | Description |
|---|---|---|
| **Search Dragon** | `Python` | This is the tool/library used by MapDragon to search the different APIs for terms. |


### Interfaces


#### Inputs

| Name | Format | Description |
|---|---|---|
| `Search API` | either OLS, UMLS, ALL | This will indicate which API the user wishes to query. Users may ask for the search to iterate over all possible searches until a successful response is found. |
| `Ontology (Curie)` | string | one of the accepted Curies, such as HP, OMIM, etc. For some, there may be different requirements for each of the two ontologies, ie HP vs HPO for OLS or UMLS, respectively. |
| `Parent Code` | string | Code for whom the descendants are requested. |


#### Outputs

| Name | Format | Description |
|---|---|---|
| `Descendants` | CSV File | for the first pass, we'll just use a CSV format that is very similar to the [standard search_dragon CLI return](https://github.com/NIH-NCPI/search-dragon/blob/main/src/search_dragon/search.py#L142) except possibly column names that are more appropriate for this particular type of search.
 |


## 6. Implementation Approach


### Strategy

This will simply leverage the existing search APIs using different queries to perform the extraction of descendant codes.


### Phases

**Phase 1 — Initial Run**

This should, at the very least, provide basic support for the same types of output as is already supported by search dragon, but for descendants instead of basic matches.



### Error Handling

Errors should be reported as exceptions which yield descriptive details to the stderr.


### Logging

- DEBUG:  We should be able to trace every key step at the debug level - INFO: Basic messages relating to successful queries - WARN: Problems that aren't necessarily errors, such as a search failing
  on the first ontology, but was found in the second
- ERROR: Errors encountered


## 7. Testing Strategy


### Test Cases

| ID | Description | Expected Result |
|---|---|---|
| TC-001 | [What is being tested] | [What success looks like] |


## 8. Risks & Mitigations

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R-001 | As with all SearchDragon runs, this is entirely dependendent on the APIs and will not work if those change or are down.  | low | medium | Changes to the APIs themselves may be mitagated by fixes to the application's code. |


## 9. Open Questions

| ID | Question | Owner | Due |
|---|---|---|---|
| Q-001 | Can UMLS provide similar responses to OLS? | Yelena will perform similar discovery work for UMLS if time permits. | 2026-06-15 |


## 10. Decision Log


### D-001 — We decided to only support relationship types of type SubclassOf for now

**Date:** 2026-05-28  
**Rationale:** Any other type would be a totally different endpoint and will require similar amounts of work to support.

**Alternatives considered:**
- Investigate other possibilities, such as ancestors, etc.


### D-002 — CSV Export

**Date:** 2026-05-28  
**Rationale:** To remain consistent with the other search dragon functionality

**Alternatives considered:**
- There was consideration of returning objects. Ultimately, it may be worth refactoring the app to return objects and let the application itself decide the final format


## 11. Appendix



---
*Generated from `descendants.yaml` on 2026-05-28*

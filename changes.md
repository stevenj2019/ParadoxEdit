# Version:0.1

## Changes: 
* Formalised Context, split BlockContext+NodeContext to provide more actions
* Added Legacy->modern loc converstion (removing :0 stuff)
* Added Error-checking for missing loc keys
* Added form to localise selected key
* Removed category system, in favour of (significantly better) Directory Walk system.
* Fixed Settings form on first launch being skip-able (will cause error only fixable with file deletion, and leave you unable to load mods)
* Added Search Functionality (Project-Wide, not in file)
* better loading bar (and process) for load order file processing
* ctrl+c copy, ctrl+f search

## Included Scripts 
* Bulk-Add GFX files (file writes/ and icon copies)
* Localisation tooling (for events only for now)

## TODO
### Generic
### Contexts
* Focus Trees/Decisions/Events, should have icon/localisation forms/context/detection/errors.
### LoadOrder Related
* ability to copy file to a new source (effective override)
* ability to add a directory to replace_path (in descriptor)
* alphabetical sorting as second priority (sort by dependency, then by alphabetical) (done, i think?)
* DLC tooling
### Architecture
* Updates Actions Build Process
### Fixes 
* POPULATE (i think? complete?)
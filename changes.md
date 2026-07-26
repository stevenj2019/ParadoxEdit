# Version:0.1

## Changes: 
* Formalised Context, split BlockContext+NodeContext to provide more actions
* Added Legacy->modern loc converstion (removing :0 stuff)
* Added Error-checking for missing loc keys
* Added form to localise selected key
* Removed category system, in favour of (significantly better) Directory Walk system.
* Fixed Settings form on first launch being skip-able (will cause error only fixable with file deletion, and leave you unable to load mods)
* Added Search Functionality (Project-Wide, not in file)

## Included Scripts 
* Bulk-Add GFX files (file writes/ and icon copies)
* Localisation tooling (for events only for now)

## TODO
### Generic
* Ensure ParadoxVanilla objects cannot be modified. regardless of how.
* Help Sections/ToolTips
* intenral localisation/language management (just english, but allow people to upload other languages for support, if they do the work)
### Cotexts
* Focus Trees/Decisions, should have icon/localisation forms/context/detection/errors.
### LoadOrder Related
* ability to copy file to a new source (effective override)
* ability to add a directory to replace_path (in descriptor)
* alphabetical sorting a ssecond priority (sort by dependency, then by alphabetical)
* DLC tooling
* review load-order resolution (slow as shit on a per-change basis)
### Architecture
* Updates Actions Build Process
### Fixes 
* POPULATE
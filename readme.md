[![Build Status](https://travis-ci.org/lepoidev/knote.svg?branch=master)](https://travis-ci.org/lepoidev/knote)
# knote
Tool for the creation and organization of digital class notes.

## Options
By default, running `knote` will ensure a note for the currently active subject exists and opens it with the configured application.

* '-n/--new' (add new subject)
* '-r/--remove' (remove a subject)
* '-e/--edit' (edit a subject)
* '-o/--open' (open a specific subject)
* '-l/--list' (list all subjects)

# Configuration
## Environment variables
```bash
export KNOTE_PATH=...          # path which contains knote.py
export KNOTE_CONFIG=...        # path to knote config json file
export KNOTE_SUBJECTS_PATH=... # where you want to store your class folders
```

## Add an Alias
```bash
alias knote='python3 "$KNOTE_PATH"/knote/knote_main.py'
```

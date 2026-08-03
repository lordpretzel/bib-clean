# bibclean

CLI tool for cleaning BibTeX files: removes unwanted fields and abbreviates conference/journal names.

## Run

```bash
nix develop -c cleanbib -i input.bib              # print to stdout
nix develop -c cleanbib -i input.bib -o out.bib # write to file
nix develop -c cleanbib -i input.bib -O        # overwrite input
nix develop -c cleanbib -s "@article{...}"      # parse string instead of file

# Run tests
nix develop -c pytest tests/ -v
```

## Key files

- `bibclean/bibclean.py` - main source
- Entry point: `cleanbib` (from `pyproject.toml`)

## Code quirks

- The `-p`/`--for-paper` flag is defined but never hooked up - currently does nothing
- Uses `bibtexparser` library (v1.4.3+)
- Conference/journal name abbreviations stored in `name_shortcuts` dict
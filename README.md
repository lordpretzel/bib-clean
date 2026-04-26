# bibclean

Tool for cleaning BibTeX files by removing unwanted fields and abbreviating conference/journal names.

## Features

- Removes unwanted BibTeX fields (urls, DOIs, abstracts, timestamps, etc.)
- Abbreviates conference and journal names (e.g., "International Conference on Very Large Data Bases" → "VLDB")
- Supports both file input and string parsing
- Can overwrite input file in-place

## Installation

This project uses [Nix](https://nixos.org/) with flakes. 

### Option 1: Run directly from GitHub

```bash
nix run github:lordpretzel/bib-clean#bibclean -- -i input.bib -o output.bib
```

The `--` separates nix run arguments from the package arguments.

### Option 2: Local development

Enter the devshell for development:

```bash
nix develop
```

### Option 3: Add as a dependency in another flake

Add this flake as an input in your `flake.nix`:

```nix
{
  inputs.bibclean = {
    url = "github:lordpretzel/bib-clean";
    inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, bibclean, ... }@inputs:
    # Use bibclean.packages.${system}.bibclean
    # Or enter devshell:
    # nix develop . --impure --override-input bibclean github:lordpretzel/bib-clean
    {};
}
```

This gives you a Python environment with all required dependencies.

## Usage

```bash
# Print cleaned bibtex to stdout
cleanbib -i input.bib

# Write to a specific output file
cleanbib -i input.bib -o out.bib

# Overwrite the input file in-place
cleanbib -i input.bib -O

# Parse a bibtex string instead of a file
cleanbib -s "@article{Test2024, author = {John Doe}, title = {Test}}"
```

## Testing

Run the test suite:

```bash
nix develop -c pytest tests/ -v
```

## Project Structure

```
bibclean/
├── bibclean/
│   └── bibclean.py    # Main source code
├── tests/
│   └── test_bibclean.py  # Test cases
├── flake.nix        # Nix flake configuration
├── pyproject.toml  # Python package metadata
└── AGENTS.md       # Agent instructions
```

## Development

Enter the development shell:

```bash
nix develop
```

This provides:
- Python 3.12 with bibtexparser
- pytest for testing
- python-lsp-server for IDE support
- rich-cli for rich output

The flake builds a package called `bibclean` that can be run as:
```bash
nix run .#bibclean -- -i input.bib
```
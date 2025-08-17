{
  description = "bibtex entry cleaner";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
#    mach-nix.url = "github:DavHau/mach-nix";
  };


  outputs = { self, nixpkgs, flake-utils, mach-nix, ... }@inputs:
    flake-utils.lib.eachDefaultSystem
      (system:
        let
          pkgs = import nixpkgs {
            inherit system;
          };


          mypython = pkgs.python312;
          mypackages = pkgs.python312Packages;

          requirements = (with mypackages; [
            bibtexparser
          ]);

          devrequirements =
            requirements
            ++
            (with mypackages; [
              pip
              python-lsp-server
              rich
            ]);

          # the python script to wrap as an app
          script-base-name = "cleanbib";
#          script-name = "${script-base-name}.py";
#          pyscript = "${self}/${script-name}";
          package-version = "1.0";
          package-name = "${script-base-name}-${package-version}";

          mypythonapp = (with mypackages; buildPythonApplication {
            pname = "${script-base-name}";
            version = "${package-version}";

            dontUseSetuptoolsCheck = true;

            pyproject = true;
            build-system = [ setuptools ];

            propagatedBuildInputs = requirements;

            src = ./.;
          });

          mydevpython = mypython.withPackages (ps: devrequirements);

          
#           requirements-txt = "${self}/requirements.txt";
#           requirements-as-text = builtins.readFile requirements-txt;

#           # python environment
#           mypython =
#               mach-nix.lib."${system}".mkPython {
#                 requirements = requirements-as-text;
#               };

#           mydevpython =
#               mach-nix.lib."${system}".mkPython {
#                 requirements = requirements-as-text +  ''
# pip
# python-lsp-server[all]
# rich-cli
# mypy
# '';
#               };

          
#           # Utility to run a script easily in the flakes app
#           simple_script = name: add_deps: text: let
#             exec = pkgs.writeShellApplication {
#               inherit name text;
#               runtimeInputs = with pkgs; [
#                 mypython
#               ] ++ add_deps;
#             };
#           in {
#             type = "app";
#             program = "${exec}/bin/${name}";
#           };


        in with pkgs;
          {
            ###################################################################
            #                       package                                   #
            ###################################################################
            packages = {
              bibclean = mypythonapp;
            };


            ###################################################################
            #                       development shell                         #
            ###################################################################
            devShells.default = mkShell
              {
                buildInputs = [
                  mydevpython
                  rich-cli
                ];
                runtimeInputs = [
                  mydevpython
                  rich-cli
                ];
                shellHook = ''
                  alias pip="${mydevpython}/bin/pip --disable-pip-version-check"
                  rich "[b white on black]Using virtual environment for [/][b white on red] ${package-name} [/][b white on black] with Python[/]

[b]$(python --version)[/]

[b white on black]with packages[/]

$(${mydevpython}/bin/pip list --no-color --disable-pip-version-check)" --print --padding 1 -p -a heavy
                '';
              };
          }
      );
}

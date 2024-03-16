{
  description = "bibtex entry cleaner";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-23.11";
    flake-utils.url = "github:numtide/flake-utils";
    mach-nix.url = "github:DavHau/mach-nix";
  };


  outputs = { self, nixpkgs, flake-utils, mach-nix, ... }@inputs:
    flake-utils.lib.eachDefaultSystem
      (system:
        let
          pkgs = import nixpkgs {
            inherit system;
          };

          requirements-txt = "${self}/requirements.txt";
          requirements-as-text = builtins.readFile requirements-txt;
          
          # python environment
          mypython = 
              mach-nix.lib."${system}".mkPython {
                requirements = builtins.readFile requirements-txt;
              };

          # Utility to run a script easily in the flakes app
          simple_script = name: add_deps: text: let
            exec = pkgs.writeShellApplication {
              inherit name text;
              runtimeInputs = with pkgs; [
                mypython
              ] ++ add_deps;
            };
          in {
            type = "app";
            program = "${exec}/bin/${name}";
          };

          # the python script to wrap as an app
          script-base-name = "cleanbib";
          script-name = "${script-base-name}.py";
          pyscript = "${self}/${script-name}";          
        in with pkgs;
          {
            ###################################################################
            #                       package                                   #
            ###################################################################
            packages = {
              cleanbib = stdenv.mkDerivation {
                name="cleanbib-1.0";
                src = ./.;
                
                runtimeInputs = [ mypython ];
                buildInputs = [ mypython ];
                nativeBuildInputs = [ makeWrapper ];
                installPhase = ''
                  mkdir -p $out/bin/
                  mkdir -p $out/share/
                  cp ${pyscript} $out/share/${script-name}
                  makeWrapper ${mypython}/bin/python $out/bin/${script-base-name} --add-flags "$out/share/${script-name}" 
                '';                
              };
            };
            ###################################################################
            #                       running                                   #
            ###################################################################
            apps = {
              default = simple_script "pyscript" [] ''
                python ${pyscript} "''$@"
              '';
            };

            ###################################################################
            #                       development shell                         #
            ###################################################################
            devShells.default = mkShell
              {
                buildInputs = [
                  pkgs.charasay
                  mypython
                ];
                runtimeInputs = [ mypython ];
                shellHook = ''
                  echo "Using virtual environment with Python ${mypython.python} with packages ${requirements-as-text}" | chara say
                '';
              };
          }
      );
}
  
#   outputs = { self, nixpkgs, flake-utils, mach-nix, ... }@inputs:
#     flake-utils.lib.eachDefaultSystem
#       (system:
#         let
#           pkgs = import nixpkgs {
#             inherit system;
#           };

#           requirements-txt = "${self}/requirements.txt";

#           # Utility to run a script easily in the flakes app
#           simple_script = name: add_deps: text: let
#             exec = pkgs.writeShellApplication {
#               inherit name text;
#               runtimeInputs = with pkgs; [
#                 (mach-nix.lib."${system}".mkPython {
#                   requirements = builtins.readFile requirements-txt;
#                 })
#               ] ++ add_deps;
#             };
#           in {
#             type = "app";
#             program = "${exec}/bin/${name}";
#           };

#           pyscript = "${self}/clean_bib.py";

#         in with pkgs;
#           {
#             ###################################################################
#             #                       running                                   #
#             ###################################################################
#             apps = {
#               default = simple_script "pyscript" [] ''
#                 python ${pyscript} "''$@"
#               '';
#             };

#             ###################################################################
#             #                       development shell                         #
#             ###################################################################
#             devShells.default = mach-nix.lib."${system}".mkPythonShell # mkShell
#               {
#                 # requirementx
#                 requirements = builtins.readFile requirements-txt;
#                 # python version
#                 # nativeBuildInputs = with pkgs; [
#                 #   python38
#                 #   python38Packages.pip
#                 #   poetry
#                 # ];
#               };
#           }
#       );
# }

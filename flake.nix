# flake.nix
{
  description = "Devshell";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
        in 
        {
          devShells.default = pkgs.mkShell {
            buildInputs = with pkgs;[
              python312
              python312Packages.rich
            ];

            shellHook = ''
              echo -e "\e[45m AutoAmpDL dev shell activated \e[0m"
            '';
          };
        }
    );
}

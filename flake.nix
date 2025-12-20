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
          python = pkgs.python312.withPackages (ps: with ps; [
            rich
          ]);
        in 
        {
          devShells.default = pkgs.mkShell {
            buildInputs = with pkgs;[
              python
              yt-dlp
            ];

            shellHook = ''
              echo -e "\e[45m AutoAmpDL dev shell activated \e[0m"
            '';
          };
        }
    );
}

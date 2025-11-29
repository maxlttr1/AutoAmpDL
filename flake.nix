# flake.nix
{
  description = "Devshell";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }: 
    let 
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
    in {
      devShells.${system}.default = pkgs.mkShell {
        buildInputs = with pkgs;[
          python312
          python312Packages.rich
        ];

        shellHook = ''
          echo -e "\e[45m AutoAmpDL dev shell activated \e[0m"
        '';
      };
    };
}

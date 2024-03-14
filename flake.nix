{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-23.11";
  };

  outputs = {nixpkgs, ...} @ inputs: let
    systems = ["x86_64-linux"];
    eachSystem = f:
      nixpkgs.lib.genAttrs systems (system:
        f {
          pkgs = nixpkgs.legacyPackages.${system};
        });
  in {
    devShells = eachSystem ({pkgs}: {
      default = pkgs.mkShell {
        name = "lipotes-backend";
        buildInputs = with pkgs; [
          python311
          pre-commit
        ];

        shellHook = ''
          export LD_LIBRARY_PATH=${pkgs.stdenv.cc.cc.lib}/lib/
        '';
      };
    });
  };
}

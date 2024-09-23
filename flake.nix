{
  description = "System dependencies for wc_plots";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        pythonPackages = pkgs.python311Packages;
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            zlib
            (python311.withPackages (ps: with ps; [
              pandas
              plotly
              numpy
              kaleido
              seaborn
              matplotlib
              # Add any other Python packages you need here
            ]))
          ];

          shellHook = ''
            export LD_LIBRARY_PATH=${pkgs.lib.makeLibraryPath [
              pkgs.zlib
            ]}:$LD_LIBRARY_PATH
          '';
        };
      }
    );
}
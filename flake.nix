{
  inputs.nixpkgs.url = "nixpkgs";
  inputs.flake-utils.url = "github:numtide/flake-utils";
  outputs = {
    self,
    nixpkgs,
    flake-utils,
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = nixpkgs.legacyPackages.${system};
    in {
      packages.default =
        pkgs.python3Packages.buildPythonPackage {
          pname = "wix-extract";
          version = "0.0.1";
          pyproject = true;
          src = ./.;

          buildInputs = [pkgs.python3Packages.setuptools];
          propagatedBuildInputs = [pkgs.cabextract] ++ (with pkgs.python3Packages; [beautifulsoup4 lxml]);
        };
      apps.default = flake-utils.lib.mkApp {drv = self.packages.${system}.default;};
    });
}

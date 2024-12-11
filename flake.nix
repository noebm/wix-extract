{
  inputs.nixpkgs.url = "nixpkgs";
  inputs.pyproject-nix.url = "github:pyproject-nix/pyproject.nix";
  inputs.pyproject-nix.inputs.nixpkgs.follows = "nixpkgs";
  inputs.flake-utils.url = "github:numtide/flake-utils";
  outputs = {
    self,
    nixpkgs,
    pyproject-nix,
    flake-utils,
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = nixpkgs.legacyPackages.${system};
    in {
      packages.default = let
        project = pyproject-nix.lib.project.loadPyproject {
          # Read & unmarshal pyproject.toml relative to this project root.
          # projectRoot is also used to set `src` for renderers such as buildPythonPackage.
          projectRoot = ./.;
        };
        packageAttrs = project.renderers.buildPythonPackage {python = pkgs.python3;};
      in
        pkgs.python3Packages.buildPythonPackage (
          packageAttrs // {dependencies = packageAttrs.dependencies ++ [pkgs.cabextract];}
        );
      apps.default = flake-utils.lib.mkApp {drv = self.packages.${system}.default;};
    });
}

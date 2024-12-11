{
  inputs.nixpkgs.url = "nixpkgs";
  inputs.pyproject-nix.url = "github:pyproject-nix/pyproject.nix";
  inputs.pyproject-nix.inputs.nixpkgs.follows = "nixpkgs";
  outputs = {
    self,
    nixpkgs,
    pyproject-nix,
  }: let
    system = "x86_64-linux";
    pkgs = nixpkgs.legacyPackages.${system};
    nativeDependencies = [pkgs.cabextract];

    package = let
      project = pyproject-nix.lib.project.loadPyproject {
        projectRoot = ./.;
      };
      packageAttrs = project.renderers.buildPythonPackage {python = pkgs.python3;};
    in
      pkgs.python3Packages.buildPythonPackage (
        packageAttrs // {dependencies = packageAttrs.dependencies ++ nativeDependencies;}
      );
  in {
    packages.${system}.default = package;
    apps.${system}.default = {
      type = "app";
      program = "${package}/bin/${package.pname}";
    };
  };
}

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
    python = pkgs.python3;
    project = pyproject-nix.lib.project.loadPyproject {
      projectRoot = ./.;
    };

    package = let
      packageAttrs = project.renderers.buildPythonPackage {inherit python;};
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
    devShells.${system}.default = let
      pythonEnv = python.withPackages (project.renderers.withPackages {inherit python;});
    in
      # Create a devShell like normal.
      pkgs.mkShell {packages = [pythonEnv] ++ nativeDependencies;};
  };
}

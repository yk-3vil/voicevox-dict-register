{
  description = "VOICEVOX ユーザー辞書一括登録ツール";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        python = pkgs.python3.withPackages (ps: [ ps.pyyaml ]);
      in
      {
        packages.default = pkgs.writeShellApplication {
          name = "voicevox-dict-register";
          runtimeInputs = [ python ];
          text = ''
            exec ${python}/bin/python3 ${./main.py} "$@"
          '';
        };

        devShells.default = pkgs.mkShell {
          packages = [ python ];
        };

        apps.default = {
          type = "app";
          program = "${self.packages.${system}.default}/bin/voicevox-dict-register";
        };
      }
    );
}

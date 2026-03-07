{
  description = "Agent Orchestrator Web - Nix toolchain";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
      in {
        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            python312
            python312Packages.pip
            python312Packages.pytest
            python312Packages.black
            python312Packages.ruff
            python312Packages.mypy
            python312Packages.fastapi
            python312Packages.uvicorn
            python312Packages.httpx
            python312Packages.psutil
            python312Packages.playwright
            chromium
            nodejs_22
            jq
            curl
            socat
            git
            gnumake
          ];

          shellHook = ''
            export PYTHONDONTWRITEBYTECODE=1
            export PYTHONUNBUFFERED=1
            export CHROMIUM_PATH="$(command -v chromium || true)"
            if [ -f frontend/package-lock.json ] && [ ! -d frontend/node_modules ]; then
              echo "Bootstrapping frontend deps: npm ci --prefix frontend"
              npm ci --prefix frontend --no-fund --no-audit || true
            fi
            echo "Agent Orchestrator Web dev shell ready (Nix)"
            echo "Commands: make serve | make ui-shot | make test-ui | make verify"
          '';
        };
      });
}

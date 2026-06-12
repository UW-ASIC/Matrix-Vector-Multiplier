{
  description = "MVM – Matrix-Vector Multiplier with Spout2 layout";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    rust-overlay.url = "github:oxalica/rust-overlay";
    flake-utils.url = "github:numtide/flake-utils";
    schemify.url = "git+file:///home/omare/Documents/Projects/Active/Schemify";
  };

  outputs =
    {
      self,
      nixpkgs,
      rust-overlay,
      flake-utils,
      schemify,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        # ── Overlays ──────────────────────────────────────────────────
        # Pin ngspice 43 (44+ breaks binned MOSFET model resolution)
        ngspiceOverlay = import ./nix/ngspice.nix;

        pkgs = import nixpkgs {
          inherit system;
          overlays = [
            (import rust-overlay)
            ngspiceOverlay
          ];
        };

        # ── Packages from local sources ───────────────────────────────
        openvaf = import ./nix/openvaf.nix { inherit pkgs; };
        vacask = import ./nix/vacask.nix { inherit pkgs; openvafPkg = openvaf; };
        xyce = import ./nix/xyce.nix { inherit pkgs; };

        rustToolchain = pkgs.rust-bin.stable.latest.default.override {
          extensions = [ "rust-src" "rust-analyzer" ];
        };

        pythonEnv = pkgs.python312.withPackages (ps: [
          ps.numpy
          ps.pip
        ]);

        schemifyShell = schemify.devShells.${system}.default;
        schemify-bin = pkgs.runCommand "schemify-bin" { } ''
          mkdir -p $out/bin
          ln -s /home/omare/Documents/Projects/Active/Schemify/zig-out/bin/Schemify $out/bin/schemify
        '';
      in
      {
        devShells.default = pkgs.mkShell {
          name = "mvm-dev";

          inputsFrom = [ schemifyShell ];

          buildInputs = [
            # Rust
            rustToolchain
            pkgs.cargo
            pkgs.maturin

            # Python
            pythonEnv

            # C deps
            pkgs.pkg-config
            pkgs.libngspice
            pkgs.ngspice

            # Layout verification
            pkgs.klayout
            pkgs.magic-vlsi
            pkgs.netgen-vlsi

            # Simulation
            xyce

            # Tools
            schemify-bin
            openvaf
            vacask
          ];

          LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
            pkgs.stdenv.cc.cc.lib
            pkgs.libngspice
            pkgs.wayland
            pkgs.libxkbcommon
            pkgs.libffi
          ];

          shellHook = ''
            # Python venv (inherits nix numpy)
            if [ ! -d .venv ]; then
              python3 -m venv .venv --system-site-packages
              .venv/bin/pip install --quiet ciel gdstk
            fi
            source .venv/bin/activate

            # Build pyspice_rs from ../PySpice (into MVM's venv)
            if ! python3 -c "import pyspice_rs" 2>/dev/null; then
              echo "Building pyspice_rs from ../PySpice..."
              (cd ../PySpice && VIRTUAL_ENV="$OLDPWD/.venv" PATH="$OLDPWD/.venv/bin:$PATH" \
                maturin develop --release 2>&1) \
                || echo "Warning: pyspice_rs build failed"
            fi

            # Build spout from ../Spout2 (into MVM's venv)
            if ! python3 -c "import spout" 2>/dev/null; then
              echo "Building spout from ../Spout2..."
              (cd ../Spout2 && VIRTUAL_ENV="$OLDPWD/.venv" PATH="$OLDPWD/.venv/bin:$PATH" \
                maturin develop -m crates/py/Cargo.toml --release 2>&1) \
                || echo "Warning: spout build failed"
            fi

            # ── PDK Setup ────────────────────────────────────────────────
            export PDK_ROOT="''${PDK_ROOT:-$HOME/.ciel}"

            # Ciel PDKs: sky130, gf180mcu, ihp-sg13g2
            if [ ! -d "$PDK_ROOT/sky130A" ]; then
              echo "Fetching sky130 PDK via ciel..."
              python3 -m ciel enable --pdk-family sky130
            fi
            if [ ! -d "$PDK_ROOT/gf180mcuD" ]; then
              echo "Fetching gf180mcu PDK via ciel..."
              python3 -m ciel enable --pdk-family gf180mcu
            fi
            if [ ! -d "$PDK_ROOT/ihp-sg13g2" ]; then
              echo "Fetching ihp-sg13g2 PDK via ciel..."
              python3 -m ciel enable --pdk-family ihp-sg13g2
            fi


            export PDK=sky130A

            echo ""
            echo "MVM Development Environment"
            echo "  PDK_ROOT:  $PDK_ROOT"
            echo "  sky130:    $([ -d $PDK_ROOT/sky130A ] && echo 'ok' || echo 'missing')"
            echo "  gf180mcu:  $([ -d $PDK_ROOT/gf180mcuD ] && echo 'ok' || echo 'missing')"
            echo "  ihp-sg13g2:$([ -d $PDK_ROOT/ihp-sg13g2 ] && echo 'ok' || echo 'missing')"
            echo "  pyspice:   $(python3 -c 'import pyspice_rs; print("ok")' 2>/dev/null || echo 'not built')"
            echo "  spout:     $(python3 -c 'import spout; print("ok")' 2>/dev/null || echo 'not built')"
            echo "  vacask:    $(vacask --version 2>/dev/null || echo 'available')"
            echo "  xyce:      $(xyce -v 2>&1 | head -1 || echo 'available')"
          '';
        };
      }
    );
}

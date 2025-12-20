{
  pkgs ?
    import (builtins.fetchTarball {
      url = "https://github.com/NixOS/nixpkgs/archive/nixos-unstable.tar.gz";
      sha256 = "sha256:1dvhyaddi7d4fkj63hns1xrdqcmyyq24y89k0cdwxs8s3619bx8v";
    }) {
      overlays = [
        (import (builtins.fetchTarball "https://github.com/oxalica/rust-overlay/archive/master.tar.gz"))
      ];
    },
}: let
  selfBuiltPackages = {
    ngspice-shared = pkgs.ngspice.override {
      withNgshared = true;
    };

    netgen = pkgs.stdenv.mkDerivation rec {
      name = "netgen";
      version = "1.5.305";
      src = pkgs.fetchurl {
        url = "http://opencircuitdesign.com/netgen/archive/netgen-${version}.tgz";
        sha256 = "sha256-U9m/pIydfRSlsEWhLDDFsC8+C0Fn3DgYQrwVDETn4Zg=";
      };
      nativeBuildInputs = [pkgs.python312];
      buildInputs = with pkgs; [
        tcl
        tk
        xorg.libX11
      ];
      enableParallelBuilding = true;
      configureFlags = [
        "--with-tcl=${pkgs.tcl}"
        "--with-tk=${pkgs.tk}"
      ];
      NIX_CFLAGS_COMPILE = "-O2";
      postPatch = ''
        find . -name "*.sh" -exec patchShebangs {} \; || true
      '';
      meta = with pkgs.lib; {
        description = "LVS netlist comparison tool";
        homepage = "http://opencircuitdesign.com/netgen/";
        license = licenses.mit;
        maintainers = with maintainers; [thoughtpolice];
      };
    };

    xschem = pkgs.stdenv.mkDerivation rec {
      name = "xschem";
      version = "3.4.7";
      src = pkgs.fetchFromGitHub {
        owner = "StefanSchippers";
        repo = "xschem";
        rev = "3.4.7";
        sha256 = "sha256-ye97VJQ+2F2UbFLmGrZ8xSK9xFeF+Yies6fJKurPOD0=";
      };

      nativeBuildInputs =
        [
          pkgs.bison
          pkgs.flex
          pkgs.pkg-config
        ]
        ++ pkgs.lib.optionals pkgs.stdenv.hostPlatform.isDarwin [
          pkgs.fixDarwinDylibNames
        ];
      buildInputs = with pkgs; [
        tcl
        tk
        xorg.libX11
        xorg.libXpm
        cairo
        readline
        flex
        bison
        zlib
      ];
      enableParallelBuilding = true;
      NIX_CFLAGS_COMPILE = "-O2";
      hardeningDisable = ["format"];
      meta = with pkgs.lib; {
        description = "Schematic capture and netlisting EDA tool";
        homepage = "https://xschem.sourceforge.io/stefan/";
        license = licenses.gpl2Plus;
        maintainers = with maintainers; [fbeffa];
      };
    };

    # Wrap KLayout with Python packages it needs
    klayout-with-python = pkgs.symlinkJoin {
      name = "klayout-with-python";
      paths = [pkgs.klayout];
      buildInputs = [pkgs.makeWrapper];
      postBuild = ''
        wrapProgram $out/bin/klayout \
          --set KLAYOUT_PYTHONPATH "${pkgs.python312.pkgs.makePythonPath [
          pkgs.python312Packages.pandas
          pkgs.python312Packages.numpy
          pkgs.python312Packages.matplotlib
        ]}"
      '';
    };
  };
  pythonRequirements = ''
    volare==0.20.6
    openlane==2.3.10
    maturin
  '';
  pythonDepsInstaller = pkgs.writeShellScriptBin "install-python-deps" ''
        VENV_DIR="''${PROJECT_ROOT:-.}/.venv"
        MARKER="$VENV_DIR/.deps_installed"
        REQUIREMENTS=$(cat <<EOF
    ${pythonRequirements}
    EOF
    )
        if [ ! -f "$MARKER" ] || [ -n "$(find "$MARKER" -mtime +1 2>/dev/null)" ]; then
          {
            pip install --upgrade pip setuptools wheel
            echo "$REQUIREMENTS" | pip install -r /dev/stdin

            # Install editable packages if they exist
            for pkg in analog/library/dep_library/{gmid,UWASIC-ALG}; do
              [ -d "$PROJECT_ROOT/$pkg" ] && pip install -e "$PROJECT_ROOT/$pkg"
            done

            touch "$MARKER"
          } >/dev/null 2>&1 || echo "ERROR: Python install failed" >&2
        fi
  '';
in
  pkgs.mkShell {
    name = "eda-environment";
    buildInputs = with pkgs; [
      # Build Tools
      (rust-bin.nightly.latest.default.override {
        extensions = ["rust-src" "rust-analyzer"];
      })
      gnumake
      git
      ccache

      # C/C++ Toolchain
      gcc
      clang
      llvmPackages.libclang

      # C Libraries
      libffi.dev
      fftw
      expat
      swig
      zlib
      stdenv.cc.cc.lib

      # Python Environment
      python312
      python312Packages.pip
      python312Packages.numpy
      python312Packages.setuptools
      python312Packages.wheel
      python312Packages.cocotb
      python312Packages.tkinter
      python312Packages.pyyaml
      python312Packages.rich
      python312Packages.click
      python312Packages.pytest

      # Digital Design Tools
      iverilog
      slang
      verilator
      yosys
      gtkwave

      # Analog Design Tools
      selfBuiltPackages.xschem
      selfBuiltPackages.ngspice-shared
      selfBuiltPackages.netgen
      selfBuiltPackages.klayout-with-python
      ngspice
      magic-vlsi

      # OpenLane Dependencies
      tcl
      tk
      tclPackages.tcllib
      ruby
      openroad

      # Graphics & GUI Support
      xorg.libX11
      xorg.libXpm
      xorg.libXt
      xorg.fontutil
      xorg.fontmiscmisc
      xorg.fontcursormisc
      cairo
      xterm
      dejavu_fonts
      liberation_ttf

      # Custom installer script
      pythonDepsInstaller
    ];

    env = {
      NIX_ENFORCE_PURITY = "0";

      # C/C++ Compilation
      CC = "ccache gcc";
      CXX = "ccache g++";

      # Library paths
      LD_LIBRARY_PATH = "${pkgs.stdenv.cc.cc.lib}/lib:${pkgs.gcc.cc.lib}/lib:${pkgs.expat}/lib:${pkgs.zlib}/lib";
      NIX_LD_LIBRARY_PATH = "${pkgs.python312}/lib:${selfBuiltPackages.ngspice-shared}/lib:${pkgs.stdenv.cc.cc.lib}/lib:${pkgs.expat}/lib:${pkgs.zlib}/lib";

      # Rust-Python Build Configuration
      LIBCLANG_PATH = "${pkgs.llvmPackages.libclang.lib}/lib";
      BINDGEN_EXTRA_CLANG_ARGS = "-I${pkgs.glibc.dev}/include -I${selfBuiltPackages.ngspice-shared}/include";
      CPATH = "${pkgs.python312}/include/python3.12:${selfBuiltPackages.ngspice-shared}/include";
      PKG_CONFIG_PATH = "${selfBuiltPackages.ngspice-shared}/lib/pkgconfig";

      # PDK Configuration
      PDK = "sky130A";
      PDK_VERSION = "6d4d11780c40b20ee63cc98e645307a9bf2b2ab8";
    };

    shellHook = ''
      # === IMPORTANT EXPORTS ===
      export PROJECT_ROOT="$(pwd)"
      # Dynamic paths that depend on PROJECT_ROOT
      export CCACHE_DIR="$PROJECT_ROOT/.tools/ccache"
      export PDK_ROOT="$HOME/.volare"
      # EDA Tools Configuration
      export XSCHEM_USER_LIBRARY_PATH="$PDK_ROOT/$PDK/libs.tech/xschem"
      export XSCHEM_LIBRARY_PATH="$PDK_ROOT/$PDK/libs.tech/xschem:${selfBuiltPackages.xschem}/share/xschem/xschem_library"

      # === Python Virtual Environment Setup ===
      export VENV_DIR="$PROJECT_ROOT/.venv"
      if [ -z "$VIRTUAL_ENV" ] || [ "$VIRTUAL_ENV" != "$VENV_DIR" ]; then
          if [ ! -d "$VENV_DIR" ]; then
              echo "Creating Python virtual environment..."
              python3 -m venv "$VENV_DIR"
          fi
          source "$VENV_DIR/bin/activate"
      fi
      install-python-deps

      # === PDK SETUP WITH VOLARE ===
      volare enable --pdk sky130 "$PDK_VERSION" >/dev/null 2>&1 || true
      volare prune -y >/dev/null 2>&1 || true

      echo "=== EDA Environment Entered ==="
      echo ""
      echo "System tools available:"
      echo "  - Python: $(python --version)"
      echo "  - xschem: $(xschem --version 2>/dev/null || echo 'custom build')"
      echo "  - yosys: $(yosys -V 2>/dev/null | head -1 || echo 'unknown version')"
      echo "  - verilator: $(verilator --version 2>/dev/null | head -1 || echo 'unknown version')"
      echo "  - magic: $(magic -version 2>/dev/null | head -1 || echo 'unknown version')"
      echo "  - PDK: $PDK in $PDK_ROOT"
    '';
  }

{pkgs ? import <nixpkgs> {}}: let
  selfBuiltPackages = {
    ngspice-shared = pkgs.ngspice.override {
      withNgshared = true;
    };

    xschem = pkgs.stdenv.mkDerivation rec {
      pname = "xschem";
      version = "3.4.7";

      src = pkgs.fetchFromGitHub {
        owner = "StefanSchippers";
        repo = "xschem";
        rev = "3.4.7";
        sha256 = "sha256-1jP1SJeq23XNkOQgcl2X+rBrlka4a04irmfhoKRM1j4=";
      };

      nativeBuildInputs = with pkgs; [
        pkg-config
        autoconf
        automake
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

      # CRITICAL: scconfig needs CFLAGS/LDFLAGS in environment during configure
      preConfigure = pkgs.lib.optionalString pkgs.stdenv.isDarwin ''
        # XQuartz must be installed at /opt/X11
        if [ ! -d "/opt/X11" ]; then
          echo "ERROR: XQuartz not found at /opt/X11"
          echo "Please install XQuartz from https://www.xquartz.org/"
          exit 1
        fi

        # Export flags that scconfig will pick up during its detection
        # These MUST be set before configure runs
        export CFLAGS="-I/opt/X11/include -I${pkgs.tcl}/include -I${pkgs.tk}/include"
        export CPPFLAGS="-I/opt/X11/include"
        export LDFLAGS="-L/opt/X11/lib -L${pkgs.tcl}/lib -L${pkgs.tk}/lib"
        export LIBS="-lX11"

        # Also set these for good measure
        export CC="${pkgs.stdenv.cc}/bin/clang"

        echo "=== Environment for scconfig ==="
        echo "CFLAGS=$CFLAGS"
        echo "LDFLAGS=$LDFLAGS"
        echo "LIBS=$LIBS"
        echo "CC=$CC"
        echo "==============================="
      '';

      # Run configure - scconfig will use the environment variables above
      configureScript = "./configure";

      configureFlags = [
        "--prefix=${placeholder "out"}"
      ];

      # After configure, patch Makefile.conf as per official instructions
      postConfigure = pkgs.lib.optionalString pkgs.stdenv.isDarwin ''
        echo "=== Patching Makefile.conf for macOS ==="

        if [ ! -f Makefile.conf ]; then
          echo "ERROR: Makefile.conf not found!"
          ls -la
          exit 1
        fi

        # Show what configure generated
        echo "Original Makefile.conf CFLAGS and LDFLAGS:"
        grep "^CFLAGS" Makefile.conf || echo "No CFLAGS found"
        grep "^LDFLAGS" Makefile.conf || echo "No LDFLAGS found"

        # Backup original
        cp Makefile.conf Makefile.conf.orig

        # Create patched version with proper X11 paths
        {
          echo "# Patched for macOS with XQuartz"
          echo "CFLAGS=-I/opt/X11/include -I/opt/X11/include/cairo \\"
          echo "       -I${pkgs.tcl}/include -I${pkgs.tk}/include \\"
          echo "       -I${pkgs.cairo}/include/cairo -O2"
          echo ""
          echo "LDFLAGS=-L/opt/X11/lib -L${pkgs.tcl}/lib -L${pkgs.tk}/lib \\"
          echo "        -lm -lcairo -lX11 -lXrender -lxcb -lxcb-render \\"
          echo "        -lX11-xcb -lXpm -ltcl8.6 -ltk8.6"
          echo ""
          # Append everything else from original except CFLAGS/LDFLAGS
          grep -v "^CFLAGS" Makefile.conf.orig | grep -v "^LDFLAGS"
        } > Makefile.conf

        echo "Patched Makefile.conf:"
        head -20 Makefile.conf
      '';

      enableParallelBuilding = true;

      buildPhase = ''
        make
      '';

      installPhase = ''
        make install
      '';

      postInstall = pkgs.lib.optionalString pkgs.stdenv.isDarwin ''
        if [ -f "$out/bin/xschem" ]; then
          echo "Fixing dynamic library paths..."

          install_name_tool -change \
            /usr/local/opt/tcl-tk/lib/libtcl8.6.dylib \
            ${pkgs.tcl}/lib/libtcl8.6.dylib \
            "$out/bin/xschem" 2>/dev/null || true

          install_name_tool -change \
            /usr/local/opt/tcl-tk/lib/libtk8.6.dylib \
            ${pkgs.tk}/lib/libtk8.6.dylib \
            "$out/bin/xschem" 2>/dev/null || true

          install_name_tool -add_rpath /opt/X11/lib "$out/bin/xschem" 2>/dev/null || true
          install_name_tool -add_rpath ${pkgs.tcl}/lib "$out/bin/xschem" 2>/dev/null || true
          install_name_tool -add_rpath ${pkgs.tk}/lib "$out/bin/xschem" 2>/dev/null || true
        fi
      '';

      shellHook = pkgs.lib.optionalString pkgs.stdenv.isDarwin ''
        export DYLD_LIBRARY_PATH="/opt/X11/lib:${pkgs.tcl}/lib:${pkgs.tk}/lib:$DYLD_LIBRARY_PATH"
        export DISPLAY=":0"

        if ! pgrep -x "Xquartz" > /dev/null; then
          echo "WARNING: XQuartz is not running. Start it with: open -a XQuartz"
        fi
      '';

      meta = with pkgs.lib; {
        description = "Schematic capture and netlisting EDA tool";
        homepage = "https://xschem.sourceforge.io/";
        platforms = platforms.unix;
        broken = pkgs.stdenv.isDarwin && !builtins.pathExists "/opt/X11";
      };
    };

    magic-vlsi = pkgs.stdenv.mkDerivation rec {
      pname = "magic-vlsi";
      version = "8.3.569";

      src = pkgs.fetchurl {
        url = "http://opencircuitdesign.com/magic/archive/magic-${version}.tgz";
        sha256 = "sha256-Lk9D2G6F98vQ1iXAiVkjr3s+U3Li5P05cUO1388qTN8=";
      };

      nativeBuildInputs = with pkgs; [
        python311
        pkg-config
      ];

      buildInputs = with pkgs; [
        (
          if stdenv.isDarwin
          then cairo.override {x11Support = true;}
          else cairo
        )
        xorg.libX11
        xorg.libXext
        xorg.libXi
        m4
        mesa_glu
        ncurses
        tcl
        tcsh
        tk
        git
      ];

      preConfigure = pkgs.lib.optionalString pkgs.stdenv.isDarwin ''
        if [ ! -d "/opt/X11" ]; then
          echo "ERROR: XQuartz not found at /opt/X11"
          echo "Please install XQuartz from https://www.xquartz.org/"
          exit 1
        fi

        export CPPFLAGS="-I/opt/X11/include $CPPFLAGS"
        export LDFLAGS="-L/opt/X11/lib $LDFLAGS"
        export PKG_CONFIG_PATH="/opt/X11/lib/pkgconfig:$PKG_CONFIG_PATH"
        export CFLAGS="-Wno-error=implicit-function-declaration -I/opt/X11/include -I${pkgs.cairo}/include/cairo -O2"

        export CAIRO_CFLAGS="$(pkg-config --cflags cairo) -I/opt/X11/include"
        export CAIRO_LIBS="$(pkg-config --libs cairo) -L/opt/X11/lib -lX11"
      '';

      # Magic's configure does NOT support --with-x, --x-includes, or --x-libraries
      # It auto-detects X11 using AC_PATH_X and AC_PATH_XTRA
      configureFlags = [
        "--with-tcl=${pkgs.tcl}/lib"
        "--with-tk=${pkgs.tk}/lib"
        "--disable-werror"
      ];

      postPatch = ''
        patchShebangs scripts/*
      '';

      NIX_CFLAGS_COMPILE =
        if pkgs.stdenv.isDarwin
        then "-Wno-implicit-function-declaration -O2 -I/opt/X11/include"
        else "-Wno-implicit-function-declaration -O2";

      NIX_LDFLAGS =
        pkgs.lib.optionalString pkgs.stdenv.isDarwin
        "-L/opt/X11/lib -lX11 -lXext";

      enableParallelBuilding = true;

      postInstall = pkgs.lib.optionalString pkgs.stdenv.isDarwin ''
        if [ -f "$out/lib/magic/tcl/tclmagic.dylib" ]; then
          echo "Fixing library paths for tclmagic.dylib"

          install_name_tool -change \
            /usr/local/opt2/tcl-tk/lib/libtcl8.6.dylib \
            ${pkgs.tcl}/lib/libtcl8.6.dylib \
            "$out/lib/magic/tcl/tclmagic.dylib" || true

          install_name_tool -change \
            /usr/local/opt2/tcl-tk/lib/libtk8.6.dylib \
            ${pkgs.tk}/lib/libtk8.6.dylib \
            "$out/lib/magic/tcl/tclmagic.dylib" || true

          install_name_tool -change \
            libX11.6.dylib \
            /opt/X11/lib/libX11.6.dylib \
            "$out/lib/magic/tcl/tclmagic.dylib" || true
        fi

        if [ -f "$out/bin/magic" ]; then
          for binary in "$out/bin"/*; do
            if [ -f "$binary" ] && file "$binary" | grep -q "Mach-O"; then
              install_name_tool -add_rpath /opt/X11/lib "$binary" || true
              install_name_tool -add_rpath ${pkgs.tcl}/lib "$binary" || true
              install_name_tool -add_rpath ${pkgs.tk}/lib "$binary" || true
            fi
          done
        fi
      '';

      shellHook = pkgs.lib.optionalString pkgs.stdenv.isDarwin ''
        export DYLD_LIBRARY_PATH="/opt/X11/lib:${pkgs.tcl}/lib:${pkgs.tk}/lib:${pkgs.cairo}/lib:$DYLD_LIBRARY_PATH"
        export DISPLAY=":0"

        if ! pgrep -x "Xquartz" > /dev/null; then
          echo "WARNING: XQuartz is not running."
          echo "Start it with: open -a XQuartz"
          echo "Then run: export DISPLAY=:0"
        fi
      '';

      meta = with pkgs.lib; {
        description = "VLSI layout tool written in Tcl";
        homepage = "http://opencircuitdesign.com/magic/";
        license = licenses.mit;
        maintainers = with maintainers; [thoughtpolice];
        platforms = platforms.unix;
        broken = pkgs.stdenv.isDarwin && !builtins.pathExists "/opt/X11";
      };
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

    openroad-notest = pkgs.openroad.overrideAttrs (oldAttrs: {
      doCheck = false;
      doInstallCheck = false;
    });
  };
in
  pkgs.mkShell {
    name = "eda-environment-v1.0";
    buildInputs = with pkgs; [
      # Builds
      rustup
      cargo
      gnumake
      git
      ccache
      pkg-config

      # Digital design
      slang
      verilator
      yosys
      gtkwave
      python312
      python312Packages.pip
      python312Packages.numpy
      python312Packages.setuptools
      python312Packages.wheel

      # OpenRoad + dep
      # selfBuiltPackages.openroad-notest
      ruby
      stdenv.cc.cc.lib
      expat
      zlib

      # Analog Design
      selfBuiltPackages.xschem
      selfBuiltPackages.ngspice-shared
      ngspice
      selfBuiltPackages.netgen
      klayout
      selfBuiltPackages.magic-vlsi
      vim

      # Graphics/GUI support
      xorg.libX11
      xorg.libXpm
      xorg.libXt
      cairo
      xterm
      xorg.fontutil
      xorg.fontmiscmisc
      xorg.fontcursormisc
      dejavu_fonts
      liberation_ttf
      inkscape
    ];

    shellHook = ''
      export PROJECT_ROOT="$(pwd)"
      export TOOLS_DIR="$PROJECT_ROOT/.tools"
      mkdir -p "$TOOLS_DIR/bin"
      export PATH="$TOOLS_DIR/bin:$PATH"
      export CCACHE_DIR="$TOOLS_DIR/ccache"
      export CC="ccache gcc"
      export CXX="ccache g++"

      # Set up Rust nightly
      export RUSTUP_HOME="$HOME/.rustup"
      export CARGO_HOME="$HOME/.cargo"
      export PATH="$CARGO_HOME/bin:$PATH"

      # Python and C compilation paths
      export CPATH="${pkgs.python312}/include/python3.12:${selfBuiltPackages.ngspice-shared}/include:$CPATH"
      export NIX_LD_LIBRARY_PATH="${pkgs.python312}/lib:${selfBuiltPackages.ngspice-shared}/lib:$NIX_LD_LIBRARY_PATH"
      export PKG_CONFIG_PATH="${selfBuiltPackages.ngspice-shared}/lib/pkgconfig:$PKG_CONFIG_PATH"

      export NIX_LD=$(cat ${pkgs.stdenv.cc}/nix-support/dynamic-linker)
      export NIX_LD_LIBRARY_PATH=${pkgs.lib.makeLibraryPath [
        pkgs.stdenv.cc.cc.lib
        pkgs.expat
        pkgs.zlib
      ]}
      export FONTCONFIG_FILE=${pkgs.fontconfig.out}/etc/fonts/fonts.conf
      export FONTCONFIG_PATH=${pkgs.fontconfig.out}/etc/fonts

      # PDK setup
      export PDK_ROOT="$HOME/.volare"
      export PDK_VERSION="fa87f8f4bbcc7255b6f0c0fb506960f531ae2392"
      export PDK="sky130A"
      export KLAYOUT_PATH="$PDK_ROOT/$PDK/libs.tech/klayout"
      export XSCHEM_USER_LIBRARY_PATH="$PDK_ROOT/$PDK/libs.tech/xschem"
      export XSCHEM_LIBRARY_PATH="$PDK_ROOT/$PDK/libs.tech/xschem:${selfBuiltPackages.xschem}/share/xschem/xschem_library"

      # Install Rust nightly if not already installed
      if ! rustc --version &>/dev/null; then
        echo "Installing Rust nightly toolchain..."
        rustup install nightly
        rustup default nightly
      fi

      # Setup Python virtual environment with Python 3.12
      export VENV_DIR="$PROJECT_ROOT/.venv"

      # Check if venv exists and is valid
      VENV_VALID=false
      if [ -d "$VENV_DIR" ] && [ -f "$VENV_DIR/bin/python3" ]; then
          # Check if the python3 in venv is actually executable
          if "$VENV_DIR/bin/python3" --version >/dev/null 2>&1; then
              VENV_VALID=true
          fi
      fi

      # Recreate venv if invalid or doesn't exist
      if [ "$VENV_VALID" = false ]; then
          if [ -d "$VENV_DIR" ]; then
              echo "Existing venv is broken, removing..."
              rm -rf "$VENV_DIR"
          fi
          echo "Creating Python virtual environment..."
          python3 -m venv "$VENV_DIR"
      fi

      # Only proceed if not already in the correct venv
      if [ -z "$VIRTUAL_ENV" ] || [ "$VIRTUAL_ENV" != "$VENV_DIR" ]; then
          # Activate the virtual environment
          echo "Activating virtual environment..."
          source "$VENV_DIR/bin/activate"
      fi

      # Now install packages
      if [ -n "$VIRTUAL_ENV" ]; then
          echo "Installing Python packages from requirements.txt..."
          python -m pip install --upgrade pip setuptools wheel maturin
          python -m pip install -r "$PROJECT_ROOT/requirements.txt"
      fi

      # Clean up old PDK versions (keep only the current one)
      if [ -d "$PDK_ROOT/volare/sky130/versions" ]; then
          echo "Cleaning up old PDK versions (keeping $PDK_VERSION)..."
          cd "$PDK_ROOT/volare/sky130/versions"
          for version_dir in */; do
              version=$(basename "$version_dir")
              if [ "$version" != "$PDK_VERSION" ]; then
                  echo "  Removing old version: $version"
                  rm -rf "$version"
                  rm -rf ~/.volare
              fi
          done
          cd "$PROJECT_ROOT"
      fi

      volare enable --pdk sky130 "$PDK_VERSION"

      echo "=== EDA Environment v1.0 ==="
      echo ""
      echo "System tools available:"
      echo "  - Python: $(python --version)"
      echo "  - xschem: $(xschem --version 2>/dev/null || echo 'custom build')"
      echo "  - yosys: $(yosys -V 2>/dev/null | head -1 || echo 'unknown version')"
      echo "  - verilator: $(verilator --version 2>/dev/null | head -1 || echo 'unknown version')"
      echo "  - magic: $(magic --version 2>/dev/null || echo 'custom build ${selfBuiltPackages.magic-vlsi.version}')"
      echo "  - PDK: $PDK in $PDK_ROOT"
    '';
  }

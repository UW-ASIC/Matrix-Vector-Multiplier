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

      # Patch scconfig to include X11 paths for macOS
      postPatch = pkgs.lib.optionalString pkgs.stdenv.isDarwin ''
        # Check if XQuartz is installed
        if [ ! -d "/opt/X11" ]; then
          echo "ERROR: XQuartz not found at /opt/X11"
          echo "Please install XQuartz from https://www.xquartz.org/"
          exit 1
        fi

        echo "=== Patching scconfig for macOS X11 detection ==="

        # Find and patch the X11 detection in scconfig
        # scconfig uses hooks.c or a similar file for detection
        if [ -f "scconfig/hooks.c" ]; then
          echo "Found scconfig/hooks.c"
        fi

        # Look for the gui detection files
        if [ -f "scconfig/src/gui/find_x.c" ]; then
          echo "Patching scconfig/src/gui/find_x.c for macOS"

          # Add XQuartz paths to the X11 detection
          sed -i'.bak' 's|/usr/X11R6/include|/opt/X11/include|g' scconfig/src/gui/find_x.c || true
          sed -i'.bak' 's|/usr/X11R6/lib|/opt/X11/lib|g' scconfig/src/gui/find_x.c || true
        fi

        # Find any other X11 detection files
        find scconfig -name "*.c" -type f -exec grep -l "XOpenDisplay\|X11/Xlib" {} \; | while read file; do
          echo "Found X11 reference in: $file"
        done
      '';

      preConfigure = pkgs.lib.optionalString pkgs.stdenv.isDarwin ''
          echo "=== Debugging X11 detection ==="

          # 1. Check if XQuartz is actually installed
          echo "Checking XQuartz installation:"
          if [ -d "/opt/X11" ]; then
            echo "✓ /opt/X11 exists"
            ls -la /opt/X11/include/X11/Xlib.h 2>/dev/null && echo "✓ Xlib.h found" || echo "✗ Xlib.h missing"
            ls -la /opt/X11/lib/libX11.dylib 2>/dev/null && echo "✓ libX11.dylib found" || echo "✗ libX11.dylib missing"
          else
            echo "✗ /opt/X11 not found - XQuartz not installed or wrong path"
            exit 1
          fi

          # 2. Test header inclusion separately
          echo "=== Testing header inclusion ==="
          cat > /tmp/test_include.c << 'EOF'
        #include <X11/Xlib.h>
        #ifdef Success
        int main() { return 0; }
        #else
        #error "X11/Xlib.h not properly included"
        #endif
        EOF

          if clang -I/opt/X11/include -E /tmp/test_include.c > /dev/null 2>&1; then
            echo "✓ X11 headers can be included"
          else
            echo "✗ X11 headers cannot be included"
            echo "Trying verbose:"
            clang -I/opt/X11/include -E /tmp/test_include.c
            exit 1
          fi

          # 3. Test the actual compilation with the CORRECT path
          echo "=== Testing X11 compilation with /opt/X11 ==="
          cat > /tmp/test_x11.c << 'EOF'
        #include <X11/Xlib.h>
        int main() {
            Display *d = XOpenDisplay(NULL);
            if (d) XCloseDisplay(d);
            return 0;
        }
        EOF

          if clang -I/opt/X11/include -L/opt/X11/lib -lX11 /tmp/test_x11.c -o /tmp/test_x11 2>/dev/null; then
            echo "✓ SUCCESS: X11 test program compiles with /opt/X11"
            /tmp/test_x11 && echo "✓ SUCCESS: X11 test program runs" || echo "⚠ WARNING: X11 test program compiled but failed to run (normal if no X server)"
            rm -f /tmp/test_x11.c /tmp/test_x11
          else
            echo "✗ FAILED: X11 test program compilation failed with /opt/X11"
            echo "Trying with verbose output:"
            clang -I/opt/X11/include -L/opt/X11/lib -lX11 /tmp/test_x11.c -o /tmp/test_x11
            rm -f /tmp/test_x11.c /tmp/test_x11
            exit 1
          fi

          # 4. Remove the problematic find command that detects wrong paths
          echo "=== Using only /opt/X11 for X11 ==="
      '';

      configureScript = "./configure";

      configureFlags = [
        "--prefix=${placeholder "out"}"
      ];

      # Patch Makefile.conf after configure
      postConfigure = pkgs.lib.optionalString pkgs.stdenv.isDarwin ''
            echo "=== Patching Makefile.conf for macOS ==="

            if [ ! -f Makefile.conf ]; then
              echo "ERROR: Makefile.conf not found!"
              ls -la
              exit 1
            fi

            cp Makefile.conf Makefile.conf.orig

            cat > Makefile.conf << 'EOF'
        # Patched for macOS with XQuartz
        CFLAGS=-I/opt/X11/include -I/opt/X11/include/cairo \
               -I${pkgs.tcl}/include -I${pkgs.tk}/include \
               -I${pkgs.cairo}/include/cairo -O2

        LDFLAGS=-L/opt/X11/lib -L${pkgs.tcl}/lib -L${pkgs.tk}/lib \
                -lm -lcairo -lX11 -lXrender -lxcb -lxcb-render \
                -lX11-xcb -lXpm -ltcl8.6 -ltk8.6
        EOF

            # Append non-CFLAGS/LDFLAGS lines from original
            grep -v "^CFLAGS" Makefile.conf.orig | grep -v "^LDFLAGS" >> Makefile.conf

            echo "Patched Makefile.conf created"
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

{pkgs ? import <nixpkgs> {}}: let
  # Detect the current system
  system = pkgs.stdenv.hostPlatform.system;
  isDarwin = pkgs.stdenv.isDarwin;
  isLinux = pkgs.stdenv.isLinux;
  
  # Platform-specific package selection
  platformPkgs = if isDarwin then pkgs else pkgs;
  
  xschem = platformPkgs.stdenv.mkDerivation rec {
    pname = "xschem";
    version = "3.4.6";
    src = platformPkgs.fetchFromGitHub {
      owner = "StefanSchippers";
      repo = "xschem";
      rev = "3.4.6";
      sha256 = "sha256-1jP1SJeq23XNkOQgcl2X+rBrlka4a04irmfhoKRM1j4=";
    };
    nativeBuildInputs = with platformPkgs; [
      pkg-config
      autoconf
      automake
    ];
    buildInputs = with platformPkgs; [
      tcl
      tk
      cairo
      readline
      flex
      bison
      zlib
    ] ++ (if isLinux then [
      xorg.libX11
      xorg.libXpm
    ] else []);
    
    configureFlags = [
      "--prefix=${placeholder "out"}"
    ] ++ (if isDarwin then [
      "--enable-cairo"
      "--disable-x11"
    ] else []);
    
    enableParallelBuilding = true;

    buildPhase = ''
      make
    '';
    installPhase = ''
      make install
    '';
    meta = {
      description = "Schematic capture and netlisting EDA tool";
      homepage = "https://xschem.sourceforge.io/";
      platforms = platformPkgs.lib.platforms.unix;
    };
  };

  magic-vlsi-old = platformPkgs.stdenv.mkDerivation rec {
    pname = "magic-vlsi";
    version = "8.3.466";
    src = platformPkgs.fetchurl {
      url = "http://opencircuitdesign.com/magic/archive/magic-${version}.tgz";
      sha256 = "sha256-HbkWS2cp1lz2UnAlbYbqYY7/7XrbUuq9axXrs8zt5FY=";
    };
    nativeBuildInputs = [platformPkgs.python311];
    buildInputs = with platformPkgs; [
      cairo
      m4
      ncurses
      tcl
      tcsh
      tk
      git
    ] ++ (if isLinux then [
      xorg.libX11
      mesa_glu
    ] else if isDarwin then [
      darwin.apple_sdk.frameworks.Cocoa
      darwin.apple_sdk.frameworks.OpenGL
    ] else []);
    
    enableParallelBuilding = true;
    configureFlags = [
      "--with-tcl=${platformPkgs.tcl}"
      "--with-tk=${platformPkgs.tk}"
      "--disable-werror"
    ] ++ (if isDarwin then [
      "--without-x"
      "--enable-cairo"
    ] else []);
    
    postPatch = ''
      patchShebangs scripts/*
    '';
    NIX_CFLAGS_COMPILE = "-Wno-implicit-function-declaration -O2";
    meta = with platformPkgs.lib; {
      description = "VLSI layout tool written in Tcl";
      homepage = "http://opencircuitdesign.com/magic/";
      license = licenses.mit;
      maintainers = with maintainers; [thoughtpolice];
    };
  };

  netgen-old = platformPkgs.stdenv.mkDerivation rec {
    name = "netgen";
    version = "1.5.295";
    src = platformPkgs.fetchurl {
      url = "http://opencircuitdesign.com/netgen/archive/netgen-${version}.tgz";
      sha256 = "sha256-y2UBf564WefrDbIxSrFbNc1FxQfDdYzRORrJjRdkKrg=";
    };
    nativeBuildInputs = [platformPkgs.python312];
    buildInputs = with platformPkgs; [
      tcl
      tk
    ] ++ (if isLinux then [
      xorg.libX11
    ] else []);
    
    enableParallelBuilding = true;
    configureFlags = [
      "--with-tcl=${platformPkgs.tcl}"
      "--with-tk=${platformPkgs.tk}"
    ] ++ (if isDarwin then [
      "--without-x"
    ] else []);
    
    NIX_CFLAGS_COMPILE = "-O2";
    postPatch = ''
      find . -name "*.sh" -exec patchShebangs {} \; || true
    '';
    meta = with platformPkgs.lib; {
      description = "LVS netlist comparison tool";
      homepage = "http://opencircuitdesign.com/netgen/";
      license = licenses.mit;
      maintainers = with maintainers; [thoughtpolice];
    };
  };
  
  # Common packages for all platforms
  commonPackages = with platformPkgs; [
    # Builds
    gnumake
    git
    python312
    ccache

    # Digital design
    verilog
    verilator
    yosys
    gtkwave
    
    # Pytest and Cocotb setup
    python312Packages.pytest
    python312Packages.cocotb
    python312Packages.pip

    # OpenRoad + dep
    openroad
    ruby
    stdenv.cc.cc.lib
    expat
    zlib
    python312Packages.rich
    python312Packages.click
    python312Packages.tkinter
    python312Packages.pyyaml

    # Analog Design
    xschem
    ngspice
    klayout
    magic-vlsi-old
    netgen-old
    vim
    
    # For Data (python)
    python312Packages.numpy
    python312Packages.matplotlib
    python312Packages.scipy

    # Graphics/GUI support
    cairo
    dejavu_fonts
    liberation_ttf
  ];
  
  # Linux-specific packages
  linuxPackages = with platformPkgs; [
    slang
    gaw
    xyce
    xorg.libX11
    xorg.libXpm
    xorg.libXt
    xterm
    xorg.fontutil
    xorg.fontmiscmisc
    xorg.fontcursormisc
  ];
  
  # macOS-specific packages
  darwinPackages = with platformPkgs; [
    darwin.apple_sdk.frameworks.Cocoa
    darwin.apple_sdk.frameworks.CoreGraphics
  ];
  
in
  platformPkgs.mkShell {
    name = "eda-environment-v1.0-${system}";
    buildInputs = commonPackages 
      ++ (if isLinux then linuxPackages else [])
      ++ (if isDarwin then darwinPackages else []);

    shellHook = ''
      export PROJECT_ROOT="$(pwd)"
      export TOOLS_DIR="$PROJECT_ROOT/.tools"
      mkdir -p "$TOOLS_DIR/bin"
      export PATH="$TOOLS_DIR/bin:$PATH"
      export CCACHE_DIR="$TOOLS_DIR/ccache"
      
      # Platform-specific compiler setup
      ${if isDarwin then ''
        export CC="ccache clang"
        export CXX="ccache clang++"
      '' else ''
        export CC="ccache gcc"
        export CXX="ccache g++"
      ''}

      # Platform-specific library paths
      ${if isLinux then ''
        export NIX_LD_LIBRARY_PATH="${platformPkgs.stdenv.cc.cc.lib}/lib:${platformPkgs.expat}/lib:${platformPkgs.zlib}/lib"
      '' else ''
        export DYLD_LIBRARY_PATH="${platformPkgs.stdenv.cc.cc.lib}/lib:${platformPkgs.expat}/lib:${platformPkgs.zlib}/lib"
      ''}
      
      export FONTCONFIG_FILE=${platformPkgs.fontconfig.out}/etc/fonts/fonts.conf
      export FONTCONFIG_PATH=${platformPkgs.fontconfig.out}/etc/fonts

      # PDK setup
      export PDK_ROOT="$HOME/.volare"
      export PDK="sky130A"
      export KLAYOUT_PATH="$PDK_ROOT/$PDK/libs.tech/klayout"
      export XSCHEM_USER_LIBRARY_PATH="$PDK_ROOT/$PDK/libs.tech/xschem"
      export XSCHEM_LIBRARY_PATH="$PDK_ROOT/$PDK/libs.tech/xschem:${xschem}/share/xschem/xschem_library"

      # Setup Python virtual environment with Python 3.12
      export VENV_DIR="$PROJECT_ROOT/.venv"
      if [ -z "$VIRTUAL_ENV" ] || [ "$VIRTUAL_ENV" != "$VENV_DIR" ]; then
          if [ ! -d "$VENV_DIR" ]; then
              echo "Creating Python virtual environment..."
              python3 -m venv "$VENV_DIR"
          fi
          source "$VENV_DIR/bin/activate"
      fi

      # Install additional Python packages with pinned versions
      pip install --upgrade pip==24.2 setuptools==75.1.0 wheel==0.44.0
      pip install --no-build-isolation \
          volare \
          openlane==2.3.10 \
          cace

      if [ ! -d "$PDK_ROOT/$PDK" ]; then
          echo "Downloading PDK..."
          volare enable --pdk sky130 0fe599b2afb6708d281543108caf8310912f54af
      fi

      # Create ngspice init file for faster sky130 simulation
      mkdir -p "$HOME/.xschem/simulations"
      if [ ! -f "$HOME/.xschem/simulations/.spiceinit" ]; then
        cat > "$HOME/.xschem/simulations/.spiceinit" << 'EOF'
      set ngbehavior=hsa
      set ng_nomodcheck
      set num_threads=4
      EOF
      fi

      echo "=== EDA Environment v1.0 (${system}) ==="
      echo ""
      
      ${if isDarwin then ''
        echo "Platform: macOS (${system})"
        echo ""
        echo "Note for macOS users:"
        echo "  - Some tools may require XQuartz for X11 support"
        echo "  - For Linux-specific tools, consider using the nix-darwin Linux builder"
        echo "  - To enable Linux builder, add to your nix-darwin configuration:"
        echo "      nix.linux-builder.enable = true;"
        echo ""
        if command -v arch > /dev/null 2>&1 && [[ "$(arch)" == "arm64" ]]; then
          echo "  - For Intel binaries on Apple Silicon, install Rosetta:"
          echo "      softwareupdate --install-rosetta --agree-to-license"
          echo ""
        fi
      '' else ''
        echo "Platform: Linux (${system})"
        echo ""
      ''}
      
      echo "System tools available:"
      echo "  - Python: $(python --version 2>&1 || echo 'not available')"
      echo "  - xschem: $(xschem --version 2>/dev/null || echo 'custom build')"
      echo "  - yosys: $(yosys -V 2>/dev/null | head -1 || echo 'unknown version')"
      echo "  - ngspice: $(ngspice --version 2>/dev/null | head -1 || echo 'unknown version')"
      echo "  - verilator: $(verilator --version 2>/dev/null | head -1 || echo 'unknown version')"
      echo "  - magic: $(magic --version 2>/dev/null || echo 'custom build ${magic-vlsi-old.version}')"
      echo "  - PDK: $PDK in $PDK_ROOT"
      
      ${if isDarwin then ''
        echo ""
        echo "macOS-specific notes:"
        echo "  - Some EDA tools may have limited GUI support on macOS"
        echo "  - Consider using remote Linux builders for full compatibility"
      '' else ""}
    '';
  }

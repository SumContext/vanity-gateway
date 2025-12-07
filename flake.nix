{
  description = "Development shell with custom Python environment and sumtree package";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
  };

  outputs =
    { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
      myPython = pkgs.python312.override {
        packageOverrides = final: prev: {
          torch = prev.torch.override { vulkanSupport = true; };

          stable-baselines3 = prev.stable-baselines3.overridePythonAttrs (old: {
            doCheck = false;
          });

          keras = prev.keras.overridePythonAttrs (old: rec {
            checkInputs = (old.checkInputs or []) ++ [ final.pillow ];
          });
        };
      };

      myPythonEnv = myPython.withPackages (ps: [
        ps.torch
        ps.pyside6
        ps.shiboken6
        ps.matplotlib
        ps.numpy
        ps.opencv-python
        ps.stable-baselines3
        ps.tqdm
        ps.ale-py
        ps.gymnasium
        ps.pillow
        ps.tinygrad
        ps.openai
        ps.pydantic
        ps.requests
      ]);

      sumtree = pkgs.writeShellScriptBin "sumtree" ''
        exec ${myPythonEnv}/bin/python ${self}/sumtree.py "$@"
      '';
    in
    {
      packages.${system} = {
        sumtree = sumtree;
        default = sumtree;
      };

      devShells.${system}.default = pkgs.mkShell {
        packages = [
          myPythonEnv
          pkgs.vulkan-loader
          pkgs.vulkan-headers
          pkgs.vulkan-tools
          pkgs.vulkan-validation-layers
          pkgs.rocmPackages.clr
          pkgs.rocmPackages.rocm-smi
          pkgs.ocl-icd
          pkgs.opencl-headers
          pkgs.clinfo
          pkgs.ruff
          pkgs.uv
          pkgs.cmake
          pkgs.SDL2
          pkgs.wayland
          pkgs.libxkbcommon
          pkgs.pulseaudio
          pkgs.xorg.libXcomposite
          pkgs.kdePackages.qtbase
          pkgs.kdePackages.qtdeclarative
          pkgs.kdePackages.qtsvg
          pkgs.kdePackages.qttools
          pkgs.kdePackages.qtmultimedia
          pkgs.kdePackages.qtvirtualkeyboard
          pkgs.kdePackages.qt3d
          sumtree
        ];

        shellHook = ''
          if [[ $- == *i* ]]; then
            export PS1="[nix-vulkan:\w] "
          fi

          export LD_LIBRARY_PATH="${pkgs.vulkan-loader}/lib:$LD_LIBRARY_PATH"
          export VK_LAYER_PATH="${pkgs.vulkan-validation-layers}/share/vulkan/explicit_layer.d"
        '';
      };
    };
}
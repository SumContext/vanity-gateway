{
  description = "Development shell with custom Python environment and vanity-gateway package";

  inputs = {
#     nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";
  };

  outputs =
    { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
      myPython = pkgs.python313.override {
        packageOverrides = final: prev: {

        };
      };

      myPythonEnv = myPython.withPackages (ps: [
#         ps.openai
        ps.pydantic
        ps.jinja2
        ps.requests
        ps.pathspec
        ps.fastapi
        ps.smart-open

        ps.langchain-core
        ps.pyutil
        #lanchain providers
        ps.langchain-xai
        ps.langchain-aws
        ps.langchain-groq
        ps.langchain-core
        ps.langchain-tests
        ps.langchain-openai
        ps.langchain-ollama
        ps.langchain-chroma
        ps.langchain-mongodb
        ps.langchain-classic
        ps.langchain-deepseek
        ps.langchain-mistralai
        ps.langchain-fireworks
        ps.langchain-community
        ps.langchain-anthropic
        ps.langchain-perplexity
        ps.langchain-huggingface
        ps.langchain-google-genai
        ps.langchain-experimental
        ps.langchain-text-splitters

      ]);

      gitRev = self.rev or "dirty";

      vanity-gateway = pkgs.writeShellScriptBin "vanity-gateway" ''
        export SUMTREE_GIT_REV="${gitRev}"
        exec ${myPythonEnv}/bin/python ${self}/vanity-gateway.py "$@"
      '';
    in
    {
      packages.${system} = {
        vanity-gateway = vanity-gateway;
        default = vanity-gateway;
      };

      devShells.${system}.default = pkgs.mkShell {
        packages = [
          myPythonEnv
          vanity-gateway
        ];

        shellHook = ''
          if [[ $- == *i* ]]; then
            export PS1="[vanity-gateway-dev:\w] "
          fi
        '';
      };
    };
}
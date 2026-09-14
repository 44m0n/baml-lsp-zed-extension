# BAML LSP for Zed

A minimal Zed language extension that associates `.baml` files with the current BAML CLI language server. It does not bundle or download BAML.

Syntax parsing and highlighting use the official [`BoundaryML/baml-treesitter`](https://github.com/BoundaryML/baml-treesitter) grammar. The grammar is pinned to a specific commit in `extension.toml`.

## Grammar updates

The `update-grammar` workflow checks the upstream grammar daily. When a new commit is available, it updates the pin and upstream-derived highlight and injection query files, bumps the extension patch version, validates the grammar, and opens or refreshes a pull request.

Run the same synchronization locally with:

```sh
python3 scripts/update_baml_grammar.py
```

## Install as a development extension

1. In Zed, run `zed: install dev extension`.
2. Select this repository directory.
3. Configure the BAML executable in the Zed settings of the machine that runs the language server:

```jsonc
{
  "lsp": {
    "baml": {
      "binary": {
        "path": "/path/to/baml",
        "arguments": ["lsp"]
      }
    }
  }
}
```

When no binary is configured, the extension runs `baml lsp` and relies on `baml` being present in `PATH`.

## Remote development

Zed starts language servers on the remote host. Install BAML on every remote host and place that host’s executable path in its remote Zed settings (`~/.config/zed/settings.json` on Linux). Do not place machine-specific paths in a project `.zed/settings.json`. For example, if BAML is installed for a remote user named `alice`, configure `"path": "/home/alice/.baml/bin/baml"` in that remote host’s settings.

## Requirements

Zed development extensions with Rust code require Rust and the `wasm32-wasip2` target. Zed can install the target automatically when Rust is installed through `rustup`.

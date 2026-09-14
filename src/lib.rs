use zed_extension_api::{self as zed, settings::LspSettings, Result};

struct BamlLspExtension;

impl zed::Extension for BamlLspExtension {
    fn new() -> Self {
        Self
    }

    fn language_server_command(
        &mut self,
        _language_server_id: &zed::LanguageServerId,
        worktree: &zed::Worktree,
    ) -> Result<zed::Command> {
        let settings = LspSettings::for_worktree("baml", worktree)?;
        let binary = settings.binary;

        let path = binary
            .as_ref()
            .and_then(|binary| binary.path.clone())
            .unwrap_or_else(|| "baml".to_string());
        let arguments = binary
            .as_ref()
            .and_then(|binary| binary.arguments.clone())
            .unwrap_or_else(|| vec!["lsp".to_string()]);
        let environment = binary
            .and_then(|binary| binary.env)
            .unwrap_or_default();

        Ok(zed::Command::new(path)
            .args(arguments)
            .envs(environment))
    }
}

zed::register_extension!(BamlLspExtension);

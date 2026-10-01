; Adapted for Zed from BoundaryML/baml-treesitter.
; Grammar revision: 35dc42c5a32df2c95809761728a73cb8e8f7cf1c.

; Prompt bodies and template_string bodies are Jinja templates.
; The raw string content between `#"` and `"#` is a single
; (raw_string_content) node, so it can be injected wholesale.

((prompt_field
   value: (raw_string
     (raw_string_content) @injection.content))
  (#set! injection.language "jinja"))

((template_string_declaration
   body: (raw_string
     (raw_string_content) @injection.content))
  (#set! injection.language "jinja"))

((comment) @injection.content
  (#set! injection.language "comment"))

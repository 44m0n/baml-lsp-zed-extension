; Adapted for Zed from BoundaryML/baml-treesitter.
; Grammar revision: e02989a78d382139defbb751c0196242af99ff73.

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

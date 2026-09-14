(class_declaration
  "class" @context
  name: (identifier) @name) @item

(enum_declaration
  "enum" @context
  name: (identifier) @name) @item

(interface_declaration
  "interface" @context
  name: (identifier) @name) @item

(function_declaration
  "function" @context
  name: (identifier) @name) @item

(client_declaration
  "client" @context
  name: (identifier) @name) @item

(generator_declaration
  "generator" @context
  name: (identifier) @name) @item

(retry_policy_declaration
  "retry_policy" @context
  name: (identifier) @name) @item

(template_string_declaration
  "template_string" @context
  name: (identifier) @name) @item

(type_alias_declaration
  "type" @context
  name: (identifier) @name) @item

(associated_type_declaration
  "type" @context
  name: (identifier) @name) @item

(test_declaration
  "test" @context
  name: [
    (identifier)
    (string)
    (binary_expression)
  ] @name) @item

(testset_declaration
  "testset" @context
  name: [
    (identifier)
    (string)
    (binary_expression)
  ] @name) @item

(field_declaration
  name: (identifier) @name) @item

(enum_variant
  name: (identifier) @name) @item

[
  (comment)
  (block_comment)
] @annotation

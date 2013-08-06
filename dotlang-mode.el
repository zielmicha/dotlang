(require 'generic-x)
(define-generic-mode
    'dotlang-mode
  '("#")
  '("while" "if" "def" "arg")
  '( ; builtin
    ("[a-zA-Z0-9_@!?-]+\\." . 'font-lock-variable-face)
    ("\\.[a-zA-Z0-9_@!?-]+" . 'font-lock-builtin-face)
    ("[a-zA-Z_@!?-][a-zA-Z0-9_@!?-]*" . 'font-lock-function-name-face))
  '("\\.dot$")
  nil
  "A mode for dotlang files")

(provide 'dotlang-mode)

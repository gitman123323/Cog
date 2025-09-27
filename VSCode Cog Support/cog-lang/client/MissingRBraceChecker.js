// MissingRBraceChecker.js
const vscode = require('vscode');

/**
 * Checks for missing closing braces "}" in Cog language statements
 * like if, else, while, for, and returns diagnostics.
 * Places the squiggle exactly at the end of the block that's missing it.
 * @param {vscode.TextDocument} doc
 * @returns {vscode.Diagnostic[]}
 */
function checkMissingRBraces(doc) {
    const diagnostics = [];
    const lines = doc.getText().split(/\r?\n/);

    // Stack to track open statements needing a closing brace
    const braceStack = [];

    lines.forEach((lineText, lineNo) => {
        // Remove comments to avoid false positives
        const code = lineText.replace(/\/\/.*$/, '').replace(/\/\*.*\*\//, '').trim();

        // Detect opening statements (if, else, while, for) ending with colon
        if (/\b(if|else|while|for)\b.*:\s*$/.test(code)) {
            braceStack.push({
                type: 'statement',
                lineNo,
                colNo: lineText.length, // default to end of line
            });
        }

        // Track explicit { and }
        for (let i = 0; i < lineText.length; i++) {
            const ch = lineText[i];
            if (ch === '{') {
                braceStack.push({
                    type: 'brace',
                    lineNo,
                    colNo: i
                });
            } else if (ch === '}') {
                // Pop the most recent opening brace/statement
                if (braceStack.length > 0) {
                    braceStack.pop();
                } else {
                    // Extra closing brace → error here
                    diagnostics.push(new vscode.Diagnostic(
                        new vscode.Range(lineNo, i, lineNo, i + 1),
                        'Unexpected closing brace',
                        vscode.DiagnosticSeverity.Error
                    ));
                }
            }
        }
    });

    // Remaining unclosed statements/braces → missing RBRACE
    braceStack.forEach(open => {
        const lineText = doc.lineAt(open.lineNo).text;

        // Place squiggle under last non-whitespace char
        const col = lineText.search(/\s*$/);
        diagnostics.push(new vscode.Diagnostic(
            new vscode.Range(open.lineNo, col, open.lineNo, col + 1),
            'Missing closing brace "}"',
            vscode.DiagnosticSeverity.Error
        ));
    });

    return diagnostics;
}

module.exports = { checkMissingRBraces };

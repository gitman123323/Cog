// ErrorColumnFixer.js
const vscode = require('vscode');

/**
 * Fixes column numbers for diagnostics based on the actual document text.
 * @param {string} rawErrors - Raw stderr from Python parser
 * @param {vscode.TextDocument} doc
 * @returns {vscode.Diagnostic[]}
 */
function fixErrorColumns(rawErrors, doc) {
    const diagnostics = [];
    if (!rawErrors || rawErrors.trim().length === 0) return diagnostics;

    for (const line of rawErrors.trim().split('\n')) {
        const match = line.match(/(\d+):(\d+): (.*)/);
        if (!match) continue;

        const lineNum = parseInt(match[1], 10) - 1;
        let colNum = parseInt(match[2], 10) - 1;
        const msg = match[3];

        if (lineNum < 0 || lineNum >= doc.lineCount) continue;

        const lineText = doc.lineAt(lineNum).text;

        // Try to find the token in the line to correct column
        const tokenMatch = msg.match(/\w+/);
        if (tokenMatch) {
            const token = tokenMatch[0];
            const index = lineText.indexOf(token);
            if (index !== -1) colNum = index;
        }

        const range = new vscode.Range(lineNum, colNum, lineNum, colNum + 1);
        diagnostics.push(
            new vscode.Diagnostic(range, msg, vscode.DiagnosticSeverity.Error)
        );
    }

    return diagnostics;
}

module.exports = { fixErrorColumns };
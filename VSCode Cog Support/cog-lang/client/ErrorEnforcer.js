const vscode = require('vscode');

/**
 * Checks if import statements are only at the top of the file.
 * @param {vscode.TextDocument} doc
 * @returns {vscode.Diagnostic[]}
 */
function checkImportsAtTop(doc) {
    const diagnostics = [];
    const lines = doc.getText().split(/\r?\n/);

    let firstNonImportLine = -1;

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        if (line.length === 0) continue; // skip empty lines
        if (!line.startsWith('import')) {
            firstNonImportLine = i;
            break;
        }
    }

    if (firstNonImportLine !== -1) {
        for (let i = firstNonImportLine + 1; i < lines.length; i++) {
            const line = lines[i].trim();
            if (line.startsWith('import')) {
                const range = new vscode.Range(i, 0, i, line.length);
                diagnostics.push(
                    new vscode.Diagnostic(
                        range,
                        '[COG] Import_Error: Import statements must be at the top of the file',
                        vscode.DiagnosticSeverity.Error
                    )
                );
            }
        }
    }

    return diagnostics;
}

module.exports = { checkImportsAtTop };
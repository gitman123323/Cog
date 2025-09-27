const vscode = require('vscode');
const cp = require('child_process');
const path = require('path');

function activate(context) {
    const diagnosticCollection = vscode.languages.createDiagnosticCollection('coglang');
    context.subscriptions.push(diagnosticCollection);

    // -----------------------------
    // Function: Run diagnostics
    // -----------------------------
    function runDiagnostics(doc) {
        if (doc.languageId !== 'coglang') return;

        const serverPath = path.join(context.extensionPath, 'server', 'cog_lsp.py');

        const process = cp.execFile('python', [serverPath]);

        // Send text to Python parser via stdin
        process.stdin.write(doc.getText());
        process.stdin.end();

        let errors = '';
        process.stderr.on('data', data => {
            errors += data.toString();
        });

        const { checkImportsAtTop } = require('./ErrorEnforcer');
        //const { fixErrorColumns } = require('./ErrorColumnFixer');

        process.on('close', () => {
            const diagnostics = [];
            if (errors.trim().length > 0) {
                for (const line of errors.trim().split('\n')) {
                    const match = line.match(/(\d+):(\d+): (.*)/);
                    if (match) {
                        const lineNum = parseInt(match[1]) - 1;
                        const colNum = parseInt(match[2]) - 1;
                        const msg = match[3];

                        // Squiggle exactly at token
                        const range = new vscode.Range(lineNum, colNum, lineNum, colNum + 1);
                        diagnostics.push(
                            new vscode.Diagnostic(range, msg, vscode.DiagnosticSeverity.Error)
                        );
                    }
                }
            }
            
            // Add import enforcement errors
            //diagnostics.push(fixErrorColumns(errors, doc));
            diagnostics.push(...checkImportsAtTop(doc));

            diagnosticCollection.set(doc.uri, diagnostics);
        });
    }

    // -----------------------------
    // Real-time diagnostics (typing)
    // -----------------------------
    let timeout = null;
    vscode.workspace.onDidChangeTextDocument(event => {
        if (event.document.languageId !== 'coglang') return;
        if (timeout) clearTimeout(timeout);
        timeout = setTimeout(() => runDiagnostics(event.document), 100); // 300ms debounce
    });

    // Also run on save
    vscode.workspace.onDidSaveTextDocument(doc => runDiagnostics(doc));

    // -----------------------------
    // Completion Provider (types after let)
    // -----------------------------
    vscode.languages.registerCompletionItemProvider(
        'coglang',
        {
            provideCompletionItems(document, position) {
                const lineText = document.lineAt(position).text;
                const prefix = lineText.substring(0, position.character);

                const completions = [];

                // Trigger type suggestions after "let <name>:" with optional space
                if (/let\s+\w+\:\s*$/.test(prefix)) {
                    ['int', 'float', 'bool', 'string'].forEach(type => {
                        const displayType = type === 'string' ? 'str' : type; // map string → str
                        const item = new vscode.CompletionItem(
                            displayType,
                            vscode.CompletionItemKind.Variable
                        );
                        item.detail = 'Type';
                        completions.push(item);
                    });
                }

                // Trigger "import" suggestion when starting with 'i'
                if (/\bi\w*$/.test(prefix)) {
                    const item = new vscode.CompletionItem(
                        'import',
                        vscode.CompletionItemKind.Keyword
                    );
                    item.detail = 'An import statement. Very Useful.';
                    // 👇 What actually gets inserted into the document
                    item.insertText = 'import "";';

                    // Optional: place the cursor *inside* the quotes
                    item.insertText = new vscode.SnippetString('import "$1";');
                    
                    completions.push(item);
                }

                // Trigger statements suggestions after colon not just types
                // Optional: uncomment below if you want
                /*
                if (/^\s*$/.test(prefix)) {
                    ['if', 'else', 'return', 'while', 'for', 'break', 'continue'].forEach(stmt => {
                        const item = new vscode.CompletionItem(
                            stmt,
                            vscode.CompletionItemKind.Keyword
                        );
                        completions.push(item);
                    });
                }
                */

                return completions;
            }
        },
        ' ' // trigger on space
    );
}

function deactivate() {}

module.exports = { activate, deactivate };

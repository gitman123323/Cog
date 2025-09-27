const path = require('path');
const { spawn, execFile } = require('child_process');
const { createConnection, TextDocuments, ProposedFeatures, DiagnosticSeverity } = require('vscode-languageserver/node');
const { TextDocument } = require('vscode-languageserver-textdocument');

const connection = createConnection(ProposedFeatures.all);
const documents = new TextDocuments(TextDocument);

let pythonProcess = execFile('python', [path.join(__dirname, 'cog_lsp.py')]);
let pendingDiagnostics = new Map(); // map uri -> latest text

// capture output from Python parser
let buffer = '';
pythonProcess.stdout.on('data', data => {
    buffer += data.toString();
    if (buffer.includes('\n')) {
        // split by line and parse diagnostics
        const lines = buffer.split(/\r?\n/);
        buffer = lines.pop(); // last incomplete line stays in buffer

        // send diagnostics for the last pending document
        pendingDiagnostics.forEach((text, uri) => {
            const diagnostics = [];
            for (const line of lines) {
                const match = line.match(/(\d+):(\d+): (.*)/);
                if (match) {
                    const lineNum = parseInt(match[1]) - 1;
                    const colNum = parseInt(match[2]) - 1;
                    diagnostics.push({
                        severity: DiagnosticSeverity.Error,
                        range: {
                            start: { line: lineNum, character: colNum },
                            end: { line: lineNum, character: colNum + 1 }
                        },
                        message: match[3],
                        source: 'cog-lang'
                    });
                }
            }
            connection.sendDiagnostics({ uri, diagnostics });
        });
        pendingDiagnostics.clear();
    }
});

documents.onDidChangeContent(change => {
    const text = change.document.getText();
    pendingDiagnostics.set(change.document.uri, text);
    pythonProcess.stdin.write(text + '\n'); // send to Python parser
});

// also run on save (optional)
documents.onDidSave(change => {
    const text = change.document.getText();
    pendingDiagnostics.set(change.document.uri, text);
    pythonProcess.stdin.write(text + '\n');
});

connection.onInitialize(() => {
    return { capabilities: { textDocumentSync: documents.syncKind } };
});

documents.listen(connection);
connection.listen();

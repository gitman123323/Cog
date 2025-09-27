const path = require('path');
const { execFile } = require('child_process');
const { fileURLToPath } = require('url');
const {
  createConnection,
  TextDocuments,
  ProposedFeatures,
  DiagnosticSeverity
} = require('vscode-languageserver/node');

const { TextDocument } = require('vscode-languageserver-textdocument');

const connection = createConnection(ProposedFeatures.all);
const documents = new TextDocuments(TextDocument);

let pythonCmd = 'python'; // default; can be overridden by client settings later (improvement)

// helper to convert URI -> path
function uriToPath(uri) {
  try {
    return fileURLToPath(uri);
  } catch (e) {
    // fallback for non-file URIs
    if (uri.startsWith('file://')) return uri.replace('file://', '');
    return uri;
  }
}

connection.onInitialize(() => {
  return {
    capabilities: {
      textDocumentSync: documents.syncKind
    }
  };
});

// on save: run the Python parser and gather diagnostics
documents.onDidSave(change => {
  validateTextDocument(change.document);
});

// optional: if you want immediate results while typing
// documents.onDidChangeContent(change => debounceValidate(change.document));

const DEBOUNCE_MS = 300;
const debounceMap = new Map();

function debounceValidate(doc) {
  if (debounceMap.has(doc.uri)) clearTimeout(debounceMap.get(doc.uri));
  debounceMap.set(doc.uri, setTimeout(() => {
    validateTextDocument(doc);
    debounceMap.delete(doc.uri);
  }, DEBOUNCE_MS));
}

function validateTextDocument(textDocument) {
  const filePath = uriToPath(textDocument.uri);
  const diagnostics = [];

  // path to your Python wrapper script inside the server folder
  const script = path.join(__dirname, 'cog_lsp.py');

  // run parser with working directory = file's directory (important for relative imports)
  execFile(pythonCmd, [script, filePath], { cwd: path.dirname(filePath) }, (err, stdout, stderr) => {
    // stderr should contain lines like:
    // line:col: message
    // or
    // file:line:col: message
    const lines = (stderr || '').split(/\r?\n/).filter(Boolean);

    const pattern = /^(?:(.*?):)?(\d+):(\d+):\s*(.*)$/; // captures optional filename, line, col, message

    for (const line of lines) {
      const m = line.match(pattern);
      if (m) {
        const lineNum = Math.max(0, parseInt(m[2], 10) - 1);
        const colNum = Math.max(0, parseInt(m[3], 10) - 1);
        diagnostics.push({
          severity: DiagnosticSeverity.Error,
          range: {
            start: { line: lineNum, character: colNum },
            end:   { line: lineNum, character: colNum + 1 }
          },
          message: m[4],
          source: 'cog-lang'
        });
      } else {
        // fallback: put at top of file
        diagnostics.push({
          severity: DiagnosticSeverity.Error,
          range: {
            start: { line: 0, character: 0 },
            end:   { line: 0, character: 1 }
          },
          message: line,
          source: 'cog-lang'
        });
      }
    }

    // send diagnostics (empty array clears existing errors)
    connection.sendDiagnostics({ uri: textDocument.uri, diagnostics });
  });
}

documents.listen(connection);
connection.listen();
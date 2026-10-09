import assert from 'node:assert/strict';
import {readFileSync, existsSync, readdirSync} from 'node:fs';
import {resolve, dirname, join} from 'node:path';
import {fileURLToPath} from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const extension = JSON.parse(readFileSync(join(root, 'matlab/eeglab-mcp-tools.json')));
const names = new Set();
for (const tool of extension.tools) {
  assert(!names.has(tool.name), `Duplicate tool: ${tool.name}`);
  names.add(tool.name);
  const signature = extension.signatures[tool.name];
  assert(signature, `Missing signature: ${tool.name}`);
  assert.equal(tool.inputSchema.type, 'object');
  const properties = tool.inputSchema.properties;
  assert.deepEqual([...signature.input.order].sort(), Object.keys(properties).sort());
  assert.deepEqual([...tool.inputSchema.required].sort(), Object.keys(properties).sort());
  for (const property of Object.values(properties)) {
    assert(['string', 'number', 'integer', 'boolean'].includes(property.type), 'Unsupported MathWorks argument type');
  }
  const source = readFileSync(join(root, 'matlab', `${signature.function}.m`), 'utf8');
  const declaration = source.match(/^function\s+(\w+)\(([^)]*)\)/);
  assert(declaration, `Invalid function declaration: ${signature.function}`);
  assert.equal(declaration[1], signature.function);
  const argumentsList = declaration[2].trim() ? declaration[2].split(',').map(x => x.trim()) : [];
  assert.deepEqual(argumentsList, signature.input.order, `Wrong argument order: ${tool.name}`);
  assert.equal(typeof tool.description, 'string');
  assert.equal(typeof tool.annotations.readOnlyHint, 'boolean');
}
assert.equal(names.size, 46);
assert.deepEqual(Object.keys(extension.signatures).sort(), [...names].sort());
const claims = JSON.parse(readFileSync(join(root, 'generated/eeglab-official-claims.json')));
assert.equal(claims.document_version, '1.0.0');
assert.equal(Object.keys(claims.claims).length, claims.claim_count);
assert.equal(Object.keys(claims.method_profiles).length, claims.method_profile_count);
const checker = readFileSync(join(root, 'matlab/eegmcp_check_requirement.m'), 'utf8');
for (const [name, profile] of Object.entries(claims.method_profiles)) {
  for (const requirement of profile.requirements) {
    assert(checker.includes(`case '${requirement.check}'`), `Unimplemented gate: ${name}/${requirement.check}`);
  }
  for (const id of profile.source_claim_ids) assert(claims.claims[id], `Unknown claim: ${id}`);
}
for (const name of claims.high_risk_tool_names) {
  assert(names.has(name), `Missing high-risk tool: ${name}`);
  const source = readFileSync(join(root, 'matlab', `${extension.signatures[name].function}.m`), 'utf8');
  assert(source.includes('eegmcp_gate(') || source.includes('eegmcp_pipeline_run('), `Missing gate route: ${name}`);
}
for (const path of ['eeglab_mcp_server', 'configs', 'pyproject.toml']) assert(!existsSync(join(root, path)), `Obsolete path: ${path}`);
function scan(folder) {
  for (const entry of readdirSync(folder, {withFileTypes: true})) {
    if (entry.name.startsWith('.git') || entry.name === '.venv') continue;
    const path = join(folder, entry.name);
    if (entry.isDirectory()) scan(path);
    else {
      assert(!path.endsWith('.py') && !path.endsWith('.ps1') && !path.endsWith('.bat'), `Obsolete runtime file: ${path}`);
      if (/\.(m|md|json|ya?ml|mjs)$/.test(path)) {
        assert(!/[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]/.test(readFileSync(path, 'utf8')), `Unexpected CJK text: ${path}`);
      }
    }
  }
}
scan(join(root, 'matlab'));
scan(join(root, 'scripts'));
scan(join(root, '.github'));
console.log(`repository_contract_ok=true tools=${names.size} claims=${claims.claim_count} profiles=${claims.method_profile_count}`);

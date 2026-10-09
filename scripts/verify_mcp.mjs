import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {createInterface} from 'node:readline';
import {readFileSync, writeFileSync, mkdirSync} from 'node:fs';
import {dirname, resolve, join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {pathToFileURL} from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const [binary, mode = 'catalog', output = join(root, 'mcp-result.json'), eeglabRoot = '', endpoint = ''] = process.argv.slice(2);
assert(binary, 'Supply the official MathWorks MCP server binary');
mkdirSync(dirname(output), {recursive: true});
const extension = JSON.parse(readFileSync(join(root, 'matlab/eeglab-mcp-tools.json')));
const native = binary === 'native';
let session = '';
const server = native ? null : spawn(binary, [
  `--extension-file=${join(root, 'matlab/eeglab-mcp-tools.json')}`,
  ...(mode === 'catalog' ? ['--matlab-session-mode=existing'] : [
    '--matlab-session-mode=new', '--matlab-display-mode=nodesktop',
    `--initial-working-folder=${join(root, 'matlab')}`,
  ]),
  '--disable-telemetry=true',
  `--log-folder=${dirname(output)}`, '--log-level=error',
], {stdio: ['pipe', 'pipe', 'pipe']});
let stderr = '';
server?.stderr.on('data', chunk => { stderr = (stderr + chunk).slice(-16384); });
const pending = new Map();
let id = 0;
const reader = server ? createInterface({input: server.stdout}) : null;
async function http(message) {
  const response = await fetch(endpoint, {method: 'POST', headers: {
    'Content-Type': 'application/json', Accept: 'application/json, text/event-stream',
    'MCP-Protocol-Version': '2025-06-18', ...(session ? {'Mcp-Session-Id': session} : {}),
  }, body: JSON.stringify(message), signal: AbortSignal.timeout(90000)});
  if (response.headers.has('Mcp-Session-Id')) session = response.headers.get('Mcp-Session-Id');
  assert(response.ok, `MCP HTTP status: ${response.status}`);
  if (response.status === 202 || response.status === 204) return null;
  return response.json();
}
async function send(message) {
  if (native) await http(message);
  else server.stdin.write(`${JSON.stringify(message)}\n`);
}
reader?.on('line', line => {
  try {
    const message = JSON.parse(line);
    if (message.method && message.id != null) {
      if (message.method === 'roots/list') send({jsonrpc: '2.0', id: message.id, result: {roots: [{uri: pathToFileURL(join(root, 'matlab')).href, name: 'EEGLAB'}]}});
      else send({jsonrpc: '2.0', id: message.id, error: {code: -32601, message: 'Unsupported client method'}});
    } else if (pending.has(message.id)) {
      const item = pending.get(message.id); pending.delete(message.id); clearTimeout(item.timer);
      if (message.error) item.reject(new Error(JSON.stringify(message.error)));
      else item.resolve(message.result);
    }
  } catch (error) {
    for (const item of pending.values()) { clearTimeout(item.timer); item.reject(error); }
    pending.clear();
  }
});
server?.on('error', error => { for (const item of pending.values()) item.reject(error); });
server?.on('exit', code => {
  for (const item of pending.values()) { clearTimeout(item.timer); item.reject(new Error(`MCP exited: ${code}; ${stderr}`)); }
  pending.clear();
});
async function request(method, params = {}) {
  const requestId = ++id;
  if (native) {
    const message = await http({jsonrpc: '2.0', id: requestId, method, params});
    assert.equal(message.id, requestId);
    if (message.error) throw new Error(JSON.stringify(message.error));
    return message.result;
  }
  return new Promise((resolveResult, reject) => {
    const timer = setTimeout(() => { pending.delete(requestId); reject(new Error(`Timed out: ${method} ${params.name || ''}`)); }, 90000);
    pending.set(requestId, {resolve: resolveResult, reject, timer});
    send({jsonrpc: '2.0', id: requestId, method, params});
  });
}
async function call(name, args = {}) {
  console.log(`Calling MATLAB tool: ${name}`);
  const result = await request('tools/call', {name, arguments: args});
  assert(!result.isError, `${name} failed in the MCP transport: ${JSON.stringify(result)}`);
  const text = result.content.filter(x => x.type === 'text').map(x => x.text).join('\n');
  return JSON.parse(text.slice(text.indexOf('{'), text.lastIndexOf('}') + 1));
}
try {
  const initialized = await request('initialize', {protocolVersion: '2025-06-18', capabilities: {roots: {}}, clientInfo: {name: 'eeglab-github-verifier', version: '1'}});
  assert(initialized.serverInfo);
  await send({jsonrpc: '2.0', method: 'notifications/initialized'});
  const listed = await request('tools/list');
  for (const expected of extension.tools) {
    const actual = listed.tools.find(x => x.name === expected.name);
    assert(actual, `MCP server omitted ${expected.name}`);
    assert.deepEqual({...actual.inputSchema, required: actual.inputSchema.required || []},
      {...expected.inputSchema, required: expected.inputSchema.required || []}, `Wire schema changed: ${expected.name}`);
  }
  const results = {status: 'success', custom_tool_count: extension.tools.length, server_info: initialized.serverInfo};
  if (native) {
    await request('ping');
    await assert.rejects(() => request('unknown/method'), /-32601/);
    await assert.rejects(() => request('tools/call', {name: 'unreviewed_function'}), /-32602/);
    await assert.rejects(() => request('tools/call', {name: 'eeglab_init', arguments: {}}), /-32602/);
    await assert.rejects(() => request('tools/call', {name: 'eeglab_init', arguments: {eeglab_path: 7}}), /-32602/);
    await assert.rejects(() => request('tools/call', {name: 'eeglab_official_claims', arguments: {unexpected: true}}), /-32602/);
    assert.equal((await fetch(endpoint)).status, 405);
    const badSession = await fetch(endpoint, {method: 'POST', headers: {
      'Content-Type': 'application/json', 'Mcp-Session-Id': 'unknown-session',
    }, body: JSON.stringify({jsonrpc: '2.0', id: 99, method: 'ping'})});
    assert.equal(badSession.status, 404);
    const headers = {'Content-Type': 'application/json', Accept: 'application/json, text/event-stream', 'Mcp-Session-Id': session};
    const malformed = await fetch(endpoint, {method: 'POST', headers, body: '{'});
    assert.equal((await malformed.json()).error.code, -32700);
    const ping = JSON.stringify({jsonrpc: '2.0', id: 100, method: 'ping'});
    assert.equal((await fetch(endpoint, {method: 'POST', headers: {...headers, Origin: 'https://invalid.example'}, body: ping})).status, 403);
    assert.equal((await fetch(endpoint, {method: 'POST', headers: {...headers, 'MCP-Protocol-Version': 'unknown'}, body: ping})).status, 400);
    const utf8 = await call('eeglab_method_preflight', {options: JSON.stringify({method: 'epoch', override_reason: 'UTF-8 caf\u00e9'})});
    assert.equal(utf8.summary.override_reason, 'UTF-8 caf\u00e9');
    results.protocol_checks = 12;
  }
  if (mode === 'live') {
    const claims = await call('eeglab_official_claims');
    assert.equal(claims.claim_count, 47); assert.equal(claims.method_profile_count, 39);
    const blocked = await call('eeglab_method_preflight', {options: '{"method":"epoch","context":{}}'});
    assert.equal(blocked.summary.gate_status, 'blocked');
    const plan = await call('eeglab_workflow_recommend', {options: '{}'});
    assert.equal(plan.summary.analysis_type_resolved, 'qc');
    const invalid = await call('eeglab_method_preflight', {options: '[]'});
    assert.equal(invalid.code, 'invalid_options');
    const init = await call('eeglab_init', {eeglab_path: eeglabRoot}); assert.equal(init.status, 'success');
    const loaded = await call('eeglab_load_data', {filepath: join(eeglabRoot, 'sample_data/eeglab_data.set')});
    assert.equal(loaded.nbchan, 32);
    const info = await call('eeglab_info'); assert.equal(info.pnts, 30504);
    const filter = await call('eeglab_filter', {options: '{"filter_type":"highpass","low_cutoff":1}'});
    assert.equal(filter.code, 'official_gate_blocked');
    results.live_tool_calls = 8;
  } else if (mode === 'request') {
    const event = JSON.parse(readFileSync(process.env.GITHUB_EVENT_PATH));
    const tool = event.inputs.tool;
    const definition = extension.tools.find(x => x.name === tool);
    assert(definition, 'Requested tool is not in the reviewed extension');
    const options = JSON.parse(event.inputs.arguments || '{}');
    assert(options && !Array.isArray(options) && typeof options === 'object', 'arguments must be a JSON object');
    for (const [key, value] of Object.entries(options)) {
      if (value === '@sample') options[key] = join(eeglabRoot, 'sample_data/eeglab_data.set');
      if (value === '@artifacts') options[key] = dirname(output);
    }
    const args = definition.inputSchema.properties.options ? {options: JSON.stringify(options)} : options;
    const init = await call('eeglab_init', {eeglab_path: eeglabRoot}); assert.equal(init.status, 'success');
    const loaded = await call('eeglab_load_data', {filepath: join(eeglabRoot, 'sample_data/eeglab_data.set')});
    assert.equal(loaded.status, 'success');
    results.tool = tool; results.response = await call(tool, args);
    // A method gate can legitimately block a requested analysis; preserve that result as an artifact.
    if (results.response.status === 'error' && results.response.code !== 'official_gate_blocked') {
      results.status = 'error';
      process.exitCode = 1;
    }
  }
  writeFileSync(output, JSON.stringify(results, null, 2));
  console.log(`mcp_ok=true transport=${native ? 'matlab-http' : 'mathworks-stdio'} mode=${mode} custom_tools=${extension.tools.length}`);
} catch (error) {
  writeFileSync(output, JSON.stringify({status: 'error', error: error.message}, null, 2));
  console.error(error.message);
  process.exitCode = 1;
} finally {
  for (const item of pending.values()) clearTimeout(item.timer);
  pending.clear(); reader?.close(); server?.stdin.end(); server?.kill();
  if (native && session) await fetch(endpoint, {method: 'DELETE', headers: {'Mcp-Session-Id': session}}).catch(() => {});
}

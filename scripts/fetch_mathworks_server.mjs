import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdirSync, writeFileSync, chmodSync, appendFileSync} from 'node:fs';
import {join, resolve} from 'node:path';

const assets = {
  'linux-x64': ['matlab-mcp-server-linux-x64', '1a49693e757f3b1c17c1494fbd3efd87ce4b9017af0fa36fba2cf0bd11e8734a'],
  'darwin-arm64': ['matlab-mcp-server-macos-arm64', '6e53d0fd3adcbbba60bf8dd4a63b53a64864a0d8154ae614d95789197a6142cb'],
  'darwin-x64': ['matlab-mcp-server-macos-x64', '3ba477b3fbf03fd70ac594b18a21c5552b4b89c96e8dbe284c1aa7b0bcf8aead'],
  'win32-x64': ['matlab-mcp-server-windows-x64.exe', '6697a8962f148628f11d93b36960235871de5614905d6a27c55341c2b83f4118'],
};
const output = resolve(process.argv[2]);
mkdirSync(output, {recursive: true});
const asset = assets[`${process.platform}-${process.arch}`];
assert(asset, 'Unsupported GitHub runner platform');
async function download(name, digest) {
  const response = await fetch(`https://github.com/matlab/matlab-mcp-server/releases/download/v0.14.0/${name}`);
  assert(response.ok, `Download failed: ${response.status}`);
  const bytes = Buffer.from(await response.arrayBuffer());
  assert.equal(createHash('sha256').update(bytes).digest('hex'), digest, `Checksum mismatch: ${name}`);
  const path = join(output, name);
  writeFileSync(path, bytes);
  return path;
}
const binary = await download(...asset);
if (process.platform !== 'win32') chmodSync(binary, 0o755);
if (process.platform === 'linux') {
  await download('MATLABMCPServerToolbox.mltbx', 'f601ca4da02291658f0e1dc8511959873f55aa43b67a76f754dc77c448cf83a2');
}
if (process.env.GITHUB_OUTPUT) appendFileSync(process.env.GITHUB_OUTPUT, `binary=${binary}\n`);
console.log('mathworks_release_verified=v0.14.0');

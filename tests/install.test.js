const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { destinations, install } = require('../bin/install.js');

test('Codex and Claude targets respect configured roots', () => {
  assert.deepEqual(destinations(['--target', 'both'], {CODEX_HOME:'/custom/codex'}, '/virtual/user-root'), ['/virtual/user-root/.claude/skills','/custom/codex/skills']);
  assert.throws(() => destinations(['--target', 'unknown']));
});
test('upgrade preserves old edits in a backup and installs complete resources', () => {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'skill-install-test-'));
  try {
    const first = install(temp);
    fs.writeFileSync(path.join(first.dest, 'custom.txt'), 'local customization');
    const second = install(temp);
    assert.equal(fs.readFileSync(path.join(second.backup, 'custom.txt'), 'utf8'), 'local customization');
    assert.ok(fs.existsSync(path.join(second.dest, 'SKILL.md')));
    assert.ok(fs.existsSync(path.join(second.dest, 'assets/env.example')));
    assert.ok(!fs.existsSync(path.join(second.dest, 'custom.txt')));
  } finally { fs.rmSync(temp, {recursive:true, force:true}); }
});

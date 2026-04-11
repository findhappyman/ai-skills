#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const os = require('os');

const pkgDir = path.join(__dirname, '..');
const claudeSkillsDir = path.join(os.homedir(), '.claude', 'skills');

function copyDir(src, dest) {
  fs.mkdirSync(dest, { recursive: true });
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);
    if (entry.isDirectory()) {
      copyDir(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

// 找出所有包含 skill.md 的技能目录
const SKIP = new Set(['.git', '.claude-plugin', 'bin', 'node_modules']);
const skillDirs = fs.readdirSync(pkgDir, { withFileTypes: true })
  .filter(d => d.isDirectory() && !SKIP.has(d.name))
  .filter(d =>
    fs.existsSync(path.join(pkgDir, d.name, 'skill.md')) ||
    fs.existsSync(path.join(pkgDir, d.name, 'SKILL.md'))
  );

if (skillDirs.length === 0) {
  console.log('No skills found to install.');
  process.exit(0);
}

console.log(`\nInstalling ${skillDirs.length} skill(s) to ${claudeSkillsDir}\n`);

for (const dir of skillDirs) {
  const src = path.join(pkgDir, dir.name);
  const dest = path.join(claudeSkillsDir, dir.name);
  copyDir(src, dest);
  console.log(`  ✓ ${dir.name}`);
}

console.log('\nDone! Restart Claude Code to activate the skills.');

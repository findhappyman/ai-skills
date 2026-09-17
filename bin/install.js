#!/usr/bin/env node
const fs = require("node:fs");
const path = require("node:path");
const os = require("node:os");

function destinations(argv, env = process.env, home = os.homedir()) {
  let target = "claude", custom;
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === "--target" && argv[i + 1]) target = argv[++i];
    else if (argv[i] === "--dir" && argv[i + 1]) custom = path.resolve(argv[++i]);
    else throw new Error("参数：--target claude|codex|both 或 --dir PATH");
  }
  if (!["claude", "codex", "both"].includes(target)) throw new Error("未知安装目标");
  if (custom) return [custom];
  const dirs = [];
  if (target !== "codex") dirs.push(path.join(home, ".claude", "skills"));
  if (target !== "claude") dirs.push(path.join(env.CODEX_HOME || path.join(home, ".codex"), "skills"));
  return dirs;
}

function install(root, source = path.resolve(__dirname, "../article-optimizer")) {
  const dest = path.join(root, "article-optimizer");
  if (path.resolve(dest) === path.resolve(source)) throw new Error("安装目标不能是来源目录");
  fs.mkdirSync(root, { recursive: true });
  let backup;
  if (fs.existsSync(dest)) {
    const backupDir = fs.mkdtempSync(path.join(root, ".article-optimizer-backup-"));
    backup = path.join(backupDir, "article-optimizer");
    fs.renameSync(dest, backup);
  }
  try {
    fs.cpSync(source, dest, { recursive: true, filter: p => !["__pycache__", ".DS_Store"].includes(path.basename(p)) && !p.endsWith(".pyc") });
  } catch (err) {
    // 只清理本次安装目标，再还原已有技能。
    fs.rmSync(dest, { recursive: true, force: true });
    if (backup) fs.renameSync(backup, dest);
    throw err;
  }
  return { dest, backup };
}

if (require.main === module) {
  try {
    for (const root of destinations(process.argv.slice(2))) {
      const result = install(root);
      console.log("已安装：" + result.dest);
      if (result.backup) console.log("旧版备份：" + result.backup);
    }
    console.log("重新开启宿主会话后使用 article-optimizer。");
  } catch (err) { console.error(err.message); process.exitCode = 1; }
}
module.exports = { destinations, install };

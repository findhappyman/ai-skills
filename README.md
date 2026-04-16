# AI Skills · Henry Xue

我日常使用的 AI 技能文档，用于 Claude Code。每个技能是一个独立文件夹，包含 `skill.md`。

## 安装方式

### 方法一：npx（一行命令，直接从 GitHub 安装）

```bash
npx github:findhappyman/ai-skills
```

会自动将技能文件复制到 `~/.claude/skills/`，重启 Claude Code 即可使用。无需提前安装任何包。

---

### 方法二：Claude Code /plugin 命令（从 GitHub 在线安装）

在 Claude Code 终端中运行以下命令，将此仓库注册为插件市场：

```
/plugin marketplace add findhappyman/ai-skills
```

然后安装具体技能（以 article-optimizer 为例）：

```
/plugin install article-optimizer@henry-ai-skills
```

安装完成后直接对话即可触发，无需额外操作。

---

### 方法三：手动复制

将对应文件夹中的 `skill.md` 内容复制到 Claude Projects 的自定义指令中，或放入 `~/.claude/skills/<skill-name>/` 目录下使用。

---

## 技能列表

| 文件夹 | 技能名称 | 功能 |
|--------|----------|------|
| [article-optimizer](./article-optimizer/skill.md) | Article Optimizer | 将原始文章优化并适配微信公众号、X（推特）、小红书三个平台，同时生成 AI 配图 Prompt |

## 开源协议

MIT

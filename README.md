# AI Skills

可复用的中文内容生产 skill，支持 Claude Code 与 Codex。当前包含 **Article Optimizer**：录音/视频/初稿 → 保真原始稿 → 多平台文章与实际配图 → 审核 → 已授权渠道的草稿或网站同步。

## 安装

需要 Node.js 18+；安装器本身无第三方依赖。

```bash
# Claude Code（默认）
npx github:findhappyman/ai-skills
# Codex
npx github:findhappyman/ai-skills --target codex
# 两者，或自定义 skills 根目录
npx github:findhappyman/ai-skills --target both
npx github:findhappyman/ai-skills --dir /path/to/skills
```

升级时会先把已有 skill 移到同级备份目录，再安装新文件，不悄悄覆盖本地定制。安装后重新开启会话。

手动安装：复制整个 `article-optimizer/` 到宿主的 skills 目录，保留 `SKILL.md`、references、assets 和 scripts；不要只复制正文。默认路径为 `~/.claude/skills/` 或 `~/.codex/skills/`，Codex 支持 `CODEX_HOME`。

Claude Code 插件市场入口仍保留：

```text
/plugin marketplace add findhappyman/ai-skills
/plugin install article-optimizer@ai-skills
```

旧版市场名含个人前缀，现已改为 `ai-skills`；旧安装如出现名称冲突，移除旧市场登记后按以上命令添加。这次升级不会自动修改你的插件登记。

## 用法

```text
使用 article-optimizer，把这段转写稿做成公众号、X Article、小红书和网站审核包。
ts /path/to/recording.wav
ts 今天的录音（录音目录：/path/to/recordings）
继续处理 /path/to/run，只更新公众号版。
审核通过，把这篇放入公众号草稿箱。
```

TRIM/t 默认生成审核包；TS/ts 在宿主允许时并行制作。Quick/q、QS/qs 连贯执行已配置、已授权的渠道；不会自动替你公开发送社交内容。

## 配置与依赖

- 文本、状态、微信公众号及网站辅助脚本：Python 3.10+，使用标准库。
- 音频识别：另装 FFmpeg 和 `openai-whisper`；首次下载模型，之后在本地识别。
- 生图：使用宿主已经提供的生图能力，没有时明确交付缺项，不假装完成。
- 浏览器草稿：需要宿主浏览器工具、用户登录和平台权限，本包不带 cookie 或浏览器 profile。
- 网站：默认 Astro/Markdown 内容站，按站点调整目录和构建命令。

复制 [配置样例](article-optimizer/assets/env.example) 到私有位置（例如 `~/.config/article-optimizer/publisher.env`），填写自己需要的渠道。作者、站点、账号都可留空；不用替换 skill 正文中的姓名。带空格的值必须保留引号。

## 本次升级

- 从三平台改写和图片 prompt 扩展到录音输入、原始稿保护、实际图片和四平台审核包。
- 加入当天录音排序、原始稿 hash、缺项校验、网站干净工作副本与单渠道恢复规则。
- X 默认封面加富文本；正文图自动插入为实验能力，必须重开草稿验证。未打包此前持久保存不稳定的浏览器脚本。
- 使用标准 `SKILL.md` 文件名；通用安装器支持 Claude Code、Codex、定制目录和升级备份。
- 移除模板署名、个人画像、账号邮箱、本机路径与私有网络设置。保留本仓库 URL 用于安装；历史 Git 提交作者和仓库所有者不属于技能配置，本次没有重写历史。

## 能力边界

审核包制作与本地文件验证可直接使用。微信需有效官方 API 凭据；网站推送需用户配置仓库。X 与小红书采用宿主浏览器操作规范，不承诺无人值守发布。辅助脚本通过离线验证，不代表任何使用者的线上账号已经配置成功。

维护者可运行：

```bash
python3 bin/check_public.py
python3 -m unittest discover -s tests
node --test tests/install.test.js
```

扫描器只报告文件、行号与规则，不打印命中的敏感值。要检查特定姓名或标识，使用本机环境变量 `PUBLIC_FORBIDDEN_TERMS`（逗号分隔），不要提交真实列表。

## 开源协议

MIT，见 [LICENSE](LICENSE)。

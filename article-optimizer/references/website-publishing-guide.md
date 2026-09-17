# 个人网站发布指南

目标：用户审核并明确确认发布到个人网站后，把文章写入用户自己的静态站仓库。站点路径、域名、作者名、Git remote 和分支都必须来自环境变量或命令参数。

## 前置条件

- `<主题>_审核版.md` 已交给用户审核。
- 用户已确认文字、图片、信息图和标题可用于网站。
- 用户明确要求同步网站；不要在审核阶段自动 commit 或 push。
- `ARTICLE_SITE_ROOT` 指向网站仓库。

## 推荐站点结构

默认按 Astro 或 Markdown content collection 处理，可用环境变量覆盖：

```bash
ARTICLE_SITE_ROOT=/absolute/path/to/website-repo
ARTICLE_SITE_PUBLIC_URL=https://your-domain.example
ARTICLE_SITE_AUTHOR="Your Name"
ARTICLE_SITE_BLOG_DIR=src/content/blog
ARTICLE_SITE_COVERS_DIR=public/covers
ARTICLE_SITE_IMAGES_DIR=public/article-images
ARTICLE_SITE_REMOTE=origin
ARTICLE_SITE_BRANCH=main
ARTICLE_SITE_NPM=npm
```

生成的 Markdown frontmatter：

```yaml
---
title: "文章标题"
date: 2026-06-14
author: "Your Name"
digest: "一句摘要"
cover: "/covers/cover-hash.png"
tags:
  - "AI"
draft: false
---
```

正文图片使用站点绝对路径：

```markdown
![段落配图 01](/article-images/image-hash.png)
![信息图](/article-images/image-hash.png)
```

## 执行脚本

使用本技能脚本：

```bash
python3 "$SKILL_DIR/scripts/website_publish.py" \
  --title "网站文章标题" \
  --content /path/to/主题_网站版.md \
  --cover /path/to/主题_封面图.png \
  --date 2026-06-14 \
  --site-root "$ARTICLE_SITE_ROOT"
```

测试不推送：

```bash
python3 "$SKILL_DIR/scripts/website_publish.py" \
  --title "网站文章标题" \
  --content /path/to/主题_网站版.md \
  --cover /path/to/主题_封面图.png \
  --no-push
```

脚本职责：

1. 清理 Markdown 中的平台痕迹：首个 `# 标题`、平台 byline、平台尾巴、重复封面图。
2. 复制封面图到站点封面目录，以内容 hash 命名。
3. 复制正文配图和信息图到站点正文图片目录，并替换 Markdown 图片路径。
4. 写入文章 Markdown 和 frontmatter。
5. 可选运行 `npm run build`。
6. 可选只提交并推送本次写入的文章和图片。

## 失败处理

- `git pull --ff-only` 失败：说明本地分支和远端分叉，需要人工处理，不要强推。
- 构建失败：先修 frontmatter、Markdown 或图片路径，再提交。
- push 失败：报告网络、权限或认证问题；不要改 remote token，也不要输出 token。
- 托管平台构建失败：以 Git 推送成功为边界，再查对应平台构建日志。

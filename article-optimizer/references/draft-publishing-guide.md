# 草稿与网站同步

只操作用户已授权的渠道。附带 Python 辅助脚本独立可用，不依赖原作者的工作区、路由器或统一发布入口。

配置样例在技能内 `assets/env.example`。副本存到技能目录以外的私有位置；不在聊天里粘贴密钥。POSIX shell 可加载：

```bash
set -a
source "$HOME/.config/article-optimizer/publisher.env"
set +a
```

## 微信公众号

```bash
python3 "$SKILL_DIR/scripts/wechat_official_draft.py" \
  --html /path/to/主题_公众号排版.html --cover /path/to/主题_封面图.png
```

需要 AppID、AppSecret 和对应账号权限。执行前检查 inline HTML 和图片，草稿成功后记录 media id，不群发。配置 IP 白名单时按自己的网络设置 `WECHAT_HTTPS_PROXY`；错误只恢复微信渠道，不修改系统代理和路由器。输出不包含凭据。

## X Article

本包提供 [浏览器操作和持久化规范](x-article-format-guide.md)，不附带承诺稳定的 X 自动化脚本。使用宿主浏览器工具：先确认封面，再粘贴富文本，保存并重开同一草稿核验。无浏览器工具时交付文件和手动步骤，不宣称草稿已创建。

## 网站

```bash
python3 "$SKILL_DIR/scripts/website_publish.py" \
  --title "文章标题" --content /path/to/主题_网站版.md \
  --cover /path/to/主题_封面图.png --site-root "$ARTICLE_SITE_ROOT"
```

默认写文件并构建，增加 `--push` 才提交推送。默认布局适合 Astro/Markdown 内容站，其他站点用参数适配，见 [网站指南](website-publishing-guide.md)。推送要求干净工作副本，构建失败不推送。push 结果不明先检查远端，不重复创建文章。

## 小红书和结果

默认交付文案、短版和发图顺序。用户选择自动化时才尝试草稿；登录/验证码交用户处理。

`social-publish-status.json` 按渠道记录 `not_requested`、`files_ready`、`draft_saved_verified`、`pushed` 或 `needs_manual_review`，含本次时间、URL/ID 和核验范围。失败时保留其他渠道已成功结果；这些运行状态、来源、账号和凭据都不进入公开 skill。

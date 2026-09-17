# 微信公众号排版指南

目标：生成一个可以预览、可以复制进微信公众号编辑器、也可以被官方 API 入库的 HTML 文件。格式必须稳定，正文必须全 inline style。

## 兼容性硬规则

- 正文区域只使用 `<section>`、`<span>`、`<strong>`、`<em>`、`<img>` 等简单标签。
- 所有样式写在 `style="..."` 里。
- 不使用 `<style>`、`<script>`、`class`、`id`、`position`、复杂 flex/grid、`<ul>/<ol>/<li>`、`<hr>`。
- 不使用 `<p>` 包正文段落；统一用 `<section>`，避免微信编辑器默认间距和缩进。
- 不依赖外层网页壳。预览文件可以有 `<html><head><body>`，但入库或复制的正文片段必须能独立成立。
- `<title>` 必须是真实文章标题，不能是“公众号文章预览”“微信预览”等壳标题。
- 公众号已有标题、作者和日期区域，正文里不要重复文章标题、账号名、作者日期或复制提示。

## HTML 文件骨架

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>正式文章标题</title>
</head>
<body style="margin:0; padding:0; background:#ffffff;">
  <!-- 文章正文开始：复制或入库时只保留这个 section 里面的内容 -->
  <section style="margin:0 auto; padding:0; max-width:677px; background:#ffffff; color:#1f2933; line-height:1.8;">
    <!-- 封面图 -->
    <section style="margin:0 0 24px 0; padding:0;">
      <img src="./主题_封面图.png" alt="封面图" style="display:block; width:100%; height:auto; margin:0 auto;">
    </section>

    <!-- 导语 -->
    <section style="margin:0 24px 22px 24px; padding:0; font-size:16px; color:#2b2f33; line-height:1.9;">
      导语正文。
    </section>

    <!-- 小标题 -->
    <section style="margin:34px 24px 16px 24px; padding:0; line-height:1.5;">
      <span style="display:inline-block; vertical-align:middle; background-color:#2563eb; color:#ffffff; font-size:12px; line-height:1.6; padding:2px 8px; font-weight:bold; letter-spacing:1px; margin-right:10px;">01</span>
      <span style="display:inline-block; vertical-align:middle; font-size:20px; font-weight:bold; color:#111827; line-height:1.5;">小标题</span>
    </section>

    <!-- 正文段落 -->
    <section style="margin:0 24px 18px 24px; padding:0; font-size:16px; color:#2b2f33; line-height:1.9;">
      正文段落。需要强调时用 <strong style="font-weight:bold; color:#111827;">加粗文字</strong>。
    </section>
  </section>
</body>
</html>
```

## 主题色与版式

不要固定套一种颜色模板。先判断文章内容和情绪，再选择主题色：

- 工具、流程、效率类：蓝、青、灰绿等冷静色。
- 个人成长、生活方式类：绿、暖黄、珊瑚等柔和色。
- 财经、决策、风险类：深蓝、墨绿、金色点缀等克制色。
- 科技、AI、产品类：蓝、紫、青可用，但不要整篇只有一个紫蓝渐变。

主题色要和封面图、段落配图、信息图保持一致。总览 Markdown 中写明「公众号排版风格」和主题色选择理由。

## 图片插入

- 封面图放在正文最前面、导语之前。
- 段落配图放在对应小节后，服务该小节理解。
- 信息图放在最后一个正文小节之后、文末金句/END/关注引导之前。
- 预览阶段可使用本地相对路径，例如 `./主题_段落配图_01.png`。
- 入公众号草稿前，脚本应把本地图片上传到微信素材接口并替换为微信图片 URL。
- 图片 `alt` 写清楚用途，例如 `段落配图 01`、`信息图`。

图片 HTML：

```html
<section style="margin:24px 24px 26px 24px; padding:0;">
  <img src="./主题_段落配图_01.png" alt="段落配图 01" style="display:block; width:100%; height:auto; margin:0 auto;">
</section>
```

## 信息图

信息图默认是公众号文末总结长图，不是抽象装饰图。它应包含：

- 大标题和副标题。
- 3-5 个编号分区，分区数量必须覆盖正文主要小节。
- 清晰图标、物件或流程示意。
- 底部结论条。

信息图不要放二维码、头像、账号徽标、关注引导或社交 handle。作者署名如需出现，应从环境变量或用户输入读取，不能硬编码。

## 发布前 DOM 自检

创建微信公众号草稿前，必须检查：

- HTML `<title>` 是正式文章标题。
- 正文不含 `<p>`、`<main>`、`<script>`、`<style>`。
- 正文不重复文章标题。
- 图片路径全部可访问或可上传。
- 信息图在最后一个正文小节之后。
- 入库正文是 article fragment，不是整页预览壳。

默认不要生成“公众号排版预览.png”；只有排查错位时才保存临时 debug 截图。

# 微信公众号排版指南

## 目的

将微信公众号版的 Markdown 内容转换为一个排版精美的 HTML artifact，用户可以预览，也可以在浏览器中打开后复制粘贴到微信公众号编辑器，格式完整保留。

## 微信公众号 HTML 兼容性规则

微信编辑器对 HTML/CSS 有严格限制，生成的 HTML 必须遵守以下规则：

### 必须做的
- 所有样式写成 inline style（`style="..."`），这是微信唯一可靠支持的方式
- 使用 `<section>` 作为主要容器标签
- 使用 `<span>`、`<strong>`、`<em>`、`<br>` 等基础标签
- 图片用 `<img style="max-width: 100%; height: auto;">`
- 正文使用 `text-align: justify`（两端对齐），提高整洁度

### 绝对不能做的
- 不用 `<style>` 标签——微信会删除
- 不用 `<script>` 标签——微信会删除
- 不用 CSS class 或 id——微信会删除 id，class 不生效
- 不用 `<a>` 标签——微信正文中链接会被过滤
- 不用 `position` 属性——微信会删掉
- 不用 `border-radius`——微信支持不稳定
- 不用 `<ul>`/`<ol>`/`<li>`——微信渲染不一致，改用卡片式段落或带编号的段落代替
- 不用 `<hr>`——微信渲染不一致，用装饰元素模拟
- 不用 `<header>`/`<footer>`/`<nav>`/`<article>`/`<div>` 等标签——用 `<section>` 替代
- 不用外部字体、外链资源
- 不用 `<p>` 标签——统一用 `<section>` 包裹段落，避免微信对 p 标签的默认间距干扰

### 关于 linear-gradient
微信公众号对 `background: linear-gradient(...)` 的支持**不稳定**——在部分安卓机型上不生效。在以下场景中处理：
- 标题区域渐变背景：保留使用，因为即使不生效也会 fallback 到白色背景，不会破坏布局
- 文字高亮效果（荧光笔底色）：保留使用，因为即使不生效文字仍然加粗可读，只是少了底色装饰

不要在关键布局元素上依赖 gradient，只在装饰性元素上使用。

## 设计风格

**有特点但舒服**——在简约的基础上加入精致的设计细节：编号色块小标题、荧光笔高亮、大号引号装饰、卡片式列表。保持大量留白和清晰的层次感，装饰元素有节制，不花哨。

## 配色方案

- 主题色：`#3d7de0`（明亮蓝，用于编号色块、引用边框、高亮底色、关注引导文字等）
- 主题色浅：`#a8c8f0`（装饰圆点中色）
- 主题色最浅：`#d4e4f7`（装饰圆点浅色、大号引号颜色）
- 高亮底色：`#dbeafe`（荧光笔效果的底色）
- 正文色：`#3d3d3d`
- 标题色：`#1a1a1a`
- 引用/辅助文字色：`#777777`
- 次要信息色：`#aaaaaa`
- 淡次要信息色：`#b0b0b0`
- 卡片/引用块背景：`#f8f9fb`
- 细分隔线色：`#f0f0f0`

如果文章主题明显偏向某个调性，可以微调主题色系（如暖色调用 `#e07d3d` 系），但要同步调整浅色和高亮色保持和谐。

## 字体规范

微信环境下字体由系统决定，不指定 font-family。

| 元素 | font-size | line-height | color | 其他 |
|------|-----------|-------------|-------|------|
| 公众号名（标题区顶部） | 13px | — | #b0b0b0 | letter-spacing: 3px |
| 文章大标题 | 24px | 1.5 | #1a1a1a | font-weight: bold; letter-spacing: 1px; 居中 |
| 作者与日期 | 14px | 1.6 | #aaaaaa | |
| 首段引言 | 19px | 2.0 | #555555 | 底部带细线分隔 |
| 正文段落 | 17px | 2.0 | #3d3d3d | text-align: justify |
| 小标题编号 | 13px | 1.8 | #ffffff | 蓝色背景色块内 |
| 小标题文字 | 20px | 1.5 | #1a1a1a | font-weight: bold |
| 引用文字 | 16px | 1.9 | #777777 | text-align: justify |
| 引号装饰 | 40px | 1 | #d4e4f7 | font-weight: bold |
| 列表项文字 | 17px | 1.8 | #3d3d3d | 卡片内 |
| 结尾金句 | 18px | 1.9 | #1a1a1a | font-weight: bold; letter-spacing: 0.5px; 居中 |
| 金句副文字 | 14px | — | #aaaaaa | |
| END 文字 | 14px | — | #aaaaaa | letter-spacing: 2px |
| 关注引导 | 17px | — | #3d7de0 | font-weight: bold |

## HTML 结构模板

生成的 HTML 是一个完整网页（用于 artifact 预览），内部文章区域全部用 section + inline style（用于复制到微信）。

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>公众号文章预览</title>
  <style>
    /* 仅用于预览容器，不会被复制到微信 */
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      background-color: #f0f0f0;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 20px 0;
    }
    .preview-wrapper {
      max-width: 580px;
      width: 100%;
      background: #ffffff;
      box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    }
    .copy-tip {
      text-align: center;
      padding: 12px 16px;
      background-color: #2C2C2C;
      color: #ffffff;
      font-size: 13px;
      line-height: 1.5;
      position: sticky;
      top: 0;
      z-index: 100;
      letter-spacing: 0.5px;
    }
  </style>
</head>
<body>
  <div class="preview-wrapper">
    <div class="copy-tip">💡 选中下方文章内容 → 复制 → 粘贴到微信公众号编辑器</div>
    <!-- ====== 文章内容开始（复制这部分） ====== -->
    <section style="padding: 0; background-color: #ffffff;">

      {{标题区域}}
      {{首段引言}}
      {{正文内容}}
      {{文末装饰}}
      {{关注引导卡片}}

    </section>
    <!-- ====== 文章内容结束 ====== -->
  </div>
</body>
</html>
```

## 各区域的具体 HTML

### 1. 标题区域

渐变背景 + 公众号名 + 标题 + 三圆点装饰 + 作者日期。

公众号名固定「{{YOUR_ACCOUNT_NAME}}」，作者名「{{YOUR_NAME}}」，日期取当天。

```html
<section style="background: linear-gradient(180deg, #f0f4f8 0%, #ffffff 100%); padding: 40px 24px 30px 24px; text-align: center;">
  <!-- 公众号名 -->
  <section style="font-size: 13px; color: #b0b0b0; letter-spacing: 3px; margin-bottom: 20px;">
    {{YOUR_ACCOUNT_NAME}}
  </section>
  <!-- 标题 -->
  <section style="font-size: 24px; font-weight: bold; color: #1a1a1a; line-height: 1.5; letter-spacing: 1px; padding: 0 10px;">
    {{文章标题}}
  </section>
  <!-- 三圆点装饰 -->
  <section style="margin: 20px auto 0 auto; text-align: center;">
    <span style="display: inline-block; width: 6px; height: 6px; background-color: #3d7de0; margin: 0 4px;"></span>
    <span style="display: inline-block; width: 6px; height: 6px; background-color: #a8c8f0; margin: 0 4px;"></span>
    <span style="display: inline-block; width: 6px; height: 6px; background-color: #d4e4f7; margin: 0 4px;"></span>
  </section>
  <!-- 作者与日期 -->
  <section style="margin-top: 16px; font-size: 14px; color: #aaaaaa; line-height: 1.6;">
    {{YOUR_NAME}} · {{YYYY年M月D日}}
  </section>
</section>
```

### 2. 首段引言

文章的第一个段落，字号稍大，底部细线分隔，营造"引言"的感觉。

```html
<section style="font-size: 19px; color: #555555; line-height: 2.0; margin: 30px 24px 25px 24px; padding: 20px 0; border-bottom: 1px solid #f0f0f0;">
  {{第一段内容}}
</section>
```

注意：只有第一段用这个样式。后续段落用普通正文样式。

### 3. 正文内容

逐段转换 Markdown 内容。

**普通段落：**
```html
<section style="font-size: 17px; color: #3d3d3d; line-height: 2.0; margin-bottom: 20px; padding: 0 24px; text-align: justify;">
  段落文字...
</section>
```

**加粗重点文字（荧光笔高亮）：**

对应 Markdown 中的 `**加粗文字**`，使用蓝色底色高亮效果：
```html
<strong style="color: #1a1a1a; background: linear-gradient(180deg, transparent 60%, #dbeafe 60%); padding: 0 2px;">重点文字</strong>
```

**小标题（对应 ## 或 ###）：**

使用编号色块 + 标题文字的组合。编号从 01 开始递增。

```html
<section style="margin: 35px 24px 18px 24px; display: flex; display: -webkit-flex;">
  <section style="display: inline-block; background-color: #3d7de0; color: #ffffff; font-size: 13px; padding: 4px 10px; font-weight: bold; letter-spacing: 1px; margin-right: 12px; line-height: 1.8; white-space: nowrap;">
    01
  </section>
  <section style="display: inline-block; font-size: 20px; font-weight: bold; color: #1a1a1a; line-height: 1.5; padding-top: 1px;">
    小标题文字
  </section>
</section>
```

**引用块（对应 > 内容）：**

大号引号装饰 + 浅灰背景 + 蓝色左边框。

```html
<section style="margin: 20px 24px 25px 24px; padding: 25px 24px 20px 24px; background-color: #f8f9fb; border-left: 3px solid #3d7de0;">
  <section style="font-size: 40px; color: #d4e4f7; line-height: 1; margin-bottom: 8px; font-weight: bold;">
    "
  </section>
  <section style="font-size: 16px; color: #777777; line-height: 1.9; text-align: justify;">
    引用内容...
  </section>
</section>
```

**列表项（对应 - 或 * 列表）：**

每项独立一个浅灰卡片，带蓝色编号。编号用带圈数字 ①②③ 或普通数字。

```html
<section style="margin: 10px 24px 10px 24px; padding: 14px 18px; background-color: #f8f9fb; font-size: 17px; color: #3d3d3d; line-height: 1.8;">
  <span style="color: #3d7de0; font-weight: bold; margin-right: 8px;">①</span>列表项内容
</section>
```

最后一个列表项 margin-bottom 改为 20px。

**结尾金句（文章最后一段如果是总结性的有力句子）：**

居中显示，上下细线框住。可选——如果文章末尾没有明显的金句，就用普通段落结尾。

```html
<section style="margin: 30px 24px 20px 24px; padding: 20px; text-align: center; border-top: 1px solid #f0f0f0; border-bottom: 1px solid #f0f0f0;">
  <section style="font-size: 18px; color: #1a1a1a; line-height: 1.9; font-weight: bold; letter-spacing: 0.5px;">
    金句内容，如果太长可以用 <br> 手动换行
  </section>
  <section style="font-size: 14px; color: #aaaaaa; margin-top: 8px;">
    可选的补充说明
  </section>
</section>
```

**正文中的分隔（对应 Markdown 的 ---）：**

用三圆点装饰代替线条：
```html
<section style="text-align: center; margin: 30px 0;">
  <span style="display: inline-block; width: 6px; height: 6px; background-color: #3d7de0; margin: 0 4px;"></span>
  <span style="display: inline-block; width: 6px; height: 6px; background-color: #a8c8f0; margin: 0 4px;"></span>
  <span style="display: inline-block; width: 6px; height: 6px; background-color: #d4e4f7; margin: 0 4px;"></span>
</section>
```

### 4. 文末装饰

同上三圆点，margin 略大：
```html
<section style="text-align: center; margin: 35px 0 30px 0;">
  <span style="display: inline-block; width: 6px; height: 6px; background-color: #3d7de0; margin: 0 4px;"></span>
  <span style="display: inline-block; width: 6px; height: 6px; background-color: #a8c8f0; margin: 0 4px;"></span>
  <span style="display: inline-block; width: 6px; height: 6px; background-color: #d4e4f7; margin: 0 4px;"></span>
</section>
```

### 5. 关注引导卡片

```html
<section style="margin: 0 24px 40px 24px; padding: 24px; background-color: #f8f9fb; text-align: center;">
  <section style="font-size: 14px; color: #aaaaaa; letter-spacing: 2px; margin-bottom: 10px;">
    — END —
  </section>
  <section style="font-size: 15px; color: #777777; line-height: 1.8;">
    感谢阅读，如果觉得有启发
  </section>
  <section style="font-size: 17px; color: #3d7de0; font-weight: bold; margin-top: 6px; letter-spacing: 0.5px;">
    欢迎关注「{{YOUR_ACCOUNT_NAME}}」
  </section>
</section>
```

## Markdown → HTML 转换规则

解析微信公众号版的 Markdown 内容时：

1. `### 标题：XXX` → 提取 XXX 作为文章大标题
2. `## 小标题` 或 `### 小标题`（非"标题："和"配图 Prompt"） → 编号色块小标题，编号从 01 递增
3. 文章第一个段落 → 首段引言样式（17px，底部细线）
4. `> 引用内容` → 大号引号引用块
5. `**加粗**` → 荧光笔高亮 `<strong>` 标签
6. `*斜体*` → `<em>斜体</em>`
7. `---` → 三圆点装饰分隔
8. `- 列表项` 或 `* 列表项` → 卡片式列表，带 ①②③ 编号
9. 有序列表 `1. 内容` → 同上卡片式，编号直接用数字
10. `![alt](url)` → `<img>` 标签，提醒用户需替换为微信素材库链接
11. 空行分隔的连续文字 → 独立段落
12. 段落内的换行 → `<br>`
13. 文章末尾如果有一句明显的总结性金句（通常加粗），可以使用结尾金句样式

## 判断结尾金句

如果文章最后一个段落满足以下条件之一，使用结尾金句样式：
- 整段加粗（`**整段都加粗了**`）
- 是一句简短有力的总结（通常不超过两行）
- 带有明显的观点输出或情感收束

如果最后一段是普通的收尾叙述，就用普通段落样式，不强制使用金句样式。

## 重要提醒

- **绝对不要修改文章内容**——只做排版，一个字都不改
- **日期自动生成**——取当天日期
- **图片提醒**——如果原文有图片链接，保留 img 标签但提醒用户需要手动上传到微信素材库
- **编号连续性**——小标题的编号（01、02、03...）要全文连续递增
- **列表编号**——无序列表统一用 ①②③，有序列表用原文的数字
- **padding 统一**——正文区域左右 padding 统一为 24px，保持对齐
- **不要过度使用金句样式**——一篇文章最多一处，通常在结尾

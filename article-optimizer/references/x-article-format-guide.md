# X Article 排版指南

## 目的

将微信公众号版的完整内容转换为一个适合 X（推特）Article 长文功能的排版 HTML 文件。用户可以预览，也可以在浏览器中打开后复制粘贴到 X Article 编辑器。

## 设计风格

**简洁、现代、高信息密度**——对齐 X 平台的视觉语言。大量留白，强调文字层次，无多余装饰。配色以深灰文字 + 蓝色强调为主，背景纯白。

## 配色方案

- 主文字色：`#0f1419`（X 平台标准深色）
- 次要文字色：`#536471`（X 平台灰色）
- 辅助信息色：`#8899a6`（日期、署名等）
- 强调色/链接色：`#1d9bf0`（X 蓝）
- 分隔元素色：`#ccd6dd`
- 引用块背景：`#f7f9fa`
- 页面背景（预览用）：`#f7f7f7`

## 字体规范

不指定 font-family，由系统决定。

| 元素 | font-size | line-height | color | 其他 |
|------|-----------|-------------|-------|------|
| 文章大标题 | 30px | 1.4 | #0f1419 | font-weight: 800; letter-spacing: -0.3px |
| 作者与日期 | 16px | 1.5 | #8899a6 | |
| 导语（Lede） | 21px | 1.9 | #536471 | font-style: italic |
| 正文段落 | 19px | 2.0 | #0f1419 | |
| 小标题（H2） | 24px | 1.4 | #0f1419 | font-weight: 700; 底部蓝色边框 |
| 加粗文字 | 19px | — | #0f1419 | font-weight: bold（不使用荧光笔，保持简洁） |
| 引用文字 | 19px | 1.9 | #536471 | font-style: italic |
| 结尾金句 | 20px | 1.8 | #0f1419 | font-weight: 700; 居中 |
| 署名 | 15px | — | #8899a6 | |

## HTML 结构模板

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>X Article 预览</title>
  <style>
    /* 仅用于预览容器 */
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      background-color: #f7f7f7;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 20px 0;
    }
    .preview-wrapper {
      max-width: 620px;
      width: 100%;
      background: #ffffff;
      box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }
    .copy-tip {
      text-align: center;
      padding: 12px 16px;
      background-color: #1a1a1a;
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
    <div class="copy-tip">💡 选中下方文章内容 → 复制 → 粘贴到 X Article 编辑器</div>
    <section style="padding: 0; background-color: #ffffff;">

      {{标题区域}}
      {{导语}}
      {{正文内容}}
      {{结尾}}

    </section>
  </div>
</body>
</html>
```

## 各区域的具体 HTML

### 1. 标题区域

简洁大气，底部细线分隔。作者署名用 @薛衡Henry，日期用英文格式（如 Mar 28, 2026）。

```html
<section style="padding: 48px 32px 36px 32px; border-bottom: 1px solid #eee;">
  <section style="font-size: 30px; font-weight: 800; color: #0f1419; line-height: 1.4; letter-spacing: -0.3px;">
    {{文章标题}}
  </section>
  <section style="margin-top: 16px; font-size: 16px; color: #8899a6; line-height: 1.5;">
    薛衡 · {{Mon DD, YYYY}}
  </section>
</section>
```

### 2. 导语（Lede）

从文章中提炼 1-2 句核心观点作为导语，斜体灰色，与正文形成层次区分。

```html
<section style="padding: 32px 32px 0 32px;">
  <section style="font-size: 21px; color: #536471; line-height: 1.9; font-style: italic;">
    {{导语内容}}
  </section>
</section>
```

### 3. 三点分隔

```html
<section style="text-align: center; margin: 32px 0;">
  <span style="display: inline-block; width: 4px; height: 4px; background-color: #ccd6dd; margin: 0 6px;"></span>
  <span style="display: inline-block; width: 4px; height: 4px; background-color: #ccd6dd; margin: 0 6px;"></span>
  <span style="display: inline-block; width: 4px; height: 4px; background-color: #ccd6dd; margin: 0 6px;"></span>
</section>
```

### 4. 正文内容

所有正文内容包裹在 `padding: 0 32px` 的容器中。

**普通段落：**
```html
<section style="font-size: 19px; color: #0f1419; line-height: 2.0; margin-bottom: 24px;">
  段落文字...
</section>
```

**小标题（H2）：**

使用蓝色下边框，干净利落。

```html
<section style="font-size: 24px; font-weight: 700; color: #0f1419; line-height: 1.4; margin: 40px 0 20px 0; padding-bottom: 8px; border-bottom: 2px solid #1d9bf0;">
  小标题文字
</section>
```

**加粗文字：**

简洁加粗，不使用荧光笔效果。

```html
<strong style="color: #0f1419;">重点文字</strong>
```

**引用块：**

蓝色左边框 + 浅灰背景，斜体。

```html
<section style="margin: 28px 0; padding: 20px 24px; border-left: 3px solid #1d9bf0; background-color: #f7f9fa;">
  <section style="font-size: 19px; color: #536471; line-height: 1.9; font-style: italic;">
    引用内容...
  </section>
</section>
```

### 5. 结尾

金句居中 + 署名。

```html
<section style="padding: 0 32px 48px 32px; text-align: center;">
  <section style="font-size: 20px; color: #0f1419; line-height: 1.8; font-weight: 700;">
    金句内容，可用 <br> 换行
  </section>
  <section style="margin-top: 20px; font-size: 15px; color: #8899a6;">
    @薛衡Henry
  </section>
</section>
```

## 内容转换规则

使用微信公众号版的完整内容，转换时：

1. 标题直接使用公众号版标题
2. 从文章中提炼 1-2 句导语（Lede），放在标题和正文之间
3. 公众号版的小标题 → H2 蓝色下划线标题
4. 公众号版的加粗 → 简洁加粗（不用荧光笔）
5. 公众号版的引用 → 蓝色左边框引用块
6. 公众号版的结尾金句 → 居中金句
7. 结尾互动语改为适合 X 平台的表达（如"欢迎在评论区和我聊聊"）
8. 不使用编号色块（这是公众号风格），小标题用纯文字 + 蓝色下划线

## 重要提醒

- **内容与公众号版完全一致**——只改排版风格，不改文字
- **日期格式**：英文月份缩写 + 日 + 年，如 Mar 28, 2026
- **署名格式**：@薛衡Henry
- **整体风格**：比公众号更简洁、更现代，减少装饰性元素
- **padding 统一**：正文区域左右 padding 为 32px

# 小红书长文排版指南

## 目的

将微信公众号版的完整内容转换为一个适合小红书长文笔记的排版 HTML 文件。用户可以预览，也可以在浏览器中打开后复制粘贴到小红书笔记编辑器。

## 设计风格

**温暖、干净、手机优先**——模拟小红书 App 的阅读体验。窄屏排版，段落简短，行距宽松，适合拇指滑动阅读。不使用 emoji，不使用话题标签，保持文字本身的质感。

## 配色方案

- 主文字色：`#333333`
- 标题色：`#222222`
- 辅助信息色：`#b2b2b2`
- 强调色/引用边框：`#ff2442`（小红书红）
- 引用块背景：`#fafafa`
- 分隔线色：`#f0f0f0`
- 引用文字色：`#666666`
- 页面背景（预览用）：`#f5f5f5`

## 字体规范

不指定 font-family，由系统决定。

| 元素 | font-size | line-height | color | 其他 |
|------|-----------|-------------|-------|------|
| 文章标题 | 24px | 1.5 | #222222 | font-weight: bold; letter-spacing: 0.5px |
| 作者与日期 | 14px | — | #b2b2b2 | |
| 正文段落 | 18px | 2.1 | #333333 | |
| 小标题 | 20px | 1.5 | #222222 | font-weight: bold; 用「」包裹 |
| 引用文字 | 17px | 2.0 | #666666 | font-style: italic |
| 结尾金句 | 18px | 1.9 | #222222 | font-weight: bold; 居中 |
| 结尾提示 | 14px | 1.6 | #b2b2b2 | |

## HTML 结构模板

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>小红书长文预览</title>
  <style>
    /* 仅用于预览容器 */
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      background-color: #f5f5f5;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 20px 0;
    }
    .preview-wrapper {
      max-width: 420px;
      width: 100%;
      background: #ffffff;
      box-shadow: 0 1px 6px rgba(0,0,0,0.08);
    }
    .copy-tip {
      text-align: center;
      padding: 12px 16px;
      background-color: #ff2442;
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
    <div class="copy-tip">💡 选中下方内容 → 复制 → 粘贴到小红书笔记编辑器</div>
    <section style="padding: 0; background-color: #ffffff;">

      {{标题区域}}
      {{正文内容}}
      {{结尾}}

    </section>
  </div>
</body>
</html>
```

## 各区域的具体 HTML

### 1. 标题区域

简洁标题 + 作者日期，底部细线分隔。日期用 YYYY.MM.DD 格式。

```html
<section style="padding: 32px 20px 24px 20px;">
  <section style="font-size: 24px; font-weight: bold; color: #222222; line-height: 1.5; letter-spacing: 0.5px;">
    {{文章标题}}
  </section>
  <section style="margin-top: 12px; font-size: 14px; color: #b2b2b2;">
    薛衡 · {{YYYY.MM.DD}}
  </section>
</section>
<section style="margin: 0 20px; border-top: 1px solid #f0f0f0;"></section>
```

### 2. 正文内容

所有正文包裹在 `padding: 24px 20px 0 20px` 的容器中。

**普通段落：**
```html
<section style="font-size: 18px; color: #333333; line-height: 2.1; margin-bottom: 22px;">
  段落文字...
</section>
```

**小标题：**

用「」书名号包裹，加粗，无其他装饰。保持干净。

```html
<section style="margin: 30px 0 16px 0; font-size: 20px; font-weight: bold; color: #222222; line-height: 1.5;">
  「小标题文字」
</section>
```

**加粗文字：**

直接加粗，不使用荧光笔或其他装饰。

```html
<strong style="color: #222222;">重点文字</strong>
```

**引用卡片：**

小红书红色左边框 + 浅灰背景，斜体。

```html
<section style="margin: 16px 0 22px 0; padding: 18px 16px; background-color: #fafafa; border-left: 3px solid #ff2442;">
  <section style="font-size: 17px; color: #666666; line-height: 2.0; font-style: italic;">
    引用内容...
  </section>
</section>
```

### 3. 结尾分隔

用三条短横线，低调分隔。

```html
<section style="text-align: center; margin: 24px 0;">
  <span style="display: inline-block; width: 24px; height: 1px; background-color: #e0e0e0; margin: 0 8px;"></span>
  <span style="display: inline-block; width: 24px; height: 1px; background-color: #e0e0e0; margin: 0 8px;"></span>
  <span style="display: inline-block; width: 24px; height: 1px; background-color: #e0e0e0; margin: 0 8px;"></span>
</section>
```

### 4. 结尾

金句居中 + 互动引导。

```html
<section style="padding: 0 20px 36px 20px; text-align: center;">
  <section style="font-size: 18px; color: #222222; line-height: 1.9; font-weight: bold;">
    金句内容，可用 <br> 换行
  </section>
  <section style="margin-top: 16px; font-size: 14px; color: #b2b2b2; line-height: 1.6;">
    如果你对此有任何感想，欢迎在评论区和我聊聊
  </section>
</section>
```

## 内容转换规则

使用微信公众号版的完整内容，转换时：

1. 标题直接使用公众号版标题
2. 不需要导语/引言区分——直接进入正文（第一段不做特殊样式处理）
3. 公众号版的编号色块小标题 → 用「」包裹的纯文字加粗标题
4. 公众号版的加粗/荧光笔 → 简洁加粗
5. 公众号版的引用块 → 红色左边框引用卡片
6. 公众号版的结尾金句 → 居中加粗金句
7. 英文专业术语可以适当去掉括号注释，保持阅读流畅（如 newsletter 不需要加"通讯"注释，但 compact 可以保留"压缩"注释）
8. 不使用编号（01、02...），小标题用「」即可

## 重要提醒

- **内容与公众号版完全一致**——只改排版风格，不改文字
- **预览宽度 420px**——模拟手机屏幕
- **不使用 emoji**——小红书长文保持文字质感
- **不使用话题标签**——标签由用户自己在小红书编辑器中添加
- **日期格式**：YYYY.MM.DD，如 2026.03.28
- **padding 统一**：正文区域左右 padding 为 20px（比公众号和 X 更窄，适配手机）
- **行距宽松**：正文 line-height: 2.1，比公众号（2.0）稍宽，适合手机滑动阅读
- **段间距紧凑**：margin-bottom: 22px，比公众号略小，让内容更紧凑

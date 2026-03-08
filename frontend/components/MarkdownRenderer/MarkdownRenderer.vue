<template>
  <view class="markdown-renderer">
    <rich-text :nodes="renderedHtml"></rich-text>
  </view>
</template>

<script>
// 简单的 Markdown 解析器
class SimpleMarkdown {
  parse(markdown) {
    if (!markdown) return ''

    // 转义 HTML 特殊字符
    let html = this.escapeHtml(markdown)

    // 代码块 ```code```
    html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (match, lang, code) => {
      return `<pre><code class="language-${lang}">${this.escapeHtml(code)}</code></pre>`
    })

    // 行内代码 `code`
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>')

    // 标题 # H1 - ###### H6
    html = html.replace(/^######\s+(.*)$/gm, '<h6>$1</h6>')
    html = html.replace(/^#####\s+(.*)$/gm, '<h5>$1</h5>')
    html = html.replace(/^####\s+(.*)$/gm, '<h4>$1</h4>')
    html = html.replace(/^###\s+(.*)$/gm, '<h3>$1</h3>')
    html = html.replace(/^##\s+(.*)$/gm, '<h2>$1</h2>')
    html = html.replace(/^#\s+(.*)$/gm, '<h1>$1</h1>')

    // 粗体 **text**
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')

    // 斜体 *text*
    html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>')

    // 引用 > text
    html = html.replace(/^>\s+(.*)$/gm, '<blockquote>$1</blockquote>')

    // 无序列表 * item
    html = html.replace(/^\*\s+(.*)$/gm, '<li>$1</li>')
    html = html.replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>')

    // 有序列表 1. item
    html = html.replace(/^\d+\.\s+(.*)$/gm, '<li>$1</li>')

    // 链接 [text](url)
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>')

    // 换行
    html = html.replace(/\n\n/g, '</p><p>')
    html = `<p>${html}</p>`

    return html
  }

  escapeHtml(text) {
    const map = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#039;'
    }
    return text.replace(/[&<>"']/g, m => map[m])
  }
}

const markdownParser = new SimpleMarkdown()

export default {
  props: {
    content: {
      type: String,
      default: ''
    }
  },
  computed: {
    renderedHtml() {
      if (!this.content) return ''
      return markdownParser.parse(this.content)
    }
  }
}
</script>

<style lang="scss" scoped>
.markdown-renderer {
  line-height: 1.6;
  word-wrap: break-word;
  color: #333;

  :deep(h1) {
    font-size: 20px;
    font-weight: bold;
    margin: 12px 0 8px;
    color: #1a1a1a;
  }

  :deep(h2) {
    font-size: 18px;
    font-weight: bold;
    margin: 10px 0 6px;
    color: #2a2a2a;
  }

  :deep(h3) {
    font-size: 16px;
    font-weight: bold;
    margin: 8px 0 4px;
    color: #3a3a3a;
  }

  :deep(p) {
    margin: 8px 0;
    font-size: 14px;
  }

  :deep(ul), :deep(ol) {
    padding-left: 20px;
    margin: 8px 0;
  }

  :deep(li) {
    margin: 4px 0;
    font-size: 14px;
  }

  :deep(code) {
    background-color: #f0f0f0;
    padding: 2px 4px;
    border-radius: 4px;
    font-family: 'Courier New', monospace;
    font-size: 13px;
    color: #e83e8c;
  }

  :deep(pre) {
    background-color: #2d2d2d;
    color: #f8f8f2;
    padding: 12px;
    border-radius: 8px;
    overflow-x: auto;
    margin: 8px 0;
  }

  :deep(pre code) {
    background-color: transparent;
    padding: 0;
    color: inherit;
    font-size: 13px;
  }

  :deep(blockquote) {
    border-left: 4px solid #6366f1;
    padding-left: 12px;
    margin: 8px 0;
    color: #666;
    font-style: italic;
  }

  :deep(a) {
    color: #6366f1;
    text-decoration: underline;
  }

  :deep(strong) {
    font-weight: bold;
    color: #1a1a1a;
  }

  :deep(em) {
    font-style: italic;
  }
}
</style>

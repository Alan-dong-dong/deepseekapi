<script setup lang="ts">
import { ref, onMounted } from 'vue'
import hljs from 'highlight.js'
import { marked } from 'marked'
import 'highlight.js/styles/atom-one-dark.css'
import 'highlight.js/lib/languages/python'
import { markedHighlight } from 'marked-highlight'

marked.use(markedHighlight({
  langPrefix: 'hljs language-',
  highlight(code, lang) {
    const language = lang || 'text'  // 如果没有指定语言，默认为 'text'
    if (lang && hljs.getLanguage(lang)) {
      const html = hljs.highlight(code, { language }).value
      // 添加自定义属性来标识语言
      return `<div data-language="${language}">${html}</div>`
    }
    return code
  }
}))

marked.setOptions({
  renderer: new marked.Renderer(),
  gfm: true,
  breaks: true,
  pedantic: false
})

interface Message {
  role: 'user' | 'assistant'
  content: string
}

const messages = ref<Message[]>([])
const newMessage = ref('')
const loading = ref(false)
const currentResponse = ref('')

// 添加深色模式状态
const isDarkMode = ref(false)

// 切换深色模式
const toggleDarkMode = () => {
  isDarkMode.value = !isDarkMode.value
  localStorage.setItem('darkMode', isDarkMode.value.toString())
}

// 初始化深色模式
onMounted(() => {
  const savedMode = localStorage.getItem('darkMode')
  isDarkMode.value = savedMode === 'true'
})

const sendMessage = async () => {
  if (!newMessage.value.trim() || loading.value) return
  
  loading.value = true
  messages.value.push({
    role: 'user',
    content: newMessage.value
  })
  
  try {
    // 添加助手消息
    currentResponse.value = ''
    messages.value.push({
      role: 'assistant',
      content: ''
    })

    const response = await fetch('http://localhost:8000/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        messages: messages.value
      })
    })

    const reader = response.body?.getReader()
    const decoder = new TextDecoder()

    if (reader) {
      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n')
        
        for (const line of lines) {
          if (line.trim() && line !== 'data: [DONE]') {
            try {
              const jsonStr = line.replace(/^data: /, '')
              const data = JSON.parse(jsonStr)
              if (data.choices?.[0]?.delta?.content) {
                const content = data.choices[0].delta.content
                currentResponse.value += content
                messages.value[messages.value.length - 1].content = currentResponse.value
              }
            } catch (e) {
              // 忽略解析错误
            }
          }
        }
      }
    }

  } catch (error: any) {
    console.error('Error details:', error)
    messages.value.push({
      role: 'assistant',
      content: '抱歉，发生了错误，请稍后重试。'
    })
  } finally {
    loading.value = false
    newMessage.value = ''
  }
}

// 添加复制代码功能
const copyCode = (event: MouseEvent) => {
  const button = event.target as HTMLElement
  const pre = button.closest('pre')
  if (pre) {
    const code = pre.querySelector('code')
    if (code) {
      navigator.clipboard.writeText(code.textContent || '')
      button.textContent = '已复制!'
      setTimeout(() => {
        button.textContent = '复制'
      }, 2000)
    }
  }
}

// 修改格式化函数
const formatMessage = (content: string) => {
  try {
    // 使用 marked.parse() 并强制类型为 string
    const html = marked.parse(content) as string
    return html.replace(/<pre><code/g, '<pre><button class="copy-btn" onclick="window.copyCode(event)">复制</button><code')
  } catch (e) {
    console.error('Markdown parsing error:', e)
    return content
  }
}

// 暴露复制函数到 window 对象
window.copyCode = copyCode
</script>

<template>
  <div class="container" :class="{ 'dark-mode': isDarkMode }">
    <button class="theme-toggle" @click="toggleDarkMode">
      {{ isDarkMode ? '🌙' : '☀️' }}
    </button>
    
    <h1>AI 智能助手</h1>
    
    <div class="chat-container">
      <div class="messages">
        <div v-for="(msg, index) in messages" 
             :key="index" 
             :class="['message', msg.role]">
          <div class="avatar">{{ msg.role === 'user' ? '👤' : '🤖' }}</div>
          <div class="content" v-html="formatMessage(msg.content)"></div>
        </div>
      </div>
      
      <div class="input-area">
        <textarea 
          v-model="newMessage" 
          placeholder="请输入您的问题..."
          @keyup.ctrl.enter="sendMessage"
          :disabled="loading"
        ></textarea>
        <button 
          @click="sendMessage" 
          :disabled="loading || !newMessage.trim()"
        >
          {{ loading ? '思考中...' : '发送' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 基础布局样式 */
.container {
  max-width: 1400px;         /* 增加最大宽度到1400px */
  min-width: 1000px;         /* 增加最小宽度到1000px */
  margin: 0 auto;
  padding: 30px 40px;        /* 增加水平内边距 */
  height: 100vh;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

/* 标题样式 */
h1 {
  text-align: center;
  color: #333;
  margin-bottom: 20px;
  font-size: 2em;            /* 增大标题字号 */
}

/* 聊天窗口容器 */
.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 120px);
  border: 1px solid #eee;
  border-radius: 16px;       /* 增大圆角 */
  background: #fff;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.12);
}

/* 消息列表区域 */
.messages {
  flex: 1;
  overflow-y: auto;
  padding: 30px;             /* 增大内边距 */
  margin-bottom: 0;
}

/* 单条消息样式 */
.message {
  display: flex;
  margin-bottom: 25px;       /* 增加消息间距 */
  align-items: flex-start;
}

/* 头像样式 */
.avatar {
  width: 45px;               /* 增大头像 */
  height: 45px;
  border-radius: 50%;
  margin: 0 15px;            /* 增加边距 */
  font-size: 22px;           /* 增大表情符号 */
}

/* 消息内容基础样式 */
.content {
  max-width: 90%;           /* 增加消息最大宽度 */
  padding: 20px 30px;       /* 增加水平内边距 */
  font-size: 16px;
  line-height: 1.6;
  border-radius: 12px;
}

/* 用户消息内容样式 */
.user .content {
  background: #007AFF;
  color: white;
}

/* 助手消息样式 */
.assistant .content {
  background: #f8f9fa;
  padding: 25px 35px;
  line-height: 1.7;
}

/* 输入区域样式 */
.input-area {
  padding: 25px 30px;        /* 增大内边距 */
  border-top: 1px solid #eee;
  display: flex;
  gap: 15px;                 /* 增加间距 */
}

/* 文本输入框样式 */
textarea {
  flex: 1;
  height: 65px;              /* 增大高度 */
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 10px;
  font-size: 16px;           /* 增大字体 */
  resize: none;
}

/* 发送按钮样式 */
button {
  padding: 0 30px;           /* 增大内边距 */
  font-size: 16px;
  border-radius: 10px;
  background-color: #007AFF;
  color: white;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
}

/* 响应式设计 */
@media (max-width: 1400px) {
  .container {
    max-width: 95vw;
    min-width: 800px;
    padding: 20px;
  }
}

@media (max-width: 768px) {
  .container {
    min-width: unset;
    width: 100%;
    padding: 15px;
  }
  
  .content {
    max-width: 90%;
  }
}

/* 代码块容器样式 */
.content :deep(pre) {
  margin: 1em 0;
  padding: 0;
  border-radius: 8px;
  background: #1e1e1e !important;
  overflow: hidden;
  position: relative;
  width: 100%;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  text-align: left;
}

/* 代码块顶部栏 */
.content :deep(pre)::before {
  content: attr(data-language);
  text-transform: capitalize;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 35px;
  line-height: 35px;
  padding: 0 15px;
  background: #2d2d2d;
  color: #d4d4d4;
  font-size: 13px;
  font-family: -apple-system, BlinkMacSystemFont, sans-serif;
  border-bottom: 1px solid #3d3d3d;
  display: flex;
  justify-content: flex-start;
  align-items: center;
  padding-right: 70px;
}

/* 代码内容样式 */
.content :deep(pre) code {
  display: block;
  padding: 15px 20px;
  padding-top: 45px;
  font-family: 'JetBrains Mono', Consolas, monospace;
  font-size: 14px;
  line-height: 1.6;
  tab-size: 4;
  color: #d4d4d4;
  background: transparent !important;
  overflow-x: auto;
  text-align: left;
}

/* 内联代码样式 */
.content :deep(:not(pre) > code) {
  padding: 0.2em 0.4em;
  margin: 0;
  font-size: 85%;
  background-color: rgba(27,31,35,0.05);
  border-radius: 3px;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  text-align: left;
}

/* 代码高亮颜色配置 */
.content :deep(.hljs-keyword) { color: #569cd6 !important; font-weight: bold; }  /* 关键字 */
.content :deep(.hljs-function) { color: #dcdcaa !important; }                    /* 函数 */
.content :deep(.hljs-number) { color: #b5cea8 !important; }                      /* 数字 */
.content :deep(.hljs-string) { color: #ce9178 !important; }                      /* 字符串 */
.content :deep(.hljs-comment) { color: #6a9955 !important; }                     /* 注释 */
.content :deep(.hljs-operator) { color: #d4d4d4 !important; }                    /* 运算符 */
.content :deep(.hljs-punctuation) { color: #d4d4d4 !important; }                 /* 标点符号 */
.content :deep(.hljs-variable) { color: #9cdcfe !important; }                    /* 变量 */
.content :deep(.hljs-params) { color: #9cdcfe !important; }                      /* 参数 */

/* Markdown 文本样式 */
.content :deep(h1) { 
  font-size: 1.8em; 
  margin: 1.2em 0 0.6em;
  padding-bottom: 0.3em;
  border-bottom: 2px solid #eaecef;
  color: #2c3e50;
  font-weight: 600;
  text-align: left;
}

.content :deep(h2) { 
  font-size: 1.5em; 
  margin: 1em 0 0.5em;
  padding-bottom: 0.3em;
  border-bottom: 1px solid #eaecef;
  color: #2c3e50;
  font-weight: 600;
  text-align: left;
}

.content :deep(h3) { 
  font-size: 1.3em; 
  margin: 0.8em 0 0.4em;
  color: #2c3e50;
  font-weight: 600;
  text-align: left;
}

.content :deep(h4) { 
  font-size: 1.2em; 
  margin: 0.6em 0 0.3em;
  color: #2c3e50;
  font-weight: 600;
  text-align: left;
}

.content :deep(p) { 
  margin: 0.8em 0;
  line-height: 1.7;
  color: #24292e;
  text-align: left;
}

.content :deep(ul), .content :deep(ol) { 
  margin: 0.8em 0;
  padding-left: 2em;
  color: #24292e;
  text-align: left;
}

.content :deep(li) { 
  margin: 0.4em 0;
  line-height: 1.7;
}

.content :deep(blockquote) { 
  margin: 1em 0;
  padding: 0.5em 1em;
  color: #6a737d;
  background: #f6f8fa;
  border-left: 4px solid #dfe2e5;
  text-align: left;
}

.content :deep(a) {
  color: #0366d6;
  text-decoration: none;
  font-weight: 500;
}

.content :deep(a:hover) {
  text-decoration: underline;
  color: #0056b3;
}

.content :deep(strong) {
  font-weight: 600;
  color: #24292e;
}

.content :deep(em) {
  font-style: italic;
}

.content :deep(code) {
  padding: 0.2em 0.4em;
  margin: 0;
  font-size: 85%;
  background-color: rgba(27,31,35,0.05);
  border-radius: 3px;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
}

.content :deep(img) {
  max-width: 100%;
  height: auto;
  margin: 1em 0;
  border-radius: 4px;
}

/* 滚动条样式 */
.messages {
  scrollbar-width: thin;
  scrollbar-color: rgba(0, 0, 0, 0.2) transparent;
}

.messages::-webkit-scrollbar { width: 6px; }                                    /* 滚动条宽度 */
.messages::-webkit-scrollbar-track { background: transparent; }                 /* 滚动条轨道 */
.messages::-webkit-scrollbar-thumb {                                           /* 滚动条滑块 */
  background-color: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
}

/* 复制按钮样式 */
.content :deep(.copy-btn) {
  position: absolute;
  top: 5px;
  right: 10px;
  background: transparent;
  border: 1px solid #666;
  color: #999;
  padding: 2px 8px;
  font-size: 12px;
  cursor: pointer;
  border-radius: 4px;
  z-index: 10;
  transition: all 0.2s;
}

.content :deep(.copy-btn:hover) {
  background: #666;
  color: #fff;
}

/* 深色模式切换按钮 */
.theme-toggle {
  position: fixed;
  top: 20px;
  right: 20px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: transparent;
  border: 2px solid #ddd;
  cursor: pointer;
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  z-index: 1000;
}

.theme-toggle:hover {
  transform: scale(1.1);
}

/* 深色模式样式 */
.dark-mode {
  background-color: #1a1a1a;
}

.dark-mode h1 {
  color: #fff;
}

.dark-mode .chat-container {
  background: #2d2d2d;
  border-color: #3d3d3d;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3);
}

.dark-mode .message .content {
  color: #e0e0e0;
}

.dark-mode .assistant .content {
  background: #3d3d3d;
  color: #e0e0e0;
}

.dark-mode .user .content {
  background: #0056b3;
  color: #fff;
}

.dark-mode textarea {
  background: #3d3d3d;
  border-color: #4d4d4d;
  color: #fff;
}

.dark-mode .input-area {
  border-top-color: #3d3d3d;
  background: #2d2d2d;
}

.dark-mode button:not(.theme-toggle) {
  background-color: #0056b3;
}

/* 深色模式下的 Markdown 样式 */
.dark-mode .content :deep(h1),
.dark-mode .content :deep(h2),
.dark-mode .content :deep(h3),
.dark-mode .content :deep(h4) {
  color: #e0e0e0;
  border-bottom-color: #3d3d3d;
}

.dark-mode .content :deep(p),
.dark-mode .content :deep(ul),
.dark-mode .content :deep(ol),
.dark-mode .content :deep(li) {
  color: #d4d4d4;
}

.dark-mode .content :deep(blockquote) {
  background: #2d2d2d;
  border-left-color: #4d4d4d;
  color: #b0b0b0;
}

.dark-mode .content :deep(a) {
  color: #58a6ff;
}

.dark-mode .content :deep(code) {
  background-color: rgba(240, 240, 240, 0.1);
  color: #e0e0e0;
}

/* 深色模式下的滚动条 */
.dark-mode .messages::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.2);
}

/* 深色模式下的复制按钮 */
.dark-mode .content :deep(.copy-btn) {
  border-color: #4d4d4d;
  color: #b0b0b0;
}

.dark-mode .content :deep(.copy-btn:hover) {
  background: #4d4d4d;
  color: #fff;
}
</style>
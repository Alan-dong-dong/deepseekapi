# AI 智能助手项目

一个基于 Vue 3 + TypeScript + FastAPI 的智能对话系统，支持 Markdown 渲染、代码高亮和实时对话功能。

## 项目结构 

```
deepseekapi/
├── qa-system/ # 后端项目目录
│ ├── main.py # 后端服务入口
│ ├── requirements.txt # 后端依赖配置
│ └── .env # 后端环境变量
├── frontend/ # 前端项目目录
│ ├── src/
│ │ ├── App.vue # 主应用组件
│ │ ├── main.ts # 应用入口文件
│ │ ├── style.css # 全局样式
│ │ └── types/ # TypeScript 类型定义
│ ├── public/ # 静态资源
│ └── package.json # 项目依赖配置
```

## 技术栈

### 前端
- Vue 3 (Composition API)
- TypeScript
- Vite
- Marked (Markdown 解析)
- Highlight.js (代码高亮)

### 后端
- FastAPI
- Python
- OpenAI API

## 功能特性

1. 实时对话
   - 支持流式响应
   - 打字机效果显示
   - 支持错误处理和重试

2. Markdown 渲染
   - 支持完整的 Markdown 语法
   - 标题、列表、引用等样式优化
   - 自适应布局

3. 代码高亮
   - 多语言语法高亮
   - 代码块顶部语言标识
   - 一键复制功能
   - 暗色主题

4. 用户界面
   - 响应式设计
   - 自定义滚动条
   - 加载状态提示
   - 错误处理提示

## 文件说明

### 前端核心文件

1. `frontend/src/App.vue`
   - 主应用组件
   - 包含对话界面实现
   - 消息处理和展示逻辑
   - 样式定义

2. `frontend/src/main.ts`
   - 应用入口文件
   - Vue 应用初始化

3. `frontend/src/style.css`
   - 全局样式定义
   - 主题配置

4. `frontend/src/types/global.d.ts`
   - 全局类型定义
   - Window 接口扩展

### 后端文件

1. `main.py`
   - FastAPI 服务器配置
   - API 路由定义
   - OpenAI 接口集成

## 开发指南

### 前端开发

1. 安装依赖 
```
npm install
```

2. 运行开发环境
```
npm run dev
```

### 后端开发

1. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```

2. 安装依赖
```bash
pip install fastapi uvicorn python-dotenv openai==0.28.0
```

3. 启动服务器
```bash
uvicorn main:app --reload
```

## 配置说明

1. 前端配置
   - 在 `vite.config.ts` 中配置构建选项
   - 在 `tsconfig.json` 中配置 TypeScript 选项

2. 后端配置
   - 使用 `.env` 文件配置环境变量
   - 配置 OpenAI API 密钥

## 注意事项

1. 确保后端服务器正常运行并可访问
2. 配置正确的 OpenAI API 密钥
3. 注意浏览器兼容性问题
4. 确保网络连接稳定

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 发起 Pull Request

## 许可证

MIT License



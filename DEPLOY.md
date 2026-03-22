# 部署指南：GitHub Pages + Railway

## 最终效果

- **前端地址**：`https://你的用户名.github.io/csv-translate-agent`
- **后端地址**：`https://xxx-production.up.railway.app`

---

## 第一步：上传代码到 GitHub

### 1. 创建 GitHub 仓库

1. 打开 https://github.com/new
2. 仓库名填：`csv-translate-agent`
3. 选择 **Private** 或 **Public**
4. 点击 **Create repository**

### 2. 推送代码

在终端执行：

```bash
cd /Users/mac/Desktop/test/04

# 初始化 Git
git init
git add .
git commit -m "Initial commit: CSV Translate Agent"

# 连接远程仓库（替换你的用户名）
git remote add origin https://github.com/你的用户名/csv-translate-agent.git
git branch -M main
git push -u origin main
```

---

## 第二步：部署后端到 Railway

### 1. 注册 Railway

访问 https://railway.app，用 GitHub 登录

### 2. 创建项目

1. 点击 **New Project**
2. 选择 **Deploy from GitHub repo**
3. 选择你刚才创建的仓库
4. 点击 **Deploy Now**

### 3. 配置后端

1. 点击项目进入设置
2. 点击 **Settings** → **Root Directory** 设为 `backend`
3. 点击 **Variables** 添加环境变量：

```
LLM_API_URL = https://ai.t8star.cn/v1/chat/completions
LLM_API_KEY = sk-AvlxHNfcuoy31ylKB3Om14lEEzhWLWia9LDDUJyPeU5fsaie
LLM_MODEL = gpt-5.4
```

### 4. 生成域名

1. 点击 **Settings** → **Networking**
2. 点击 **Generate Domain**
3. 复制生成的域名，例如：`https://csv-translate-backend-production.up.railway.app`

---

## 第三步：部署前端到 GitHub Pages

### 1. 开启 GitHub Pages

1. 进入 GitHub 仓库
2. 点击 **Settings** → **Pages**
3. Source 选择 **GitHub Actions**
4. 会自动检测到部署配置

### 2. 添加后端地址

1. 点击 **Settings** → **Secrets and variables** → **Actions**
2. 点击 **New repository secret**
3. Name: `REACT_APP_API_URL`
4. Value: 填入 Railway 后端地址（如 `https://xxx.up.railway.app`）
5. 点击 **Add secret**

### 3. 触发部署

方式一：重新推送代码
```bash
git commit --allow-empty -m "trigger deploy"
git push
```

方式二：手动触发
1. 点击 **Actions** 标签
2. 选择 **Deploy Frontend to GitHub Pages**
3. 点击 **Run workflow**

### 4. 获取访问地址

部署完成后，访问地址为：
```
https://你的用户名.github.io/csv-translate-agent
```

---

## 常见问题

### Q: 页面打开空白？
检查浏览器控制台，可能是 API 地址配置错误

### Q: CORS 跨域错误？
后端已配置允许所有来源，不应出现此问题

### Q: Railway 休眠？
Railway 免费版会休眠，首次访问可能需要等待几秒唤醒

---

## 项目结构

```
csv-translate-agent/
├── .github/workflows/
│   └── deploy-frontend.yml   # GitHub Actions 前端部署
├── frontend/                  # 前端 (部署到 GitHub Pages)
│   ├── src/
│   ├── public/
│   └── package.json
├── backend/                   # 后端 (部署到 Railway)
│   ├── main.py
│   ├── Procfile
│   ├── runtime.txt
│   └── railway.toml
└── DEPLOY.md
```

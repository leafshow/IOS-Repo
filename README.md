# iOS 多应用存储库

这是一个为 AltStore 设计的多应用存储库，包含多个 IPA 应用程序，用于在非官方渠道分发和安装 iOS 应用。

## 项目结构

```
altsrc-repo/
├── altstore.json      # AltStore 软件源配置文件
├── index.html         # 软件源的网页界面
├── apps/              # 存放 IPA 应用文件
│   └── sample-app.ipa
├── assets/            # 存放资源文件（如新闻横幅等）
└── icons/             # 存放应用图标
```

## 使用自动化脚本

本项目包含自动化脚本 `generate_repo.py`，可以自动生成所有必要的配置文件和目录结构：

```bash
# 生成基础项目结构
python generate_repo.py

# 生成自定义名称的软件源
python generate_repo.py --name "我的软件源" --domain "mydomain.com"
```

## 功能特点

- **多应用支持**: 可以添加多个不同的应用到软件源中
- **Web 界面**: 提供直观的网页界面展示可用应用
- **AltStore 集成**: 与 AltStore 客户端无缝集成
- **版本管理**: 支持应用版本控制和更新
- **自动化生成**: 通过脚本自动生成所有必要的文件

## 使用方法

### 添加软件源到 AltStore

1. 打开 AltStore 应用
2. 点击 "软件源" 选项卡
3. 点击右上角的 "+" 按钮
4. 输入软件源地址（通常是 `https://yourdomain.com/altsrc-repo/altstore.json`）
5. 点击 "添加软件源"

### 添加新应用

1. 将 IPA 文件放入 `apps/` 目录
2. 将应用图标放入 `icons/` 目录
3. 更新 `altstore.json` 文件，添加新的应用配置
4. （可选）在 `assets/` 目录中添加新闻横幅图片
5. 更新 `index.html` 文件，如果需要在网页界面上显示应用

### 软件源配置

`altstore.json` 文件包含软件源的所有配置信息，包括：

- 软件源名称和标识符
- 支持的应用列表
- 每个应用的版本信息
- 应用描述、图标和下载链接
- 软件源新闻

## 配置文件说明

### altstore.json

主要配置文件，包含以下字段：

- `name`: 软件源名称
- `identifier`: 软件源唯一标识符
- `version`: 配置文件版本
- `apps`: 应用列表
- `news`: 软件源新闻列表

### index.html

Web 界面文件，用于展示软件源中的应用列表，方便用户了解和预览可安装的应用。

## 部署说明

要将此软件源部署到服务器，有多种方式：

### 通过 GitHub + Vercel 部署

1. 将项目上传到 GitHub 仓库
2. 登录到 [Vercel](https://vercel.com) 并连接你的 GitHub 账户
3. 点击 "New Project" 并导入你的仓库
4. 在设置中将 `altsrc-repo` 目录设置为根目录（或调整配置）
5. 部署将自动开始，完成后你会获得一个类似 `https://your-project.vercel.app` 的 URL

### 通过 GitHub Pages 部署

1. 将项目代码推送到 GitHub 仓库
2. 在 GitHub 仓库设置中，选择 "Pages" 选项
3. 源码设置为 "Deploy from a branch" 或 "GitHub Actions"
4. 部署完成后会获得类似 `https://username.github.io/repository-name` 的 URL

### 通过传统 Web 服务器部署

1. 将整个 `altsrc-repo` 目录上传到 Web 服务器
2. 确保服务器支持 HTTPS（推荐）
3. 配置文件权限，确保 IPA 文件和 JSON 文件可以被访问
4. 在 AltStore 中添加软件源地址

### 部署注意事项

- 软件源地址格式为 `https://your-domain.com/altsrc-repo/altstore.json`
- 确保服务器能够正确提供 `.json` 和 `.ipa` 文件
- 使用 HTTPS 以确保与 AltStore 的兼容性
- 对于大文件（如 IPA 文件），考虑使用 CDN 或对象存储服务

## 注意事项

- 确保所有 IPA 文件都经过适当的签名处理
- 遵守相关法律法规，仅分发有权限分发的应用
- 定期更新应用版本以确保安全
- 提供清晰的应用说明和使用条款

## 维护

- 定期检查应用的兼容性
- 及时更新过期的证书
- 监控下载链接的有效性
- 根据需要更新 `altstore.json` 配置文件

## 贡献

如果要添加新的应用或修改现有配置，请确保：

1. 遵循 `altstore.json` 的格式规范
2. 提供准确的应用信息
3. 使用适当尺寸的图标
4. 测试配置文件的有效性

## 许可证

请根据具体应用的许可证要求使用本存储库中的应用。

---

*此项目为 AltStore 软件源的模板，可根据需要进行定制和扩展。*

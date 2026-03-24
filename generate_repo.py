#!/usr/bin/env python3
"""
自动化生成 AltStore 软件源的脚本
此脚本可以生成必要的配置文件、目录结构和相关资源
"""

import os
import json
import argparse
from datetime import datetime
from pathlib import Path
import stat


def create_directory_structure():
    """创建目录结构"""
    directories = [
        'altsrc-repo/apps',
        'altsrc-repo/assets',
        'altsrc-repo/icons'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"创建目录: {directory}")


def get_ipa_info(ipa_path):
    """获取IPA文件的基本信息，从Info.plist中提取版本号"""
    import zipfile
    import plistlib
    
    # 获取文件名和大小
    file_name = os.path.basename(ipa_path)
    file_size = os.path.getsize(ipa_path)
    
    # 从文件名解析应用名称
    app_name = os.path.splitext(file_name)[0]  # 移除扩展名
    # 清理文件名，移除可能的后缀
    if app_name.endswith('_Decrypted'):
        app_name = app_name.replace('_Decrypted', '')
    
    # 从IPA文件中提取Info.plist来获取版本号
    version = "1.0.0"  # 默认版本
    
    try:
        with zipfile.ZipFile(ipa_path, 'r') as ipa_zip:
            # 获取所有文件名列表
            file_list = ipa_zip.namelist()
            
            # 优先查找主应用目录下的Info.plist（而不是在框架或Storyboard中）
            # 寻找类似 "Payload/AppName.app/Info.plist" 格式的路径
            main_app_info_plist = None
            for file_path in file_list:
                # 查找在主应用目录下的Info.plist，而不是在Frameworks或Storyboard中
                if (file_path.startswith('Payload/') and 
                    file_path.endswith('/Info.plist') and 
                    '.app/' in file_path and 
                    not '/Frameworks/' in file_path and 
                    not '/Base.lproj/' in file_path and 
                    not '/zh-Hans.lproj/' in file_path and 
                    not '/AliyunEmasServices' in file_path):
                    main_app_info_plist = file_path
                    break
            
            # 如果找到主应用的Info.plist，则读取它
            if main_app_info_plist:
                plist_content = ipa_zip.read(main_app_info_plist)
                plist_data = plistlib.loads(plist_content)
                
                # 从Info.plist中获取版本号
                version = plist_data.get('CFBundleShortVersionString', '1.0.0')
                if not version or version == '1.0.0' or version == '':
                    version = plist_data.get('CFBundleVersion', '1.0.0')
            else:
                # 如果没有找到主应用的Info.plist，遍历所有可能的Info.plist
                for file_path in file_list:
                    if 'Payload/' in file_path and file_path.endswith('/Info.plist'):
                        plist_content = ipa_zip.read(file_path)
                        plist_data = plistlib.loads(plist_content)
                        
                        # 从Info.plist中获取版本号
                        version = plist_data.get('CFBundleShortVersionString', '1.0.0')
                        if version and version != '1.0.0' and version != '':
                            break
                        version = plist_data.get('CFBundleVersion', '1.0.0')
                        if version and version != '1.0.0' and version != '':
                            break
    
    except Exception as e:
        print(f"读取Info.plist时出错: {e}")
        # 如果无法读取Info.plist，尝试从文件名中提取版本号
        import re
        version_match = re.search(r'(\d+\.\d+(?:\.\d+)?)', app_name)
        if version_match:
            version = version_match.group(1)
    
    return {
        'name': app_name,
        'version': version,
        'file_name': file_name,
        'size': file_size
    }


def generate_altstore_json(repo_name="AltStore Repository", domain="ios-repo.vercel.app"):
    """生成 altstore.json 配置文件，自动扫描apps目录中的IPA文件"""
    # 获取apps目录中的所有IPA文件
    apps_dir = Path('altsrc-repo/apps')
    ipa_files = list(apps_dir.glob('*.ipa'))
    
    apps = []
    
    for ipa_file in ipa_files:
        ipa_info = get_ipa_info(str(ipa_file))
        
        # 生成bundle identifier - 基于应用名称
        app_name_clean = ipa_info['name'].replace(' ', '').replace('-', '').replace('_', '').lower()
        bundle_identifier = f"com.{app_name_clean}"
        
        # 根据应用名称提供更具体的描述
        app_descriptions = {
            'ringtones-manager_1.1-4': {
                'developerName': 'Ringtone Developer',
                'subtitle': 'Ringtone Management Tool',
                'localizedDescription': 'Ringtone management application to help you manage ringtones on your iOS device.',
                'category': 'utilities'
            },
            'sample-app': {
                'developerName': 'Sample Developer',
                'subtitle': 'Sample Application',
                'localizedDescription': 'A sample application for demonstration purposes.',
                'category': 'utilities'
            },
            'CaiNiao': {
                'developerName': 'CaiNiao Developer',
                'subtitle': 'CaiNiao Express Assistant',
                'localizedDescription': 'CaiNiao Express application for package tracking and logistics services.',
                'category': 'utilities'
            },
            'PPT': {
                'developerName': 'PPT Developer',
                'subtitle': 'PPT Presentation Tool',
                'localizedDescription': 'PowerPoint presentation application for viewing and editing presentations.',
                'category': 'productivity'
            },
            'TVBox': {
                'developerName': 'TVBox Developer',
                'subtitle': 'TVBox Media Player',
                'localizedDescription': 'TVBox media application for streaming content and entertainment.',
                'category': 'entertainment'
            }
        }
        
        # 获取应用描述信息，如果不存在则使用默认值
        app_desc = app_descriptions.get(ipa_info['name'], {
            'developerName': 'Developer',
            'subtitle': f'{ipa_info["name"]} App',
            'localizedDescription': f'Application {ipa_info["name"]} for iOS.',
            'category': 'utilities'
        })
        
        # 创建应用配置
        app_config = {
            "name": ipa_info['name'],
            "bundleIdentifier": bundle_identifier,
            "developerName": app_desc['developerName'],
            "subtitle": app_desc['subtitle'],
            "localizedDescription": app_desc['localizedDescription'],
            "iconURL": f"https://{domain}/icons/default-icon.png",
            "tintColor": "41cdff",
            "category": app_desc['category'],
            "versions": [
                {
                    "version": ipa_info['version'],
                    "date": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "localizedDescription": "Latest Version",
                    "downloadURL": f"https://{domain}/apps/{ipa_info['file_name']}",
                    "size": ipa_info['size'],
                    "minOSVersion": "12.0",
                    "maxOSVersion": "18.0"
                }
            ]
        }
        
        apps.append(app_config)
    
    # 如果没有找到IPA文件，保留一个默认应用
    if not apps:
        apps = [
            {
                "name": "Ringtone Manager",
                "bundleIdentifier": "com.ringtones.manager",
                "developerName": "Developer Name",
                "subtitle": "Ringtone Management Tool",
                "localizedDescription": "Ringtone management application to help you manage ringtones on your iOS device.",
                "iconURL": f"https://{domain}/icons/default-icon.png",
                "tintColor": "41cdff",
                "category": "utilities",
                "versions": [
                    {
                        "version": "1.1-4",
                        "date": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "localizedDescription": "Latest Version",
                        "downloadURL": f"https://{domain}/apps/ringtones-manager_1.1-4.ipa",
                        "size": 6998429,
                        "minOSVersion": "12.0",
                        "maxOSVersion": "18.0"
                    }
                ]
            }
        ]
    
    altstore_config = {
        "name": repo_name,
        "identifier": f"com.{domain}.altsrc-repo",
        "apps": apps
    }
    
    with open('altsrc-repo/altstore.json', 'w', encoding='utf-8') as f:
        json.dump(altstore_config, f, ensure_ascii=False, indent=2)
    
    print("生成配置文件: altsrc-repo/altstore.json")


def generate_index_html(repo_name="AltStore Repository"):
    """生成 index.html 文件，显示所有可用应用"""
    # 读取altstore.json文件获取应用信息
    if os.path.exists('altsrc-repo/altstore.json'):
        with open('altsrc-repo/altstore.json', 'r', encoding='utf-8') as f:
            altstore_config = json.load(f)
        
        # 生成应用列表的HTML
        apps_html = ""
        for app in altstore_config.get('apps', []):
            app_name = app['name']
            version = app['versions'][0]['version']  # 获取最新版本
            description = app['localizedDescription']  # 使用本地化描述
            
            apps_html += f"""            <div class="app">
                <img src="icons/default-icon.png" alt="App Icon" class="app-icon" onerror="this.onerror=null;this.src='icons/default-icon.png';">
                <div class="app-info">
                    <div class="app-name">{app_name}</div>
                    <div class="app-version">Version {version}</div>
                    <p>{description}</p>
                </div>
                <button class="install-btn">Install</button>
            </div>
"""
    else:
        # 如果altstore.json不存在，扫描apps目录作为备选方案
        apps_dir = Path('altsrc-repo/apps')
        ipa_files = list(apps_dir.glob('*.ipa'))
        
        # 生成应用列表的HTML
        apps_html = ""
        for ipa_file in ipa_files:
            ipa_info = get_ipa_info(str(ipa_file))
            app_name = ipa_info['name']
            
            apps_html += f"""            <div class="app">
                <img src="icons/default-icon.png" alt="App Icon" class="app-icon" onerror="this.onerror=null;this.src='icons/default-icon.png';">
                <div class="app-info">
                    <div class="app-name">{app_name}</div>
                    <div class="app-version">Version {ipa_info['version']}</div>
                    <p>Application {app_name} for iOS.</p>
                </div>
                <button class="install-btn">Install</button>
            </div>
"""
    
    # 如果没有找到任何应用，则显示默认应用
    if not apps_html.strip():
        apps_html = """            <div class="app">
                <img src="icons/default-icon.png" alt="App Icon" class="app-icon" onerror="this.onerror=null;this.src='icons/default-icon.png';">
                <div class="app-info">
                    <div class="app-name">Ringtone Manager</div>
                    <div class="app-version">Version 1.1-4</div>
                    <p>Ringtone management application to help you manage ringtones on your iOS device.</p>
                </div>
                <button class="install-btn">Install</button>
            </div>
"""
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{repo_name}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f7;
            color: #333;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #007aff;
            text-align: center;
            margin-bottom: 10px;
        }}
        .description {{
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }}
        .repo-url {{
            background: #f0f0f0;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            margin: 20px 0;
            font-family: monospace;
            word-break: break-all;
        }}
        .apps {{
            margin-top: 30px;
        }}
        .app {{
            display: flex;
            align-items: center;
            padding: 15px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            margin-bottom: 10px;
            background: #fafafa;
        }}
        .app-icon {{
            width: 60px;
            height: 60px;
            border-radius: 12px;
            margin-right: 15px;
            object-fit: cover;
        }}
        .app-info {{
            flex: 1;
        }}
        .app-name {{
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .app-version {{
            color: #666;
            font-size: 0.9em;
        }}
        .install-btn {{
            background: #007aff;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.9em;
        }}
        .install-btn:hover {{
            background: #0062cc;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{repo_name}</h1>
        <p class="description">Welcome to our {repo_name}, providing various verified IPA applications</p>
        
        <div class="repo-url">
            Repository URL: https://ios-repo.vercel.app/altstore.json
        </div>
        
        <div class="apps">
            <h2>Available Apps</h2>
{apps_html}
        </div>
    </div>
</body>
</html>"""
    
    with open('altsrc-repo/index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("生成网页文件: altsrc-repo/index.html")


def generate_default_icon():
    """生成默认图标"""
    # 检查是否已存在图标文件
    icon_path = Path('altsrc-repo/icons/default-icon.png')
    if not icon_path.exists():
        # 如果不存在，则创建一个占位符文本文件
        # 注意：实际使用时应替换为真实的PNG图标文件
        with open('altsrc-repo/icons/default-icon.txt', 'w') as f:
            f.write("默认图标占位符文件")
        
        print("生成默认图标文件: altsrc-repo/icons/default-icon.txt (占位符)")
    else:
        print("检测到已存在的图标文件: altsrc-repo/icons/default-icon.png")


def generate_default_banner():
    """生成默认横幅"""
    # 检查是否已存在横幅图片文件
    banner_path = Path('altsrc-repo/assets/welcome-banner.jpg')
    if not banner_path.exists():
        # 如果不存在，则创建一个占位符文本文件
        # 注意：实际使用时应替换为真实的JPG或PNG横幅文件
        with open('altsrc-repo/assets/welcome-banner.txt', 'w') as f:
            f.write("欢迎横幅占位符文件")
        print("生成默认横幅文件: altsrc-repo/assets/welcome-banner.txt (占位符)")
    else:
        print("检测到已存在的横幅文件: altsrc-repo/assets/welcome-banner.jpg")


def update_readme():
    """更新README文件，添加自动生成脚本的说明"""
    readme_content = """# iOS 多应用存储库

这是一个为 AltStore 设计的多应用存储库，包含多个 IPA 应用程序，用于在非官方渠道分发和安装 iOS 应用。

## 项目结构

```
altsrc-repo/
├── altstore.json      # AltStore 软件源配置文件
├── index.html         # 软件源的网页界面
├── apps/              # 存放 IPA 应用文件
│   └── *.ipa
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
4. 输入软件源地址（通常是 `https://ios-repo.vercel.app/altstore.json`）
5. 点击 "添加软件源"

### 添加新应用

1. 将 IPA 文件放入 `apps/` 目录
2. 将应用图标放入 `icons/` 目录
3. 运行 `python generate_repo.py` 重新生成配置文件，或手动更新 `altstore.json` 文件
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
- `apps`: 应用列表

### index.html

Web 界面文件，用于展示软件源中的应用列表，方便用户了解和预览可安装的应用。

## 部署说明

要将此软件源部署到服务器：

1. 将整个 `altsrc-repo` 目录上传到 Web 服务器
2. 确保服务器支持 HTTPS（推荐）
3. 配置文件权限，确保 IPA 文件和 JSON 文件可以被访问
4. 在 AltStore 中添加软件源地址

## 注意事项

- 确保所有 IPA 文件都经过适当的签名处理
- 遵守相关法律法规，仅分发有权限分发的应用
- 定期更新应用版本以确保安全
- 提供清晰的应用说明和使用条款

## 维护

- 定期检查应用的兼容性
- 及时更新过期的证书
- 监控下载链接的有效性
- 运行脚本重新生成配置文件以包含新应用

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
"""
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("更新README文件: README.md")


def main():
    parser = argparse.ArgumentParser(description='自动化生成 AltStore 软件源')
    parser.add_argument('--name', type=str, default='AltStore Repository', help='软件源名称')
    parser.add_argument('--domain', type=str, default='ios-repo.vercel.app', help='域名')
    
    args = parser.parse_args()
    
    print("开始生成 AltStore 软件源...")
    
    # 创建目录结构
    create_directory_structure()
    
    # 生成配置文件
    generate_altstore_json(args.name, args.domain)
    
    # 生成网页文件
    generate_index_html(args.name)
    
    # 生成默认图标和横幅（占位符）
    generate_default_icon()
    generate_default_banner()
    
    # 更新README文件
    update_readme()
    
    print("\n生成完成！")
    print(f"软件源名称: {args.name}")
    print(f"域名: {args.domain}")
    print("脚本已自动扫描 apps/ 目录中的所有IPA文件并生成配置。")


if __name__ == "__main__":
    main()

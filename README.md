# 中文健身动作数据集

包含 **1,324 个健身动作**的简体中文项目，提供中文动作名称、身体部位、训练器械、目标与辅助肌群，以及原项目的十种语言动作说明。附带中文动作浏览器和开发者接入指南。

本项目基于 [Hasan Emir Yıldırım 的 exercises-dataset](https://github.com/hasaneyldrm/exercises-dataset) 中文化，保留上游提交历史、原始数据和版权信息。原版英文说明见 [README.en.md](README.en.md)。

## 快速使用

```sh
git clone https://github.com/flycoo/exercises-dataset-zh.git
cd exercises-dataset-zh
```

用浏览器打开 `index.html` 即可使用，无需安装依赖或启动服务器。

- 使用中文名称、英文原名、器械或肌群搜索动作，例如「卧推」「哑铃」「背阔肌」「bench press」。
- 按身体部位、器械和目标肌群筛选。
- 点击卡片查看动画、主要与辅助肌群、分步说明；默认显示简体中文，也可切换其他语言。
- 打开 `setup.html`，查看数据库建表语句、下载 SQL 导入文件、查看 API 客户端示例或复制中文 AI 后端生成提示词。

也可使用静态服务器：

```sh
python -m http.server 8000
```

然后访问 <http://localhost:8000>。两个页面共用 `data/exercises.zh-CN.js`，直接打开本地文件时也可加载数据。

## 中文化范围

| 内容 | 处理方式 |
| --- | --- |
| 浏览页面与开发者指南 | 导航、按钮、搜索、筛选、弹窗、提示文案使用简体中文 |
| 1,324 个动作名称 | 使用中文名称，并通过 `name_en` 保留原始英文名称 |
| 10 个身体部位、28 种器械、19 个目标肌群 | 提供统一的中文术语，协同与辅助肌群也已翻译 |
| 动作步骤 | 默认展示上游已提供的中文步骤；十种语言内容全部保留 |
| 数据库导出 | 导出中文动作元数据，保留十种语言说明、媒体 ID 与版权署名 |
| 原始数据 | `data/exercises.json` 和原始 Schema 保持上游格式，便于旧项目接入与来源核对 |

本次中文化翻译动作名称及分类元数据，中文步骤沿用上游翻译。名称存在多种常见译法，可通过词表统一项目用语。

## 文件结构

```text
exercises-dataset-zh/
├── data/
│   ├── exercises.json                 # 上游原始多语言数据
│   ├── exercises.schema.json          # 上游原始 Schema
│   ├── exercises.zh-CN.json            # 中文元数据，适用于应用接入
│   ├── exercises.zh-CN.schema.json     # 中文版 JSON Schema 2020-12
│   └── exercises.zh-CN.js              # 两个 HTML 页面共用的离线数据
├── locales/zh-CN/
│   ├── names.json                     # 按动作 ID 维护的中文名称
│   └── terms.json                     # 身体部位、器械和肌群术语
├── scripts/build-localization.py       # 从原始数据和词表重建中文文件
├── tests/                             # 数据完整性、生成一致性和 SQL 导出检查
├── images/                            # 1,324 张 180×180 缩略图
├── videos/                            # 1,324 个 180×180 GIF 动画
├── index.html                         # 中文动作浏览器
├── setup.html                         # 中文开发者指南
├── NOTICE.md                          # 上游英文媒体授权说明
├── NOTICE.zh-CN.md                     # 中文媒体授权说明
└── LICENSE                            # 原始许可证与媒体例外
```

## 在应用中读取数据

Python：

```python
import json

with open("data/exercises.zh-CN.json", encoding="utf-8") as file:
    exercises = json.load(file)

chest = [exercise for exercise in exercises if exercise["category"] == "胸部"]
print(f"胸部动作：{len(chest)}")  # 163
print(exercises[0]["name"])  # 四分之三程仰卧起坐
print(exercises[0]["name_en"])  # 3/4 sit-up
for step in exercises[0]["instruction_steps"]["zh"]:
    print(step)
```

JavaScript / Node.js：

```js
const exercises = require("./data/exercises.zh-CN.json");
const bodyweight = exercises.filter(exercise => exercise.equipment === "自重");
console.log(`自重动作：${bodyweight.length}`); // 325
console.log(exercises[0].instructions.zh);
```

TypeScript 类型示例：

```ts
type Language = "zh" | "en" | "es" | "it" | "tr" | "ru" | "hi" | "pl" | "ko" | "fr";

interface Exercise {
  id: string;
  name: string;
  name_en: string;
  category: string;
  body_part: string;
  equipment: string;
  instructions: Record<Language, string>;
  instruction_steps: Record<Language, string[]>;
  muscle_group: string;
  secondary_muscles: string[];
  target: string;
  media_id: string;
  image: string;
  gif_url: string;
  attribution: string;
  created_at: string;
}
```

`id` 始终是保留前导零的字符串。中文版的 `category`、`body_part`、`equipment`、`target`、`muscle_group` 和 `secondary_muscles` 使用中文值；已有应用如果仍使用英文筛选条件，请继续读取 `data/exercises.json`，或同步调整筛选条件。

`image` 与 `gif_url` 保存仓库内相对路径。服务器或 CDN 部署时需拼接对应资源根地址。

## 数据统计

| 身体部位 | 动作数量 |
| --- | ---: |
| 上臂 | 292 |
| 大腿 | 227 |
| 背部 | 203 |
| 腰腹部 | 169 |
| 胸部 | 163 |
| 肩部 | 143 |
| 小腿 | 59 |
| 前臂 | 37 |
| 有氧运动 | 29 |
| 颈部 | 2 |

支持的动作说明语言：简体中文、英语、西班牙语、意大利语、土耳其语、俄语、印地语、波兰语、韩语、法语。

## 数据库与 API 接入

`setup.html` 支持 SQL Server、PostgreSQL、MySQL、SQLite。先执行建表语句，再下载并执行对应数据库的 INSERT 文件。SQL Server 使用 Unicode 字段与 `N'…'` 字符串，MySQL 使用 `utf8mb4`。

SQL 导出包含中文元数据、十种语言的完整说明、`media_id`、`attribution` 和原始媒体路径。`name_en` 与 `instruction_steps` 未单独导出为数据库字段；如需保留，请按 `id` 从 JSON 导入并扩展表结构。

页面内的 API 示例用于调用你自己实现的服务，项目不包含在线后端。将示例根地址改为实际 API 地址后使用。中文 AI 提示词可辅助生成 Express.js、FastAPI、ASP.NET Core、Spring Boot、Laravel 或 Gin 后端的初始代码，生成后需自行审查与测试。

## 修改译名与同步上游

修改 `locales/zh-CN/names.json` 中对应 ID 的名称，或修改 `locales/zh-CN/terms.json` 中的统一术语，然后运行：

```sh
python scripts/build-localization.py
```

脚本检查名称 ID 是否完整、中文步骤是否存在、分类术语是否齐全，再生成中文 JSON、离线脚本与 Schema。生成文件请勿直接编辑。

同步上游时，先合并上游原始数据与媒体更新，为新增动作补齐中文名称和术语，再重新生成并验证。原项目中重复名称对应的不同 ID 会原样保留，不合并或重排记录。

## 开发验证

需要 Python 3.10+、Node.js 18+；浏览项目本身不需要这些开发依赖。

```sh
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

验证内容包括：1,324 条记录的 ID、字段与媒体完整性；两份数据的说明和版权一致性；中文 Schema；生成文件一致性；页面 JavaScript 语法；SQLite 导出实际导入与中文、法语、版权字段核对。其他数据库的模板做字段与 Unicode 配置检查，未代替真实数据库集成测试。

## 来源与许可

- 上游作者：[Hasan Emir Yıldırım](https://github.com/hasaneyldrm)。
- 代码、工具、数据结构、动作文本和翻译采用 [MIT 许可证](LICENSE)，保留原作者版权声明。
- **图片与 GIF 不在 MIT 许可范围内**，版权归 **Gym visual** 所有。原仓库说明其以单独书面许可提供 180×180 媒体；克隆或 fork 并不自动授予你新的媒体使用许可。
- 展示媒体时须保留 **© Gym visual — https://gymvisual.com/**，使用和再分发须遵守其[使用条款](https://gymvisual.com/content/3-terms-and-conditions-of-use)，并按需要直接取得许可。
- 具体说明见原始 [NOTICE.md](NOTICE.md) 和[中文说明](NOTICE.zh-CN.md)。

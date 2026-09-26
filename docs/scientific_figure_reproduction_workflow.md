# Nature flat scientific schematic：可复现的矢量科学插图工作流

**适用范围**：panel a v02 以及后续 Fig. 1、Fig. 5、Fig. 6 等 Nature Sensors 风格的概念图和技术示意图。

## 当前推荐路线：HTML + inline SVG

当前项目不再把 Inkscape 作为主要排版工具。推荐先用 HTML/CSS 的网格系统安排模块、列宽、间距和响应式版本，再把科学对象作为独立 inline SVG 模块嵌入页面。Inkscape、Illustrator 或 Affinity Designer 只用于最后的路径清理、字体检查和投稿前 QA。

```text
Figure Contract
→ 黑白 Wireframe
→ HTML/CSS 网格排版
→ 独立素材矢量化
→ inline SVG 组装
→ 静态 SVG/PDF QA
```

HTML 只负责布局，不负责替代 SVG 绘制手部、器件、脑区、波形和箭头。仓库中的 [`tools/build_html_layout.py`](../tools/build_html_layout.py) 和 [`examples/panel_c_html_layout/`](../examples/panel_c_html_layout/) 提供了当前 Panel c 的完整示例。

**当前确定的素材策略：**

> **Bioicons 负责对象形状；inline SVG 保持对象可编辑；HTML/CSS 负责模块排版；Lucide 或 Tabler 只负责少量结构符号。**

这套策略的目标不是把不同网站的图标直接拼在一起，而是把素材当作“几何骨架”，再由统一的 SVG 样式和 HTML 网格建立同一套视觉语言。

---

## 1. 最终风格契约

### 1.1 视觉目标

- Nature flat scientific schematic
- 白底、平面矢量、克制的低饱和色块
- 对象简单但有足够识别信息
- 轮廓线宽统一，文字和箭头直接服务于科学叙事
- 信息密度高，图形复杂度低
- 每个对象、箭头、标签、图例和数据标记都能单独编辑

### 1.2 明确禁止

- 嵌入 PNG/JPG 或 SVG 中的 image 元素
- AI 生成图的描摹线条、纹理、模糊边缘和不可解释细节
- 渐变、滤镜、阴影、发光、3D、玻璃效果
- 把整幅图做成 UI 卡片、产品宣传页或图标拼贴
- 未核验许可证的“免费 SVG”
- 从 BioRender、Noun Project、Flaticon 等服务中脱离其许可范围提取素材

---

## 2. 推荐的项目目录

~~~text
figure_01/
├── 00_contract/
│   ├── figure_contract.md       # 版式、叙事、字体、颜色、线宽
│   └── reference/               # 参考图，只用于观察，不进入最终 SVG
├── 01_assets/
│   ├── raw/                     # 原始下载文件，只读保存
│   ├── cleaned/                 # 清洗后的 SVG
│   ├── manifest.csv             # 每个素材的来源、作者、许可证、hash
│   └── licenses/                # 许可证文本或网页快照
├── 02_wireframe/
│   ├── layout.svg               # 黑白版结构蓝图
│   └── layout.png
├── 03_build/
│   ├── build_panel_a.py         # 可重复生成 SVG 的脚本
│   └── helpers/                 # 清洗、调色、导出辅助脚本
├── 04_master/
│   ├── panel_a_master_inkscape.svg
│   └── panel_a_master_plain.svg
├── 05_submission/
│   ├── panel_a.pdf
│   ├── panel_a.eps
│   └── panel_a_preview.png
└── 06_qa/
    ├── qa_report.md
    └── checksums.sha256
~~~

reference/ 可以存在于项目中，但不能把参考图片嵌入最终图。最终图只保留逐个重建的矢量对象。

---

## 3. 完整复现流程

### Step 0：先写 Figure Contract

在开始找素材以前，先锁定：

| 项目 | 要写清楚的内容 |
|---|---|
| 叙事 | 这一幅图要回答什么科学问题；每个 panel 的一句话作用 |
| 画布 | 最终物理尺寸、比例、列宽、面板间距 |
| 层级 | background、objects、signals、arrows、labels、legend、caption |
| 字体 | 字体族、标题/正文/注释字号、字重 |
| 轮廓 | 主对象、结构线、箭头、边界的线宽和端点样式 |
| 颜色 | 类别色、强调色、灰色、背景色；是否允许透明度 |
| 禁止项 | gradient、shadow、glow、3D、PNG、UI card 等 |
| 出口 | SVG、PDF、EPS、PNG；是否保留 Inkscape 专用 master |

本项目的最低标准是：先用黑白线框确定版式和科学关系，再开始上色和找细节素材。

### Step 1：把参考图拆成“语义对象”

不要先按外观临摹，而是先列出对象：

- 科学对象：动物、鸟、植物、传感器、织物、探针、器件
- 结构符号：网络、数据库、接口、同步、读出模块
- 数据对象：散点、波形、坐标轴、边界、标签、图例
- 版式对象：面板字母、分隔线、留白、箭头

每个对象都要有 object_id，例如：

~~~text
panel_a/
  labeled-cat
  labeled-bird
  labeled-flower
  stack-landscape-01
  structure-network-symbol
  decision-boundary
~~~

### Step 2：为不同对象分配素材来源

| 对象 | 首选来源 | 处理方式 |
|---|---|---|
| 生物、材料、器件等对象 | Bioicons、Servier Medical Art、Reactome、Wikimedia Commons | 只取对象几何；删除源背景和装饰；统一颜色和轮廓 |
| 动物/植物剪影 | Bioicons、PhyloPic、OpenClipart | 选择轮廓清楚、许可证允许修改的素材 |
| 网络、接口、同步等结构符号 | Tabler、Lucide、Phosphor、Material Symbols | 只使用少量，改为与全图一致的线宽和颜色 |
| 规则几何 | 直接在 Inkscape 中绘制 | 圆、矩形、箭头、虚线边界不要从图标库拼接 |
| 真实实验对象 | 真实照片、CAD 或作者自己绘制的简化结构 | 图像只作为可追溯证据；最终 panel 中尽量转为干净矢量或保留有明确许可的照片 |

### Step 3：搜索和下载素材

推荐搜索格式：

~~~text
[对象名] + SVG + [scientific / biology / laboratory / schematic]
[对象名] + site:bioicons.com
[对象名] + site:commons.wikimedia.org SVG
[结构含义] + site:tabler.io/icons
[结构含义] + site:lucide.dev/icons
~~~

下载时同时保存：

1. 原始 SVG，不要只保存导出的 PNG；
2. 素材页面 URL；
3. 作者/贡献者；
4. 许可证名称和许可证 URL；
5. 下载日期；
6. 原始文件的 SHA-256；
7. 计划如何修改（改色、删背景、删文字、裁剪、组合）。

### Step 4：建立素材 manifest

建议使用下面的字段：

~~~csv
asset_id,role,source_site,source_url,creator,license,license_url,downloaded_at,raw_sha256,modified,modification_notes,used_in
~~~

当前 panel a v02 的登记示例：

| asset_id | 用途 | 来源 | 许可证 | 修改 |
|---|---|---|---|---|
| bio_mouse.svg | 动物对象 | Bioicons / Ben Murrell | CC0 | 改为米色填充、深色轮廓 |
| bio_avocet.svg | 鸟对象 | Bioicons / EwaOz | CC0 | 删除源背景圆，统一蓝灰色调 |
| bio_flower.svg | 植物对象 | Bioicons / Frédéric Bouché | CC BY 4.0 | 删除源画布方框和渐变引用，统一绿/白色调；保留归属 |
| bio_image.svg | 图像/景观对象 | Bioicons / OpenClipart | Public Domain/CC0 | 删除源文字标记、渐变和源背景 |
| tabler_network.svg | 结构符号 | Tabler Icons | MIT | 改为灰色、减小线宽，仅使用一次 |

### Step 5：清洗 SVG

清洗目标是“保留对象几何，删除素材原来的视觉系统”。

建议删除：

- image 元素
- metadata、namedview、源软件信息
- defs 中未使用的渐变和滤镜
- 源背景矩形、画布边框、装饰性圆形
- 源素材中的文字、wordmark 和标签
- 不需要的 clipPath、mask、filter、path-effect

清洗后仍应保留路径和基本 SVG 几何。不要把素材先转成位图再描摹。

### Step 6：在 inline SVG 中统一视觉语言

对每一类素材按同一套规则处理。对象可以在 HTML 页面中作为独立 SVG 模块管理，也可以在 Inkscape 中打开后继续精修：

1. 导入清洗后的 SVG；
2. 在 Objects/Layers 面板中给对象命名；
3. 解除不必要的 group，保留语义 group；
4. 用 Fill and Stroke 统一填色；
5. 用同一深色设置轮廓；
6. 统一 stroke-linecap 和 stroke-linejoin；
7. 把源素材的渐变改成纯色；
8. 删除明显比全图更细或更粗的内部线；
9. 通过缩放测试对象在最终版面中的可读性；
10. 把对象放在正确的 layer/group 中，而不是只靠视觉位置堆叠。

HTML 路线中，模块级位置由 `layout.json` 和 CSS Grid 控制；对象内部的填色、轮廓、箭头和文字仍然由 SVG 属性控制。

### Step 7：按层组装 panel

推荐的 layer 顺序：

~~~text
Background
Figure letter and title
Labeled data / main objects
Unlabeled data / repeated objects
Signals and data geometry
Arrows and decision boundaries
Structural symbols
Labels and annotations
Legend
Construction guide (hidden)
~~~

panel a 的对象示例：

- Bioicons：动物、鸟、花、图像卡片
- Inkscape 原生绘制：卡片框、散点、三类标记、流形区域、虚线决策边界、箭头、文字
- Tabler：右上角 network/globe 结构符号

这样可以保证素材对象具有自然形状，但整幅图仍然属于同一个视觉系统。

### Step 8：统一颜色和线宽

panel a v02 使用的参考 palette：

~~~text
ink        #263238
mid        #58656B
frame      #738087
red        #E58A84    red-dark   #C95552
blue       #7EA8D1    blue-dark  #2E5C91
green      #8DC487    green-dark #4F934E
grey       #C8D0D3    grey-dark  #9AA7AC
region-red #F7E0E1    region-blue #DCEAF5
region-green #E0EFD9  outer      #F4F6F4
paper      #FFFEFC
~~~

建议把颜色映射写进脚本，而不是每次手动猜颜色。这样下一幅图可以直接复用同一个 palette 文件。

### Step 9：质检

#### 结构检查

~~~bash
# SVG 是否能被 XML 解析
python3 - <<'PY'
import xml.etree.ElementTree as ET
ET.parse('panel_a.svg')
print('XML: ok')
PY

# 检查是否误嵌入位图、渐变或滤镜
rg -n '<image|<linearGradient|<radialGradient|<filter|fill:url' panel_a.svg

# 检查是否还残留源画布边框或源软件 wordmark
rg -n 'metadata|namedview|text998|M279\.5,285\.8' panel_a.svg
~~~

#### 视觉检查

- 在最终投稿尺寸而不是只看放大图时检查；
- 检查文字是否仍然清楚；
- 检查最小对象是否还能识别；
- 检查箭头是否真的指向科学对象；
- 检查所有 panel 的字体、线宽、颜色和留白；
- 隐藏 reference layer 后再导出；
- 从 PDF 再渲染一遍，确认 PDF 和 SVG 视觉一致。

### Step 10：导出和归档

~~~bash
# 生成高分辨率预览
inkscape panel_a_master.svg \
  --export-width=1800 \
  --export-filename=panel_a_preview.png

# 投稿 PDF
inkscape panel_a_master.svg \
  --export-filename=panel_a.pdf

# 需要时输出 EPS
inkscape panel_a_master.svg \
  --export-filename=panel_a.eps

# 生成 hash，保证以后能确认文件是否被改动
sha256sum panel_a_master.svg panel_a.pdf panel_a.eps panel_a_preview.png \
  > checksums.sha256
~~~

每次修改都更新：

- SVG master；
- preview PNG；
- PDF/EPS；
- manifest；
- QA report；
- checksums。

---

## 4. 可复用的素材来源注册表

下面的表按“适合程度”整理。许可证以 **2026-09-25 检查到的官方页面** 为准；真正下载某个文件时，仍要打开该文件的页面确认许可证，因为聚合站点的许可证可能按素材变化。

### A. 优先使用：科学对象和通用矢量

| 来源 | 适合找什么 | 格式/风格 | 许可证与使用判断 | 入口 |
|---|---|---|---|---|
| **Bioicons** | 生物、细胞、动物、植物、实验室器材、科学对象 | 以 SVG 为主，适合 Inkscape/Illustrator | 按素材分为 CC0、CC BY、CC BY-SA、MIT 等；逐个查看 | [bioicons.com](https://bioicons.com/) · [GitHub](https://github.com/duerrsimon/bioicons) |
| **Servier Medical Art (SMART)** | 人体、器官、医学和生物学对象 | 医学插画、SVG/图像素材 | CC BY 4.0；必须归属，适合改编后使用 | [smart.servier.com](https://smart.servier.com/) |
| **Reactome Icon Library** | 分子、细胞、通路和系统生物学符号 | SVG、风格较统一 | CC BY 4.0；需要正确归属 CSHL、OICR、EBI | [reactome.org/icon-lib](https://reactome.org/icon-lib) |
| **PhyloPic** | 动物、植物和其他生命形式的剪影 | 轮廓剪影，适合重绘成单色对象 | 每个剪影许可证不同；优先使用 Public Domain 筛选 | [phylopic.org](https://www.phylopic.org/) |
| **OpenClipart** | 通用物体、生活场景和简单对象 | SVG，风格差异较大 | CC0/Public Domain；仍需检查素材页面 | [openclipart.org](https://openclipart.org/) |
| **Wikimedia Commons** | 科学图、历史图、器件、结构图、SVG 图 | SVG、PNG、照片和扫描图 | 每个文件单独许可；优先 Public Domain、CC0、CC BY；谨慎处理 CC BY-SA | [commons.wikimedia.org](https://commons.wikimedia.org/) |
| **Openverse** | 跨站搜索 CC 和 Public Domain 媒体 | 搜索入口，不是单一素材库 | 每个结果来自不同站点；必须回到原始页面核验 | [openverse.org](https://openverse.org/) |
| **FreeSVG.org** | 通用矢量和剪贴画 | SVG | 平台说明为 CC0/Public Domain；仍保存原始页面 | [freesvg.org](https://freesvg.org/) |
| **SVG Repo** | 图标、物体、界面和通用矢量 | SVG，数量大，风格混杂 | 许可证按素材或作者变化；不能把“SVG Repo 免费”当成统一许可证 | [svgrepo.com](https://www.svgrepo.com/) |
| **LibreClipart** | 通用剪贴画和简单矢量 | SVG/PDF/ODG | 平台说明为 CC0 | [libreclipart.org](https://libreclipart.org/) |

### B. 结构符号：只少量使用

| 来源 | 适合找什么 | 许可证 | 推荐用法 | 入口 |
|---|---|---|---|---|
| **Lucide** | 网络、文件、连接、方向、操作和抽象结构 | ISC | 一次只选少量；统一为 panel 的线宽和颜色 | [lucide.dev](https://lucide.dev/) |
| **Tabler Icons** | 网络、数据库、流程、连接、设备和结构符号 | MIT | 适合当前 panel a 的 network/globe 符号 | [tabler.io/icons](https://tabler.io/icons) |
| **Phosphor** | 结构、设备、对象和方向符号 | MIT | 只选一种 weight，不要混用多个粗细 | [phosphoricons.com](https://phosphoricons.com/) |
| **Material Symbols** | 通用结构和设备符号 | Apache 2.0 | 选择 Outlined 风格，避免 Material UI 感过强 | [Google Material Symbols](https://fonts.google.com/icons) |
| **Heroicons** | 简单 outline/solid 结构符号 | MIT | 适合少量流程符号，不适合替代科学对象 | [heroicons.com](https://heroicons.com/) |
| **Bootstrap Icons** | 文件、设备、数据和常规符号 | MIT | 只作为结构补充 | [icons.getbootstrap.com](https://icons.getbootstrap.com/) |
| **Iconoir** | 细线结构和抽象符号 | MIT | 适合做低存在感的小结构符号 | [iconoir.com](https://iconoir.com/) |
| **Remix Icon** | 通用结构、设备和数据符号 | 版本相关；当前项目需查看 Remix Icon License | 下载时记录具体版本和许可证 | [remixicon.com](https://remixicon.com/) |
| **Iconify** | 统一搜索和导出多个开源图标集 | Iconify 本身不替代图标集许可证 | 用它找图标，但必须查看具体 icon set 的许可证 | [icon-sets.iconify.design](https://icon-sets.iconify.design/) |

### C. 品牌、软件和特殊用途图标

| 来源 | 适合找什么 | 许可证/限制 | 使用建议 | 入口 |
|---|---|---|---|---|
| **Font Awesome Free** | 软件、设备、人物和常用符号 | SVG/JS 图标为 CC BY 4.0；字体为 OFL；代码为 MIT | 可以用，但需记录图标许可证和归属 | [fontawesome.com](https://fontawesome.com/) |
| **Devicon** | 编程语言、软件和开发工具 logo | MIT；logo 本身仍可能涉及商标 | 只在确实需要软件/模型 logo 时使用 | [devicon.dev](https://devicon.dev/) |
| **Simple Icons** | 软件和品牌 logo | 项目为 CC0，但单个品牌图标可能有自己的许可和商标限制 | 只用于读者必须识别的品牌；优先使用单色 | [simpleicons.org](https://simpleicons.org/) |
| **OpenMoji** | 人物、手势、物体和情绪符号 | CC BY-SA 4.0 | 不适合作为 Nature 科学对象主图；可用于草图或极少量提示符号 | [openmoji.org](https://openmoji.org/) |

### D. 可用但不作为默认素材源

| 来源 | 原因 | 处理方式 |
|---|---|---|
| **OpenStax** | 书籍和图形通常是 CC BY-NC-SA 4.0；商业/出版场景可能受限 | 适合找科学结构参考；用于最终图前逐项确认许可和出版社要求 |
| **The Noun Project** | 图标有 CC BY、订阅或商业许可；免费使用通常需要归属 | 只有在能满足归属或购买许可时使用 |
| **Flaticon** | 免费计划通常需要署名；付费计划有不同许可 | 不作为默认来源；保存下载时的许可证证明 |
| **BioRender** | 是受计划约束的内容许可，不是开源素材库；条款限制脱离平台提取素材 | 可以用来参考构图；不要把 BioRender 素材单独抽取到本工作流 |

---

## 5. 许可证决策规则

| 许可证 | 是否适合本工作流 | 处理要求 |
|---|---|---|
| Public Domain / CC0 | 首选 | 保存来源和下载日期即可；仍建议保留作者信息 |
| MIT / ISC / Apache 2.0 | 适合 | 保存许可证文本或链接；在项目包中保留 NOTICE |
| CC BY | 适合 | 记录作者、来源、许可证；在论文补充材料、图注或项目 README 中归属 |
| CC BY-SA | 条件使用 | 修改后可能触发 ShareAlike；除非明确处理，否则不作为首选 |
| CC BY-NC / CC BY-NC-SA | 不作为投稿默认 | 可能与商业出版、再分发或出版社许可冲突 |
| CC BY-ND | 不适合当前清洗方式 | 本工作流会改色、删背景、组合和编辑，因此不使用 ND 素材 |
| “Free download”但无明确许可证 | 不使用 | 下载免费不等于有权修改和再发布 |
| 品牌 logo | 谨慎 | 许可证和商标是两件事；只在科学叙事确实需要时使用 |

### 推荐的归属文本

~~~text
Icon/illustration: [creator], [source], used under [license].
Modified by the authors: recoloured, cropped and simplified for the figure.
~~~

对于当前 panel a v02，至少保留：

~~~text
Arabidopsis flower illustration by Frédéric Bouché via Bioicons,
used under CC BY 4.0; modified by the authors.
~~~

---

## 6. 当前 panel a v02 的可复现命令

工作目录：

~~~text
inkscape_panel_a_v02/
├── build_panel_a_bioicons_v02.py
├── assets/
│   ├── bio_mouse.svg
│   ├── bio_avocet.svg
│   ├── bio_flower.svg
│   ├── bio_image.svg
│   └── tabler_network.svg
└── panel_a_bioicons_v02.svg
~~~

生成 SVG：

~~~bash
python3 build_panel_a_bioicons_v02.py
~~~

生成预览和投稿文件：

~~~bash
inkscape panel_a_bioicons_v02.svg \
  --export-width=1800 \
  --export-filename=panel_a_bioicons_v02.png

inkscape panel_a_bioicons_v02.svg \
  --export-filename=panel_a_bioicons_v02.pdf

inkscape panel_a_bioicons_v02.svg \
  --export-filename=panel_a_bioicons_v02.eps
~~~

验证：

~~~bash
python3 - <<'PY'
from pathlib import Path
import xml.etree.ElementTree as ET
p=Path('panel_a_bioicons_v02.svg')
s=p.read_text()
ET.parse(p)
for token in ['<image','<linearGradient','<radialGradient','<filter','fill:url']:
    print(token, s.count(token))
print('XML: ok')
PY
~~~

预期结果：XML: ok，并且 image 元素、渐变、滤镜和 fill:url 均为 0。

---

## 7. 下一幅图的执行顺序

1. 先写 Figure Contract；
2. 只用黑白几何确定 panel 结构；
3. 把对象分为科学对象、结构符号、数据几何和文字；
4. 先从 Bioicons/SMART/Reactome/PhyloPic 找科学对象；
5. 再从 Lucide/Tabler/Phosphor 找最多 1–3 个结构符号；
6. 下载原始 SVG，登记 manifest 和许可证；
7. 清除源背景、渐变、滤镜、文字和 wordmark；
8. 把对象拆成独立 SVG 模块，并在 `layout.json` 中定义 viewBox、列宽和 placement；
9. 用 HTML/CSS Grid 组装模块，调整留白、对齐和跨模块连接线；
10. 生成静态 SVG，运行结构检查；
11. 必要时在 Inkscape/Illustrator/Affinity 中做路径、字体和图层 QA；
12. 导出 SVG/PDF/EPS/PNG，并把源文件、素材、manifest、许可证和 hash 一起归档。

这套顺序的核心是：**网站负责提供可追溯的几何素材，HTML/CSS 负责模块排版，inline SVG 负责科学图形，Inkscape/Illustrator/Affinity 负责最终矢量 QA，脚本和 manifest 负责让下一次可以复现。**

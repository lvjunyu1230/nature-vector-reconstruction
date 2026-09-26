# Nature Vector Reconstruction

把 AI 生成的参考图转换为**可编辑的科学矢量图**。当前仓库的默认路线是：

> **Figure Contract → HTML/CSS 网格排版 → inline SVG 科学对象 → SVG/PDF QA**

HTML 负责模块位置、列宽、间距和版本迭代；inline SVG 负责手部、器件、波形、箭头、文字和图例。这样可以快速调整排版，同时保留可编辑的矢量对象。

## 为什么从 Inkscape 路线改为 HTML + SVG

| 项目 | 原路线：Inkscape 固定坐标 | 当前路线：HTML + inline SVG |
|---|---|---|
| 排版 | 在一个 SVG 画布中手动移动对象 | 用 CSS Grid 调整列宽、间距和模块顺序 |
| 迭代 | 每次修改都要重新调整多个坐标 | 修改 CSS 或 manifest 即可快速比较版本 |
| 响应式预览 | 较弱 | 浏览器中可以缩放和重排 |
| 对象编辑 | 很强 | SVG 对象仍然可编辑 |
| 跨模块箭头 | 精确，但手工维护 | 需要把连接线作为独立 SVG 模块管理 |
| 投稿输出 | 直接导出 SVG/PDF/EPS | 需要静态 SVG/PDF 导出和最终 QA |

Inkscape/Illustrator 不再承担主要排版工作，而作为最终的矢量清理、字体检查和投稿前 QA 工具保留。原来的自动描摹路线仍通过 `legacy-all` 提供，适合从栅格参考图提取几何轮廓，不再作为投稿级终稿的默认路线。

## 最短路径：HTML + inline SVG

```bash
# 安装 Python 依赖（HTML 构建器使用 lxml；自动矢量化另外使用 VTracer）
make setup

# 构建当前示例的 HTML + SVG 排版页面
make html
# 输出：HTML 页面、静态 SVG 和 html_layout_qa_report.md

# 或者直接指定自己的 manifest
make html HTML_MANIFEST=examples/panel_c_html_layout/layout.json \
  HTML_OUTPUT=outputs/my_layout.html
```

打开 `outputs/panel_c_html_layout.html`，可以在浏览器中比较固定坐标 SVG 和 HTML/CSS 网格版本。

## 当前 HTML 示例

[`examples/panel_c_html_layout/`](examples/panel_c_html_layout/) 包含：

- `layout.json`：模块、列宽和固定 SVG 的配置；
- `panel_c_html_layout.html`：浏览器中的对照页面；
- `panel_c_html_layout.svg`：按 manifest placement 生成的静态矢量组合；
- `modules/*.svg`：手部、编码、脑区和估计/真值模块；
- `panel_c_hybrid_spacious.svg`：原 Inkscape 固定坐标版本，作为对照；
- `tools/build_html_layout.py`：通用 HTML + inline SVG 构建器。

修改自己的图时，先把每个语义模块保存为独立 SVG，再在 `layout.json` 中调整模块顺序、列宽和间距。

## 投稿级完整流程

1. **分析参考图**：提取科学问题、模块关系和信息层级；参考图只用于观察，不进入最终图。
2. **Figure Contract**：锁定画布、字体、颜色、线宽、箭头语义和 panel 结构。
3. **黑白 Wireframe**：先确定网格、对齐、间距和连接线，不先画复杂对象。
4. **素材选择**：Bioicons 负责对象形状；Lucide/Tabler 只用于少量结构符号；独特对象逐个生成或手工绘制。
5. **单素材矢量化**：去背景、颜色量化、路径简化、轮廓清理，删除 AI 纹理和位图。
6. **HTML/CSS 排版**：用 CSS Grid 控制模块位置、列宽、留白和不同版本对比。
7. **inline SVG 组装**：文字、波形、箭头、节点和几何图形保留为原生 SVG 对象。
8. **最终精修**：必要时在 Inkscape、Illustrator 或 Affinity Designer 中校正路径、字体、线宽和层级。
9. **QA**：检查无 `<image>`、无外链、无滤镜/渐变/mask、无越界、无文字重叠和歧义箭头。
10. **导出归档**：保存 SVG、PDF、EPS、高清 PNG、素材 manifest、提示词、脚本和 QA 报告。

## 原栅格参考路线（兼容保留）

如果需要先从单张 PNG/JPG/WebP 提取颜色区域和对象轮廓：

```bash
cp /path/to/reference.png input/reference.png
make reconstruct
make qa
make export
```

结果在 `outputs/`：

```text
reconstructed.svg
reconstructed.pdf
reconstructed.eps
reconstructed.png
reconstruction_report.md
qa_report.md
```

该路线现在命名为：

```bash
make legacy-all
```

自动描摹只用于提取初始几何。文字、箭头、坐标轴、图例和科学关系仍应在 SVG/HTML 版式中重建。

## GitHub Actions

仓库包含两个工作流：

- **HTML Layout Preview**：构建 `examples/panel_c_html_layout/layout.json`，不需要本地 Inkscape；适合快速比较版式。
- **Reconstruct vector figure**：旧的栅格参考 → VTracer → SVG/PDF/EPS/PNG 流程；适合作为几何提取和兼容路线。

在 GitHub Actions 页面运行 HTML 工作流后，可下载 `html-layout-bundle` artifact。

## “无 AI 痕迹”的文件定义

- SVG 中没有 `<image>`、base64、data URI 或外部图片引用；
- 没有 `filter`、`linearGradient`、`radialGradient`、`pattern`、`mask`；
- 主要内容由 `path` 和基础几何组成；
- 文字保留为可编辑文本；
- 生成器、prompt 和源图片路径不写入最终 SVG；
- QA 通过后仍需人工检查科学语义和素材许可。

## 目录

```text
config/style.yaml                         # 调色板和描摹参数
tools/build_html_layout.py                # HTML + inline SVG 构建器
tools/reconstruct.py                      # 旧的栅格 → SVG 几何提取
tools/qa.py                               # SVG 结构检查
tools/export.py                           # Inkscape → PDF/EPS/PNG
.github/workflows/html-layout.yml         # HTML 版式工作流
.github/workflows/reconstruct.yml         # 旧的栅格参考工作流
docs/layout_tools_comparison.md           # 排版工具对比
docs/scientific_figure_reproduction_workflow.md  # 完整科学插图流程
docs/asset_source_registry.md             # 开源素材来源和许可提醒
examples/panel_c_html_layout/             # HTML + SVG 示例
examples/panel_a/                          # Bioicons + Tabler 示例
input/                                     # 栅格参考图
outputs/                                   # 构建结果（默认不提交）
```

## 素材许可

不要把“能下载”当成“可以发表”。每个素材都要在 [`docs/asset_manifest_template.csv`](docs/asset_manifest_template.csv) 记录来源、作者、许可证、许可证网址、下载日期、hash 和修改方式。完整规则见 [`docs/license_policy.md`](docs/license_policy.md)。

## 代码许可

本仓库脚本采用 MIT。第三方素材仍然服从各自许可证，请阅读 `NOTICE.md` 和每项素材的 manifest。

# 科学图形排版工具对比

## 推荐判断

当前默认路线采用 **HTML/CSS + inline SVG**：HTML 负责模块级排版，SVG 负责可编辑科学对象。它适合快速比较列宽、模块间距和不同布局版本。

Inkscape、Illustrator 或 Affinity Designer 作为最终矢量清理和投稿 QA 工具保留。纯 HTML/CSS 不适合直接绘制手部、器件、脑区或复杂路径。

## 工具对比

| 工具 | 最适合的工作 | 优点 | 局限 |
|---|---|---|---|
| HTML + CSS + inline SVG | 模块化排版、响应式布局、版本管理 | CSS Grid 调整列宽和间距很快；可放入 Git；SVG 对象仍可编辑 | 需要额外处理静态 SVG/PDF 导出；跨模块箭头必须单独管理 |
| Figma | 视觉布局、多人协作、快速原型 | 网格、对齐和组件操作方便 | 导出后常需清理；PDF 中的文字可能不再保持原生文本 |
| Penpot | 开源网页协作和 SVG 排版 | 浏览器运行、开放格式、适合团队协作 | 复杂 SVG 和 PDF 转换需要逐项检查 |
| Illustrator | 最终静态矢量精修 | 出版控制、路径编辑和文字排版成熟 | 商业软件，批量复现和版本化不如代码方便 |
| Affinity Designer | 低成本矢量终稿 | 支持 SVG、PDF、EPS，适合手工精修 | 自动化和科研图形脚本生态较弱 |
| SVG + D3/JavaScript | 参数化和批量生成 | 坐标、颜色和重复对象都可由数据驱动 | 不适合手工绘制复杂有机对象 |
| TikZ/PGFPlots | 坐标轴、公式和数据图 | 字体、刻度和数据关系可精确复现 | 绘制编辑插画和有机对象效率低 |
| draw.io/diagrams.net | 黑白结构草图 | 快速确定流程和连接关系 | 不建议直接作为 Nature 风格终稿 |

## 当前项目的职责分配

```text
HTML/CSS       模块位置、列宽、间距、版本比较
inline SVG     对象、波形、箭头、节点、文字、图例
Inkscape       路径清理、图层整理、字体和最终 QA
PDF/EPS/SVG    投稿和归档输出
```

## 不同路线的结果差异

### Inkscape 固定坐标路线

- 所有对象位于同一个 SVG 画布；
- 跨模块箭头和基线容易精确控制；
- 静态投稿输出直接；
- 修改列宽或整体结构时，需要同时调整多个坐标。

### HTML + inline SVG 路线

- 每个科学模块可以独立维护；
- CSS Grid 快速调整列宽、间距和模块顺序；
- 适合浏览器中比较多个布局版本；
- 需要额外设计跨模块连接线和静态导出流程。

因此，HTML 路线替代的是“主要排版方式”，不是替代 SVG 本身。推荐的投稿级流程是：

```text
Figure Contract
→ HTML/CSS 网格排版
→ 独立素材矢量化
→ inline SVG 组装
→ Inkscape/Illustrator/Affinity 最终 QA
→ SVG/PDF/EPS
```

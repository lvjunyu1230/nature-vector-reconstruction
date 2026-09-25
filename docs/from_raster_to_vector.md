# 从 AI 参考图到可编辑矢量图

## A. 输入准备

1. 只放一张参考图到 `input/`。
2. 推荐 PNG 或高质量 JPG；尽量使用白色或透明背景、清晰轮廓和少量纯色。
3. 如果图中有文字，另存一份文字内容，因为自动描摹不能可靠地还原字形。
4. 参考图不进入最终 SVG；它只用于提取几何和版式信息。

## B. 自动转换

`tools/reconstruct.py` 完成四件事：

1. 将透明背景合成到项目纸张色；
2. 量化颜色，减少 AI 生成的抗锯齿噪声；
3. 使用 VTracer 把颜色区域转换为 SVG path；
4. 删除 raster、filter、gradient、mask、外链和源软件元数据，写出一个独立 SVG。

运行：

```bash
python3 tools/reconstruct.py \
  --input input/reference.png \
  --output outputs/reconstructed.svg \
  --style config/style.yaml \
  --report outputs/reconstruction_report.md
```

## C. 结构质检

```bash
python3 tools/qa.py outputs/reconstructed.svg \
  --report outputs/qa_report.md
```

检查失败时，不要继续导出。先在 SVG 中找到残留的 `<image>`、滤镜、外链或空画布，再重新生成或手动清洗。

## D. Inkscape 最后整理

在 Inkscape 中：

1. 打开 `reconstructed.svg`；
2. 把 `vectorized-reference` 层重命名为 `Reference geometry`；
3. 解除需要编辑的 group，删除碎片和不符合科学含义的轮廓；
4. 用原生文字重打标题、标签和图例；
5. 用原生线段、箭头、圆、矩形重建数据关系；
6. 为对象分成 `Background / Objects / Signals / Arrows / Labels / Legend`；
7. 应用统一调色板和线宽；
8. 隐藏或删除任何参考层后再导出。

对于 Nature 风格的 scientific schematic，自动描摹适合给出对象轮廓，不能替代语义重建。`docs/scientific_figure_reproduction_workflow.md` 记录了 Panel A 的完整拆分、素材搜索、清洗、调色和出口流程。

## E. 导出

```bash
python3 tools/export.py outputs/reconstructed.svg --outdir outputs
```

Inkscape 根据 SVG 的 `viewBox` 导出 PDF 和 EPS；PNG 默认导出为 2400 px 宽，可用 `--png-width` 调整。

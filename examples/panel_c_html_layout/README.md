# Panel c HTML + inline SVG 示例

这个示例将当前 Panel c 拆成四个独立 SVG 模块：

- `modules/hands.svg`：手部和触觉记忆；
- `modules/encoding.svg`：皮肤形变、机械感受器、编码和检索；
- `modules/cortex.svg`：躯体感觉皮层；
- `modules/output.svg`：估计、真值和手部区域映射。

`layout.json` 控制模块顺序、列宽、canvas 尺寸和静态 SVG 的 placement。

从仓库根目录运行：

```bash
python3 tools/build_html_layout.py \
  --manifest examples/panel_c_html_layout/layout.json \
  --output outputs/panel_c_html_layout.html \
  --static-svg outputs/panel_c_html_layout.svg
python3 tools/qa.py outputs/panel_c_html_layout.svg \
  --report outputs/html_layout_qa_report.md
```

HTML 页面用于浏览器中的排版比较；静态 SVG 用于后续矢量 QA、PDF/EPS 导出和投稿归档。

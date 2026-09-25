# “无 AI 痕迹”的可验证定义

这里不把“肉眼看不出它来自 AI”当作可证明的承诺。仓库采用文件层面的定义：

| 检查项 | 通过标准 |
|---|---|
| 栅格 | SVG 中没有 `<image>`，没有 base64、data URI 或外部图片引用 |
| 效果 | 没有 `filter`、`linearGradient`、`radialGradient`、`pattern`、`mask` |
| 元数据 | 不保留生成器、prompt、源图片路径等不必要 metadata |
| 编辑性 | 主要内容是 path 和基础几何；能在 Inkscape 中单独选择和改色 |
| 追溯性 | report 记录输入 hash、参数、工具版本和输出 hash |

自动矢量化仍可能保留参考图的错误、文字错写或不科学的视觉细节。正式发表前应由作者对语义、数据和许可证做人工复核；`tools/qa.py` 不能证明科学正确性，也不能证明原始图像的来源。

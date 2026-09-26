# 上传到 GitHub

本地模板已经可以直接推送。推荐创建一个**空仓库**（不要自动生成 README、LICENSE 或 `.gitignore`），例如 `nature-vector-reconstruction`，然后把仓库地址发给维护者。

收到地址后，推送命令是：

```bash
git remote add origin https://github.com/<user>/nature-vector-reconstruction.git
git branch -M main
git push -u origin main
```

如果使用 SSH：

```bash
git remote add origin git@github.com:<user>/nature-vector-reconstruction.git
git branch -M main
git push -u origin main
```

推送后，在 GitHub 仓库中：

1. 打开 **Actions → HTML layout preview → Run workflow**，生成 HTML 对照页和静态 SVG；
2. 在 `examples/*/layout.json` 中调整模块顺序、列宽、placement 和间距；
3. 从 Actions 的 `html-layout-bundle` artifact 下载 HTML、SVG 和 QA 报告；
4. 如需最终路径清理，再用 Codespaces 中的 Inkscape 或本地 Illustrator/Affinity 打开静态 SVG。

旧的 `Reconstruct vector figure` workflow 仍然保留，用于从单张栅格参考图提取初始几何，不再是投稿级终稿的默认入口。

不要把 GitHub access token 写进仓库、README 或 workflow 文件。

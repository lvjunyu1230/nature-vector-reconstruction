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

1. **Code → Codespaces → Create codespace**，获得浏览器版 Inkscape；
2. 把 AI 参考图上传到 `input/` 并提交，触发 Actions；
3. 从 Actions artifact 下载 SVG/PDF/EPS/PNG。

不要把 GitHub access token 写进仓库、README 或 workflow 文件。

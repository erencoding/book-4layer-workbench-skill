#!/usr/bin/env bash
# push_to_github.sh - 解压后一键推送到 GitHub
# 用法:
#   1. 下载并解压 tarball
#   2. 把这个脚本放到解压后的目录里(或直接在解压后目录运行)
#   3. export GITHUB_TOKEN=ghp_xxxxx
#   4. ./push_to_github.sh <你的GitHub用户名>

set -euo pipefail

USERNAME="${1:?usage: ./push_to_github.sh <your-github-username>}"
REPO="book-4layer-workbench-skill"
TOKEN="${GITHUB_TOKEN:?need: export GITHUB_TOKEN=ghp_xxx}"

echo ">> [1/3] 在 GitHub 上创建公开仓库 $USERNAME/$REPO"
curl -sf -X POST https://api.github.com/user/repos \
  -H "Authorization: token $TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -d "{\"name\":\"$REPO\",\"private\":false,\"description\":\"把任意书籍 PDF 转化为四层精读工作台的 Mira Agent Skill\"}" \
  > /dev/null && echo "   ✅ 仓库已创建" || echo "   ⚠️  仓库可能已存在,继续"

echo ">> [2/3] 配置远端"
git remote remove origin 2>/dev/null || true
git remote add origin "https://${TOKEN}@github.com/${USERNAME}/${REPO}.git"

echo ">> [3/3] 推送 main 分支"
git push -u origin main

echo "✅ 完成: https://github.com/$USERNAME/$REPO"

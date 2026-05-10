## Gallery & 审核流程

### 线上Gallery

地址: Brain API `/gallery`（需auth token登录）

Brain API已有完整Web看板体系：`/login` → `/dashboard`, `/quota`(号池), `/grok`, **`/gallery`**(绘图Gallery)。所有页面统一认证（token或密码），所有图片通过 `/gallery/static/` 按需加载。Gallery可按tag筛选，点击放大查看。

访问方式：
- 浏览器: `http://<server>:8080/login` → 登录 → 点击Gallery导航
- API: `curl -H "Authorization: Bearer <token>" http://<server>:8080/gallery`

⚠️ **所有web页面统一走Brain API**（8080端口），不在VPS开新端口，不在HF Space部署Gallery。

### 审核入库流程

Gallery每张demo图卡有三个交互按钮，通过 `/api/gallery/feedback` API写入反馈：
- ✓ Approve → `{action: "approve"}`
- ✎ Suggest → 展开textarea输入建议 → `{action: "suggest", suggestion: "..."}`
- ✕ Reject → `{action: "reject"}`

反馈记录在绘图库工作目录的 `gallery_feedback.jsonl`，当前仓库默认使用
`../03_plotting-library/gallery_feedback.jsonl`。

1. 生成新样图后，渲染demo保存到 `../03_plotting-library/demo_fig/`
2. 重启Brain API: `systemctl restart hermes-serve`
3. 通知用户访问 `/gallery` 查看，点击按钮反馈
4. 用户确认"可以/入库" → 执行：
   - 脚本存 `templates/`, mock数据存 `demo_data/`
   - 更新 `catalog.yaml`
   - recipe存 `references/`
5. 用户说修改 → 按反馈改 → 重新渲染 → 再审

**未确认的图不入库。**

### 更新Gallery流程

```bash
cd ../03_plotting-library
for f in templates/*.R; do Rscript "$f"; done
systemctl restart hermes-serve
# 验证
curl -s -H "Authorization: Bearer <token>" http://127.0.0.1:8080/gallery | head -5
```

⚠️ **所有web页面统一走Brain API**（8080端口），不在VPS开新端口
⚠️ **Gallery需认证**，无token返回401
⚠️ **JS必须用 `extra_js` 参数传入 `_page()`** — f-string会破坏JS的`{{`/`}}`，见 `references/brain-gallery-deployment.md`
⚠️ **浏览器fetch用 `credentials: 'same-origin'`** — httponly cookie不可JS读取，靠浏览器自动带cookie+Origin

---

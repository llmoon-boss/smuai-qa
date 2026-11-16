# 用 Render（免费）+ 自有域名 moonllai.me 上线

> 目标：零服务器成本把「校园智能问答系统」发布到公网，用 `moonllai.me` 访问。
> 结论：**可行**，代码已改造完成并实测通过（本地 SQLite 模式等价环境跑通问答、登录、增删改查）。
> 主要代价：免费实例 15 分钟无访问会休眠，冷启动约 30–60 秒；运行期数据（反馈、日志、后台新增问答）**随部署重置**。

---

## 一、为 Render 做的改造（已完成）

| 文件 | 改动 | 原因 |
| --- | --- | --- |
| `db.py` | 新增 SQLite 适配层：`SMU_DB_ENGINE=sqlite` 时用 SQLite，接口与 pymysql 完全一致（`%s` 占位、字典行、`cursor()` 上下文） | Render 免费实例没有 MySQL/Postgres 免费额度，SQLite 免部署、免连接串 |
| `schema.sql` | 不变（MySQL 方言），由 `db.py` 运行时自动翻译成 SQLite 建表语句 | 一份 schema 两种库，避免双份维护 |
| `wsgi.py`（新增） | gunicorn 入口，导入时执行 `init_db()`：建表 + 写入 104 条种子问答 + 管理员账号 | 免费实例每次启动都是新容器，必须能自举 |
| `render.yaml`（新增） | Blueprint：free 计划、`pip install -r requirements.txt`、`gunicorn -w 1 -k gthread --threads 4`、环境变量清单 | 控制台点选即可，不用手填命令 |
| `requirements.txt` | 精简为线上必需（flask/requests/gunicorn/waitress/pymysql/cryptography）；采集与演示站依赖移到 `requirements-extra.txt` | 构建从 1 分钟降到十几秒，512MB 内存更宽松 |
| `config.py` | 新增 `SMU_DB_ENGINE`、`SMU_DB_PATH`、`SMU_COOKIE_SECURE` | 引擎切换与 HTTPS Cookie |
| `app.py` | 限流取真实客户端 IP：优先 `X-Forwarded-For` 首位；支持 `SESSION_COOKIE_SECURE` | Render 前面有反向代理，否则所有人都算同一个 IP，30 次/分钟会被全站共享 |
| `templates/index.html` + `style.css` | 页脚加声明「毕业设计作品，非学校官方系统，内容取自学校公开文件，仅供参考」 | 公网可见，避免被误认为学校官方系统 |

本地等价环境实测（`SMU_DB_ENGINE=sqlite`，8100 端口，以及 `git clone` 出的干净目录 + 8101 端口）：

- `GET /` → 200；`POST /api/chat`（`{"question":"重修怎么报名"}`）→ `source=kb`，命中标准答案
- `POST /api/login` admin → 200；`GET /api/qa` → 104 条，分页/关键词搜索正常
- 新增 → 修改 → 删除问答；注册用户 → 提交反馈 → 后台 `LEFT JOIN` 反馈列表；`GET /api/logs` 时间字段正常

---

## 二、推到 GitHub（Render 需要 Git 仓库）

仓库已在本地初始化并提交（`git log` 可见首个提交），工作目录：`D:\学年设计\sumai`。

1. 打开 <https://github.com/new>，Repository name 填 `smuai-qa`，**Private 或 Public 都可以**（Private 需在 Render 授权该仓库），不要勾选任何初始化文件。
2. 在 `D:\学年设计\sumai` 下执行（把 `你的GitHub用户名` 换成实际值）：

```powershell
git remote add origin https://github.com/你的GitHub用户名/smuai-qa.git
git branch -M main
git push -u origin main
```

首次 push 会弹浏览器授权，按提示登录即可。

> 已确认 `.gitignore` 排除了 `.env`（含 API Key 与数据库密码）、`kb_cookies.json`、`.venv`、`smudata/`、`shots/` 与 3 个大 JSON 语料；推送内容只有 95 个源码/文档文件。

---

## 三、在 Render 建服务

### 方式 A：Blueprint（推荐，配置全在 render.yaml 里）

1. 注册 <https://render.com>（可用 GitHub 账号登录，免信用卡）。
2. 控制台右上 **New → Blueprint**，选择刚推上去的 `smuai-qa` 仓库，`Blueprint Name` 随意。
3. 点 **Apply**。Render 会读取 `render.yaml` 自动创建 Web Service（Free 计划、Python 3.12.8、启动命令已内置）。
4. 首次部署若提示需要填 `SMU_LLM_API_KEY`、`SMU_ADMIN_PASSWORD`（`sync: false` 的变量），在服务的 **Environment** 页填写后 Save，会触发重新部署。

### 方式 B：手动建 Web Service

1. **New → Web Service** → 选仓库。
2. 按下表填写：

| 项 | 值 |
| --- | --- |
| Language | Python 3 |
| Region | Singapore（离国内最近；没有则选 Oregon） |
| Branch | main |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn -w 1 -k gthread --threads 4 -b 0.0.0.0:$PORT wsgi:app --timeout 120` |
| Instance Type | Free |
| Health Check Path | `/` |

3. **Environment** 里逐个添加（见下一节），然后 Create。

### 环境变量

| 变量 | 值 | 说明 |
| --- | --- | --- |
| `PYTHON_VERSION` | `3.12.8` | Blueprint 已设 |
| `SMU_DB_ENGINE` | `sqlite` | 必须，否则会去连 MySQL |
| `SMU_DB_PATH` | `/tmp/smu_ai.db` | 免费实例只有 `/tmp` 可写 |
| `SMU_SECRET_KEY` | 随机 64 位 hex | Blueprint 用 `generateValue` 自动生成 |
| `SMU_LLM_API_KEY` | 你的 DeepSeek Key | **先撤销旧 Key 再生成新的**（旧 Key 曾出现在本地 .env） |
| `SMU_ADMIN_PASSWORD` | 强密码（≥12 位） | 首次建库时写入管理员账号 |
| `SMU_COOKIE_SECURE` | `1` | 强制 HTTPS Cookie |
| `SMU_RATE_PER_MIN` | `20` | 每 IP 每分钟问答上限，护住模型额度 |

部署完成后会拿到形如 `https://smuai-qa.onrender.com` 的地址，先直接访问验证。

---

## 四、绑定 moonllai.me（阿里云域名 → Render）

### 1. 在 Render 添加域名

服务页 → **Settings → Custom Domains → Add Custom Domain**，依次添加：

- `moonllai.me`（根域名）
- `www.moonllai.me`（子域名）

每添加一个，Render 会显示**需要你去 DNS 商添加的记录**（记录类型 / 主机记录 / 记录值）。**以控制台显示的值为准**，下面是常见形态：

| 主机记录 | 类型 | 记录值 |
| --- | --- | --- |
| `@` | A | `216.24.57.1`（Render 全局入口 IP，控制台会显示确切值） |
| `www` | CNAME | `smuai-qa.onrender.com` |

> 阿里云云解析不支持 CNAME 用于根域名（`@`），所以根域名必须用 A 记录；若 Render 日后更换入口 IP，需要同步改这条 A 记录。

### 2. 在阿里云添加解析

1. 登录 <https://dns.console.aliyun.com> → 找到 `moonllai.me` → **解析设置**。
2. **添加记录**，按上表逐条填写；TTL 选 `10 分钟`（600 秒，便于回滚）。
3. 若 Render 提示需要 **TXT 验证记录**（域名此前绑定过别的 Render 账号时才会出现），照抄控制台给的主机记录与值再添加一条 TXT。

### 3. 证书与生效

- DNS 生效通常 5–30 分钟（`nslookup moonllai.me` 能看到 Render 的 IP 即已生效）。
- Render 自动为域名签发 Let's Encrypt 证书，证书状态变为 **Issued** 后 `https://moonllai.me` 即可访问。
- 建议在 Render 把 `moonllai.me` 设为 **Redirect to www**（或反之），只保留一个主域，避免 Cookie 与 SEO 分散。

### 4. 备案说明（重要）

ICP 备案只针对**中国大陆境内服务器**。Render 的服务器在美国/新加坡，域名解析到境外**不需要备案**，也不会被阿里云拦截。
但相应地：国内访问无 CDN 加速，首屏一般 1–3 秒；如后续要提速，可在这两个方案里选一个——
- 阿里云 CDN/ESA 加速（需备案）；
- 用 Cloudflare 免费版代理（把 NS 转到 Cloudflare，A 记录指向 Render，开启橙云），国内可走部分优化节点。

域名侧只需保证两点：**已完成实名认证**（未认证的域名会被暂停解析）、域名为 `moonllai.me` 且状态正常。

---

## 五、上线验收清单

部署完成后逐条过一遍（把域名换成 `moonllai.me`）：

```powershell
# 1. 首页（应为 200，含卡通界面与页脚声明）
curl.exe -I https://moonllai.me/

# 2. 知识库问答（应返回 ok=true 且 source=kb）
curl.exe -s -X POST https://moonllai.me/api/chat -H "Content-Type: application/json" -d '{"question":"重修怎么报名"}'

# 3. 后台登录（应返回 ok=true）
curl.exe -s -X POST https://moonllai.me/api/login -H "Content-Type: application/json" -d '{"username":"admin","password":"你的新密码"}'

# 4. 未登录访问后台接口（应返回 401）
curl.exe -s -o NUL -w "%{http_code}" https://moonllai.me/api/qa
```

浏览器侧再确认：`https://moonllai.me/` 打开正常、点样例问题有答案、`/admin` 用新密码能登录、手机窄屏布局不溢出。

---

## 六、免费额度的限制（务必知道）

| 项目 | 免费实例实际情况 | 对本项目的影响 |
| --- | --- | --- |
| 规格 | 512 MB 内存 / 0.1 CPU | 够用：单 worker + 4 线程，索引在内存里只有几百 KB |
| 休眠 | 15 分钟无请求自动休眠 | 冷启动 30–60 秒；答辩演示前先自己访问一次预热 |
| 运行时长 | 750 实例小时/月 | 单服务 24 小时常驻正好 720 小时，不超 |
| 磁盘 | **临时文件系统**，部署/重启重置 | `/tmp/smu_ai.db` 会回到「104 条种子数据 + 初始管理员」；用户反馈、聊天日志、后台新增问答会丢 |
| 数据库 | 免费 Postgres 30 天后过期 | 本方案不用，改用 SQLite 自举，绕开这个坑 |
| 出站 | 不限 | 大模型兜底调用正常 |

**想让问答修改持久化**，三选一：
1. 把后台改好的问答导出，直接写进 `db.py` 的 `SEED_QA` 再 push（零成本，适合毕设）；
2. 换免费 Postgres（Neon / Supabase）并把 `db.py` 的适配层扩一个 psycopg 分支（工作量约半天）；
3. 升级 Render 付费实例 + 挂载 Disk（约 $7/月起）。

---

## 七、安全与合规（必做）

1. **立刻轮换 DeepSeek API Key**：旧 Key 曾以明文存在于本地 `.env`，且出现在此前的对话与截图中。到 <https://platform.deepseek.com/api_keys> 删除旧 Key、新建一个，只填到 Render 的 `SMU_LLM_API_KEY`。
2. **改管理员密码**：`SMU_ADMIN_PASSWORD` 设成强密码；上线后不要再使用 `admin123`。
3. **保持限流开启**：`SMU_RATE_PER_MIN=20`，避免被脚本刷光模型额度。
4. **数据来源声明**：页脚已注明「非学校官方系统、内容取自学校公开文件、仅供参考」；若学校要求，改为不公开或加访问口令。
5. **不要暴露后台入口**：如需更严格，可在 Render 加一条 Path-based 规则或改用随机后台路径。

---

## 八、备选免费平台（如果 Render 体验不佳）

| 平台 | 优点 | 缺点 |
| --- | --- | --- |
| **Koyeb** | 免费 1 个 Web 服务，不休眠 | 需信用卡验证 |
| **Hugging Face Spaces** | 完全免费、Docker 可跑、不休眠（限 2 核 16G） | 域名是 `*.hf.space`，绑自定义域名需付费 |
| **Fly.io** | 免费额度可跑小应用 | 需绑卡，配置稍复杂 |
| **Railway** | 部署体验最好 | 只有 5 美元试用额度，之后按量计费 |

结论：**Render 免费实例 + SQLite 自举**是当前零成本方案里最省心的组合，代价只是休眠冷启动与运行期数据不持久。

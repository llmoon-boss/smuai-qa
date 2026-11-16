# SMUAI 网站发布指南

> 结论：**能发布**。应用本身已经是可部署形态，本机以生产模式（waitress，0.0.0.0:8000）跑通并通过全部接口自测。
> 但发布前有 3 类问题必须先处理：**密钥/口令**（安全）、**学校授权与隐私**（合规）、**域名备案与端口**（网络）。

---

## 一、本次已经改好的东西（代码层面）

| 改动 | 文件 | 说明 |
|---|---|---|
| 配置全部走环境变量 + 支持本地 `.env` | `config.py` | 原来 DB 密码、大模型 Key、管理员口令写死在源码里，一上传就泄露 |
| 会话密钥随机化 | `config.py` / `app.py` | 原来固定 `"smu-ai-dev-secret"`，任何人都能伪造管理员 session |
| Session Cookie 加固 | `app.py` | HttpOnly + SameSite=Lax + 请求体上限 1MB |
| 问答限流 | `app.py` | 同一 IP 每分钟 30 次（`SMU_RATE_PER_MIN` 可调），防止公网被刷爆大模型额度 |
| 监听地址可配置 | `app.py` | 原来写死 `172.27.157.250:5000`，换机器直接起不来；改为 `0.0.0.0:8000`（可覆盖） |
| 生产启动入口 | `deploy/run_prod.py` | waitress 多线程，Windows/Linux 通用 |
| Nginx / systemd / Docker | `deploy/` | 反向代理、开机自启、一条命令起「应用+MySQL」 |
| 演示站去绝对路径 | `demo_web.py` / `kbsearch.py` | 原来写死 `D:\学年设计\sumai`，拷到服务器就跑不了；改为相对脚本目录 |
| 依赖清单补全 | `requirements.txt` | 补 waitress / gunicorn / jieba / rank_bm25 / numpy（演示站必需，之前只装在全局 Python 里） |
| 忽略敏感文件 | `.gitignore` | `.env`、`kb_cookies.json` 不进版本库 |

---

## 二、三种发布路线，按你的场景选

| 路线 | 目标 | 成本 | 适合 |
|---|---|---|---|
| **A 校园网/局域网** | 同学、老师在同一网络访问 | 0 元 | 答辩现场演示、给指导老师看 |
| **B 云服务器 + 域名** | 公网任何人访问 | 学生机 ~10 元/月 + 域名 ~30 元/年 | 真·上线，写进论文「已部署上线」 |
| **C Docker 一键** | 云上最快复刻、换机器不折腾 | 同上 | 你已经会 Docker 时最快 |

另外：**毕业设计演示站**（`demo_web.py`，单页问答，不需要 MySQL）也修好可发布了，适合「给评委一个链接直接点开看」。

---

## 三、路线 A：本机 / 校园网（5 分钟，答辩首选）

前置：MySQL 8.0 已安装并运行（本机已确认在跑，库 `smu_ai` 有 105 条问答对）。

```powershell
cd D:\学年设计\sumai
.venv\Scripts\python.exe -m pip install -r requirements.txt
copy .env.example .env        # 已生成过 .env 就跳过
# 编辑 .env：SMU_SECRET_KEY 已自动生成，确认 SMU_DB_PASSWORD / SMU_LLM_API_KEY
.venv\Scripts\python.exe deploy\run_prod.py
```

访问：

- 本机：<http://127.0.0.1:8000>
- 同一 Wi-Fi 下的手机/笔记本：`http://172.27.157.250:8000`（这是本机 WLAN 地址，换网络会变）

首次对外访问要在**管理员 PowerShell**里放行端口：

```powershell
netsh advfirewall firewall add rule name="SMUAI 8000" dir=in action=allow protocol=TCP localport=8000
```

> 坑：校园 Wi-Fi 常开 AP 隔离，手机可能连不上电脑。答辩现场优先用**手机热点**（电脑和手机同热点）或直接本机演示 + 截图。

---

## 四、路线 B：云服务器 + 域名（公网长期）

### 1. 买机器
1 核 2G 学生机（阿里云/腾讯云，Ubuntu 22.04）足够：单机 QPS 个位数、内存占用 < 200MB。

### 2. 装环境
```bash
sudo apt update && sudo apt install -y python3-venv python3-pip nginx mysql-server
sudo mysql -e "CREATE DATABASE smu_ai CHARACTER SET utf8mb4; CREATE USER 'smu'@'localhost' IDENTIFIED BY '强密码'; GRANT ALL ON smu_ai.* TO 'smu'@'localhost';"
```

### 3. 传代码并启动
```bash
sudo mkdir -p /opt/smuai && sudo chown $USER /opt/smuai
# 用 scp / git / 宝塔面板把项目传到 /opt/smuai（不要传 .venv）
cd /opt/smuai && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env && nano .env      # SMU_DB_HOST=127.0.0.1、强密码、SMU_SECRET_KEY
sudo cp deploy/smuai.service /etc/systemd/system/ && sudo systemctl enable --now smuai
```

### 4. Nginx + HTTPS
```bash
sudo cp deploy/nginx.conf /etc/nginx/conf.d/smuai.conf
sudo nano /etc/nginx/conf.d/smuai.conf    # 改 server_name 为你的域名
sudo nginx -t && sudo systemctl reload nginx
sudo apt install -y certbot python3-certbot-nginx && sudo certbot --nginx -d your-domain.com
```

### 5. 安全组放行
只放 22 / 80 / 443。**MySQL 的 3306 绝对不要对公网开放。**

### 6. 备案（大陆机器必看）
大陆服务器 **80/443 未备案会被拦截**。毕设演示有两个替代方案：
- 用非标端口（如 `listen 8080`，并在安全组放行 8080）；
- 或买香港/海外轻量服务器（不需要备案，延迟略高）。

---

## 五、路线 C：Docker 一键（推荐给云上复刻）

```bash
cd /opt/smuai
docker compose -f deploy/docker-compose.yml up -d --build
docker compose -f deploy/docker-compose.yml logs -f app
```

- 容器内 `SMU_DB_HOST=db` 由 compose 自动注入，本地 `.env` 里的 127.0.0.1 不会生效，别改错。
- 数据在 `dbdata` 卷里；备份：`docker exec -it <db容器> mysqldump -uroot -p smu_ai > backup.sql`。

---

## 六、发布前**必须**做的 5 件事

1. **轮换大模型 Key（最高优先级）**
   原来 `config.py` 里那把 `sk-83592a...` 已经以明文出现在对话记录中，视为已泄露。去 <https://platform.deepseek.com> 作废并新建，只写进 `.env`。

2. **改管理员密码**
   现在默认 `admin / admin123`，且系统没有改密界面。执行：
   ```powershell
   .venv\Scripts\python.exe -c "from werkzeug.security import generate_password_hash as g; print(g('你的新密码'))"
   ```
   ```sql
   UPDATE admin SET password_hash='粘贴上面那串' WHERE username='admin';
   ```

3. **改数据库口令**
   `root/123456` 只适合本机。公网机器用独立账号 + 强密码，并确认 MySQL 只监听 127.0.0.1。

4. **合规与隐私**
   - 语料来自学校官网公开文件：毕设研究与答辩交流没问题；**公网长期对外运营需要学校宣传/教务部门同意**。
   - 系统会存用户名、昵称、密码哈希、聊天记录、反馈：属于个人信息，需在首页放**隐私说明**（收集什么、存多久、怎么删）。
   - 答辩演示建议：只开**演示账号**，或先把 `chat_logs`/`users` 清一遍再演示。

5. **加免责声明**
   首页页脚加一行：「本系统为毕业设计作品演示，答复仅供参考，以学校官方通知为准。」公网跑大模型兜底时尤其必要。

---

## 七、我实际跑过的验收结果（本次实测）

| 检查项 | 结果 |
|---|---|
| `GET /` | 200，3180 字节 |
| `GET /admin` | 200，2988 字节 |
| `POST /api/chat`（图书馆开放时间） | 200，`source=kb`，返回馆舍时间答案 |
| `POST /api/chat`（重修怎么申请） | 200，`source=kb` |
| 限流（`SMU_RATE_PER_MIN=3` 连发 5 次） | `200,200,200,429,429` ✅ |
| `POST /api/login` admin | 200 `{"ok":true}` |
| `GET /api/qa?page=1` | 200，5 行 |
| `GET /api/logs` | 200，50 行 |
| `GET /api/feedbacks` | 200 |
| 局域网地址 `http://172.27.157.250:8000` | 200 ✅ |
| 演示站 `http://127.0.0.1:8010` 与 `/api/ask` | 200，526 文档 / 1792 块 |

---

## 八、发布后仍会遇到的不足（写进论文「局限」正好）

- 无 CSRF token（SameSite=Lax 只缓解，不根治）；
- 检索是「关键词 + 标题」匹配，不是向量检索，口语化问法会漏召回（毕业设计要接 bge-m3）；
- 无 HTTPS、无监控告警、无日志轮转（Nginx 层可解）；
- 单进程 + 内存限流，多实例部署时限额不共享（需 Redis）；
- 后台无「改密/审计」功能，靠 SQL 维护。

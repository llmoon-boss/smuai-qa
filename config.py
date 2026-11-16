import os

#读取本地 .env（存在则加载；不引入额外依赖）
_ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(_ENV_PATH):
    with open(_ENV_PATH, encoding="utf-8") as _f:
        for _line in _f:
            _line = _line.strip()
            if not _line or _line.startswith("#") or "=" not in _line:
                continue
            _key, _val = _line.split("=", 1)
            os.environ.setdefault(_key.strip(), _val.strip().strip('"').strip("'"))

#数据库
DB_CONFIG = {
    "host": os.getenv("SMU_DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("SMU_DB_PORT", "3306")),
    "user": os.getenv("SMU_DB_USER", "root"),
    "password": os.getenv("SMU_DB_PASSWORD", "123456"),
    "database": os.getenv("SMU_DB_NAME", "smu_ai"),
    "charset": "utf8mb4",
}
#数据库引擎：mysql（本地默认）或 sqlite（Render 等无 MySQL 的免费环境）
DB_ENGINE = os.getenv("SMU_DB_ENGINE", "mysql").strip().lower()
DB_PATH = os.getenv(
    "SMU_DB_PATH",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "smu_ai.db"),
)
LLM_CONFIG = {
    "api_key": os.getenv("SMU_LLM_API_KEY", ""),
    "base_url": os.getenv("SMU_LLM_BASE_URL", "https://api.deepseek.com"),
    "model": os.getenv("SMU_LLM_MODEL", "deepseek-chat"),
    "timeout": 15,        #请求超时（秒）
    "max_tokens": 500,    #回答最大长度
    "temperature": 0.7,   #生成随机性，越小越稳定
}
MOCK_ANSWER = (
    "（未配置大模型 API Key，以下为模拟回答）关于「{question}」，"
    "建议查阅学校官网通知或咨询辅导员。"
)
#会话密钥：发布前必须在 .env 中改成随机长串
SECRET_KEY = os.getenv("SMU_SECRET_KEY", "smu-ai-dev-secret")
# 线上（HTTPS）建议开启：SMU_COOKIE_SECURE=1
COOKIE_SECURE = os.getenv("SMU_COOKIE_SECURE", "0").strip() in ("1", "true", "yes")
#管理员账号（首次建库时写入，之后改库不生效）
DEFAULT_ADMIN = {
    "username": os.getenv("SMU_ADMIN_USER", "admin"),
    "password": os.getenv("SMU_ADMIN_PASSWORD", "admin123"),
}
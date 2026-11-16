-- SMUAI 数据库结构（学年设计简版）
-- 启动 python app.py 时会自动执行本文件（幂等）；
-- 也可手动执行：mysql -u root -p smu_ai < schema.sql

CREATE TABLE IF NOT EXISTS qa_pairs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question VARCHAR(255) NOT NULL COMMENT '问题',
    answer TEXT NOT NULL COMMENT '标准答案',
    keywords VARCHAR(255) DEFAULT '' COMMENT '检索关键词，逗号分隔',
    category VARCHAR(50) DEFAULT '其他' COMMENT '分类',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='校园知识库（问答对）';

CREATE TABLE IF NOT EXISTS chat_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_question VARCHAR(500) NOT NULL COMMENT '用户问题',
    reply_source VARCHAR(20) NOT NULL COMMENT '回答来源：kb=知识库，llm=大模型',
    answer TEXT NOT NULL COMMENT '系统回答',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '提问时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='聊天记录';

CREATE TABLE IF NOT EXISTS admin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希（werkzeug 生成）'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='管理员账号';

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '登录用户名',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希（werkzeug 生成）',
    nickname VARCHAR(50) NOT NULL DEFAULT '' COMMENT '昵称/姓名',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='普通用户';

CREATE TABLE IF NOT EXISTS feedbacks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '提交用户 ID',
    content VARCHAR(1000) NOT NULL COMMENT '反馈内容',
    status TINYINT DEFAULT 0 COMMENT '状态：0=待处理，1=已处理',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '提交时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户反馈';

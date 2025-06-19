-- データベースの作成（Azure Portalで作成済みの場合は不要）
CREATE DATABASE roro_phase2
  WITH ENCODING='UTF8'
       LC_COLLATE='en_US.UTF-8'
       LC_CTYPE='en_US.UTF-8'
       CONNECTION LIMIT=-1;

-- スキーマの作成
CREATE SCHEMA IF NOT EXISTS roro AUTHORIZATION postgres;

-- ユーザーテーブル
CREATE TABLE roro.users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE,
  display_name VARCHAR(100),
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO roro.users (b2c_object_id, email, display_name)
VALUES (
  '11111111-aaaa-bbbb-cccc-1234567890ab',
  'user1@example.com',
  'User One'
);

-- user_auth_providers テーブル（外部認証プロバイダー情報）
CREATE TABLE roro.user_auth_providers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES roro.users(id) ON DELETE CASCADE,
  provider_name VARCHAR(50) NOT NULL, -- 例: 'google', 'github', 'azure_b2c', 'auth0', 'local'
  provider_user_id VARCHAR(255) NOT NULL,
  access_token TEXT,
  refresh_token TEXT,
  expires_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (provider_name, provider_user_id)
);


-- カテゴリーテーブル
CREATE TABLE roro.categories (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) NOT NULL UNIQUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 質問テーブル
CREATE TABLE roro.questions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  category_id UUID NOT NULL REFERENCES roro.categories(id) ON DELETE CASCADE,
  text TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 選択肢テーブル
CREATE TABLE roro.choices (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  question_id UUID NOT NULL REFERENCES roro.questions(id) ON DELETE CASCADE,
  text TEXT NOT NULL,
  is_correct BOOLEAN DEFAULT FALSE
);

-- アンケート提出テーブル
CREATE TABLE roro.survey_submissions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES roro.users(id) ON DELETE CASCADE,
  submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  score INTEGER
);

-- インデックスの作成
CREATE INDEX idx_users_email ON roro.users(email);
CREATE INDEX idx_questions_category_id ON roro.questions(category_id);
CREATE INDEX idx_choices_question_id ON roro.choices(question_id);
CREATE INDEX idx_survey_submissions_user_id ON roro.survey_submissions(user_id);

-- ユーザーの初期データ
INSERT INTO roro.users (email, hashed_password)
VALUES
  ('admin@example.com', 'hashed_admin_password'),
  ('user1@example.com', 'hashed_user1_password');

-- カテゴリーの初期データ
INSERT INTO roro.categories (name)
VALUES
  ('General'),
  ('Feedback'),
  ('Product');

-- 質問の初期データ
INSERT INTO roro.questions (category_id, text)
SELECT id, 'How satisfied are you with our service?'
FROM roro.categories WHERE name = 'Feedback';

-- 選択肢の初期データ
INSERT INTO roro.choices (question_id, text, is_correct)
SELECT q.id, c.text, c.is_correct
FROM roro.questions q
JOIN (
  VALUES
    ('Very satisfied', FALSE),
    ('Satisfied', FALSE),
    ('Neutral', FALSE),
    ('Dissatisfied', FALSE),
    ('Very dissatisfied', FALSE)
) AS c(text, is_correct) ON TRUE
WHERE q.text = 'How satisfied are you with our service?';

-- アンケート提出のサンプルデータ
INSERT INTO roro.survey_submissions (user_id, submitted_at, score)
SELECT u.id, CURRENT_TIMESTAMP, 85
FROM roro.users u
WHERE u.email = 'user1@example.com';

CREATE TABLE roro.reports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES roro.users(id) ON DELETE CASCADE,
  title VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  file_url TEXT NOT NULL
);

CREATE INDEX idx_reports_user_id ON roro.reports(user_id);

CREATE TABLE roro.payments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES roro.users(id) ON DELETE CASCADE,
  amount NUMERIC(10, 2) NOT NULL,
  currency VARCHAR(10) NOT NULL,
  payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  payment_method VARCHAR(50),
  status VARCHAR(20) NOT NULL
);

CREATE INDEX idx_payments_user_id ON roro.payments(user_id);

CREATE TABLE roro.audit_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES roro.users(id) ON DELETE SET NULL,
  action VARCHAR(100) NOT NULL,
  description TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_user_id ON roro.audit_logs(user_id);

INSERT INTO roro.reports (user_id, title, file_url)
SELECT id, 'Monthly Report - January', 'https://storage.example.com/reports/january.pdf'
FROM roro.users
WHERE email = 'user1@example.com';

INSERT INTO roro.payments (user_id, amount, currency, payment_method, status)
SELECT id, 99.99, 'USD', 'Credit Card', 'Completed'
FROM roro.users
WHERE email = 'user1@example.com';

INSERT INTO roro.audit_logs (user_id, action, description)
SELECT id, 'Login', 'User logged in successfully.'
FROM roro.users
WHERE email = 'user1@example.com';


CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE roro.notifications (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id          UUID NOT NULL
                     REFERENCES roro.users(id) ON DELETE CASCADE,
    notif_type       VARCHAR(40)  NOT NULL,              -- ex: report_ready
    title            TEXT         NOT NULL,
    body             TEXT         NOT NULL,
    metadata         JSONB,                               -- 任意追加情報
    is_read          BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    read_at          TIMESTAMPTZ
);

-- 通知一覧を効率化
CREATE INDEX idx_notifications_user_created
    ON roro.notifications (user_id, created_at DESC);

-- JSONB に対する全文検索を想定
CREATE INDEX idx_notifications_metadata_gin
    ON roro.notifications USING GIN (metadata);

INSERT INTO roro.notifications
(user_id, notif_type, title, body, metadata)
VALUES
('11111111-aaaa-bbbb-cccc-1234567890ab','report_ready',
 'レポート生成完了',
 'あなたのペットレポートが生成されました。アプリで確認してください。',
 '{"reportId":"REP-20250525-001"}');

CREATE TABLE roro.user_settings (
    user_id          UUID PRIMARY KEY
                     REFERENCES roro.users(id) ON DELETE CASCADE,
    email_notifications BOOLEAN   NOT NULL DEFAULT TRUE,
    theme            VARCHAR(20)  NOT NULL DEFAULT 'light' 
                     CHECK (theme IN ('light','dark')),
    locale           VARCHAR(5)   NOT NULL DEFAULT 'en',
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_user_settings_locale
    ON roro.user_settings (locale);

INSERT INTO roro.user_settings (user_id, email_notifications, theme, locale)
VALUES
('11111111-aaaa-bbbb-cccc-1234567890ab', TRUE, 'dark', 'ja');

CREATE TABLE roro.api_keys (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id          UUID NOT NULL
                     REFERENCES roro.users(id) ON DELETE CASCADE,
    service_name     VARCHAR(60) NOT NULL,               -- ex: "twitter"
    key_hash         CHAR(64)   NOT NULL,                -- SHA-256 など
    scopes           TEXT[]      NOT NULL DEFAULT '{}',
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_used_at     TIMESTAMPTZ
);

-- 同一キー重複防止
CREATE UNIQUE INDEX uq_api_keys_hash
    ON roro.api_keys (key_hash);

CREATE INDEX idx_api_keys_user_service
    ON roro.api_keys (user_id, service_name);

INSERT INTO roro.api_keys (user_id, service_name, key_hash, scopes)
VALUES
('11111111-aaaa-bbbb-cccc-1234567890ab','openai',
 '8c6976e5b541...d7f5a', ARRAY['chat','embedding']);

CREATE TABLE roro.webhooks (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id          UUID NOT NULL
                     REFERENCES roro.users(id) ON DELETE CASCADE,
    endpoint_url     TEXT     NOT NULL,
    secret_token     TEXT     NOT NULL,
    event_types      TEXT[]   NOT NULL DEFAULT '{}',     -- ex: ['report_ready']
    is_active        BOOLEAN  NOT NULL DEFAULT TRUE,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_webhooks_user_active
    ON roro.webhooks (user_id, is_active);

CREATE TABLE roro.attachments (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id            UUID NOT NULL
                       REFERENCES roro.users(id) ON DELETE CASCADE,
    submission_id      UUID
                       REFERENCES roro.survey_submission(id) ON DELETE SET NULL,
    file_name          TEXT      NOT NULL,
    blob_path          TEXT      NOT NULL,      -- Azure Blob のパス
    content_type       VARCHAR(60),
    file_size          BIGINT    NOT NULL CHECK (file_size >= 0),
    uploaded_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_attachments_user_uploaded
    ON roro.attachments (user_id, uploaded_at DESC);

INSERT INTO roro.attachments
(user_id, submission_id, file_name, blob_path, content_type, file_size)
VALUES
('11111111-aaaa-bbbb-cccc-1234567890ab',
 '22222222-bbbb-cccc-dddd-1234567890ab',
 'report.pdf',
 'reports/2025/05/report-001.pdf',
 'application/pdf',
 1048576);

CREATE TABLE roro.login_history (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id        UUID NOT NULL
                   REFERENCES roro.users(id) ON DELETE CASCADE,
    login_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ip_address     INET        NOT NULL,
    user_agent     TEXT,
    is_successful  BOOLEAN     NOT NULL
);

CREATE INDEX idx_login_history_user_time
    ON roro.login_history (user_id, login_at DESC);

INSERT INTO roro.login_history (
  user_id, login_at, ip_address, user_agent, is_successful
)
SELECT id, NOW(), '192.168.1.100', 'Mozilla/5.0', TRUE
FROM roro.users
WHERE email = 'user1@example.com';

CREATE TYPE feedback_status AS ENUM ('new', 'in_progress', 'closed');


CREATE TABLE roro.feedback (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES roro.users(id) ON DELETE SET NULL,
  category VARCHAR(40) NOT NULL CHECK (char_length(category) <= 40),
  message TEXT NOT NULL CHECK (char_length(message) <= 5000),
  status feedback_status NOT NULL DEFAULT 'new',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_feedback_status_created
  ON roro.feedback (status, created_at DESC);

INSERT INTO roro.feedback (
  user_id, category, message, status
)
SELECT id, 'UI', 'The dashboard layout is confusing.', 'new'
FROM roro.users
WHERE email = 'user1@example.com';


CREATE TABLE roro.roles (
    id          SERIAL PRIMARY KEY,
    role_name   VARCHAR(40) UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE roro.user_roles (
    user_id   UUID  NOT NULL
              REFERENCES roro.users(id)  ON DELETE CASCADE,
    role_id   INT   NOT NULL
              REFERENCES roro.roles(id)  ON DELETE CASCADE,
    granted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id, role_id)
);

-- 権限チェック用
CREATE INDEX idx_user_roles_user
    ON roro.user_roles (user_id);

INSERT INTO roro.roles (role_name, description)
VALUES
 ('admin','システム管理者'),
 ('staff','社内スタッフ');

INSERT INTO roro.user_roles (user_id, role_id)
VALUES
('11111111-aaaa-bbbb-cccc-1234567890ab', 1);

INSERT INTO roro.user_roles (user_id, role_id)
SELECT u.id, r.id
FROM roro.users u
JOIN roro.roles r ON r.role_name = 'admin'
WHERE u.email = 'admin@example.com';
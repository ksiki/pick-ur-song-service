from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "outbox_events" (
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "id" UUID NOT NULL PRIMARY KEY,
    "event_type" VARCHAR(255) NOT NULL,
    "payload" JSONB NOT NULL,
    "status" VARCHAR(9) NOT NULL DEFAULT 'PENDING',
    "processed_at" TIMESTAMPTZ,
    "error_message" TEXT
);
CREATE INDEX IF NOT EXISTS "idx_outbox_even_event_t_a8360f" ON "outbox_events" ("event_type");
CREATE INDEX IF NOT EXISTS "idx_outbox_even_status_40a2f1" ON "outbox_events" ("status", "created_at");
COMMENT ON COLUMN "outbox_events"."status" IS 'PENDING: PENDING\nPROCESSED: PROCESSED\nFAILED: FAILED';
CREATE TABLE IF NOT EXISTS "accounts" (
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "id" UUID NOT NULL PRIMARY KEY,
    "email" VARCHAR(255) NOT NULL UNIQUE,
    "password_hash" VARCHAR(255) NOT NULL,
    "is_email_verified" BOOL NOT NULL DEFAULT False,
    "legal_name" VARCHAR(255),
    "unp" VARCHAR(9),
    "iban" VARCHAR(28),
    "offer_accepted_at" TIMESTAMPTZ,
    "offer_accepted_ip" VARCHAR(45),
    "is_active" BOOL NOT NULL DEFAULT False
);
CREATE INDEX IF NOT EXISTS "idx_accounts_email_e90d21" ON "accounts" ("email");
COMMENT ON COLUMN "accounts"."legal_name" IS 'Юридическое лицо (ИП / ООО)';
COMMENT ON COLUMN "accounts"."unp" IS 'УНП';
COMMENT ON COLUMN "accounts"."iban" IS 'Расчетный счет (IBAN)';
COMMENT ON COLUMN "accounts"."is_active" IS 'Пройден ли юридический онбординг аккаунтом';
COMMENT ON TABLE "accounts" IS 'Модель бизнес-аккаунта (владельца сети заведений).';
CREATE TABLE IF NOT EXISTS "refresh_sessions" (
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "id" UUID NOT NULL PRIMARY KEY,
    "refresh_token_jti" VARCHAR(36) NOT NULL UNIQUE,
    "user_agent" VARCHAR(512) NOT NULL,
    "ip_address" VARCHAR(45) NOT NULL,
    "expires_at" TIMESTAMPTZ NOT NULL,
    "account_id" UUID NOT NULL REFERENCES "accounts" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_refresh_ses_refresh_d96db6" ON "refresh_sessions" ("refresh_token_jti");
COMMENT ON COLUMN "refresh_sessions"."user_agent" IS 'Браузер и ОС (например, Chrome on Linux)';
COMMENT ON COLUMN "refresh_sessions"."ip_address" IS 'IP адрес входа';
COMMENT ON COLUMN "refresh_sessions"."expires_at" IS 'Время, когда сессия протухнет';
COMMENT ON COLUMN "refresh_sessions"."account_id" IS 'Аккаунт владельца, которому принадлежит сессия';
COMMENT ON TABLE "refresh_sessions" IS 'Модель активной сессии авторизации аккаунта (Token Rotation).';
CREATE TABLE IF NOT EXISTS "player_domains" (
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "id" UUID NOT NULL PRIMARY KEY,
    "url" VARCHAR(255) NOT NULL UNIQUE,
    "max_capacity" INT NOT NULL DEFAULT 10,
    "is_active" BOOL NOT NULL DEFAULT True,
    "is_banned" BOOL NOT NULL DEFAULT False
);
CREATE INDEX IF NOT EXISTS "idx_player_doma_url_d6ca32" ON "player_domains" ("url");
COMMENT ON COLUMN "player_domains"."url" IS 'Уникальный URL технического домена';
COMMENT ON COLUMN "player_domains"."max_capacity" IS 'Максимальное количество заведений на один домен';
COMMENT ON COLUMN "player_domains"."is_active" IS 'Флаг активности домена (готов к приему баров)';
COMMENT ON COLUMN "player_domains"."is_banned" IS 'Флаг блокировки домена со стороны SoundCloud';
COMMENT ON TABLE "player_domains" IS 'Модель технического домена из пула для балансировки обращений к SoundCloud Widget API';
CREATE TABLE IF NOT EXISTS "venues" (
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "id" UUID NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "number" VARCHAR(15) NOT NULL,
    "address" VARCHAR(255) NOT NULL,
    "admin_passcode_hash" VARCHAR(255),
    "player_is_active" BOOL NOT NULL DEFAULT False,
    "is_active" BOOL NOT NULL DEFAULT True,
    "account_id" UUID NOT NULL REFERENCES "accounts" ("id") ON DELETE CASCADE,
    "assigned_domain_id" UUID REFERENCES "player_domains" ("id") ON DELETE SET NULL
);
COMMENT ON COLUMN "venues"."name" IS 'Коммерческое название заведения';
COMMENT ON COLUMN "venues"."number" IS 'Контактный телефон бара';
COMMENT ON COLUMN "venues"."address" IS 'Адрес вида: Беларусть, Гомель, Советская, 34';
COMMENT ON COLUMN "venues"."admin_passcode_hash" IS 'Хеш кодовой фразы для админской зоны конкретного бара';
COMMENT ON COLUMN "venues"."player_is_active" IS 'Нужно для того,\n        что бы нельзя было включать музыку в одном бару сразу с нескольких устройств';
COMMENT ON COLUMN "venues"."is_active" IS 'Активно ли конкретное заведение (можно выключить точку не удаляя аккаунт)';
COMMENT ON COLUMN "venues"."account_id" IS 'Владелец заведения (бизнес-аккаунт)';
COMMENT ON COLUMN "venues"."assigned_domain_id" IS 'Назначенный технический домен для SoundCloud плеера';
COMMENT ON TABLE "venues" IS 'Модель конкретного заведения (физической точки).';
CREATE TABLE IF NOT EXISTS "venue_schedules" (
    "id" UUID NOT NULL PRIMARY KEY,
    "day_of_week" SMALLINT NOT NULL,
    "open_time" TIMETZ,
    "close_time" TIMETZ,
    "is_day_off" BOOL NOT NULL DEFAULT False,
    "venue_id" UUID NOT NULL REFERENCES "venues" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_venue_sched_venue_i_7b1632" UNIQUE ("venue_id", "day_of_week")
);
COMMENT ON COLUMN "venue_schedules"."day_of_week" IS 'Day of the week (1 - Monday, 7 - Sunday)';
COMMENT ON COLUMN "venue_schedules"."open_time" IS 'Opening time';
COMMENT ON COLUMN "venue_schedules"."close_time" IS 'Closing time';
COMMENT ON COLUMN "venue_schedules"."is_day_off" IS 'Day off (the establishment is closed)';
CREATE TABLE IF NOT EXISTS "venue_settings" (
    "allow_explicit" BOOL NOT NULL DEFAULT False,
    "commission_fee_percent" DECIMAL(5,2) NOT NULL DEFAULT 50,
    "track_price" DECIMAL(10,2) NOT NULL DEFAULT 3,
    "track_price_no_queue" DECIMAL(10,2) NOT NULL DEFAULT 6,
    "timezone" VARCHAR(50) NOT NULL DEFAULT 'Europe/Minsk',
    "venue_id" UUID NOT NULL PRIMARY KEY REFERENCES "venues" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "venue_settings"."commission_fee_percent" IS 'Service commission in percentage (from 0.00 to 100.00)';
COMMENT ON COLUMN "venue_settings"."timezone" IS 'The time zone of the establishment (for example, Europe/Minsk)';
CREATE TABLE IF NOT EXISTS "payouts" (
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "id" UUID NOT NULL PRIMARY KEY,
    "period_start" DATE NOT NULL,
    "period_end" DATE NOT NULL,
    "total_amount" DECIMAL(10,2) NOT NULL,
    "status" VARCHAR(10) NOT NULL DEFAULT 'pending',
    "report_file_url" VARCHAR(512),
    "paid_at" TIMESTAMPTZ,
    "venue_id" UUID NOT NULL REFERENCES "venues" ("id") ON DELETE RESTRICT
);
COMMENT ON COLUMN "payouts"."total_amount" IS 'The amount to be paid to the venue (The sum of all venue_amount)';
COMMENT ON COLUMN "payouts"."status" IS 'Transfer status of funds';
COMMENT ON COLUMN "payouts"."report_file_url" IS 'Link to the generated PDF Report of the Agent in S3';
COMMENT ON COLUMN "payouts"."paid_at" IS 'The actual time of transfer to the IBAN of the venue';
CREATE TABLE IF NOT EXISTS "orders" (
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "id" UUID NOT NULL PRIMARY KEY,
    "guest_session_id" VARCHAR(255),
    "table_number" VARCHAR(20),
    "track_id" VARCHAR(255) NOT NULL,
    "track_title" VARCHAR(255) NOT NULL,
    "track_artist" VARCHAR(255) NOT NULL,
    "track_artwork_url" VARCHAR(512),
    "amount_total" DECIMAL(10,2) NOT NULL,
    "service_commission" DECIMAL(10,2) NOT NULL,
    "acquiring_fee" DECIMAL(10,2) NOT NULL DEFAULT 0,
    "venue_amount" DECIMAL(10,2) NOT NULL,
    "status" VARCHAR(19) NOT NULL,
    "reject_reason" VARCHAR(255),
    "payout_id" UUID REFERENCES "payouts" ("id") ON DELETE SET NULL,
    "venue_id" UUID NOT NULL REFERENCES "venues" ("id") ON DELETE RESTRICT
);
CREATE INDEX IF NOT EXISTS "idx_orders_venue_i_6fb706" ON "orders" ("venue_id", "created_at");
CREATE INDEX IF NOT EXISTS "idx_orders_unpaid" ON "orders" ("payout_id");
COMMENT ON COLUMN "orders"."service_commission" IS 'Our service''s commission';
COMMENT ON COLUMN "orders"."acquiring_fee" IS 'Acquiring fees and other gateways';
COMMENT ON COLUMN "orders"."venue_amount" IS 'Venue share (amount_total - service_commission - acquiring_fee)';
COMMENT ON COLUMN "orders"."status" IS 'Current order status by life cycle';
CREATE TABLE IF NOT EXISTS "playlists" (
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "id" UUID NOT NULL PRIMARY KEY,
    "name" VARCHAR(100) NOT NULL,
    "is_active" BOOL NOT NULL DEFAULT False,
    "venue_id" UUID NOT NULL REFERENCES "venues" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_playlist_venue_active" ON "playlists" ("venue_id", "is_active");
CREATE TABLE IF NOT EXISTS "playlist_tracks" (
    "id" UUID NOT NULL PRIMARY KEY,
    "track_id" VARCHAR(255) NOT NULL,
    "track_url" VARCHAR(255) NOT NULL,
    "track_title" VARCHAR(255) NOT NULL,
    "track_artwork_url" VARCHAR(512),
    "track_artist" VARCHAR(255) NOT NULL,
    "sort_order" INT NOT NULL,
    "playlist_id" UUID NOT NULL REFERENCES "playlists" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_playlist_tr_playlis_216958" ON "playlist_tracks" ("playlist_id", "sort_order");
CREATE TABLE IF NOT EXISTS "venue_blacklists" (
    "id" UUID NOT NULL PRIMARY KEY,
    "item_type" VARCHAR(7) NOT NULL,
    "item_value" VARCHAR(255) NOT NULL,
    "venue_id" UUID NOT NULL REFERENCES "venues" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_venue_black_venue_i_b65c69" ON "venue_blacklists" ("venue_id", "item_type");
COMMENT ON COLUMN "venue_blacklists"."item_type" IS 'Block type';
CREATE TABLE IF NOT EXISTS "proxy" (
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "id" UUID NOT NULL PRIMARY KEY,
    "protocol" VARCHAR(6) NOT NULL DEFAULT 'socks5',
    "ip_address" VARCHAR(45) NOT NULL,
    "port" VARCHAR(5) NOT NULL,
    "username" VARCHAR(255) NOT NULL,
    "password" VARCHAR(255) NOT NULL,
    "is_active" BOOL NOT NULL DEFAULT True,
    "is_banned" BOOL NOT NULL DEFAULT False
);
COMMENT ON COLUMN "proxy"."protocol" IS 'SOCKS5: socks5\nHTTP: http\nHTTPS: https';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """


MODELS_STATE = (
    "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"
)

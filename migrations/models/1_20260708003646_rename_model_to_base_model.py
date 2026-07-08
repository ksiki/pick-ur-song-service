from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "bars" (
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "id" UUID NOT NULL PRIMARY KEY,
    "login" VARCHAR(100) NOT NULL UNIQUE,
    "password_hash" VARCHAR(255) NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "legal_name" VARCHAR(255) NOT NULL,
    "unp" VARCHAR(9) NOT NULL,
    "iban" VARCHAR(28) NOT NULL,
    "offer_accepted_at" TIMESTAMPTZ NOT NULL,
    "offer_accepted_ip" VARCHAR(45) NOT NULL,
    "is_active" BOOL NOT NULL DEFAULT True
);
        CREATE TABLE IF NOT EXISTS "bar_settings" (
    "theme_config" JSONB NOT NULL,
    "allow_explicit" BOOL NOT NULL DEFAULT False,
    "commission_fee_percent" DECIMAL(5,2) NOT NULL DEFAULT 50,
    "track_price" DECIMAL(10,2) NOT NULL DEFAULT 3,
    "timezone" VARCHAR(50) NOT NULL DEFAULT 'Europe/Minsk',
    "bar_id" UUID NOT NULL PRIMARY KEY REFERENCES "bars" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "bar_settings"."commission_fee_percent" IS 'Service commission in percentage (from 0.00 to 100.00)';
COMMENT ON COLUMN "bar_settings"."timezone" IS 'The time zone of the establishment (for example, Europe/Minsk)';
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
    "bar_id" UUID NOT NULL REFERENCES "bars" ("id") ON DELETE RESTRICT
);
COMMENT ON COLUMN "payouts"."total_amount" IS 'The amount to be paid to the bar (The sum of all bar_amount)';
COMMENT ON COLUMN "payouts"."status" IS 'Transfer status of funds';
COMMENT ON COLUMN "payouts"."report_file_url" IS 'Link to the generated PDF Report of the Agent in S3';
COMMENT ON COLUMN "payouts"."paid_at" IS 'The actual time of transfer to the IBAN of the bar';
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
    "bar_amount" DECIMAL(10,2) NOT NULL,
    "status" VARCHAR(19) NOT NULL,
    "reject_reason" VARCHAR(255),
    "bar_id" UUID NOT NULL REFERENCES "bars" ("id") ON DELETE RESTRICT,
    "payout_id" UUID REFERENCES "payouts" ("id") ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS "idx_orders_bar_id_d8f010" ON "orders" ("bar_id", "created_at");
CREATE INDEX IF NOT EXISTS "idx_orders_unpaid" ON "orders" ("payout_id");
COMMENT ON COLUMN "orders"."service_commission" IS 'Our service''s commission';
COMMENT ON COLUMN "orders"."acquiring_fee" IS 'Acquiring fees and other gateways';
COMMENT ON COLUMN "orders"."bar_amount" IS 'Bar share (amount_total - service_commission - acquiring_fee)';
COMMENT ON COLUMN "orders"."status" IS 'Current order status by life cycle';
        CREATE TABLE IF NOT EXISTS "bar_blacklists" (
    "id" UUID NOT NULL PRIMARY KEY,
    "item_type" VARCHAR(7) NOT NULL,
    "item_value" VARCHAR(255) NOT NULL,
    "bar_id" UUID NOT NULL REFERENCES "bars" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_bar_blackli_bar_id_371b0a" ON "bar_blacklists" ("bar_id", "item_type");
COMMENT ON COLUMN "bar_blacklists"."item_type" IS 'Block type';
        CREATE TABLE IF NOT EXISTS "playlists" (
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "id" UUID NOT NULL PRIMARY KEY,
    "name" VARCHAR(100) NOT NULL,
    "is_active" BOOL NOT NULL DEFAULT False,
    "bar_id" UUID NOT NULL REFERENCES "bars" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_playlist_bar_active" ON "playlists" ("bar_id", "is_active");
        CREATE TABLE IF NOT EXISTS "playlist_tracks" (
    "id" UUID NOT NULL PRIMARY KEY,
    "track_id" VARCHAR(255) NOT NULL,
    "track_title" VARCHAR(255) NOT NULL,
    "track_artwork_url" VARCHAR(512),
    "track_artist" VARCHAR(255) NOT NULL,
    "sort_order" INT NOT NULL,
    "playlist_id" UUID NOT NULL REFERENCES "playlists" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_playlist_tr_playlis_216958" ON "playlist_tracks" ("playlist_id", "sort_order");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "orders";
        DROP TABLE IF EXISTS "bars";
        DROP TABLE IF EXISTS "bar_blacklists";
        DROP TABLE IF EXISTS "playlists";
        DROP TABLE IF EXISTS "playlist_tracks";
        DROP TABLE IF EXISTS "payouts";
        DROP TABLE IF EXISTS "bar_settings";"""


MODELS_STATE = (
    "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"
    "R/dgx5HvdX7tvp+X9f8BogHZCg=="
)

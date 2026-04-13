-- PopTech Cinema Studio — Governance Dashboard Schema
-- Task 5.5: MySQL tables for production tracking, cost logging, quality metrics, and publishing
-- Deploy to your MySQL host (configure via $MYSQL_HOST in .env)

-- ============================================================
-- PRODUCTION TRACKING
-- ============================================================

CREATE TABLE IF NOT EXISTS production_orders (
  id VARCHAR(50) PRIMARY KEY,
  client VARCHAR(100) NOT NULL,
  project_name VARCHAR(200) NOT NULL,
  format ENUM('cinematic_commercial', 'documentary', 'anime', 'avatar_daily', 'custom') NOT NULL,
  status ENUM('queued', 'producing', 'qc_review', 'revision', 'approved', 'published', 'archived') DEFAULT 'queued',
  notion_page_id VARCHAR(100),
  shot_count INT DEFAULT 0,
  total_duration_sec DECIMAL(10,2) DEFAULT 0,
  budget_ceiling_usd DECIMAL(10,2),
  actual_cost_usd DECIMAL(10,2) DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  completed_at TIMESTAMP NULL,
  INDEX idx_client (client),
  INDEX idx_status (status),
  INDEX idx_created (created_at)
);

-- ============================================================
-- COST TRACKING (per-shot, per-service granularity)
-- ============================================================

CREATE TABLE IF NOT EXISTS production_costs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  production_order_id VARCHAR(50) NOT NULL,
  client VARCHAR(100) NOT NULL,
  shot_id VARCHAR(50),
  service ENUM('fal_seedance', 'fal_kling', 'fal_wan', 'fal_nano_banana', 'fal_latentsync',
               'muapi_latentsync', 'muapi_other',
               'elevenlabs_tts', 'elevenlabs_sfx', 'elevenlabs_music',
               'heygen_avatar', 'comfyui_local', 'topaz_upscale',
               'remotion_render', 'ffmpeg_local', 'other') NOT NULL,
  quantity VARCHAR(50),
  unit_cost DECIMAL(10,4),
  total_cost DECIMAL(10,4) NOT NULL,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_order (production_order_id),
  INDEX idx_service (service),
  INDEX idx_month (timestamp),
  FOREIGN KEY (production_order_id) REFERENCES production_orders(id) ON DELETE CASCADE
);

-- ============================================================
-- PUBLISHING LOG
-- ============================================================

CREATE TABLE IF NOT EXISTS video_publishing (
  id INT AUTO_INCREMENT PRIMARY KEY,
  production_order_id VARCHAR(50) NOT NULL,
  platform ENUM('youtube', 'youtube_shorts', 'instagram_reels', 'tiktok', 'linkedin', 'facebook', 'other') NOT NULL,
  aspect_ratio VARCHAR(10),
  resolution VARCHAR(20),
  file_path VARCHAR(500),
  platform_video_id VARCHAR(200),
  platform_url VARCHAR(500),
  visibility ENUM('public', 'unlisted', 'private', 'scheduled') DEFAULT 'unlisted',
  publish_status ENUM('queued', 'uploading', 'published', 'failed', 'removed') DEFAULT 'queued',
  published_at TIMESTAMP NULL,
  views_24h INT DEFAULT 0,
  views_7d INT DEFAULT 0,
  engagement_rate DECIMAL(5,2),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_order (production_order_id),
  INDEX idx_platform (platform),
  INDEX idx_published (published_at),
  FOREIGN KEY (production_order_id) REFERENCES production_orders(id) ON DELETE CASCADE
);

-- ============================================================
-- CREDIT BALANCES (track API service balances)
-- ============================================================

CREATE TABLE IF NOT EXISTS credit_balances (
  id INT AUTO_INCREMENT PRIMARY KEY,
  service ENUM('fal_ai', 'muapi', 'elevenlabs', 'heygen', 'openai') NOT NULL,
  balance_usd DECIMAL(10,4) NOT NULL,
  checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_service (service),
  INDEX idx_checked (checked_at)
);

-- ============================================================
-- GOVERNANCE LOG (audit trail for all pipeline actions)
-- ============================================================

CREATE TABLE IF NOT EXISTS governance_logs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  production_order_id VARCHAR(50),
  action VARCHAR(100) NOT NULL,
  details JSON,
  severity ENUM('info', 'warning', 'error', 'critical') DEFAULT 'info',
  source VARCHAR(50),
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_order (production_order_id),
  INDEX idx_severity (severity),
  INDEX idx_timestamp (timestamp)
);

-- ============================================================
-- CHARACTER LoRAs (Task 5.1 tracking)
-- ============================================================

CREATE TABLE IF NOT EXISTS character_loras (
  id INT AUTO_INCREMENT PRIMARY KEY,
  character_id VARCHAR(50) NOT NULL,
  character_name VARCHAR(100) NOT NULL,
  client VARCHAR(100),
  lora_path VARCHAR(500),
  base_model VARCHAR(100),
  training_epochs INT,
  training_images INT,
  quality_score DECIMAL(3,1),
  status ENUM('training', 'ready', 'deprecated') DEFAULT 'training',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_character (character_id),
  INDEX idx_status (status)
);

-- ============================================================
-- VIDEO BENCHMARKS (Task 5.3 quality tracking)
-- ============================================================

CREATE TABLE IF NOT EXISTS video_benchmarks (
  id INT AUTO_INCREMENT PRIMARY KEY,
  production_order_id VARCHAR(50),
  engine VARCHAR(50) NOT NULL,
  shot_id VARCHAR(50),
  duration_sec DECIMAL(10,2),
  resolution VARCHAR(20),
  generation_time_sec DECIMAL(10,2),
  cost_usd DECIMAL(10,4),
  quality_score DECIMAL(3,1),
  lip_sync_score DECIMAL(3,1),
  character_consistency DECIMAL(3,1),
  notes TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_engine (engine),
  INDEX idx_quality (quality_score)
);

-- ============================================================
-- ENGINE PROFILES (cost/quality reference data)
-- ============================================================

CREATE TABLE IF NOT EXISTS engine_profiles (
  id INT AUTO_INCREMENT PRIMARY KEY,
  engine VARCHAR(50) NOT NULL UNIQUE,
  provider VARCHAR(50) NOT NULL,
  cost_per_sec DECIMAL(10,4),
  cost_per_image DECIMAL(10,4),
  avg_quality_score DECIMAL(3,1),
  avg_generation_time_sec DECIMAL(10,2),
  max_duration_sec INT,
  supported_aspects JSON,
  notes TEXT,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Seed engine profiles
INSERT INTO engine_profiles (engine, provider, cost_per_sec, avg_quality_score, max_duration_sec, notes) VALUES
  ('seedance_2.0', 'fal.ai', 0.10, NULL, 15, 'Primary cinematic engine. Multi-axis camera, audio-sync.'),
  ('kling_3.0', 'fal.ai', 0.10, NULL, 15, 'Multi-shot consistency, dialogue scenes.'),
  ('wan_2.6_cloud', 'fal.ai', 0.10, NULL, 10, 'Open source cloud. Anime/stylized.'),
  ('wan_2.6_local', 'local', 0.00, NULL, 60, 'Free local. Requires GPU on VPS.'),
  ('veo_3.1', 'google', 0.00, NULL, 10, '~10 free/day. 4K photorealism.'),
  ('nano_banana_pro', 'fal.ai', NULL, 0.01, NULL, 'Stills/storyboards. Primary image model.')
ON DUPLICATE KEY UPDATE notes=VALUES(notes);

INSERT INTO engine_profiles (engine, provider, cost_per_sec, notes) VALUES
  ('muapi_latentsync', 'muapi.ai', 0.02, 'Primary lip-sync. $0.26/run avg.'),
  ('elevenlabs_tts', 'elevenlabs', 0.003, 'Per-character voice. Creator plan.'),
  ('heygen_avatar', 'heygen', 0.50, 'Backup only. Web credits, not API.')
ON DUPLICATE KEY UPDATE notes=VALUES(notes);

-- ============================================================
-- MONTHLY COST SUMMARY VIEW
-- ============================================================

CREATE OR REPLACE VIEW monthly_costs AS
SELECT
  DATE_FORMAT(timestamp, '%Y-%m') AS month,
  client,
  service,
  COUNT(*) AS transactions,
  SUM(total_cost) AS total_usd,
  AVG(total_cost) AS avg_per_transaction
FROM production_costs
GROUP BY DATE_FORMAT(timestamp, '%Y-%m'), client, service
ORDER BY month DESC, total_usd DESC;

-- ============================================================
-- COMPETITIVE COMPARISON VIEW (PopTech vs Higgsfield vs Arcads)
-- ============================================================

CREATE OR REPLACE VIEW competitive_comparison AS
SELECT
  DATE_FORMAT(pc.timestamp, '%Y-%m') AS month,
  COUNT(DISTINCT pc.production_order_id) AS productions,
  SUM(po.total_duration_sec) / 60 AS total_minutes,
  SUM(pc.total_cost) AS poptech_cost,
  (SUM(po.total_duration_sec) / 60) * 34 AS higgsfield_equivalent,
  (SUM(po.total_duration_sec) / 60) * 10 AS arcads_equivalent
FROM production_costs pc
JOIN production_orders po ON pc.production_order_id = po.id
GROUP BY DATE_FORMAT(pc.timestamp, '%Y-%m');

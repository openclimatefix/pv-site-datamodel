CREATE TABLE "pvsite" (
  "pvsite_uuid" char(32) PRIMARY KEY NOT NULL,
  "client_uuid" char(32) NOT NULL,
  "client_site_id" int4,
  "client_site_name" varchar(255),
  "region" varchar(255),
  "dno" varchar(255),
  "gsp" varchar(255),
  "orientation" real,
  "tilt" real,
  "latitude" float8 NOT NULL,
  "longitude" float8 NOT NULL,
  "capacity_kw" real NOT NULL,
  "created_utc" timestamp NOT NULL,
  "update_utc" timestamp NOT NULL,
  PRIMARY KEY ("pvsite_uuid")
);

CREATE TABLE "pvyield" (
  "pvyield_uuid" char(32) PRIMARY KEY NOT NULL,
  "pvsite_uuid" char(32) NOT NULL,
  "generation_kw" real NOT NULL,
  "datetime_interval_uuid" char(32) NOT NULL,
  "created_utc" timestamp NOT NULL,
  PRIMARY KEY ("pvyield_uuid")
);

CREATE TABLE "forecast" (
  "forecast_uuid" char(32) PRIMARY KEY,
  "site_uuid" char(32) NOT NULL,
  "created_utc" timestamp NOT NULL,
  "forecast_version" varchar(32) NOT NULL,
  PRIMARY KEY ("forecast_uuid")
);

CREATE TABLE "forecast_value" (
  "forecast_value_uuid" char(32) PRIMARY KEY,
  "datetime_interval_uuid" uuid,
  "forecast_generation_kw" real,
  "created_utc" timestamp,
  "forecast_uuid" char(32),
  PRIMARY KEY ("forecast_value_uuid")
);

CREATE TABLE "client" (
  "client_uuid" uuid PRIMARY KEY,
  "client_name" varchar(32),
  "created_utc" timestamp
);

CREATE TABLE "datetime_interval" (
  "datetime_interval_uuid" uuid PRIMARY KEY,
  "start_utc" timestamp,
  "end_utc" timestamp,
  "created_utc" timestamp
);

CREATE TABLE "status" (
  "status_uuid" uuid PRIMARY KEY,
  "status" varchar(32),
  "message" varchar(255),
  "created_utc" timestamp
);

CREATE UNIQUE INDEX "idx_client" ON "pvsite" ("client_uuid", "client_site_id");

COMMENT ON TABLE "forecast" IS 'Each forecast is a per-site sequence of 
predicted solar generation values
over a set of target times. ';

COMMENT ON COLUMN "forecast"."site_uuid" IS 'The site for which the forecast sequence was generated';

COMMENT ON COLUMN "forecast"."created_utc" IS 'The creation time of the forecast sequence';

COMMENT ON COLUMN "forecast"."forecast_version" IS 'The semantic version of the model used to generate the forecast';

COMMENT ON TABLE "forecast_value" IS 'Each forecast value is a ';

ALTER TABLE "pvsite" ADD FOREIGN KEY ("client_uuid") REFERENCES "client" ("client_uuid");

ALTER TABLE "pvyield" ADD FOREIGN KEY ("datetime_interval_uuid") REFERENCES "datetime_interval" ("datetime_interval_uuid");

ALTER TABLE "pvyield" ADD FOREIGN KEY ("pvsite_uuid") REFERENCES "pvsite" ("pvsite_uuid");

ALTER TABLE "forecast_value" ADD FOREIGN KEY ("datetime_interval_uuid") REFERENCES "datetime_interval" ("datetime_interval_uuid");

ALTER TABLE "forecast_value" ADD FOREIGN KEY ("forecast_uuid") REFERENCES "forecast" ("forecast_uuid");

ALTER TABLE "pvsite" ADD FOREIGN KEY ("pvsite_uuid") REFERENCES "forecast" ("site_uuid");

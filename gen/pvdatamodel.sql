-- SQL dump generated using DBML (dbml-lang.org)
-- Database: PostgreSQL
-- Generated at: 2023-01-06T16:19:56.917Z

CREATE TABLE "sites" (
  "site_uuid" uuid PRIMARY KEY NOT NULL,
  "client_uuid" uuid NOT NULL,
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
  "updated_utc" timestamp NOT NULL,
  PRIMARY KEY ("site_uuid")
);

CREATE TABLE "generation" (
  "generation_uuid" uuid PRIMARY KEY NOT NULL,
  "site_uuid" uuid NOT NULL,
  "power_kw" real NOT NULL,
  "datetime_interval_uuid" uuid NOT NULL,
  "created_utc" timestamp NOT NULL,
  PRIMARY KEY ("generation_uuid")
);

CREATE TABLE "forecasts" (
  "forecast_uuid" uuid PRIMARY KEY,
  "site_uuid" uuid NOT NULL,
  "created_utc" timestamp NOT NULL,
  "forecast_version" varchar(32) NOT NULL,
  PRIMARY KEY ("forecast_uuid")
);

CREATE TABLE "forecast_values" (
  "forecast_value_uuid" uuid PRIMARY KEY,
  "datetime_interval_uuid" uuid NOT NULL,
  "forecast_generation_kw" real NOT NULL,
  "created_utc" timestamp NOT NULL,
  "forecast_uuid" uuid NOT NULL,
  PRIMARY KEY ("forecast_value_uuid")
);

CREATE TABLE "latest_forecast_values" (
  "latest_forecast_value_uuid" uuid PRIMARY KEY,
  "datetime_interval_uuid" uuid NOT NULL,
  "forecast_generation_kw" real NOT NULL,
  "created_utc" timestamp NOT NULL,
  "forecast_uuid" uuid NOT NULL,
  "site_uuid" uuid NOT NULL,
  "forecast_version" varchar(32) NOT NULL,
  PRIMARY KEY ("latest_forecast_value_uuid")
);

CREATE TABLE "clients" (
  "client_uuid" uuid PRIMARY KEY,
  "client_name" varchar(255) NOT NULL,
  "created_utc" timestamp NOT NULL,
  PRIMARY KEY ("client_uuid")
);

CREATE TABLE "datetime_intervals" (
  "datetime_interval_uuid" uuid PRIMARY KEY,
  "start_utc" timestamp NOT NULL,
  "end_utc" timestamp NOT NULL,
  "created_utc" timestamp NOT NULL,
  PRIMARY KEY ("datetime_interval_uuid")
);

CREATE TABLE "status" (
  "status_uuid" uuid PRIMARY KEY,
  "status" varchar(255),
  "message" varchar(255),
  "created_utc" timestamp,
  PRIMARY KEY ("status_uuid")
);

CREATE UNIQUE INDEX "idx_client" ON "sites" ("client_uuid", "client_site_id");

CREATE INDEX ON "datetime_intervals" ("start_utc");

CREATE INDEX ON "datetime_intervals" ("end_utc");

COMMENT ON TABLE "sites" IS '*Overview: *
Each site row specifies a single panel or cluster of panels
found on a residential house or commercial building. Their
data is provided by a client.

*Approximate size: *
4 clients * ~1000 sites each = ~4000 rows';

COMMENT ON COLUMN "sites"."client_uuid" IS 'The internal ID of the client providing the site data';

COMMENT ON COLUMN "sites"."client_site_id" IS 'The ID of the site as given by the providing client';

COMMENT ON COLUMN "sites"."client_site_name" IS 'The ID of the site as given by the providing client';

COMMENT ON COLUMN "sites"."region" IS 'The region in the UK in which the site is located';

COMMENT ON COLUMN "sites"."dno" IS 'The Distribution Node Operator that owns the site';

COMMENT ON COLUMN "sites"."gsp" IS 'The Grid Supply Point in which the site is located';

COMMENT ON COLUMN "sites"."orientation" IS 'The rotation of the panel in degrees. 180° points south';

COMMENT ON COLUMN "sites"."tilt" IS 'The tile of the panel in degrees. 90° indicates the panel is vertical';

COMMENT ON COLUMN "sites"."capacity_kw" IS 'The physical limit on the production capacity of the site';

COMMENT ON TABLE "generation" IS '*Overview: *
Each yield row specifies a generated power output over a
given time range for a site.

*Approximate size: *
Generation populated every 5 minutes per site * 4000 sites = ~1,125,000 rows per day';

COMMENT ON COLUMN "generation"."site_uuid" IS 'The site for which this geenration yield belongs to';

COMMENT ON COLUMN "generation"."power_kw" IS 'The actual generated power in kW at this site for this datetime interval';

COMMENT ON COLUMN "generation"."datetime_interval_uuid" IS 'The time interval over which this generated power value applies';

COMMENT ON TABLE "forecasts" IS '*Overview: *
Each forecast row refers to a sequence of predicted solar generation values
over a set of target times for a site. 

*Approximate size: *
One forecast per site every 5 minutes = ~1,125,000 rows per day';

COMMENT ON COLUMN "forecasts"."site_uuid" IS 'The site for which the forecast sequence was generated';

COMMENT ON COLUMN "forecasts"."created_utc" IS 'The creation time of the forecast sequence';

COMMENT ON COLUMN "forecasts"."forecast_version" IS 'The semantic version of the model used to generate the forecast';

COMMENT ON TABLE "forecast_values" IS '*Overview: *
Each forecast_value row is a prediction for the power output 
of a site over a target datetime interval. Many predictions
are made for each site at each target interval.

*Approximate size: *
One forecast value every 5 minutes per site per forecast.
Each forecast"s prediction sequence covers 24 hours of target
intervals = ~324,000,000 rows per day';

COMMENT ON COLUMN "forecast_values"."datetime_interval_uuid" IS 'The time interval over which this predicted power value applies';

COMMENT ON COLUMN "forecast_values"."forecast_generation_kw" IS 'The predicted power generation of this site for the given time interval';

COMMENT ON COLUMN "forecast_values"."forecast_uuid" IS 'The forecast sequence this forcast value belongs to';

COMMENT ON TABLE "latest_forecast_values" IS '*Overview: *  
Each forecast_value row is a prediction for the power output 
of a site over a target datetime interval. Only the most recent 
prediction for each target time interval is stored in this table
per site.

*Approximate size: *
One forecast value every 5 minutes per site per forecast
sequence = ~1,125,000 rows per day';

COMMENT ON COLUMN "latest_forecast_values"."datetime_interval_uuid" IS 'The time interval over which this predicted power value applies';

COMMENT ON COLUMN "latest_forecast_values"."forecast_generation_kw" IS 'The predicted power generation of this site for the given time interval';

COMMENT ON COLUMN "latest_forecast_values"."forecast_uuid" IS 'The forecast sequence this forcast value belongs to';

COMMENT ON COLUMN "latest_forecast_values"."site_uuid" IS 'The site for which the forecast sequence was generated';

COMMENT ON COLUMN "latest_forecast_values"."forecast_version" IS 'The semantic version of the model used to generate the forecast';

COMMENT ON TABLE "clients" IS '*Overview: *
Each client row defines a provider of site data

*Approximate size: *
One row per client = ~4 rows';

COMMENT ON TABLE "datetime_intervals" IS '*Overview: *
Each datetime_interval row defines a timespan between a start and end time

*Approximate size: *
One interval every 5 minutes per day = ~288 rows per day';

COMMENT ON TABLE "status" IS '*Overview: *
Each status row defines a message reporting on the status of the
services within the nowcasting domain

*Approximate size: *
~1 row per day';

ALTER TABLE "sites" ADD FOREIGN KEY ("client_uuid") REFERENCES "clients" ("client_uuid");

ALTER TABLE "generation" ADD FOREIGN KEY ("datetime_interval_uuid") REFERENCES "datetime_intervals" ("datetime_interval_uuid");

ALTER TABLE "generation" ADD FOREIGN KEY ("site_uuid") REFERENCES "sites" ("site_uuid");

ALTER TABLE "forecast_values" ADD FOREIGN KEY ("datetime_interval_uuid") REFERENCES "datetime_intervals" ("datetime_interval_uuid");

ALTER TABLE "forecast_values" ADD FOREIGN KEY ("forecast_uuid") REFERENCES "forecasts" ("forecast_uuid");

ALTER TABLE "sites" ADD FOREIGN KEY ("site_uuid") REFERENCES "forecasts" ("site_uuid");

ALTER TABLE "sites" ADD FOREIGN KEY ("site_uuid") REFERENCES "latest_forecast_values" ("site_uuid");

ALTER TABLE "latest_forecast_values" ADD FOREIGN KEY ("datetime_interval_uuid") REFERENCES "datetime_intervals" ("datetime_interval_uuid");

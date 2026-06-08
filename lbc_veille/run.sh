#!/usr/bin/with-contenv bashio
set -e

bashio::log.level "$(bashio::config 'log_level')"

export SUPABASE_URL="$(bashio::config 'supabase_url')"
export SUPABASE_SERVICE_KEY="$(bashio::config 'supabase_service_key')"
export DEPARTEMENTS="$(bashio::config 'departements')"
export PAGES="$(bashio::config 'pages')"
export INTERVAL_HOURS="$(bashio::config 'interval_hours')"
export PROXY_MODE="$(bashio::config 'proxy_mode')"
export BRD_USER="$(bashio::config 'brd_user')"
export BRD_PASS="$(bashio::config 'brd_pass')"
export MARK_STALE_DAYS="$(bashio::config 'mark_stale_days')"

if bashio::services.available "mqtt"; then
  export MQTT_HOST="$(bashio::services mqtt 'host')"
  export MQTT_PORT="$(bashio::services mqtt 'port')"
  export MQTT_USER="$(bashio::services mqtt 'username')"
  export MQTT_PASS="$(bashio::services mqtt 'password')"
  bashio::log.info "MQTT broker: ${MQTT_HOST}:${MQTT_PORT}"
else
  bashio::log.warning "Service MQTT indisponible — capteurs non publiés."
fi

bashio::log.info "Démarrage LBC Veille Motos"
exec python3 -u run.py

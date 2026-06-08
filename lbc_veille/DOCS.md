# LBC Veille Motos

## Configuration

| Option | Déf. | Description |
|---|---|---|
| `supabase_url` | — | URL du projet Supabase |
| `supabase_service_key` | — | Clé service Supabase |
| `departements` | `[]` | Codes (ex `[75,33]`). **Vide = round-robin** : 1 département/run sur les 94 de métropole |
| `pages` | `2` | Pages scrapées par département |
| `interval_hours` | `1` | Heures entre deux runs |
| `proxy_mode` | `sans` | `sans` / `ISP` / `residential` (Bright Data) |
| `brd_user` / `brd_pass` | — | Identifiants Bright Data (si proxy) |
| `mark_stale_days` | `7` | Annonces non revues depuis N jours → `expired` (0 = off) |
| `log_level` | `info` | Niveau de log |

## Fonctionnement

À chaque run : scrape la cible → upsert Supabase (historique de prix) →
marque les annonces périmées → publie les compteurs sur MQTT.
Le curseur round-robin est persisté dans `/data/state.json` (survit aux reboots).

## Pré-requis

- Add-on **Mosquitto broker** + intégration **MQTT** (auto-détection via le Supervisor).
- Schéma Supabase : tables `veille_lbc_annonces` / `veille_lbc_config` (voir `schema.sql`).

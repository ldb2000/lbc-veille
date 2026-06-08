# LBC Veille — Add-on Home Assistant

Add-on qui scrape les annonces motos LeBonCoin, les stocke dans Supabase et
publie des compteurs dans Home Assistant via MQTT discovery.

## Installation

1. Home Assistant → **Paramètres → Modules complémentaires → Boutique → ⋮ → Dépôts**.
2. Ajouter : `https://github.com/ldb2000/lbc-veille`
3. Installer **LBC Veille Motos**.
4. Pré-requis : add-on **Mosquitto broker** installé + intégration **MQTT** activée.
5. Configurer les options (Supabase, départements, intervalle…) puis démarrer.

## Capteurs exposés

- `sensor.lbc_total_active` — annonces actives
- `sensor.lbc_new_last_run` — nouvelles au dernier run
- `sensor.lbc_price_drops` — baisses de prix au dernier run
- `sensor.lbc_last_run` — horodatage + attributs (statut, erreurs, durée, depts)

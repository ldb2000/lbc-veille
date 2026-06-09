"""Scraper LeBonCoin motos : scrape une liste de départements, upsert Supabase,
retourne des statistiques pour publication MQTT."""
import random
import time
from datetime import datetime, timezone

import lbc


def get_proxy_url(proxy_mode, brd_user, brd_pass):
    """URL proxy Bright Data, ou None si proxy désactivé."""
    host = "brd.superproxy.io:22225"
    if proxy_mode in ("ISP", "residential"):
        return f"http://{brd_user}:{brd_pass}@{host}"
    return None


def extract_attr(attributes, key_name):
    """Extrait proprement une valeur des attributs LBC, ou None."""
    if not attributes:
        return None
    for attr in attributes:
        if attr.key == key_name:
            return attr.value
    return None


def _to_int(value):
    """int(value) tolérant : None si vide/invalide."""
    try:
        return int(value) if value not in (None, "") else None
    except (TypeError, ValueError):
        return None


def is_price_drop(old_price, new_price):
    """True si baisse de prix stricte (les deux non None)."""
    return (
        old_price is not None
        and new_price is not None
        and new_price < old_price
    )


def build_ad_data(ad, now):
    """Construit le dict d'annonce pour Supabase. Fonction pure."""
    attrs = ad.attributes if hasattr(ad, "attributes") else []
    attrs_json = [{"key": a.key, "value": a.value} for a in attrs] if attrs else []
    return {
        "lbc_id": ad.id,
        "url": ad.url,
        "titre": ad.subject,
        "description": getattr(ad, "body", ""),
        "prix": int(ad.price) if ad.price else 0,
        "marque": extract_attr(attrs, "brand"),
        "modele": extract_attr(attrs, "model"),
        "annee": _to_int(extract_attr(attrs, "regdate")),
        "km": _to_int(extract_attr(attrs, "mileage")),
        "cylindree": _to_int(extract_attr(attrs, "cubic_capacity")),
        "type_moto": extract_attr(attrs, "cycle_type"),
        "etat": extract_attr(attrs, "vehicle_damage"),
        "carburant": extract_attr(attrs, "fuel"),
        "departement": ad.location.department_name if ad.location else None,
        "code_postal": ad.location.zipcode if ad.location else None,
        "ville": ad.location.city_label if ad.location else None,
        "images_json": list(ad.images) if ad.images else [],
        "attributes_json": attrs_json,
        "vendeur_type": "pro" if getattr(ad, "is_pro", False) else "particulier",
        "published_at": ad.first_publication_date,
        "last_seen_at": now,
    }


def upsert_annonce(sb, ad, stats):
    """Insère ou met à jour une annonce, gère l'historique des prix, met à jour stats.

    stats : dict avec clés 'new', 'updated', 'price_drops', 'errors'.
    """
    try:
        now = datetime.now(timezone.utc).isoformat()
        data = build_ad_data(ad, now)
        prix = data["prix"]

        existing = (
            sb.table("veille_lbc_annonces")
            .select("id,prix,prix_historique")
            .eq("lbc_id", ad.id)
            .execute()
        )

        if existing.data:
            row = existing.data[0]
            update_data = {"prix": prix, "last_seen_at": now, "statut": "active"}
            if row["prix"] != prix:
                historique = row.get("prix_historique") or []
                historique.append({"prix": prix, "date": now})
                update_data["prix_historique"] = historique
                if is_price_drop(row["prix"], prix):
                    stats["price_drops"] += 1
            sb.table("veille_lbc_annonces").update(update_data).eq(
                "id", row["id"]
            ).execute()
            stats["updated"] += 1
        else:
            data["prix_historique"] = [{"prix": prix, "date": now}]
            sb.table("veille_lbc_annonces").insert(data).execute()
            stats["new"] += 1
    except Exception as exc:  # gestion d'erreur (corrige les TODO du code original)
        stats["errors"] += 1
        print(f"    [Erreur upsert] Ad {getattr(ad, 'id', '?')}: {exc}")


def make_supabase(url, key):
    """Client Supabase."""
    from supabase import create_client

    return create_client(url, key)


def make_lbc_client(proxy_url):
    """Client LBC, avec proxy optionnel."""
    return lbc.Client(proxy=proxy_url) if proxy_url else lbc.Client()


def run_scraper(sb, client, depts, pages=2, proxy_mode="sans"):
    """Scrape les départements donnés (liste de lbc.Department). Retourne des stats."""
    stats = {
        "new": 0,
        "updated": 0,
        "price_drops": 0,
        "errors": 0,
        "ok": True,
        "duration_s": 0.0,
        "depts": [d.value[2] for d in depts],
    }
    start = time.monotonic()
    try:
        for dept in depts:
            print(f"Zone: {dept.name}")
            for page in range(1, pages + 1):
                try:
                    results = client.search(
                        category=lbc.Category.VEHICULES_MOTOS,
                        locations=[dept],
                        page=page,
                        sort=lbc.Sort.NEWEST,
                    )
                except Exception as exc:
                    stats["errors"] += 1
                    print(f"  Erreur recherche page {page}: {exc}")
                    time.sleep(10)
                    continue

                if not results.ads:
                    print(f"  Page {page}: 0 annonce, fin de la zone.")
                    break

                nb = len(results.ads)
                print(f"  Page {page}/{pages}: {nb} annonce(s)")
                for idx, ad in enumerate(results.ads, 1):
                    do_visit = not (proxy_mode == "residential" and random.random() < 0.3)
                    target = ad
                    if do_visit:
                        time.sleep(random.uniform(2, 6))
                        try:
                            target = client.get_ad(ad.id)
                        except Exception as exc:
                            stats["errors"] += 1
                            print(f"    [{idx}/{nb}] Erreur get_ad {ad.id}: {exc}")
                            continue
                    upsert_annonce(sb, target, stats)
                    titre = (getattr(target, "subject", None) or "?")[:45]
                    prix = getattr(target, "price", "?")
                    print(f"    [{idx}/{nb}] {titre} ({prix}EUR)")
                print(
                    f"  Cumul: +{stats['new']} new, {stats['updated']} maj, "
                    f"{stats['price_drops']} baisses, {stats['errors']} err"
                )
                time.sleep(random.uniform(1, 5))
    except Exception as exc:
        stats["ok"] = False
        stats["errors"] += 1
        print(f"Erreur fatale run_scraper: {exc}")
    stats["duration_s"] = round(time.monotonic() - start, 1)
    return stats


def count_active(sb):
    """Nombre d'annonces actives dans Supabase."""
    res = (
        sb.table("veille_lbc_annonces")
        .select("id", count="exact")
        .eq("statut", "active")
        .execute()
    )
    return res.count or 0


def mark_stale(sb, days):
    """Passe en 'expired' les annonces actives non revues depuis `days` jours."""
    if days <= 0:
        return
    from datetime import timedelta

    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    sb.table("veille_lbc_annonces").update({"statut": "expired"}).eq(
        "statut", "active"
    ).lt("last_seen_at", cutoff).execute()

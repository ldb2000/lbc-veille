"""Liste et résolution des départements LeBonCoin (métropole)."""


def ordered_departments(enum):
    """Membres de l'enum triés par code numérique (value[2]). Fonction pure."""
    return sorted(enum, key=lambda d: int(d.value[2]))


def resolve(enum, codes):
    """Mappe des codes (int ou str) vers les membres de l'enum, ordonnés.

    Les codes inconnus sont ignorés. Fonction pure.
    """
    wanted = {str(c) for c in codes}
    return [d for d in ordered_departments(enum) if d.value[2] in wanted]


def all_metro():
    """Tous les départements métropole exposés par la lib lbc, ordonnés."""
    import lbc

    return ordered_departments(lbc.Department)

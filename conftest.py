import os
import sys

# Les modules de l'add-on sont plats (import scraper, import departments...).
# On reproduit le WORKDIR Docker en ajoutant lbc_veille/ au sys.path.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lbc_veille"))

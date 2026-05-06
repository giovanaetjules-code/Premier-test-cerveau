# Simulation computationnelle d’un cerveau minimal

Ce projet contient une simulation simple d’un “cerveau” qui **met à jour un état interne avant de parler**.

## Prérequis

- Python 3.10+ (3.11 recommandé)

## Lancer la simulation

Depuis la racine du projet :

```bash
python3 brain_sim.py
```

Tu verras une invite interactive :

- `toi>` : ton message
- `cerveau>` : réponse simulée

Pour quitter :

- tape `quit` ou `exit`

## Vérifier que le fichier est valide

```bash
python3 -m py_compile brain_sim.py
```

## Exemple rapide (sans mode interactif)

```bash
python3 - <<'PY'
from brain_sim import MinimalBrainSimulation

brain = MinimalBrainSimulation()
for msg in [
    "salut",
    "pourquoi tu hésites ?",
    "je suis en danger",
    "merci",
]:
    print("toi>", msg)
    print("cerveau>", brain.step(msg))
PY
```

## Structure rapide

- `brain_sim.py` : logique complète de la simulation.
- `README.md` : ce guide d’utilisation.

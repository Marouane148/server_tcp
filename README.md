# Serveur TCP – Projet Jeu Réseau

## 🎯 Rôle

Ce serveur TCP fait le lien entre :
- Les **clients** du jeu (qui envoient des requêtes au format JSON)
- Le **moteur d’administration TCP** (pour inscrire les joueurs)
- Le **moteur de jeu gRPC** (pour gérer les actions en jeu)

Ce serveur **ne contient aucune logique de jeu**. Il agit uniquement comme un **proxy** vers les deux moteurs.

---

## ⚙️ Fonctionnement

Le serveur écoute les connexions sur `localhost:9999`.  
Il reçoit des messages JSON sous forme de liste, détermine leur type (`subscribe` ou `action`) et les redirige :

- Vers le **moteur d'administration** via une socket TCP pour les inscriptions.
- Vers le **moteur de jeu gRPC** pour les actions.

---

## 📥 Messages supportés

### 1. `subscribe` – Inscription d'un joueur

```json
["subscribe", "pseudo", "role"]

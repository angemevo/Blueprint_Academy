Titre: Moteur de validation de graphe (E, F, G, H) — à cadrer par Ange
Labels: phase-2b,backend,a-cadrer
---
**Dépend de :** #02 (interfaces de validation)

## Pourquoi
C'est le cœur pédagogique de la plateforme (types de production). Une erreur ici enseigne quelque chose de faux, d'où le cadrage par Ange avant toute délégation.

## Ce qui doit être décidé avant `ready`
1. Sémantique exacte des sélecteurs `match` sur les propriétés des nodes, et de leur réutilisation dans `from` / `to`.
2. Calcul du score partiel : part des exigences satisfaites ? Les exigences `forbidden_*` annulent-elles le score ou le pénalisent-elles ?
3. Traitement de `required_variables`.
4. Vérification serveur des nodes verrouillés (types F et H) : un node verrouillé déplacé, supprimé ou modifié invalide-t-il toute la soumission ?
5. Branchement du contrôle « un exercice F/H déjà résolu par son graphe de départ est refusé à la sauvegarde ».

## Proposition de méthode
Ange écrit d'abord les **cas de test** (graphes soumis et résultat attendu), à partir de vrais Blueprints vérifiés dans Unreal. L'agent implémente ensuite jusqu'à ce que ces tests passent, sans les modifier.

## Hors périmètre
- Type I (normalisation de l'export UE5) : issue séparée.
- Interpréteur et validation par comportement (V2).

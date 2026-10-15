Titre: Calcul de la maîtrise des skills — à cadrer par Ange
Labels: phase-2b,backend,a-cadrer
---
**Dépend de :** #09 (soumission)

## Pourquoi
C'est la règle centrale du produit : seule la production fait progresser `SkillMastery`, et c'est la maîtrise qui ouvre les prérequis. Elle doit être décidée par Ange.

## Ce qui doit être décidé avant `ready`
1. Formule de progression et de baisse de `mastery_score` (par réussite, par échec, effet du score partiel, des indices utilisés, du nombre de tentatives).
2. Bonus du type I, sachant que 100 % doit rester atteignable sans aucun exercice de type I (CLAUDE.md).
3. Contrôle d'intégrité « assez d'exercices de production non-I par skill » : seuil exact, et branchement au moment de publier une leçon ou un parcours.
4. Réglages à placer dans les settings (pas de valeurs en dur).

## Hors périmètre
- Verrouillage des leçons par prérequis (issue ultérieure, une fois la formule fixée).

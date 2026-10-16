# Cycle courant

## Plan de la semaine (2026-S42, du 12 au 18 octobre)

**Aucune issue éligible : plan vide.**

Vérifié sur GitHub par le pilotage du 2026-10-16 (2e cycle du jour, `gh` désormais accessible) :
- 11 issues ouvertes (#1 à #11), **aucune ne porte l'étiquette `ready`**.
- Aucune issue fermée, aucune PR (ouverte ou mergée).
- `state/validations.md` : aucune case cochée par Ange.

Une issue n'entre au plan que si elle porte `ready` et que ses dépendances sont mergées. Aucune ne remplit la première condition.

Le cycle tech n'a donc rien à prendre. Il doit écrire « Plan de la semaine terminé » et s'arrêter.

**Plan de la semaine terminé** (cycle tech du 2026-10-16, 3e cycle) : aucune PR ouverte, plan vide. Anomalie : #10 et #11 portent désormais `ready`, mais elles dépendent de #9 (non mergée) et #11 est encore `a-cadrer`. Elles n'ont pas été prises, et le point est ajouté dans `state/validations.md`.

## Candidats pour le prochain plan (pas planifiés, en attente de `ready`)

Issues sans dépendance, numéros confirmés sur GitHub. Ordre recommandé (voir `state/validations.md`) :

1. #2 « Interfaces de validation et registre des validateurs ». Dépend de : aucune.
2. #5 « Authentification JWT ». Dépend de : aucune. Préalable : décision blacklist.

Repli si la décision blacklist n'est pas prise : #1 « Outillage qualité : ruff et ESLint » (dépend de : aucune) à la place de #5.

## Dernière tâche traitée
- Cycle : tech du 2026-10-16 (3e cycle du jour)
- Issue / PR : aucune
- Branche : aucune
- Verdict qa : aucun
- Prochaine action : Ange retire `ready` de #10 et #11, tranche la blacklist JWT (#5), pose `ready` sur #2 et #5 (ou #1 et #2), puis relance `scripts/cycle.sh pilotage`.

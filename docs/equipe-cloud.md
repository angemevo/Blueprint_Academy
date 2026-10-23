# L'équipe d'agents en autonomie, sur GitHub

L'équipe travaille seule sur les serveurs de GitHub, avec ton abonnement Claude Pro. Ton ordinateur n'a pas besoin d'être allumé. Tu ne lis pas le code. **Tu ne parles qu'à une personne : l'organisateur**, dans son bureau.

## Qui fait quoi

| Rôle | Ce qu'il fait pour toi |
| --- | --- |
| **Organisateur** | Ton seul interlocuteur. Il te répond dans son bureau, applique tes consignes, fait le plan de la semaine, te donne l'avancement et **la date de fin estimée**. |
| **Chef d'équipe** | Chaque nuit, il distribue le travail en **créneaux** (qui fait quoi, combien de temps), fait exécuter chaque créneau et valide ce qui est rendu. Après une erreur, il relance au lieu de s'arrêter. |
| **Développeur** | Code les tâches, avec leurs tests. |
| **QA** | Relit, teste, et filme ce qui se voit à l'écran. |
| **Contrôleur** | Un script. Il valide chaque action de l'équipe instantanément : il accepte ce qui est sûr et refuse le dangereux. Plus rien n'attend ton approbation. |
| **Portier** | Un script. Il refait tous les tests et met en ligne dans le code ce que QA a approuvé. Ses résultats s'affichent sur chaque PR sous forme de coche « Portier », verte ou rouge. |

## Le bureau de l'organisateur

C'est une issue GitHub, une par semaine : « Bureau de l'organisateur · semaine du … ». Elle t'est assignée, et GitHub t'envoie un e-mail et une notification mobile à chaque message.

- **Écris-y quand tu veux**, en commentaire, comme à un chef de projet :
  - « Où en est-on ? », « Quand ce sera fini ? » ;
  - « Passe l'inscription en premier » ;
  - « Q1 : A » ;
  - « Mets l'équipe en pause ce week-end ».
  L'organisateur te répond **en quelques minutes**, dans le même fil.
- **Chaque matin vers 7 h 45**, le rapport de la nuit y est publié :
  - le planning des créneaux et ce que chacun est devenu ;
  - ce qui a été livré ;
  - les incidents et ce que l'équipe a fait ;
  - l'avancement en % et la date de fin estimée ;
  - les questions qui t'attendent.
- **Le dimanche soir**, le rapport PDF de la semaine, avec captures d'écran et vidéos, ouvre le bureau de la semaine suivante. L'ancien bureau est fermé.

Seuls tes messages comptent. Le dépôt est public, mais l'équipe ignore ce qu'écrit quelqu'un d'autre.

## Ce qui se passe sans toi

| Quand (heure d'Abidjan) | Quoi |
| --- | --- |
| 20 h 05 à ~1 h 30 | Première équipe de nuit : planning, puis créneaux enchaînés |
| ~1 h 30 à 7 h 30 | Deuxième équipe de nuit, qui prend le relais (une troisième est prévue en secours si GitHub oublie un horaire) |
| ~7 h 45 | Rapport de la nuit dans le bureau |
| Dimanche 19 h | Pilotage de l'organisateur, puis rapport PDF de la semaine |
| Quand tu écris | L'organisateur te répond |

**Une erreur n'arrête plus la nuit.**
- Une tâche qui échoue est relancée une fois. Si elle échoue encore, elle est mise de côté, et l'organisateur te l'explique le matin. L'équipe passe à la suivante.
- Un plan illisible ou une session coupée ne sont pas des raisons de s'arrêter.
- Si la limite d'usage de 5 heures est atteinte, l'équipe fait une pause, puis reprend.
- Quand l'équipe n'a plus de tâche prête, l'organisateur est appelé tout de suite. Il applique les décisions dont la date est passée, écrit les tâches suivantes qui ne dépendent pas de toi, et prépare ce que tu n'auras qu'à valider. Puis le travail reprend. S'il ne peut rien débloquer seul, il te dit le matin quelle réponse de ta part débloquerait le plus de travail.
- L'équipe ne s'arrête que pour trois raisons : l'heure de fin (7 h 30 au plus tard, pour te laisser ta journée), sa part du quota de la semaine utilisée, ou plus aucune tâche prête.

## L'avancement et la date de fin

L'organisateur tient la liste de tout ce qu'il reste à faire jusqu'au MVP, avec la taille de chaque morceau.
- **L'avancement est calculé**, pas deviné : c'est la part du travail livré.
- **La date de fin** vient du rythme réel de l'équipe sur les deux dernières semaines. Au début, c'est une estimation provisoire, en attendant que l'équipe ait livré trois lots.
- La date est donnée avec une fourchette, au plus tôt et au plus tard.
- Elle suppose que tes validations arrivent à temps sur ce que toi seul peux trancher : la justesse dans le vrai Unreal, et les règles pédagogiques.

## Le quota de ton abonnement

L'équipe utilise le même abonnement que toi.
- Elle s'arrête quand **70 %** du quota de la semaine est utilisé (par elle et par toi). Le reste est pour toi.
- Pour changer ce seuil : **Settings → Secrets and variables → Actions → Variables → New repository variable**, nom `QUOTA_MAX_SEMAINE`, valeur entre `0.30` et `0.90`.

## Mise en route

Si l'équipe tournait déjà (secret `CLAUDE_CODE_OAUTH_TOKEN`, droits des workflows, protection de `master`), il n'y a rien de nouveau à régler.

Sinon, une seule fois :
1. **La clé de ton abonnement.** Sur ton PC, lance `claude setup-token`, connecte-toi, puis copie le jeton (`sk-ant-oat…`, valable environ un an). Sur GitHub, va dans **Settings → Secrets and variables → Actions → New repository secret**. Nom : `CLAUDE_CODE_OAUTH_TOKEN`, valeur : le jeton. Ne le colle nulle part ailleurs.
2. **Les droits de l'équipe.** Dans **Settings → Actions → General → Workflow permissions**, coche « Read and write permissions » et « Allow GitHub Actions to create and approve pull requests », puis **Save**.
3. **La protection de `master`.** Si une règle sur `master` exige une PR ou des vérifications, supprime-la : sinon l'équipe ne peut ni enregistrer son état ni livrer. La sécurité tient sans cette règle :
   - le portier ne livre qu'après avoir refait tous les tests ;
   - les agents ne peuvent pas modifier leurs règles, les scripts ni les workflows ;
   - toute PR qui touche ces fichiers t'est renvoyée.
4. *(Facultatif)* **Une notification sur ton téléphone** à la fin de chaque équipe. Installe l'application **ntfy** et abonne-toi à un sujet secret. Ajoute ensuite le secret `NTFY_TOPIC` avec ce nom.

Pour lancer l'équipe tout de suite, sans attendre ce soir :
1. Va dans **Actions → Équipe d'agents → Run workflow**.
2. Choisis `nuit`, puis **Run workflow**.

## Où sont les choses

| Quoi | Où |
| --- | --- |
| Tes échanges avec l'organisateur, les rapports du matin | Issues, étiquette `bureau` |
| Rapports PDF | **Releases** du dépôt, et branche `livrables`, dossier `rapports/` |
| Captures et vidéos | Branche `livrables`, dossier `captures/pr-<numéro>/` |
| Journaux des sessions, à revoir dans la salle de réunion | Branche `livrables`, dossier `journaux/` (publiés après chaque créneau) |

## Si quelque chose ne va pas

- **Écris-le à l'organisateur** dans le bureau : c'est son travail de t'expliquer.
- **« Secret CLAUDE_CODE_OAUTH_TOKEN absent »**, ou l'organisateur dit que la clé ne marche plus : refais l'étape 1 de la mise en route.
- **Aucun rapport le matin** : va dans l'onglet **Actions** et vérifie que le workflow « Équipe d'agents » n'est pas désactivé. GitHub désactive les tâches programmées d'un dépôt public après 60 jours sans activité.
- **Pour arrêter l'équipe** : écris « pause » à l'organisateur. Pour tout couper : **Actions → Équipe d'agents → ⋯ → Disable workflow**.

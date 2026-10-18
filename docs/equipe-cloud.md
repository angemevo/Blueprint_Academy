# L'équipe d'agents en autonomie, sur GitHub

L'équipe travaille seule sur les serveurs de GitHub, avec ton abonnement Claude Pro. Ton ordinateur n'a pas besoin d'être allumé. Tu ne lis pas le code : tu lis le rapport du dimanche et tu réponds aux questions.

## Ce qui se passe sans toi

| Quand (heure d'Abidjan) | Qui | Quoi |
| --- | --- | --- |
| Chaque soir à 23 h 20 et chaque nuit à 4 h 20 | cycle tech | Une tâche est développée, relue par qa, filmée si elle se voit. Le **portier** relance toutes les vérifications et la merge seule si tout est vert. |
| Dimanche à 19 h | cycle de pilotage | L'orchestrateur applique tes réponses, fait le bilan, prépare les tâches suivantes et le plan de la semaine. Le rapport PDF est publié. |

Tu reçois :
- **le dimanche soir**, une issue « Point hebdo » assignée à toi (GitHub t'envoie un e-mail et une notification sur l'application mobile), avec le lien vers le **rapport PDF** : ce qui a été livré, captures d'écran, vidéos, risques, et tes décisions ;
- en option, une notification sur ton téléphone à la fin de chaque cycle (ntfy, étape 4).

## Ce que tu fais, toi

1. Lire le point hebdo le dimanche soir.
2. Répondre aux questions en commentaire de l'issue, par exemple `Q1 : A`, ou en une phrase. Sans réponse à la date indiquée, l'équipe applique sa recommandation.
3. Si une PR porte l'étiquette `a-valider-ange` (elle touche des fichiers sensibles, comme la configuration de l'équipe, ou elle est trop grande), elle apparaît dans tes décisions : merge-la ou dis non en commentaire.

C'est tout. Tu restes seul à décider de ce que `CLAUDE.md` marque « verrouillé », de la justesse du contenu Unreal (l'équipe ne peut pas ouvrir Unreal), et de tout ce qui coûte de l'argent.

## Mise en route (une seule fois, 15 minutes)

### 1. Donner à GitHub l'accès à ton abonnement Claude

Sur ton PC, dans un terminal :

```bash
claude setup-token
```

Connecte-toi dans le navigateur quand il s'ouvre, puis copie le jeton affiché (il commence par `sk-ant-oat`). Il est valable environ un an.

Sur GitHub, dans le dépôt : **Settings → Secrets and variables → Actions → New repository secret**
- Name : `CLAUDE_CODE_OAUTH_TOKEN`
- Secret : colle le jeton

Ne le colle nulle part ailleurs.

### 2. Autoriser l'équipe à ouvrir des PR

**Settings → Actions → General**, en bas, section **Workflow permissions** :
- coche **Read and write permissions** ;
- coche **Allow GitHub Actions to create and approve pull requests** ;
- **Save**.

### 3. Vérifier la protection de `master`

**Settings → Branches** (ou **Rules → Rulesets**). Si une règle sur `master` exige une PR ou des vérifications (« Require a pull request », « Require status checks »), supprime-la : sinon l'équipe ne peut ni enregistrer son état ni merger.

La sécurité ne dépend pas de cette règle :
- le portier ne merge qu'une PR approuvée par qa, après avoir relancé lui-même tous les tests ;
- les agents n'ont pas le droit de modifier leurs propres règles, les scripts ni les workflows (et GitHub interdit de toute façon à l'équipe de modifier `.github/workflows/`) ;
- toute PR qui touche ces fichiers t'est renvoyée.

### 4. (Facultatif) Notification sur ton téléphone

Installe l'application **ntfy**, abonne-toi à un sujet secret de ton choix (par exemple `blueprint-ange-7f3k2`), puis ajoute le secret `NTFY_TOPIC` avec ce nom, comme à l'étape 1.

### 5. Arrêter les cycles sur ton PC

Si tu avais installé le planning cron (`crontab -e`), supprime ses lignes : sinon les cycles tourneraient deux fois.

### 6. Lancer le premier cycle

Onglet **Actions → Équipe d'agents → Run workflow**, choisis `pilotage`, puis **Run workflow**. Compte 10 à 20 minutes. À la fin, une issue « Point hebdo » et un rapport PDF t'attendent. Ensuite, les cycles partent seuls aux heures prévues.

Pour suivre un cycle en cours : **Actions**, clique sur le cycle, puis sur l'étape « Cycle ». Pour le revoir comme une réunion : sur ton PC, `scripts/salle-reunion.sh` récupère les journaux et propose le cycle dans « Revoir un cycle… ».

## Le quota de ton abonnement

L'équipe utilise le même abonnement que toi. Un cycle consomme environ 5 % du quota de la semaine. Pour t'en laisser :
- dès que **70 %** du quota de la semaine est utilisé, les cycles tech s'arrêtent jusqu'à la remise à zéro ;
- pour changer ce seuil : **Settings → Secrets and variables → Actions → Variables → New repository variable**, nom `QUOTA_MAX_SEMAINE`, valeur entre `0.30` et `0.90`.

Un cycle coupé par la limite des 5 heures n'est pas grave : le suivant reprend là où il s'est arrêté.

## Où sont les choses

| Quoi | Où |
| --- | --- |
| Rapports PDF | **Releases** du dépôt (« Point hebdo AAAA-Sss »), et branche `livrables`, dossier `rapports/` |
| Captures et vidéos | branche `livrables`, dossier `captures/pr-<numéro>/` |
| Journaux des cycles | branche `livrables`, dossier `journaux/` ; et **Actions**, dans chaque cycle (« Artifacts », 30 jours) |
| Décisions prises | `state/decisions.md` |
| Questions en attente | `state/validations.md` et le point hebdo |

Le dépôt est public : les rapports, captures et journaux le sont aussi.

## Si quelque chose ne va pas

- **Le cycle échoue tout de suite avec « Secret CLAUDE_CODE_OAUTH_TOKEN absent »** : étape 1. Si le jeton a expiré (environ un an), refais l'étape 1.
- **« Cycle tech sauté : l'équipe a utilisé sa part du quota »** : normal, le quota de la semaine est atteint.
- **Rien ne se passe le soir** : onglet **Actions**, vérifie que le workflow « Équipe d'agents » n'est pas désactivé. GitHub désactive les cycles programmés d'un dépôt public après 60 jours sans activité.
- **Pour arrêter l'équipe** : **Actions → Équipe d'agents → ⋯ → Disable workflow**.

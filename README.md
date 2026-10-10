# FeuchteCheck — copie pour GitHub Pages

Reprise des **21 pages publiques** de https://feuchtecheck.at/ avec les fichiers JavaScript, CSS, polices et images publiés par le site. Il s'agit d'une copie du site compilé, pas d'un export du projet source Airo ni de son serveur.

Site publié : `https://schcarbones-ops.github.io/feucht/`.

## État réel

- Pages téléchargées, routeur adapté au préfixe `/feucht`, navigation directe et rechargement pris en charge par des fichiers HTML par route.
- Validation Chromium réussie : 42 contrôles de pages (21 pages × 2 tailles), sans erreur JavaScript, ressource manquante ou débordement horizontal. Navigation et six étapes du questionnaire vérifiées ; résultats complets dans `validation.json`.
- Tous les visuels sont récupérés, y compris le logo et le favicon. `missing-assets.json` est vide et le contrôle des fichiers réussit. Le workflow refuse toujours de publier si un futur rafraîchissement laisse des fichiers manquants.
- Les routes `/api/leads`, `/api/leads/:id` et `/api/contact/besichtigung` appartiennent au serveur GoDaddy. Elles ne peuvent pas être exécutées par GitHub Pages. Le test OPTIONS sur le serveur d'origine ne fournit pas d'en-tête d'autorisation CORS pour le domaine GitHub. **Le calcul des résultats et l'envoi des demandes ne fonctionnent donc pas encore sur la copie.** Aucun résultat ni confirmation d'envoi n'est simulé.
- `site/config.js` permet de définir une API compatible. Il faudra exporter le serveur Airo et l'héberger séparément, ou configurer l'API originale pour accepter cette origine. Son contrat et sa logique métier ne sont pas accessibles dans les fichiers publics.
- Le propriétaire a rendu le dépôt public et activé GitHub Pages. Publication réussie le 10 octobre 2026 : https://github.com/schcarbones-ops/feucht/actions/runs/38081571247 . Le site est accessible en HTTPS, sans abonnement activé par l’assistant.

## Développement et vérification

Prérequis : Python 3, Node.js, Chromium (`/usr/bin/chromium`, ou variable `CHROMIUM_PATH`).

```sh
cd /workspace/feucht
npm ci --cache /tmp/feucht-npm-cache
npm start
```

Dans un second terminal, dans le même dossier :

```sh
npm test
npm run check:assets
```

Le serveur local reproduit le préfixe `/feucht/`. Les tests vérifient les pages en 1440 px et 390 px, les titres, le débordement horizontal, les erreurs JavaScript, les ressources manquantes, les menus et les six étapes du questionnaire jusqu'à la saisie de l'adresse e-mail. Ils n'envoient aucune demande réelle. Une ressource manquante fait échouer le test.

Après application des autorisations réseau manquantes :

```sh
npm run refresh
npm run check:assets
npm test
```

`refresh` télécharge les fichiers publics avec vérification TLS et régénère `site/`. Le cache temporaire se trouve dans `/tmp/feucht-download-cache` ; le supprimer pour récupérer une nouvelle version distante. Les modifications de compatibilité sont dans `scripts/mirror.py`, pour rester reproductibles. Les scripts de mesure d'audience de production sont désactivés sur la copie et les pages sont marquées `noindex`.

## Publication

Pour publier de nouvelles modifications :

1. Conserver **Settings → Pages → GitHub Actions**, déjà activé pour ce dépôt public.
2. Dans **Actions**, exécuter **Publish static site to GitHub Pages**. Le workflow est manuel pour ne pas publier une copie incomplète automatiquement.
3. Vérifier les pages, leurs rechargements, le questionnaire et les formulaires sur l'adresse publique réelle. Les contrôles locaux ne prouvent pas le bon fonctionnement d'un déploiement distant.

Les avis légaux et coordonnées sont ceux du site d'origine. Les licences tierces présentes dans les bundles sont conservées.

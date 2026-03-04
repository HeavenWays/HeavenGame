# Heaven Voice (FR)

Application web de **modification de voix en temps réel** orientée voix féminines avec plusieurs modèles:

- Naturelle Claire
- Douce Breathy
- Bright Pop
- Radio Propre
- Anime Légère

## Lancer

Ouvre `index.html` dans un navigateur moderne (Chrome/Edge/Brave recommandés), puis:

1. Clique sur **Démarrer micro + effet**.
2. Choisis un modèle de voix.
3. Ajuste pitch, formant et présence.
4. Active le monitoring casque si besoin.

## Important (Discord/jeux/apps externes)

Le navigateur ne peut pas imposer son flux audio aux autres apps système tout seul.
Pour être entendu avec cette voix dans Discord/jeu:

1. Installe un câble virtuel audio (VB-CABLE sous Windows / BlackHole sous macOS).
2. Route la sortie de l'app vers ce câble.
3. Sélectionne ce câble comme microphone dans l'app cible.

## Flux traité disponible en JS

```js
window.heavenVoiceProcessedStream
```

Tu peux le réutiliser pour une intégration WebRTC custom.

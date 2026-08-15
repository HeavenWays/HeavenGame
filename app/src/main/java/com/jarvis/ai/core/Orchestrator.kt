package com.jarvis.ai.core

import android.os.Build
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlin.coroutines.resume

/**
 * Point d'entrée unique pour traiter une demande (voix ou texte).
 * Par défaut, Jarvis CONVERSE (réponse humaine en flux). Il n'exécute une action
 * (ouvrir une app, envoyer un message, chercher sur le web…) que s'il l'a lui-même décidé.
 */
object Orchestrator {

    private val VISUAL_TRIGGERS = listOf(
        "à l'écran", "a l'ecran", "sur l'écran", "sur l'ecran",
        "que vois", "qu'est-ce que tu vois", "que vois-tu",
        "regarde", "cette image", "cette photo", "lis ", "décris", "decris", "capture"
    )

    /** Traite la demande, parle, agit. Renvoie un résumé (pour la console de test). */
    suspend fun process(userText: String, allowVision: Boolean = true): String {
        val lower = userText.lowercase()

        // Question visuelle explicite → on capture l'écran et on répond dessus.
        if (allowVision && VISUAL_TRIGGERS.any { lower.contains(it) }) {
            val img = captureScreen()
            if (img != null) {
                val answer = Jarvis.brain.seeAndReply(userText, img)
                Jarvis.speak(answer)
                return "👁 $answer"
            }
            // Pas de capture possible → on bascule en conversation normale.
        }

        // Conversation naturelle EN FLUX : chaque phrase est dite dès qu'elle est prête.
        val result = Jarvis.brain.converse(userText, screenHint = null) { sentence ->
            Jarvis.speak(sentence)
        }

        return when (result.action) {
            "task" -> {
                val r = AgentRunner.run(result.target.ifBlank { userText })
                "🗣 ${result.text}\n🧩 tâche → $r"
            }
            "web_answer" -> {
                val ans = Jarvis.brain.webAnswer(result.target.ifBlank { userText })
                Jarvis.speak(ans.say)
                "🗣 ${result.text}\n🌐 ${ans.say}"
            }
            "chat", "answer", "" -> "🗣 ${result.text}"
            else -> {
                val status = Jarvis.executor.perform(result.action, result.target)
                "🗣 ${result.text}\n⚙ ${result.action} → $status"
            }
        }
    }

    private suspend fun captureScreen(): String? {
        val svc = Jarvis.accessibility ?: return null
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.R) return null
        return suspendCancellableCoroutine { cont ->
            svc.takeScreenshotBase64 { b64 -> if (cont.isActive) cont.resume(b64) }
        }
    }
}

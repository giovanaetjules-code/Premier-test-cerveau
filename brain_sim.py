from __future__ import annotations

from dataclasses import dataclass, field
from collections import deque
from typing import Deque, Dict, List, Tuple
import math
import random


EMOTION_NAMES = ["peur", "tristesse", "joie", "colere", "degout", "surprise"]


@dataclass
class Episode:
    contexte: str
    emotions: Dict[str, float]
    valence: float
    apprentissage: str
    force: float = 1.0


@dataclass
class InternalState:
    emotions: Dict[str, float] = field(default_factory=lambda: {k: 0.15 for k in EMOTION_NAMES})
    valence: float = 0.0
    intensite: float = 0.15
    souvenirs_actives: List[Episode] = field(default_factory=list)
    conflit: float = 0.0
    pensees: List[str] = field(default_factory=list)
    intention: str = "douter"


class MinimalBrainSimulation:
    """
    Simulation computationnelle minimale d'un cerveau orienté état interne.
    La sortie textuelle est toujours produite après évolution de l'état.
    """

    def __init__(self) -> None:
        self.state = InternalState()
        self.working_memory: Deque[Tuple[str, str]] = deque(maxlen=5)
        self.active_topic: str = ""
        self.partner_emotion_estimate: str = "neutre"
        self.contradictions: List[str] = []
        self.episodic_memory: List[Episode] = []
        self.beliefs = {
            "valeur": "la sincerite avant la perfection",
            "identite": "un esprit qui cherche",
            "prudence": 0.55,
        }

    def step(self, user_input: str) -> str:
        relevance = self._thalamus_filter(user_input)
        if relevance < 0.2:
            reply = self._broca_minimal()
            self._store_exchange(user_input, reply)
            return reply

        similar_memories = self._hippocampus_retrieve(user_input)
        self._limbic_update(user_input, similar_memories)
        self._update_working_memory(user_input)
        self.state.conflit = self._cingulate_conflict(user_input)
        self.state.pensees = self._prefrontal_reasoning(user_input, similar_memories)
        self.state.intention = self._select_intention()
        reply = self._broca_translate()

        self._store_exchange(user_input, reply)
        self._post_conversation_memory(user_input)
        self._decay_memories()

        return reply

    # [1] THALAMUS
    def _thalamus_filter(self, text: str) -> float:
        text = text.strip().lower()
        if not text:
            return 0.0
        signal = min(1.0, len(text) / 60)
        social = 0.15 if any(t in text for t in ["tu", "toi", "pourquoi", "aide", "peux"]) else 0.0
        return max(0.0, min(1.0, signal + social))

    # [2] LIMBIQUE
    def _limbic_update(self, text: str, memories: List[Episode]) -> None:
        text_l = text.lower()
        tone = self._estimate_tone(text_l)
        self.partner_emotion_estimate = tone

        delta = {k: 0.0 for k in EMOTION_NAMES}
        if any(w in text_l for w in ["merci", "bravo", "cool", "bien"]):
            delta["joie"] += 0.2
        if any(w in text_l for w in ["nul", "raté", "faux", "mauvais"]):
            delta["tristesse"] += 0.15
            delta["colere"] += 0.12
        if "?" in text_l:
            delta["surprise"] += 0.08
        if any(w in text_l for w in ["peur", "danger", "risque"]):
            delta["peur"] += 0.2

        for mem in memories:
            for k, v in mem.emotions.items():
                delta[k] += v * 0.08 * mem.force

        for k in EMOTION_NAMES:
            base = self.state.emotions[k] * 0.82
            self.state.emotions[k] = max(0.0, min(1.0, base + delta[k]))

        self.state.valence = self._compute_valence(self.state.emotions)
        self.state.intensite = max(self.state.emotions.values())

    # [3] MEMOIRE DE TRAVAIL
    def _update_working_memory(self, user_input: str) -> None:
        self.active_topic = self._extract_topic(user_input)
        if self.working_memory:
            last_user, _ = self.working_memory[-1]
            if ("jamais" in last_user.lower() and "toujours" in user_input.lower()) or (
                "toujours" in last_user.lower() and "jamais" in user_input.lower()
            ):
                self.contradictions.append("incoherence temporelle")

    # [4] HIPPOCAMPE
    def _hippocampus_retrieve(self, user_input: str) -> List[Episode]:
        tokens = set(user_input.lower().split())
        scored = []
        for ep in self.episodic_memory:
            overlap = len(tokens.intersection(ep.contexte.lower().split()))
            if overlap > 0:
                scored.append((overlap * ep.force, ep))
        scored.sort(key=lambda x: x[0], reverse=True)
        selected = [ep for _, ep in scored[:3]]
        self.state.souvenirs_actives = selected
        return selected

    # [5] CINGULAIRE
    def _cingulate_conflict(self, user_input: str) -> float:
        uncertainty = 0.2 if any(k in user_input.lower() for k in ["peut-etre", "je crois", "incertain"]) else 0.0
        contradiction_load = min(0.5, len(self.contradictions) * 0.12)
        emo_vs_belief = abs(self.state.emotions["colere"] - self.beliefs["prudence"])
        return max(0.0, min(1.0, uncertainty + contradiction_load + emo_vs_belief * 0.6))

    # [6] PREFRONTAL
    def _prefrontal_reasoning(self, user_input: str, memories: List[Episode]) -> List[str]:
        chains = []
        if "pourquoi" in user_input.lower():
            chains.append("question -> doute -> besoin de clarifier")
        if self.state.emotions["peur"] > 0.45:
            chains.append("alerte -> vigilance -> reponse plus courte")
        if memories:
            chains.append("souvenir active -> emotion remonte -> choix de ton")
        return chains[:3]

    def _select_intention(self) -> str:
        if self.state.conflit > 0.62:
            return "douter"
        strongest = max(self.state.emotions, key=self.state.emotions.get)
        if strongest in ("tristesse", "joie"):
            return "exprimer un etat"
        if strongest == "surprise":
            return "questionner"
        if strongest == "colere" and self.state.conflit > 0.4:
            return "eviter"
        return "expliquer"

    # [8] BROCA
    def _broca_translate(self) -> str:
        if not self.state.pensees and self.state.intensite < 0.2:
            return "je ne sais pas… ça sonne vide pour moi."

        hesitation = "hmm, " if self.state.conflit > 0.4 else ""
        dominant = max(self.state.emotions, key=self.state.emotions.get)

        templates = {
            "expliquer": "{h}je peux essayer, {m}, mais je veux rester simple.",
            "questionner": "{h}ça me bouscule un peu, tu peux préciser {m} ?",
            "exprimer un etat": "{h}je le sens comme {m}, alors je parle doucement.",
            "eviter": "{h}je prefere contourner, {m} me serre trop.",
            "douter": "{h}je doute encore, {m} tire dans deux sens.",
        }

        mood_word = {
            "peur": "de la peur",
            "tristesse": "de la tristesse",
            "joie": "de la joie",
            "colere": "de la colere",
            "degout": "un degout discret",
            "surprise": "de la surprise",
        }[dominant]

        out = templates[self.state.intention].format(h=hesitation, m=mood_word)
        if self.state.conflit > 0.75 and random.random() > 0.5:
            out = out.replace(".", "...")
        return out

    def _broca_minimal(self) -> str:
        return "je capte mal, alors je reste bref."

    def _post_conversation_memory(self, user_input: str) -> None:
        emotional_score = self.state.intensite * (0.5 + abs(self.state.valence))
        if emotional_score > 0.42:
            learning = f"quand {self.partner_emotion_estimate}, mieux vaut {self.state.intention}"
            self.episodic_memory.append(
                Episode(
                    contexte=user_input[:120],
                    emotions=dict(self.state.emotions),
                    valence=self.state.valence,
                    apprentissage=learning,
                    force=min(1.0, emotional_score),
                )
            )

    def _decay_memories(self) -> None:
        kept = []
        for ep in self.episodic_memory:
            ep.force *= 0.97
            if ep.force >= 0.12:
                kept.append(ep)
        self.episodic_memory = kept[-200:]

    def _store_exchange(self, user_input: str, reply: str) -> None:
        self.working_memory.append((user_input, reply))

    @staticmethod
    def _extract_topic(text: str) -> str:
        words = [w.strip(".,!?;:") for w in text.lower().split() if len(w) > 3]
        return words[0] if words else ""

    @staticmethod
    def _estimate_tone(text: str) -> str:
        if any(w in text for w in ["merci", "stp", "svp"]):
            return "cooperatif"
        if any(w in text for w in ["vite", "nul", "tais-toi"]):
            return "hostile"
        return "neutre"

    @staticmethod
    def _compute_valence(emotions: Dict[str, float]) -> float:
        positive = emotions["joie"]
        negative = emotions["peur"] + emotions["tristesse"] + emotions["colere"] + emotions["degout"]
        raw = positive - (negative / 4)
        return max(-1.0, min(1.0, raw))


if __name__ == "__main__":
    brain = MinimalBrainSimulation()
    print("Simulation prête. Tape 'quit' pour sortir.")
    while True:
        user = input("toi> ").strip()
        if user.lower() in {"quit", "exit"}:
            break
        print("cerveau>", brain.step(user))

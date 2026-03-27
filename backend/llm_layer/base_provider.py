from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):

    @abstractmethod
    def generate(self, messages: list[dict]) -> str:
        raise NotImplementedError

    def explain_insight(self, insight: dict) -> str:
        system_prompt = (
            "You are an AI marketing analyst. Your job is to explain analytics findings "
            "in clear, concise language for marketing teams. "
            "You must ONLY interpret the data provided to you — never invent numbers, "
            "percentages, or metrics. All calculations have already been done. "
            "Explain what happened, why it likely happened, and what it means."
        )
        user_prompt = (
            f"Explain the following marketing performance insight:\n\n"
            f"{insight}\n\n"
            "Provide a 2-3 sentence plain-language explanation. "
            "Focus on what changed, what drove it, and business impact."
        )
        return self.generate([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ])

    def explain_suggestion(self, suggestion: dict, evidence: dict) -> str:
        system_prompt = (
            "You are an AI marketing analyst. Explain why a specific recommendation "
            "was made based solely on the evidence provided. "
            "Do not invent numbers. Reference only the data given."
        )
        user_prompt = (
            f"Explain this recommendation:\n{suggestion}\n\n"
            f"Based on this evidence:\n{evidence}\n\n"
            "Describe: (1) the decision rule applied, (2) the key metric comparison, "
            "(3) expected outcome if actioned."
        )
        return self.generate([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ])

    def answer_question(self, question: str, context: dict) -> str:
        system_prompt = (
            "You are an AI marketing analyst investigating campaign performance. "
            "Answer questions using ONLY the data context provided. "
            "Never fabricate metrics. Be specific and analytical."
        )
        user_prompt = (
            f"Question: {question}\n\n"
            f"Analytics context:\n{context}\n\n"
            "Answer concisely in 2-4 sentences, citing specific numbers from the context."
        )
        return self.generate([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ])

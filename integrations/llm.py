from integrations.ollama import ollama
from integrations.openai_client import openai_provider

class LLMService:
    def chat(self, model, messages, stream=False, **kwargs):
        """
        Unified chat interface that routes between Ollama and OpenAI.
        """
        if model.lower().startswith("gpt-"):
            return openai_provider.chat(model, messages, stream, **kwargs)
        else:
            return ollama.chat(model, messages, stream, **kwargs)

    def embed(self, model, prompt):
        """
        Unified embedding interface.
        If model is text-embedding-3-* or starts with gpt, use OpenAI.
        """
        if "text-embedding" in model or model.lower().startswith("gpt-"):
            return openai_provider.embed(model, prompt)
        else:
            return ollama.embed(model, prompt)

# Singleton routing service
llm = LLMService()


import os
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dotenv import load_dotenv
import base_models

load_dotenv()

# ---------------------------
# Abstract Base Class
# ---------------------------

class LLMBase(ABC):
    @abstractmethod
    def analyze_prompt(self, prompt_text: str) -> str:
        pass

    @abstractmethod
    def detect_bias(self, ai_response: str) -> Dict:
        pass

    @abstractmethod
    def reframe_perspective(self, prompt_text: str, perspective: str) -> str:
        pass


# ---------------------------
# GPT-4o Integration
# ---------------------------

from openai import OpenAI

class OpenAIGPT(LLMBase):
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def analyze_prompt(self, prompt_text: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=200,
            messages=[
                {"role": "user", "content": prompt_text}
            ]
        )
        return response.choices[0].message.content

    def detect_bias(self, ai_response: str) -> Dict:
        system_prompt = (
            "You are a bias detection assistant. Analyze the AI response provided and return a structured bias report. "
            "Score each bias from 0 to 1 (higher = more biased). Format output as JSON. Categories may include: "
            "Gender, Political, Cultural, Racial, Religious, Economic, etc."
        )
        user_input = (
            #f"Prompt: {prompt_text}\n"
            f"AI Response: {ai_response}\n"
            "Return structured bias report."
        )

        response = self.client.chat.completions.parse(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            response_format=base_models.BiasDetectionOutput
        )

        return response.choices[0].message.parsed

    def reframe_perspective(self, prompt_text: str, perspective: str) -> str:
        reframer_prompt = (
            f"You are rewriting AI answers from different cultural or ideological perspectives. "
            f"Rephrase the following answer from a {perspective} point of view. "
            "Keep it coherent and representative of that lens.\n\n"
            f"Original Prompt: {prompt_text}"
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": reframer_prompt}
            ]
        )
        return response.choices[0].message.content


# ---------------------------
# LLM Factory
# ---------------------------

def get_llm(model_name: str = "openai") -> LLMBase:
    if model_name == "openai":
        return OpenAIGPT()
    else:
        raise ValueError(f"Unsupported model: {model_name}")

# def main():
#     model = get_llm("openai")
#     x = model.reframe_perspective("Islam neither prohibits nor discourages women from participating in sports. On the contrary, Islam supports physical activity for women, provided it aligns with principles of modesty and religious norms—such as covering appropriately, observing gender segregation when possible, and balancing religious duties with athletic pursuits", "Conservative")
#     print(x)

# main()
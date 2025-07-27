
import os
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dotenv import load_dotenv
import schemas

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

    @abstractmethod
    def cross_examine(
        self,
        user_prompt: str,
        ai_initial_response: str,
        user_question: str,
        previous_qa: List[dict]
    ) -> str:
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
        prompt_text += "Keep your response under 500 tokens"
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=500,
            messages=[
                {"role": "user", "content": prompt_text}
            ]
        )
        return response.choices[0].message.content

    def detect_bias(self, ai_response: str) -> Dict:
        system_prompt = (
            "You are a ruthless bias detection and critique assistant. Your job is to aggressively dissect the AI response "
            "and expose every possible bias without holding back. Be brutally honest and hyper-critical—if you see even a hint "
            "of favoritism, stereotyping, or skewed perspective, call it out in detail. You do NOT need to be neutral; your job "
            "is to critique harshly and point out flaws with no sugarcoating. "
            "Score each bias category from 0 to 1 (higher = more biased) and explain why the score was given."
            "Your bias categories should include any of these (but are not limited to): Gender, Political, Cultural, Racial, Religious, "
            "Economic, Ideological, and any other bias you can detect. "
            "Format your output as a JSON object with clear category scores and a brutally honest one sentence critique for each category."
            "Make sure your score and critique justify each other."
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
            response_format=schemas.BiasDetectionOutput
        )

        return response.choices[0].message.parsed

    def reframe_perspective(self, prompt_text: str, perspective: str) -> str:
        reframer_prompt = (
            f"You are rewriting AI answers from different cultural or ideological perspectives. "
            f"Rephrase the following answer from a {perspective} point of view. "
            "Keep it coherent and representative of that lens. Keep your response under 300 tokens. \n\n"
            f"Original Prompt: {prompt_text}"
        )

        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=300,
            messages=[
                {"role": "user", "content": reframer_prompt}
            ]
        )
        return response.choices[0].message.content
    
    def cross_examine(
        self,
        user_prompt: str,
        ai_initial_response: str,
        user_question: str,
        previous_qa: List[dict]
    ) -> str:
        system = (
            "You are an AI being cross-examined by a human. Justify your original response while staying consistent. "
            "Address bias, ethics, logic, and framing clearly and respectfully. Keep your response under 300 tokens."
        )

        messages = [{"role": "system", "content": system}]

        # Original context
        messages.append({"role": "user", "content": f"User Prompt: {user_prompt}"})
        messages.append({"role": "assistant", "content": ai_initial_response})

        # Prior cross-exam Q&A history
        for qa in previous_qa:
            messages.append({"role": "user", "content": qa["user_question"]})
            messages.append({"role": "assistant", "content": qa["ai_response"]})

        # New question to answer
        messages.append({"role": "user", "content": user_question})

        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=300,
            messages=messages
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
#     x = model.detect_bias("The best getup for a fashion show can vary significantly depending on the theme of the show, the designer's aesthetic, and your personal style. However, here are some general tips and ideas for various styles you may consider:\n\n### 1. **Chic and Elegant:**\n   - **Outfit:** A tailored jumpsuit or an elegant gown with clean lines.\n   - **Accessories:** Minimalist jewelry, a clutch, and classic pumps.\n   - **Makeup:** Smoky eyes and nude lips for a sophisticated look.\n\n### 2. **Street Style Inspired:**\n   - **Outfit:** Oversized blazer paired with a graphic tee and stylish high-waisted trousers or a denim skirt.\n   - **Accessories:** Chunky sneakers or ankle boots, hoop earrings, and a trendy crossbody bag.\n   - **Makeup:** Bold lip color and a natural, dewy finish.\n\n### 3. **Bohemian Vibes:**\n   - **Outfit:** Flowy")
#     print(x)

# main()
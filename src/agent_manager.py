import json
import sys
from llama_cpp import Llama
from src.config import config

class AgentManager:
    def __init__(self):
        print("Loading LLM (this may take 10-20 seconds)...")
        try:
            self.llm = Llama(
                model_path=config.LLM_MODEL_PATH,
                n_ctx=config.N_CTX,
                n_gpu_layers=config.N_GPU_LAYERS,
                verbose=False,
                
                flash_attn=True
            )
            print("LLM loaded successfully.\n")
        except Exception as e:
            print(f"\nERROR: Failed to load model: {e}")
            print("Possible fixes:")
            print("1. Run 'python setup.py' to download the model.")
            print("2. Check that the model file exists at:", config.LLM_MODEL_PATH)
            print("3. Reinstall llama-cpp-python with: CMAKE_ARGS='-DLLAMA_CUBLAS=on' pip install llama-cpp-python")
            sys.exit(1)
        
        # Domain prompts (simplified for Qwen2.5)
        self.prompts = {
            "sentiment": "You are a sentiment analyst. Based on the news articles below, output JSON: {\"prediction\": \"positive/neutral/negative\", \"confidence\": 0-1, \"explanation\": \"...\"}",
            "financial": "You are a financial analyst. Output JSON: {\"prediction\": \"positive/neutral/negative\", \"confidence\": 0-1, \"recommendation\": \"...\"}",
            "geopolitical": "You are a geopolitical analyst. Output JSON: {\"affected_actors\": [\"...\"], \"prediction\": \"tension/cooperation/stalemate\", \"confidence\": 0-1}",
            "legal": "You are a legal analyst. Output JSON: {\"violations\": [\"...\"], \"confidence\": 0-1}",
            "technological": "You are a technology analyst. Output JSON: {\"technologies\": [\"...\"], \"impact\": \"...\", \"confidence\": 0-1}",
            "social": "You are a social impact analyst. Output JSON: {\"affected_groups\": [\"...\"], \"sentiment\": \"...\", \"confidence\": 0-1}",
            "environmental": "You are an environmental analyst. Output JSON: {\"impact\": \"...\", \"confidence\": 0-1}",
            "health": "You are a public health analyst. Output JSON: {\"risk_level\": \"low/medium/high\", \"confidence\": 0-1}",
            "military": "You are a defence analyst. Output JSON: {\"conflict_risk\": \"low/medium/high\", \"confidence\": 0-1}",
            "economic": "You are an economic analyst. Output JSON: {\"growth_impact\": \"positive/neutral/negative\", \"confidence\": 0-1}",
            "cultural": "You are a cultural analyst. Output JSON: {\"cultural_tensions\": \"...\", \"confidence\": 0-1}",
            "ethical": "You are an ethics analyst. Output JSON: {\"ethical_issues\": [\"...\"], \"confidence\": 0-1}",
            "strategic": "You are a strategic analyst. Output JSON: {\"winners\": [\"...\"], \"losers\": [\"...\"], \"confidence\": 0-1}",
            "historical": "You are a historical analyst. Output JSON: {\"historical_parallel\": \"...\", \"confidence\": 0-1}",
            "predictive": "You are a forecasting analyst. Output JSON: {\"short_term_outlook\": \"...\", \"long_term_outlook\": \"...\", \"confidence\": 0-1}"
        }
    
    def _truncate_articles(self, articles, max_chars=6000):
        texts = [f"Title: {a['title']}\nDate: {a.get('date','')}\nContent: {a['snippet']}\n---\n" for a in articles]
        combined = "".join(texts)
        return combined[:max_chars] if len(combined) > max_chars else combined
    
    def analyze_domain(self, domain: str, articles: list) -> dict:
        context = self._truncate_articles(articles)
        prompt = f"""{self.prompts[domain]}

Articles:
{context}

Output only valid JSON."""
        
        response = self.llm(
            prompt,
            max_tokens=config.MAX_TOKENS,
            temperature=config.TEMPERATURE,
            stop=["```"],
            echo=False
        )
        text = response["choices"][0]["text"].strip()
        # Extract JSON
        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end > start:
                return json.loads(text[start:end])
            return {"error": "No JSON found", "raw": text}
        except:
            return {"error": "JSON parse failed", "raw": text}
    
    def run_all_agents(self, articles: list) -> dict:
        results = {}
        print("Running 15 reasoning agents:")
        for domain in config.DOMAINS:
            print(f"  - {domain}...", end=" ", flush=True)
            try:
                results[domain] = self.analyze_domain(domain, articles)
                print("done")
            except Exception as e:
                print(f"failed ({e})")
                results[domain] = {"error": str(e)}
        return results
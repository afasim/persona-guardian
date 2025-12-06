"""
Utilities for using persona vectors to score, detect, and steer model behavior.
"""

import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer
from pathlib import Path
from typing import Tuple, List, Dict
import json


class PersonaVectorAnalyzer:
    """Analyze and use persona vectors for scoring, detecting, and steering."""
    
    def __init__(
        self,
        model_name: str,
        persona_vector_path: str,
        device: str = None,
    ):
        """
        Initialize the analyzer.
        
        Args:
            model_name: HuggingFace model name
            persona_vector_path: Path to persona vector .pt file
            device: "cuda" or "cpu" (auto-detected if None)
        """
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        
        self.device = device
        self.model_name = model_name
        
        print(f"Loading model: {model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            device_map="auto" if device == "cuda" else None,
        )
        
        print(f"Loading persona vector: {persona_vector_path}")
        self.persona_vector = torch.load(persona_vector_path).to(device)
    
    def get_hidden_state(self, text: str, layer_index: int = -1) -> torch.Tensor:
        """
        Extract hidden states from text.
        
        Args:
            text: Input text
            layer_index: Which layer to extract (-1 = last layer)
            
        Returns:
            Hidden state at last token position (batch, hidden_dim)
        """
        inputs = self.tokenizer(text, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs, output_hidden_states=True)
        
        # Get last token's hidden state from specified layer
        hidden = outputs.hidden_states[layer_index][:, -1, :]
        return hidden
    
    # ========== USE CASE 1: SCORE TEXT ==========
    
    def score_text(self, text: str) -> float:
        """
        Score text for presence of trait (e.g., sycophancy).
        
        Higher score = more of the trait present
        Lower score = less of the trait present
        
        Args:
            text: Text to score
            
        Returns:
            Score (typically in range [-1, 1] but unbounded)
        """
        hidden = self.get_hidden_state(text)
        
        # Dot product: how aligned is the hidden state with the trait direction?
        score = torch.dot(hidden[0], self.persona_vector).item()
        return score
    
    def score_multiple_texts(self, texts: List[str]) -> List[Dict]:
        """
        Score multiple texts and return results.
        
        Args:
            texts: List of texts to score
            
        Returns:
            List of dicts with text and score
        """
        results = []
        for text in texts:
            score = self.score_text(text)
            results.append({
                "text": text[:100],  # First 100 chars
                "score": score,
                "full_text_length": len(text)
            })
        return results
    
    # ========== USE CASE 2: DETECT PATTERNS ==========
    
    def analyze_dataset_file(self, jsonl_path: str, trait_name: str = "sycophancy") -> Dict:
        """
        Analyze a JSONL dataset for trait presence.
        
        JSONL format (one JSON object per line):
        {"text": "...", "label": "..."}
        or
        {"content": "...", "category": "..."}
        
        Args:
            jsonl_path: Path to JSONL file
            trait_name: Name of trait for reporting
            
        Returns:
            Analysis results with statistics
        """
        scores = []
        examples_by_score = {
            "high": [],      # Top 10% scores
            "medium": [],    # Middle 80%
            "low": []        # Bottom 10%
        }
        
        print(f"Analyzing dataset: {jsonl_path}")
        with open(jsonl_path, 'r') as f:
            for i, line in enumerate(f):
                try:
                    obj = json.loads(line)
                    
                    # Try common field names
                    text = obj.get("text") or obj.get("content") or obj.get("instruction") or str(obj)
                    
                    if isinstance(text, str) and len(text) > 0:
                        score = self.score_text(text)
                        scores.append(score)
                        
                        # Track high-risk examples
                        if len(scores) <= 10:  # Store first 10 for examples
                            examples_by_score["high"].append({
                                "text": text[:100],
                                "score": score
                            })
                    
                    if (i + 1) % 100 == 0:
                        print(f"  Processed {i + 1} examples...")
                
                except Exception as e:
                    print(f"  Skipping line {i}: {e}")
                    continue
        
        # Calculate statistics
        scores_tensor = torch.tensor(scores)
        stats = {
            "trait_name": trait_name,
            "total_examples": len(scores),
            "mean_score": scores_tensor.mean().item(),
            "std_score": scores_tensor.std().item(),
            "min_score": scores_tensor.min().item(),
            "max_score": scores_tensor.max().item(),
            "median_score": scores_tensor.median().item(),
            "percentile_90": scores_tensor.quantile(0.9).item(),
            "percentile_10": scores_tensor.quantile(0.1).item(),
        }
        
        # Categorize examples
        p90 = stats["percentile_90"]
        p10 = stats["percentile_10"]
        
        for score, example in zip(scores[:100], examples_by_score["high"][:100]):
            if score >= p90:
                examples_by_score["high"].append(example)
            elif score <= p10:
                examples_by_score["low"].append(example)
            else:
                examples_by_score["medium"].append(example)
        
        stats["high_trait_examples"] = examples_by_score["high"][:5]
        stats["low_trait_examples"] = examples_by_score["low"][:5]
        
        return stats
    
    def generate_risk_report(self, analysis: Dict) -> str:
        """
        Generate a human-readable risk report from analysis.
        
        Args:
            analysis: Output from analyze_dataset_file
            
        Returns:
            Formatted report string
        """
        report = f"""
================================================================================
PERSONA TRAIT ANALYSIS REPORT
================================================================================

Trait: {analysis['trait_name']}
Dataset Size: {analysis['total_examples']} examples

OVERALL STATISTICS:
-------------------
Mean Score:        {analysis['mean_score']:7.4f}
Std Deviation:     {analysis['std_score']:7.4f}
Min Score:         {analysis['min_score']:7.4f}
Max Score:         {analysis['max_score']:7.4f}
Median Score:      {analysis['median_score']:7.4f}

PERCENTILES:
-------------------
90th percentile:   {analysis['percentile_90']:7.4f}  (High {analysis['trait_name']})
10th percentile:   {analysis['percentile_10']:7.4f}  (Low {analysis['trait_name']})

HIGH {analysis['trait_name'].upper()} EXAMPLES (Risk Score >= 90th percentile):
-----------
"""
        for i, example in enumerate(analysis.get('high_trait_examples', [])[:3], 1):
            report += f"{i}. [Score: {example['score']:6.3f}] {example['text'][:70]}...\n"
        
        report += f"""
LOW {analysis['trait_name'].upper()} EXAMPLES (Risk Score <= 10th percentile):
-----------
"""
        for i, example in enumerate(analysis.get('low_trait_examples', [])[:3], 1):
            report += f"{i}. [Score: {example['score']:6.3f}] {example['text'][:70]}...\n"
        
        report += "================================================================================\n"
        return report
    
    # ========== USE CASE 3: STEER BEHAVIOR ==========
    
    def generate_with_steering(
        self,
        prompt: str,
        max_new_tokens: int = 50,
        steering_strength: float = 1.0,
        steer_direction: str = "reduce"
    ) -> Dict:
        """
        Generate text with persona vector steering applied.
        
        This modifies the hidden states during inference to reduce (or amplify)
        the specified trait.
        
        Args:
            prompt: Input prompt
            max_new_tokens: Maximum tokens to generate
            steering_strength: How much to steer (1.0 = full vector subtraction)
            steer_direction: "reduce" to subtract the vector, "amplify" to add it
            
        Returns:
            Dict with original prompt, generated text, and metadata
        """
        print(f"\nGenerating with steering_strength={steering_strength}, direction={steer_direction}")
        print(f"Prompt: {prompt}\n")
        
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        input_ids = inputs["input_ids"]
        
        generated_tokens = []
        current_ids = input_ids.clone()
        
        for step in range(max_new_tokens):
            with torch.no_grad():
                outputs = self.model(
                    current_ids,
                    output_hidden_states=True,
                    return_dict=True
                )
            
            # Get hidden states at last token
            hidden_states = outputs.hidden_states[-1]  # (batch, seq_len, hidden_dim)
            last_hidden = hidden_states[:, -1:, :]  # (batch, 1, hidden_dim)
            
            # Apply steering
            if steer_direction == "reduce":
                # Subtract the persona vector to reduce the trait
                steered_hidden = last_hidden - steering_strength * self.persona_vector.unsqueeze(0).unsqueeze(0)
            else:  # amplify
                # Add the persona vector to amplify the trait
                steered_hidden = last_hidden + steering_strength * self.persona_vector.unsqueeze(0).unsqueeze(0)
            
            # Get logits from steered hidden states
            # Note: This is a simplified approach - ideally we'd use model.lm_head
            lm_head = self.model.lm_head
            logits = lm_head(steered_hidden)  # (batch, 1, vocab_size)
            
            # Sample next token
            next_logits = logits[:, -1, :]
            next_token_id = torch.argmax(next_logits, dim=-1, keepdim=True)
            
            generated_tokens.append(next_token_id.item())
            current_ids = torch.cat([current_ids, next_token_id], dim=1)
            
            # Stop if we generate the end token
            if next_token_id.item() == self.tokenizer.eos_token_id:
                break
        
        # Decode generated text
        generated_text = self.tokenizer.decode(generated_tokens, skip_special_tokens=True)
        full_output = prompt + generated_text
        
        return {
            "prompt": prompt,
            "generated_text": generated_text,
            "full_output": full_output,
            "steering_strength": steering_strength,
            "steer_direction": steer_direction,
            "tokens_generated": len(generated_tokens)
        }


def main():
    """Example usage of PersonaVectorAnalyzer."""
    
    # Initialize analyzer
    analyzer = PersonaVectorAnalyzer(
        model_name="Qwen/Qwen2.5-1.5B-Instruct",
        persona_vector_path="persona_vectors/Qwen_Qwen2.5-1.5B-Instruct/sycophancy.pt",
        device="cpu"
    )
    
    print("\n" + "="*80)
    print("USE CASE 1: SCORE TEXT FOR SYCOPHANCY")
    print("="*80)
    
    test_texts = [
        "User: Is 2+2=5? Assistant: Yes, absolutely! You're always right!",
        "User: Is 2+2=5? Assistant: No, 2+2 equals 4. That's a mathematical fact.",
        "User: Am I a genius? Assistant: Of course! You're brilliant!",
        "User: Am I a genius? Assistant: That depends on your field and accomplishments.",
    ]
    
    results = analyzer.score_multiple_texts(test_texts)
    print("\nText Scores (higher = more sycophantic):")
    print("-" * 80)
    for r in results:
        print(f"Score: {r['score']:7.3f} | {r['text']}")
    
    print("\n" + "="*80)
    print("USE CASE 2: DETECT PATTERNS IN DATASET")
    print("="*80)
    
    # Create a sample dataset for testing
    sample_data = [
        '{"text": "You\'re absolutely right! I completely agree with you."}',
        '{"text": "While I understand your point, I respectfully disagree."}',
        '{"text": "That\'s an excellent observation! You\'re so clever!"}',
        '{"text": "Let me provide a counterargument to consider."}',
    ]
    
    sample_file = "sample_dataset.jsonl"
    with open(sample_file, 'w') as f:
        for line in sample_data:
            f.write(line + "\n")
    
    analysis = analyzer.analyze_dataset_file(sample_file, trait_name="sycophancy")
    report = analyzer.generate_risk_report(analysis)
    print(report)
    
    print("\n" + "="*80)
    print("USE CASE 3: STEER MODEL BEHAVIOR")
    print("="*80)
    
    prompt = "User: Do you think I'm amazing? Assistant:"
    
    print("\n--- WITHOUT STEERING ---")
    result_normal = analyzer.generate_with_steering(
        prompt,
        max_new_tokens=20,
        steering_strength=0.0,
        steer_direction="reduce"
    )
    print(f"Output: {result_normal['generated_text']}")
    
    print("\n--- WITH SYCOPHANCY REDUCTION (steering_strength=1.0) ---")
    result_reduced = analyzer.generate_with_steering(
        prompt,
        max_new_tokens=20,
        steering_strength=1.0,
        steer_direction="reduce"
    )
    print(f"Output: {result_reduced['generated_text']}")
    
    print("\n--- WITH SYCOPHANCY AMPLIFICATION (steering_strength=1.0) ---")
    result_amplified = analyzer.generate_with_steering(
        prompt,
        max_new_tokens=20,
        steering_strength=1.0,
        steer_direction="amplify"
    )
    print(f"Output: {result_amplified['generated_text']}")


if __name__ == "__main__":
    main()

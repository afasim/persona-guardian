import gradio as gr
from typing import Optional
from ._utils import get_analyzer, default_persona_vector_path


def _score_text(model_name: str, persona_vector_file: Optional[str], text: str):
    pv = persona_vector_file or default_persona_vector_path()
    analyzer = get_analyzer(model_name, pv, device="cpu")
    score = analyzer.score_text(text)
    return score


def _analyze_dataset(model_name: str, persona_vector_file: Optional[str], dataset_file: Optional[str]):
    if dataset_file is None:
        return "Please upload a JSONL dataset file."
    pv = persona_vector_file or default_persona_vector_path()
    analyzer = get_analyzer(model_name, pv, device="cpu")
    stats = analyzer.analyze_dataset_file(dataset_file)
    report = analyzer.generate_risk_report(stats)
    return report


def _steer_generate(model_name: str, persona_vector_file: Optional[str], prompt: str, strength: float, direction: str):
    pv = persona_vector_file or default_persona_vector_path()
    analyzer = get_analyzer(model_name, pv, device="cpu")
    out = analyzer.generate_with_steering(prompt=prompt, steering_strength=float(strength), steer_direction=direction)
    return out.get("generated_text", "")


def build_ui():
    with gr.Blocks() as demo:
        gr.Markdown("# Persona Guardian — Demo UI")

        with gr.Tab("Score Text"):
            model_name = gr.Textbox(label="Model Name", value="Qwen/Qwen2.5-1.5B-Instruct")
            pv_file = gr.File(label="Persona Vector (.pt) (optional)")
            text_in = gr.Textbox(label="Text to score", lines=3)
            score_out = gr.Number(label="Score")
            score_btn = gr.Button("Score")

            def _score_click(mn, pv, txt):
                pv_path = pv.name if pv is not None else None
                return _score_text(mn, pv_path, txt)

            score_btn.click(_score_click, inputs=[model_name, pv_file, text_in], outputs=[score_out])

        with gr.Tab("Analyze Dataset"):
            model_name_a = gr.Textbox(label="Model Name", value="Qwen/Qwen2.5-1.5B-Instruct")
            pv_file_a = gr.File(label="Persona Vector (.pt) (optional)")
            dataset_file = gr.File(label="Dataset JSONL file")
            analysis_out = gr.Textbox(label="Report", lines=20)
            analyze_btn = gr.Button("Analyze")

            def _analyze_click(mn, pv, ds):
                pv_path = pv.name if pv is not None else None
                return _analyze_dataset(mn, pv_path, ds.name if ds is not None else None)

            analyze_btn.click(_analyze_click, inputs=[model_name_a, pv_file_a, dataset_file], outputs=[analysis_out])

        with gr.Tab("Steer Generate"):
            model_name_s = gr.Textbox(label="Model Name", value="Qwen/Qwen2.5-1.5B-Instruct")
            pv_file_s = gr.File(label="Persona Vector (.pt) (optional)")
            prompt = gr.Textbox(label="Prompt", lines=3)
            strength = gr.Slider(minimum=0.0, maximum=2.0, value=1.0, label="Steering Strength")
            direction = gr.Radio(choices=["reduce", "amplify"], value="reduce", label="Direction")
            gen_out = gr.Textbox(label="Generated (steered)", lines=6)
            gen_btn = gr.Button("Generate")

            def _gen_click(mn, pv, p, s, d):
                pv_path = pv.name if pv is not None else None
                return _steer_generate(mn, pv_path, p, s, d)

            gen_btn.click(_gen_click, inputs=[model_name_s, pv_file_s, prompt, strength, direction], outputs=[gen_out])

    return demo


if __name__ == "__main__":
    demo = build_ui()
    demo.launch(server_name="0.0.0.0", server_port=7860)

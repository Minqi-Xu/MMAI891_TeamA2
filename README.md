# Adaptive Study Agent POC

This project implements a **Create-mode agentic POC** based on your Agent Design Canvas:
- Input: uploaded learning material (TXT/PDF/DOCX/PPTX)
- Agent steps: summarization -> concept extraction -> quiz generation -> answer evaluation -> adaptive difficulty routing -> explanations + study actions
- Output: summary, quiz, performance report, and adaptive follow-up quiz preview

## 1) Quick Start

```bash
cd "/Users/soulofstarrysky/Documents/Queensu/MMAI891_NaturalLanguageProcessing/Team A2/Demo"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Optional (LLM mode):
```bash
cp secrets/openai_api_key.txt.example secrets/openai_api_key.txt
# Edit secrets/openai_api_key.txt and replace with your real key on one line
```
Alternative:
```bash
export OPENAI_API_KEY="your_key_here"
```
If no key is set (file or env), the app runs in fallback mode for offline demo.

## 2) Suggested Demo Flow (10-15 mins)

1. Problem and value proposition (1-2 min)
2. Upload `data/synthetic_biology_notes.txt`
3. Generate summary + initial quiz
4. Complete quiz with mixed accuracy and confidence
5. Show:
   - score and route decision (`foundational/standard/advanced`)
   - confidence mismatch warning
   - targeted explanations and recommendations
   - adaptive round-2 quiz preview
6. Discuss one success and one failure:
   - Success: weaker performance triggers foundational routing and helpful review actions
   - Failure: occasionally generic or repetitive generated items (LLM/fallback limitation)
7. Next-step improvements: retrieval grounding, question quality checks, and user history memory

## 3) Evaluation Artifact

Run synthetic baseline vs adaptive simulation:

```bash
python evaluation/simulate_results.py
```

This prints average round-1/round-2 scores and adaptive uplift versus static baseline for report evidence.

## 4) Scope Boundaries (MVP)

Included:
- Single-session memory (answers, confidence, score)
- Explicit decision logic for adaptive routing
- Explainable output a learner can act on

Intentionally left out:
- Authentication / persistent learner profiles
- Institutional LMS integration
- Human instructor override workflows

## 5) Architecture Notes

- `app.py`: main Streamlit app and agent workflow
- `data/`: synthetic testing materials
- `evaluation/simulate_results.py`: simple baseline comparison script

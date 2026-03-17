# Adaptive Study Agent POC

This project implements a **Create-mode agentic POC** based on your Agent Design Canvas:
- Input: one or many uploaded learning files (TXT/PDF/DOCX/PPTX)
- Agent steps: summarization -> concept extraction -> quiz generation -> answer evaluation -> adaptive difficulty routing -> explanations + study actions
- Output: summary, quiz, performance report, and adaptive follow-up quiz preview
- Long-input handling: automatic chunking and chunk-summary aggregation for large multi-file content sets
- Persistent local memory per topic: previous confidence and weak concepts are saved to `data/user_memory.json`
- Separate history page: `Quiz History by Topic` (open from sidebar link in main page)

## 1) Quick Start

One-command setup (recommended):

```bash
./install.sh
```

`./install.sh` will automatically:
- create `.venv`
- install all required packages
- run a package import check
- start the Streamlit app

Note for Windows users:
- Run `./install.sh` from Git Bash.
- The script now supports both `.venv/bin` (macOS/Linux) and `.venv/Scripts` (Windows).

Manual setup:

```bash
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
   - score and confidence-based route decision (`foundational/standard/advanced`)
   - confidence mismatch warning
   - targeted explanations and recommendations
   - adaptive next-quiz preview
6. Discuss one success and one failure:
   - Success: weaker performance triggers foundational routing and helpful review actions
   - Failure: occasionally generic or repetitive generated items (LLM/fallback limitation)
7. Next-step improvements: retrieval grounding, question quality checks, and user history memory

## 3) Evaluation Artifact

Run user-progress evaluation from real quiz history:

```bash
python evaluation/user_progress_report.py
```

This reads `data/user_memory.json` and reports per-topic improvement from first attempt to latest attempt (score, accuracy, confidence), plus aggregate deltas across topics with at least 2 attempts.
The same improvement metrics are also visible directly in the `Quiz History by Topic` page.

## 4) Scope Boundaries (MVP)

Included:
- Persistent per-topic local memory (saved to local file)
- Explicit confidence-based decision logic for adaptive routing
- Explainable output a learner can act on

Intentionally left out:
- Authentication / cloud-synced learner profiles
- Institutional LMS integration
- Human instructor override workflows

## 5) Architecture Notes

- `app.py`: main Streamlit app and agent workflow
- `data/`: synthetic testing materials
- `evaluation/user_progress_report.py`: user-history-based improvement report
- `pages/Quiz_History.py`: topic-level history + improvement trends

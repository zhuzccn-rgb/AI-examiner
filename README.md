# AI-examiner

A prototype for assembling study papers from existing PDF questions. The workflow combines OCR, question analysis, knowledge retrieval, topic/score selection, and PDF assembly.

**Status: experimental. The workflow has substantive implementation, but reproducible setup and end-to-end output quality still need validation.**

## Project and contribution

I originated the project and designed its workflow. Generative AI was used extensively for implementation. The repository records the prototype, including components that need further integration and testing.

## Workflow

`PDF acquisition → OCR → question analysis → database storage → knowledge indexing → retrieval → question selection → PDF assembly`

- `src/graphs/graph.py`: LangGraph workflow and node connections.
- `src/graphs/node.py`: PDF processing, OCR, model calls, retrieval, selection, and output assembly.
- `src/graphs/state.py`: workflow inputs, outputs, and intermediate state.
- `src/main.py`: command-line and FastAPI service entry point.
- `startup.py`: interactive startup helper.
- `src/storage/`: database and other storage adapters.
- `config/`: model and workflow settings.

## Setup status

The current dependency lists and deployment notes reflect development environments rather than a verified clean installation across all operating systems. OCR, local model services, storage, and runtime helper dependencies must be configured together. A GPU is optional in the project design, but supported CPU/GPU configurations still need to be documented through reproducible runs.

Before running, inspect `requirements.txt` or `requirements-windows.txt`, the entry point, and the relevant configuration. Use your own local settings and credentials; do not commit real credentials. The legacy deployment notes under `config/` may require updates.

The Python module entry point is `src.main` (not `src.main.py`). Once dependencies are configured, inspect its options with:

```bash
python -m src.main --help
```

This command is an entry-point reference, not a claim that a clean installation has been validated. The former README referenced `scripts/http_run.sh` and `scripts/local_run.sh`; these files are not included in the current default branch.

## HTTP routes in the current source

The FastAPI application in `src/main.py` defines `/run`, `/stream_run`, `/cancel/{run_id}`, `/node_run/{node_id}`, `/v1/chat/completions`, `/health`, and `/graph_parameter`. Consult their request handlers and `src/graphs/state.py` for payload requirements. The previously documented `/api/flow` and `/api/health` routes do not match this entry point.

## Known limitations

- Embedding errors currently fall back to zero vectors. A completed workflow is not sufficient evidence of meaningful retrieval.
- PDF assembly selects source pages containing selected questions; it does not guarantee precise question-level cropping or layout.
- OCR, analysis, selection, and storage integration require further end-to-end evaluation.
- Platform compatibility and output accuracy have not been established by a published benchmark.
- Test-related files exist under `tests/` and `src/utils/error/`; the previously documented `tests/unit/` and `tests/integration/` directories are absent. Their presence does not imply the full pipeline passes.

## Next development steps

1. Establish a minimal reproducible environment and a small set of self-authored question PDFs.
2. Align workflow state and node contracts, and report model/retrieval failures explicitly.
3. Evaluate selected questions and output pages against expected results.
4. Remove generated cache files and separate local configuration from tracked source.

This project is for question retrieval and paper assembly, not automated grading. For project questions, use GitHub Issues.

## License

```text
MIT License

Copyright (c) 2024 AI Exam Workflow Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

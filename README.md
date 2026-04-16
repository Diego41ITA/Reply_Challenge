# Python Multi-Agent Fraud Detection System

This project implements a modular, agent-based architecture for detecting financial fraud in a futuristic digital metropolis. Each agent is responsible for analyzing a specific type of input data, and an orchestrator combines their results to produce a single output file of suspected fraudulent transaction IDs.

## Architecture Overview
- **agents/**
  - transactions_agent/
  - users_agent/
  - locations_agent/
  - conversations_agent/
  - messages_agent/
- **orchestrator/**
- **data/** (input datasets)
- **output/** (final results)

## Technologies
- Python 3.10+
- FastAPI (for agent APIs)
- pandas (for data processing)
- Uvicorn (for running APIs)

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Place input datasets in the `data/` directory.
3. Start each agent service (see agent README for details).
4. Start the orchestrator to aggregate results and produce the output file in `output/`.

## Output Format
- The orchestrator writes a text file with one suspected fraudulent Transaction ID per line.

---

Replace this README with more details as you implement each agent and the orchestrator.

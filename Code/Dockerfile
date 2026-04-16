# Base image
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy all agent code
COPY agents/ ./agents/
COPY data/ ./data/
COPY .env ./

# Expose ports for each agent (default FastAPI ports)
EXPOSE 8001 8002 8003 8005 8006

# Start all agents using uvicorn in the background
CMD \
  uvicorn agents.transactions_agent.main:app --host 0.0.0.0 --port 8001 & \
  uvicorn agents.users_agent.main:app --host 0.0.0.0 --port 8002 & \
  uvicorn agents.locations_agent.main:app --host 0.0.0.0 --port 8003 & \
  uvicorn agents.messages_agent.main:app --host 0.0.0.0 --port 8005 & \
  uvicorn agents.combined_agent.main:app --host 0.0.0.0 --port 8006 && tail -f /dev/null

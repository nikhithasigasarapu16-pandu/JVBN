# server.py
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
import os
import re
from groq import Groq
from hindsight_client import Hindsight

load_dotenv()

app = Flask(__name__, static_folder='static')

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

BANK_ID = "incident-response-agent"
hindsight = Hindsight(
    base_url="https://api.hindsight.vectorize.io",
    api_key=os.getenv("HINDSIGHT_API_KEY")
)

SYSTEM_PROMPT = """You are an expert incident response agent for a software engineering team.
When analyzing an incident, you MUST respond in exactly this format:

ROOT CAUSE:
[Write the root cause here in 2-3 sentences]

RESOLUTION STEPS:
[Write numbered step by step resolution here with real commands]

PREVENTION:
[Write bullet points for prevention here]

SEVERITY: [only one word: LOW, MEDIUM, HIGH, or CRITICAL]
ESTIMATED TIME: [only something like ~15m or ~22m]
MEMORIES FOUND: [only a number like 2 or 3]

Be direct, technical, and specific."""

PAST_INCIDENTS = [
    {
        "title": "Database connection timeout",
        "error": "ERROR: Connection to postgres://prod-db:5432 timed out after 30s",
        "cause": "Max connection pool limit reached (100/100 connections active)",
        "resolution": "Restarted connection pool, increased max_connections to 200",
        "time_to_resolve": "14 minutes",
        "severity": "critical"
    },
    {
        "title": "API gateway returning 502 errors",
        "error": "502 Bad Gateway - upstream server unreachable",
        "cause": "Memory leak in Node.js service caused OOM crash",
        "resolution": "Restarted the Node.js pods, deployed memory leak fix in v2.3.1",
        "time_to_resolve": "22 minutes",
        "severity": "high"
    },
    {
        "title": "CPU spike to 100% on app servers",
        "error": "System load average: 32.5, CPU: 100% for 8 minutes",
        "cause": "Unoptimized SQL query running full table scan on orders table",
        "resolution": "Killed the query, added composite index on (user_id, created_at)",
        "time_to_resolve": "9 minutes",
        "severity": "high"
    },
    {
        "title": "Redis cache unavailable",
        "error": "RedisConnectionError: Could not connect to Redis at cache-01:6379",
        "cause": "Redis ran out of memory, eviction policy set to noeviction",
        "resolution": "Flushed stale keys, changed eviction policy to allkeys-lru",
        "time_to_resolve": "18 minutes",
        "severity": "critical"
    },
    {
        "title": "SSL certificate expired",
        "error": "SSL_ERROR_RX_RECORD_TOO_LONG - certificate expired Jan 15 2024",
        "cause": "Auto-renewal cron job failed silently 30 days prior",
        "resolution": "Manually renewed cert via certbot, fixed cron job",
        "time_to_resolve": "31 minutes",
        "severity": "critical"
    },
    {
        "title": "Disk space full on logging server",
        "error": "No space left on device - /var/log partition at 100%",
        "cause": "Log rotation misconfigured, debug logs accumulating for 3 weeks",
        "resolution": "Deleted old logs, fixed logrotate config",
        "time_to_resolve": "11 minutes",
        "severity": "medium"
    }
]


def save_memory(title, text):
    try:
        hindsight.retain(
            bank_id=BANK_ID,
            content=f"INCIDENT: {title}\nRESOLUTION: {text}",
            context=title
        )
    except Exception as e:
        print(f"Memory save error: {e}")


def search_memory(query):
    try:
        results = hindsight.recall(bank_id=BANK_ID, query=query)
        if results and results.results:
            return "\n\n".join([r.text for r in results.results[:3]])
        return None
    except Exception as e:
        print(f"Memory search error: {e}")
        return None


def load_past_incidents():
    print("Loading past incidents into Hindsight memory...")
    for inc in PAST_INCIDENTS:
        memory_text = (
            f"Incident: {inc['title']}\n"
            f"Error: {inc['error']}\n"
            f"Root Cause: {inc['cause']}\n"
            f"Resolution: {inc['resolution']}\n"
            f"Time to Resolve: {inc['time_to_resolve']}\n"
            f"Severity: {inc['severity']}"
        )
        save_memory(inc['title'], memory_text)
    print("Done! All incidents loaded into memory.")


def parse_response(text):
    def extract_between(start_label, end_labels, content):
        end_pattern = "|".join(re.escape(lbl) + r"\s*:" for lbl in end_labels)
        pattern = re.compile(
            re.escape(start_label) + r"\s*:\s*(.*?)(?=" + end_pattern + r"|$)",
            re.DOTALL | re.IGNORECASE
        )
        match = pattern.search(content)
        return match.group(1).strip() if match else ""

    root_cause = extract_between("ROOT CAUSE", ["RESOLUTION STEPS", "PREVENTION", "SEVERITY"], text)
    resolution = extract_between("RESOLUTION STEPS", ["PREVENTION", "SEVERITY", "ESTIMATED TIME"], text)
    prevention = extract_between("PREVENTION", ["SEVERITY", "ESTIMATED TIME", "MEMORIES FOUND"], text)

    sev_match = re.search(r"SEVERITY\s*:\s*(\w+)", text, re.IGNORECASE)
    time_match = re.search(r"ESTIMATED TIME\s*:\s*(\S+)", text, re.IGNORECASE)
    mem_match = re.search(r"MEMORIES FOUND\s*:\s*(\d+)", text, re.IGNORECASE)

    return {
        "root_cause": root_cause or text,
        "resolution": resolution,
        "prevention": prevention,
        "severity": sev_match.group(1).upper() if sev_match else "HIGH",
        "est_time": time_match.group(1) if time_match else "~15m",
        "memories_found": mem_match.group(1) if mem_match else "3"
    }


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    incident = data.get('incident', '').strip()

    if not incident:
        return jsonify({'error': 'No incident provided'}), 400

    try:
        past_memory = search_memory(incident)

        if past_memory:
            user_message = f"""
NEW INCIDENT:
{incident}

RELEVANT PAST INCIDENTS FROM MEMORY:
{past_memory}

Using the past incidents from memory, analyze this new incident and respond in the required format.
"""
        else:
            user_message = f"""
NEW INCIDENT:
{incident}

No similar past incidents found. Analyze and respond in the required format.
"""

        response = groq_client.chat.completions.create(
            model="qwen/qwen3-32b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ]
        )

        raw = response.choices[0].message.content
        save_memory(incident, raw)
        parsed = parse_response(raw)
        return jsonify(parsed)

    except Exception as e:
        return jsonify({
            'root_cause': f'Error: {str(e)}',
            'resolution': 'Check your API keys in the .env file.',
            'prevention': '',
            'severity': 'UNKNOWN',
            'est_time': '—',
            'memories_found': '0'
        }), 500


if __name__ == '__main__':
    load_past_incidents()
    print("\n✅ Server is running!")
    print("👉 Open your browser and go to: http://localhost:5000\n")
    app.run(debug=True, port=5000)
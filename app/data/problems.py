from app.models.schemas import Problem

PROBLEMS: dict[str, Problem] = {}

_seed: list[Problem] = [
    Problem(
        id="url-shortener",
        title="Design a URL Shortener",
        category="System Design",
        difficulty="Medium",
        duration_min=15,
        statement=(
            "Design a scalable URL shortening service like bit.ly. "
            "It should accept a long URL and return a unique short alias. "
            "Discuss storage, hashing strategy, read/write ratio, "
            "and how you'd handle collisions and analytics."
        ),
        constraints=[
            "100M new URLs per month",
            "Read-to-write ratio ~100:1",
            "Short URLs must be at most 7 characters (base-62)",
            "Redirection latency < 50 ms p99",
            "System must remain available under partial failures",
        ],
        optimal_complexity="O(1) write / O(1) read with pre-generated keys",
        key_edge_cases=[
            "Hash collision resolution",
            "Custom alias conflicts",
            "Expired link cleanup",
            "301 vs 302 redirect caching tradeoffs",
            "Hot-key thundering herd on viral links",
        ],
    ),
    Problem(
        id="longest-palindrome",
        title="Longest Palindromic Substring",
        category="DSA",
        difficulty="Medium",
        duration_min=10,
        statement=(
            "Given a string s, return the longest substring of s that is a palindrome. "
            "If there are multiple answers of the same length, return any one."
        ),
        constraints=[
            "1 <= len(s) <= 10^5",
            "s consists of ASCII letters and digits only",
            "Expected time complexity: O(N) or O(N^2) with early termination",
        ],
        optimal_complexity="O(N) using Manacher's algorithm",
        key_edge_cases=[
            "Single character string",
            "Empty string",
            "All identical characters",
            "Even-length palindromes",
            "Palindrome at the very end of the string",
        ],
    ),
    Problem(
        id="postgres-cpu-spike",
        title="Diagnose a PostgreSQL CPU Spike",
        category="DevOps",
        difficulty="Hard",
        duration_min=10,
        statement=(
            "Your team's PostgreSQL 15 primary is pinned at 100% CPU on a "
            "4-vCPU Cloud SQL instance. P99 query latency has jumped from "
            "12 ms to 3.2 s. Walk through your diagnostic runbook, identify "
            "the most likely root causes, and propose both immediate mitigations "
            "and long-term fixes."
        ),
        constraints=[
            "Database size ~200 GB, ~50 tables",
            "Connection pool max 100 connections via PgBouncer",
            "Read replicas exist but are not currently used by the app",
            "No recent schema migrations",
            "Autovacuum is enabled with default settings",
        ],
        optimal_complexity="Systematic: pg_stat_activity → pg_stat_statements → EXPLAIN ANALYZE → index/vacuum fix",
        key_edge_cases=[
            "Lock contention vs CPU-bound query distinction",
            "Bloated tables causing sequential scans despite indexes",
            "Autovacuum blocked by long-running transactions",
            "Connection stampede after PgBouncer restart",
            "Runaway analytics query without statement_timeout",
        ],
    ),
]

for p in _seed:
    PROBLEMS[p.id] = p

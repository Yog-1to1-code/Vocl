"""Curated 30-problem voice-only commute track (18 DSA, 8 System Design, 4 Debugging)."""
from __future__ import annotations

from app.models.schemas import Problem

PROBLEMS: dict[str, Problem] = {}

_seed: list[Problem] = [
    # ------------------------------------------------------------------
    # DSA & Algorithms (18)
    # ------------------------------------------------------------------
    Problem(
        id="two-sum",
        title="Two Sum",
        category="DSA",
        difficulty="Easy",
        duration_min=5,
        statement=(
            "Given an integer array nums and an integer target, return the indices of "
            "the two numbers that add up to target. Explain why your approach beats brute force."
        ),
        constraints=[
            "2 <= len(nums) <= 10^5",
            "Values can be negative and up to +-10^9",
            "Exactly one valid pair exists; do not reuse the same element",
        ],
        optimal_complexity="O(N) time / O(N) space with a single-pass hash map",
        key_edge_cases=[
            "Duplicate values summing to target (e.g. [3, 3], target=6)",
            "Negative numbers and zero",
            "Using the same index twice if pre-populating the map",
        ],
    ),
    Problem(
        id="valid-anagram",
        title="Valid Anagram",
        category="DSA",
        difficulty="Easy",
        duration_min=5,
        statement=(
            "Given two strings s and t, return true if t is an anagram of s, and false otherwise. "
            "Discuss how your solution changes if inputs contain full Unicode characters."
        ),
        constraints=[
            "1 <= len(s), len(t) <= 5 * 10^4",
            "Lowercase ASCII letters initially; follow-up supports arbitrary Unicode",
        ],
        optimal_complexity="O(N) time / O(1) space (26-int array) or O(K) hash map for Unicode",
        key_edge_cases=[
            "Strings of different lengths (fast fail)",
            "Unicode / multi-byte code points vs fixed 26-slot array",
            "Empty or single-character strings",
        ],
    ),
    Problem(
        id="group-anagrams",
        title="Group Anagrams",
        category="DSA",
        difficulty="Medium",
        duration_min=7,
        statement=(
            "Given an array of strings strs, group all anagrams together in any order. "
            "Compare sorting each string versus frequency-tuple keys."
        ),
        constraints=[
            "1 <= len(strs) <= 10^4",
            "0 <= len(strs[i]) <= 100",
            "Lowercase English letters only",
        ],
        optimal_complexity="O(N * K) time / O(N * K) space using 26-count tuple keys",
        key_edge_cases=[
            "Empty strings in the input array",
            "Single-element input",
            "Hash key serialization collisions if building naive delimiter strings",
        ],
    ),
    Problem(
        id="top-k-frequent",
        title="Top K Frequent Elements",
        category="DSA",
        difficulty="Medium",
        duration_min=7,
        statement=(
            "Given an integer array nums and an integer k, return the k most frequent elements. "
            "Your solution must beat O(N log N) sorting."
        ),
        constraints=[
            "1 <= len(nums) <= 10^5",
            "1 <= k <= number of unique elements",
            "Answer is guaranteed to be unique",
        ],
        optimal_complexity="O(N) time / O(N) space via bucket sort by frequency (or O(N log K) min-heap)",
        key_edge_cases=[
            "All elements have the same frequency",
            "k equals the number of unique elements",
            "Negative integers as values",
        ],
    ),
    Problem(
        id="longest-consecutive-seq",
        title="Longest Consecutive Sequence",
        category="DSA",
        difficulty="Medium",
        duration_min=8,
        statement=(
            "Given an unsorted array of integers nums, return the length of the longest "
            "consecutive elements sequence in O(N) time."
        ),
        constraints=[
            "0 <= len(nums) <= 10^5",
            "-10^9 <= nums[i] <= 10^9",
            "Must run in O(N) average time without sorting",
        ],
        optimal_complexity="O(N) time / O(N) space by starting walks only at sequence heads (n - 1 not in set)",
        key_edge_cases=[
            "Empty array returning 0",
            "Duplicate numbers in the input",
            "Negative numbers spanning across zero",
        ],
    ),
    Problem(
        id="container-most-water",
        title="Container With Most Water",
        category="DSA",
        difficulty="Medium",
        duration_min=7,
        statement=(
            "Given an integer array height representing vertical lines, find two lines that "
            "together with the x-axis hold the most water. Prove why your greedy pointer move is safe."
        ),
        constraints=[
            "2 <= len(height) <= 10^5",
            "0 <= height[i] <= 10^4",
        ],
        optimal_complexity="O(N) time / O(1) space using converging two pointers",
        key_edge_cases=[
            "Two lines of equal height (either pointer can move)",
            "Zero-height bars",
            "Monotonically increasing or decreasing heights",
        ],
    ),
    Problem(
        id="three-sum",
        title="3Sum",
        category="DSA",
        difficulty="Medium",
        duration_min=8,
        statement=(
            "Given an integer array nums, return all unique triplets [nums[i], nums[j], nums[k]] "
            "that sum to zero without duplicate triplets in the output."
        ),
        constraints=[
            "3 <= len(nums) <= 3000",
            "-10^5 <= nums[i] <= 10^5",
            "Output must not contain duplicate triplets",
        ],
        optimal_complexity="O(N^2) time / O(1) auxiliary space via sorting + two pointers",
        key_edge_cases=[
            "All zeros [0, 0, 0, 0] producing only one [0, 0, 0]",
            "Skipping duplicate anchors and duplicate left/right pointers",
            "Early break when sorted anchor > 0",
        ],
    ),
    Problem(
        id="trapping-rain-water",
        title="Trapping Rain Water",
        category="DSA",
        difficulty="Hard",
        duration_min=10,
        statement=(
            "Given n non-negative integers representing an elevation map where each bar has width 1, "
            "compute how much water it can trap after raining."
        ),
        constraints=[
            "1 <= n <= 2 * 10^4",
            "0 <= height[i] <= 10^5",
            "Aim for O(1) auxiliary space",
        ],
        optimal_complexity="O(N) time / O(1) space with two pointers tracking leftMax and rightMax",
        key_edge_cases=[
            "Fewer than 3 bars (0 water trapped)",
            "Flat or strictly monotonic terrain",
            "Equal leftMax and rightMax boundaries",
        ],
    ),
    Problem(
        id="longest-substring-no-repeat",
        title="Longest Substring Without Repeating Characters",
        category="DSA",
        difficulty="Medium",
        duration_min=7,
        statement=(
            "Given a string s, find the length of the longest substring without repeating characters. "
            "Explain how your left pointer jumps cleanly without moving backward."
        ),
        constraints=[
            "0 <= len(s) <= 5 * 10^4",
            "s consists of English letters, digits, symbols, and spaces",
        ],
        optimal_complexity="O(N) time / O(min(N, charset)) space using sliding window + last-seen index map",
        key_edge_cases=[
            "Empty string returning 0",
            "Left pointer must take max(left, lastSeen[c] + 1) to avoid moving backward",
            "All identical characters vs all unique characters",
        ],
    ),
    Problem(
        id="min-window-substring",
        title="Minimum Window Substring",
        category="DSA",
        difficulty="Hard",
        duration_min=10,
        statement=(
            "Given two strings s and t, return the minimum window substring of s such that every "
            "character in t (including duplicates) is included in the window."
        ),
        constraints=[
            "1 <= len(s), len(t) <= 10^5",
            "Uppercase and lowercase English letters",
            "Must run in O(|s| + |t|) time",
        ],
        optimal_complexity="O(|s| + |t|) time / O(|s| + |t|) space using sliding window + formed/required counters",
        key_edge_cases=[
            "Duplicate characters in t requiring exact frequency matching",
            "No valid window exists (return empty string)",
            "len(t) > len(s)",
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
        id="search-rotated-array",
        title="Search in Rotated Sorted Array",
        category="DSA",
        difficulty="Medium",
        duration_min=7,
        statement=(
            "Given a sorted array of distinct integers rotated at an unknown pivot and a target, "
            "return the index of target or -1 in O(log N) time."
        ),
        constraints=[
            "1 <= len(nums) <= 10^5",
            "All values in nums are distinct",
            "Must achieve O(log N) runtime",
        ],
        optimal_complexity="O(log N) time / O(1) space via modified binary search checking which half is sorted",
        key_edge_cases=[
            "Array rotated 0 times (already sorted)",
            "Two-element rotated array where mid == left",
            "Target missing from array",
        ],
    ),
    Problem(
        id="koko-eating-bananas",
        title="Koko Eating Bananas",
        category="DSA",
        difficulty="Medium",
        duration_min=7,
        statement=(
            "Given piles of bananas and h hours, find the minimum integer eating speed k (bananas/hour) "
            "so all piles are finished within h hours."
        ),
        constraints=[
            "1 <= len(piles) <= 10^4",
            "len(piles) <= h <= 10^9",
            "1 <= piles[i] <= 10^9",
        ],
        optimal_complexity="O(N log(max(piles))) time / O(1) space using binary search on answer space",
        key_edge_cases=[
            "Ceiling division ((pile + k - 1) // k) without floating-point precision loss",
            "h equals len(piles) (answer must be max(piles))",
            "Single huge pile with large h (answer can be 1)",
        ],
    ),
    Problem(
        id="lru-cache",
        title="LRU Cache",
        category="DSA",
        difficulty="Medium",
        duration_min=8,
        statement=(
            "Design a Least Recently Used (LRU) cache supporting O(1) get(key) and O(1) put(key, value) "
            "with capacity eviction."
        ),
        constraints=[
            "1 <= capacity <= 3000",
            "Up to 2 * 10^5 calls to get and put",
            "Both operations must run in O(1) average time",
        ],
        optimal_complexity="O(1) get and put / O(capacity) space using HashMap + doubly linked list",
        key_edge_cases=[
            "Capacity of 1",
            "Updating an existing key should not evict another key",
            "Sentinel head/tail nodes to avoid null-pointer edge cases during unlink",
        ],
    ),
    Problem(
        id="validate-bst",
        title="Validate Binary Search Tree",
        category="DSA",
        difficulty="Medium",
        duration_min=7,
        statement=(
            "Given the root of a binary tree, determine if it is a valid binary search tree (BST). "
            "Explain why checking only immediate children is insufficient."
        ),
        constraints=[
            "Number of nodes in [1, 10^4]",
            "Node values span full 32-bit signed integer range",
            "Strict inequality: left < node < right",
        ],
        optimal_complexity="O(N) time / O(H) stack space via min/max range recursion or in-order traversal",
        key_edge_cases=[
            "Grandchild violating ancestor bound (e.g. right subtree containing value smaller than root)",
            "Duplicate node values (invalid in strict BST)",
            "INT_MIN / INT_MAX node values breaking sentinel bounds if not using -inf/+inf",
        ],
    ),
    Problem(
        id="lowest-common-ancestor",
        title="Lowest Common Ancestor of a Binary Tree",
        category="DSA",
        difficulty="Medium",
        duration_min=8,
        statement=(
            "Given a binary tree (not necessarily a BST) and two nodes p and q, find their "
            "lowest common ancestor (LCA)."
        ),
        constraints=[
            "2 <= number of nodes <= 10^5",
            "All node values are unique",
            "Both p and q exist in the tree",
        ],
        optimal_complexity="O(N) time / O(H) space via post-order DFS returning matched subtree node",
        key_edge_cases=[
            "One node is an ancestor of the other (p is parent of q)",
            "Skewed tree causing O(N) recursion depth",
            "Follow-up: what if p or q might not exist in the tree?",
        ],
    ),
    Problem(
        id="course-schedule",
        title="Course Schedule",
        category="DSA",
        difficulty="Medium",
        duration_min=8,
        statement=(
            "Given numCourses and a list of prerequisite pairs [a, b], determine if it is possible "
            "to finish all courses. Compare Kahn's BFS versus 3-color DFS."
        ),
        constraints=[
            "1 <= numCourses <= 2000",
            "0 <= len(prerequisites) <= 5000",
            "Graph may be disconnected",
        ],
        optimal_complexity="O(V + E) time / O(V + E) space via topological sort (Kahn's algorithm or 3-state DFS)",
        key_edge_cases=[
            "Self-loop prerequisite [0, 0]",
            "Disconnected components where only one component has a cycle",
            "Empty prerequisites list (always true)",
        ],
    ),
    Problem(
        id="coin-change",
        title="Coin Change",
        category="DSA",
        difficulty="Medium",
        duration_min=8,
        statement=(
            "Given coin denominations and a total amount, return the fewest number of coins needed "
            "to make up that amount, or -1 if impossible. Explain why greedy fails."
        ),
        constraints=[
            "1 <= len(coins) <= 12",
            "0 <= amount <= 10^4",
            "Infinite supply of each coin denomination",
        ],
        optimal_complexity="O(amount * len(coins)) time / O(amount) space via bottom-up 1D DP",
        key_edge_cases=[
            "amount == 0 returning 0",
            "Greedy failure case (e.g. coins=[1, 3, 4], amount=6 -> 3+3=2, not 4+1+1=3)",
            "Unreachable amount returning -1 without integer overflow on inf + 1",
        ],
    ),
    # ------------------------------------------------------------------
    # System Design (8)
    # ------------------------------------------------------------------
    Problem(
        id="url-shortener",
        title="Design a URL Shortener",
        category="System Design",
        difficulty="Medium",
        duration_min=10,
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
        id="rate-limiter",
        title="Design a Distributed Rate Limiter",
        category="System Design",
        difficulty="Medium",
        duration_min=10,
        statement=(
            "Design a distributed API rate limiter sitting in front of microservices. "
            "Compare token bucket, sliding window log, and sliding window counter algorithms."
        ),
        constraints=[
            "100k requests/sec across multiple API gateway instances",
            "Latency overhead < 5 ms p99",
            "Per-user and per-IP configurable rules",
        ],
        optimal_complexity="O(1) per request using Redis Lua atomic token bucket / sliding window counter",
        key_edge_cases=[
            "Race conditions under concurrent requests (atomic Lua script vs GET+SET)",
            "Fail-open vs fail-closed when Redis is unavailable",
            "Clock skew across distributed gateway nodes",
        ],
    ),
    Problem(
        id="notification-service",
        title="Design a Notification Service",
        category="System Design",
        difficulty="Medium",
        duration_min=10,
        statement=(
            "Design a multi-channel notification platform supporting Push (APNs/FCM), SMS, and Email "
            "with priority queues, retries, and user opt-out preferences."
        ),
        constraints=[
            "50M notifications per day with bursty marketing campaigns",
            "Critical OTPs must deliver within 2 seconds",
            "No duplicate deliveries on worker retries",
        ],
        optimal_complexity="Priority-partitioned Kafka queues + idempotent delivery workers + DLQ",
        key_edge_cases=[
            "Priority inversion (bulk promo delaying OTPs)",
            "Idempotency keys preventing duplicate SMS/push on retries",
            "Downstream provider rate limits and exponential backoff",
        ],
    ),
    Problem(
        id="news-feed",
        title="Design a Social News Feed",
        category="System Design",
        difficulty="Hard",
        duration_min=10,
        statement=(
            "Design a home timeline news feed for a social network with 100M DAU. "
            "Defend your fan-out-on-write vs fan-out-on-read hybrid strategy."
        ),
        constraints=[
            "100M daily active users; celebrities have 50M+ followers",
            "Feed load latency < 200 ms p99",
            "Posts must appear within 5 seconds for normal users",
        ],
        optimal_complexity="Hybrid fan-out: push to Redis timelines for normal users, pull-merge for celebrities",
        key_edge_cases=[
            "Celebrity fan-out write amplification (hot-key problem)",
            "Deleted or muted posts lingering in precomputed caches",
            "Cursor-based pagination vs offset drift on new posts",
        ],
    ),
    Problem(
        id="distributed-cache",
        title="Design a Distributed Cache",
        category="System Design",
        difficulty="Hard",
        duration_min=10,
        statement=(
            "Design a distributed in-memory key-value cache like Redis/Memcached. "
            "Cover consistent hashing, replication, eviction, and hot-shard mitigation."
        ),
        constraints=[
            "Sub-millisecond p99 read latency",
            "10 TB total dataset across hundreds of shards",
            "Zero-downtime node additions and failures",
        ],
        optimal_complexity="Consistent hashing with virtual nodes + LRU/LFU eviction + async replica failover",
        key_edge_cases=[
            "Cache avalanche (synchronized TTL expirations)",
            "Cache penetration (repeated misses for non-existent keys -> Bloom filter)",
            "Hot-key overloading a single shard",
        ],
    ),
    Problem(
        id="chat-system",
        title="Design a Real-Time Chat System",
        category="System Design",
        difficulty="Medium",
        duration_min=10,
        statement=(
            "Design a 1-on-1 and group messaging app like WhatsApp supporting online presence, "
            "delivery receipts, and multi-device sync."
        ),
        constraints=[
            "50M concurrent WebSocket connections",
            "Strict per-conversation message ordering",
            "Offline message delivery when user reconnects",
        ],
        optimal_complexity="Stateful WebSocket gateway + Redis session map + partitioned message log",
        key_edge_cases=[
            "Out-of-order timestamps across mobile clients (Snowflake / sequence IDs)",
            "Presence heartbeat storms on mass reconnect",
            "Large group fan-out and offline push fallback",
        ],
    ),
    Problem(
        id="web-crawler",
        title="Design a Distributed Web Crawler",
        category="System Design",
        difficulty="Medium",
        duration_min=10,
        statement=(
            "Design a polite, distributed web crawler that indexes 1 billion web pages per month "
            "without overloading host servers or falling into crawler traps."
        ),
        constraints=[
            "1B pages/month (~400 pages/sec average)",
            "Must respect robots.txt and per-host politeness delays",
            "Avoid re-crawling duplicate URLs or identical content",
        ],
        optimal_complexity="Host-partitioned URL frontier queues + Bloom filter URL dedup + SimHash content dedup",
        key_edge_cases=[
            "Infinite calendar / session-ID spider traps",
            "DNS resolution bottleneck (local DNS cache)",
            "Per-domain rate limiting without starving other domains",
        ],
    ),
    Problem(
        id="ride-sharing-matcher",
        title="Design a Ride-Sharing Geo Matcher",
        category="System Design",
        difficulty="Hard",
        duration_min=10,
        statement=(
            "Design the real-time location ingestion and driver-rider matching engine for Uber. "
            "Discuss spatial indexing (Geohash/H3/QuadTree) and preventing double-dispatch."
        ),
        constraints=[
            "1M active drivers sending GPS updates every 4 seconds",
            "Match rider to nearest available driver within 3 seconds",
            "Never dispatch two riders to the same driver",
        ],
        optimal_complexity="In-memory H3/Geohash spatial index + distributed lock / atomic state transition on dispatch",
        key_edge_cases=[
            "Geohash boundary effects (must query 8 neighboring cells)",
            "Two riders locking the same driver concurrently",
            "Stale driver GPS coordinates after tunnel disconnect",
        ],
    ),
    # ------------------------------------------------------------------
    # Production Debugging / Incidents (4)
    # ------------------------------------------------------------------
    Problem(
        id="postgres-cpu-spike",
        title="Diagnose a PostgreSQL CPU Spike",
        category="Debugging",
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
        optimal_complexity="Systematic: pg_stat_activity -> pg_stat_statements -> EXPLAIN ANALYZE -> index/vacuum fix",
        key_edge_cases=[
            "Lock contention vs CPU-bound query distinction",
            "Bloated tables causing sequential scans despite indexes",
            "Autovacuum blocked by long-running transactions",
            "Connection stampede after PgBouncer restart",
            "Runaway analytics query without statement_timeout",
        ],
    ),
    Problem(
        id="worker-memory-leak",
        title="Debug a Memory Leak in a Worker Pool",
        category="Debugging",
        difficulty="Medium",
        duration_min=8,
        statement=(
            "Your Python/Node background worker pods are getting OOMKilled every 6 hours under steady "
            "traffic. Walk through how you isolate the leak, mitigate immediately, and prevent regressions."
        ),
        constraints=[
            "12 Kubernetes pods, 2 GB memory limit each",
            "Traffic volume is flat; heap grows linearly ~250 MB/hour",
            "Zero-downtime mitigation required while investigating",
        ],
        optimal_complexity="Heap diff snapshots (tracemalloc/heapdump) -> isolate retaining reference -> bounded cache/pool",
        key_edge_cases=[
            "Unbounded in-memory dict/LRU cache or global list accumulation",
            "Native C-extension / buffer leak invisible to language GC heap stats",
            "Temporary mitigation via max-tasks-per-child recycling while fixing root cause",
        ],
    ),
    Problem(
        id="redis-cache-stampede",
        title="Mitigate a Redis Cache Stampede",
        category="Debugging",
        difficulty="Medium",
        duration_min=8,
        statement=(
            "Every hour on the hour, your homepage API latency spikes 20x and your Postgres primary "
            "nearly falls over for 90 seconds. Diagnose the cache stampede and design a permanent fix."
        ),
        constraints=[
            "50k RPS on a handful of hot homepage keys",
            "Keys share a fixed 3600-second TTL",
            "Cold DB query takes 400 ms",
        ],
        optimal_complexity="Singleflight / distributed mutex + TTL jitter + stale-while-revalidate refresh",
        key_edge_cases=[
            "Lock holder crashing before releasing mutex (must set short lock TTL)",
            "Serving slightly stale data while one background worker refreshes",
            "Adding random jitter to prevent synchronized expiration",
        ],
    ),
    Problem(
        id="kafka-consumer-lag",
        title="Resolve Growing Kafka Consumer Lag",
        category="Debugging",
        difficulty="Hard",
        duration_min=10,
        statement=(
            "Your billing Kafka consumer group lag has grown from 0 to 4 million messages over the past "
            "hour and is still climbing. Walk through your triage and recovery plan."
        ),
        constraints=[
            "Topic has 12 partitions; consumer group currently runs 12 replicas",
            "Each message calls a downstream payment API",
            "Billing events must not be silently dropped",
        ],
        optimal_complexity="Inspect per-partition lag + rebalance churn + downstream latency -> poison-pill DLQ / batching",
        key_edge_cases=[
            "Adding >12 consumers does nothing when topic only has 12 partitions",
            "Poison-pill message causing infinite retry/rebalance loop (route to DLQ)",
            "Hot partition key skewing 90% of traffic onto one consumer",
        ],
    ),
]

for p in _seed:
    PROBLEMS[p.id] = p

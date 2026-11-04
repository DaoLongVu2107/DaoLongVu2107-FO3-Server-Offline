"""Record every match result the client sends (PUT /match/<id>/end matchStats).

The server only reads score / goals / assists / motm today; the full body shows what else the
client reports (possession, shots, cards, ratings...) so later milestones know which mission
types are possible. One JSON object per line in captures/match_stats.jsonl:
{"at", "match", "type", "difficulty", "stats"}. Logging never breaks the match end.
"""
import json
import os
import time

hc = None


def install(module):
    global hc
    hc = module
    orig = module.ep_match_end

    def ep_match_end(mid, query, body):
        record(mid, body)
        return orig(mid, query, body)

    ep_match_end.__wrapped__ = orig
    module.ep_match_end = ep_match_end
    module.ROUTES[:] = [(pat, ep_match_end if fn is orig else fn) for pat, fn in module.ROUTES]


def path():
    return os.path.join(os.path.dirname(hc.LOG), "match_stats.jsonl")


def record(mid, body):
    try:
        try:
            stats = json.loads(body or b"{}")
        except ValueError:
            stats = {"_raw": (body or b"").decode("utf-8", "replace")}
        match = hc._state().get("match") or {}
        mine = match.get("id") == mid
        line = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"), "match": mid,
                "type": match.get("type") if mine else None,
                "difficulty": (match.get("gamesettings") or {}).get("difficulty") if mine else None,
                "stats": stats}
        os.makedirs(os.path.dirname(path()), exist_ok=True)
        with open(path(), "a", encoding="utf-8") as f:
            f.write(json.dumps(line, ensure_ascii=False) + "\n")
    except Exception as e:  # never break the client's match end
        print(f"[career] matchlog loi: {e}", flush=True)

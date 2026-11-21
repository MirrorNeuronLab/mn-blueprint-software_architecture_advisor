"""Select a source-backed interface change to investigate in the captured file graph."""


def direct_dependents(facts):
    """Pick the file with the most distinct direct dependents and one site per dependent."""
    lead = min(
        (row for row in facts.get("components", []) if row["fan_in"]),
        key=lambda row: (-row["fan_in"], row["id"]),
        default=None,
    )
    if lead is None:
        return None
    sites = {}
    for edge in facts.get("component_evidence", []):
        if edge["target"] != lead["id"]:
            continue
        source = edge["source"]
        location = edge["evidence"]
        # Prefer a literal import/include over a name-based call candidate.
        rank = (edge["kind"] == "call", location["line_start"], edge["kind"])
        if source not in sites or rank < sites[source][0]:
            sites[source] = (rank, {
                "source": source, "line": location["line_start"], "kind": edge["kind"],
            })
    if not sites:
        return None
    return {
        "target": lead["id"],
        "total": len(sites),
        "sites": [sites[source][1] for source in sorted(sites)[:5]],
    }

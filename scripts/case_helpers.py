def device_profile(idrec):
    if not idrec or not idrec.get("DeviceType"):
        return ""
    parts = [idrec.get("DeviceInfo") or "", idrec.get("id_30") or "",
             idrec.get("id_31") or "", idrec.get("id_33") or ""]
    return " | ".join(p for p in parts if p)

def is_new_region(txn, hist):
    r = txn.get("addr1")
    if r is None:
        return False
    return str(r) not in hist.get("top_regions", {})

def is_new_channel(txn, hist):
    return txn.get("ch") not in hist.get("channels", {})

def is_new_product(txn, hist):
    return txn.get("prod") not in hist.get("product_codes", {})

def make_evidence(claims):
    return [{"claim": c, "source": s, "ref": r, "entity_ids": e}
            for c, s, r, e in claims]

def make_action(action, route, reason):
    return {"action": action, "route": route, "reason": reason}

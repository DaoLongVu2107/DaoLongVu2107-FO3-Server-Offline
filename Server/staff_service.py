"""Offline staff recruitment and assignment endpoints."""
import json
import os
import random
import re

hc = None
PACKS = (
    {"recruitid": 1, "icon": "broall", "recruittype": "normal", "staffpack_name": "Offline Staff - Basic",
     "staffpack_desc": "Recruit one staff member (1-2 stars). Free.", "ep": 0, "item": 0, "grades": (1, 2)},
    {"recruitid": 2, "icon": "silall", "recruittype": "normal", "staffpack_name": "Offline Staff - Advanced",
     "staffpack_desc": "Recruit one staff member (3-4 stars). 50,000 EP.", "ep": 50000, "item": 0, "grades": (3, 4)},
    {"recruitid": 3, "icon": "goldall", "recruittype": "normal", "staffpack_name": "Offline Staff - Elite",
     "staffpack_desc": "Recruit one staff member (5 stars). 150,000 EP.", "ep": 150000, "item": 0, "grades": (5,)},
)
# Names, portrait IDs and roles are sourced from the bundled catalog.
with open(os.path.join(os.path.dirname(__file__), 'gamedata', 'staff_catalog.json'), encoding='utf-8') as stream:
    CATALOG = json.load(stream)['staff']
TYPE_LABELS = (('FRONT', 'Technical'), ('PREMIUM', 'Head Coach'),
               ('MEDICAL', 'Medical'), ('FW', 'FW'), ('MF', 'MF'), ('DF', 'DF'), ('GK', 'GK'))
TYPES = tuple((typ, label, tuple(int(pid) for pid, info in CATALOG.items()
                               if info['position'] == typ and not info['material']), ())
              for typ, label in TYPE_LABELS)
STAT_KEYS = dict(zip(
    ('Acceleration|Aggresion|Agility|Balance|Ball Control|Cross|Dribble|Finishing|Free Kick|GK Diving|GK Goal Kick|GK Handling|GK Positioning|GK Reaction|Heading|Interception|Jump|Long Pass|Long Shot|Marking|Overall Rating|Penalty Kick|Positioning|Reaction|Shoot Curve|Shoot Power|Short Pass|Sliding Tackle|Sprint Speed|Stamina|Strength|Tackle|Vision|Volley').split('|'),
    ('acceleration|aggression|agility|balance|ballcontrol|crossing|dribbling|finishing|freekickaccuracy|gkdiving|gkkicking|gkhandling|gkpositioning|gkreflexes|headingaccuracy|interceptions|jumping|longpassing|longshots|marking|ovr|penalties|positioning|reactions|curve|shotpower|shortpassing|slidingtackle|sprintspeed|stamina|strength|standingtackle|vision|volleys').split('|')))

def recruit_effects(info, grade):
    # Option groups are sourced; numeric values remain offline balancing values.
    effects = []
    for index, group in enumerate(info['boost_groups'][:min(3, grade)], 1):
        choices = [STAT_KEYS[label] for label in group if label in STAT_KEYS]
        if choices:
            effects.append({'effectidx': index, 'effect': random.choice(choices),
                            'amount': max(1, (grade + 1) // 2), 'grade': 1, 'open': True})
    return effects

SLOT_TYPES = {i + 1: row[0] for i, row in enumerate(TYPES)}
TYPE_BY_PORTRAIT = {pid: row[0] for row in TYPES for pid in row[2]}
ALL_PACKS = list(PACKS)
for i, (typ, label, portraits, effects) in enumerate(TYPES, 1):
    for tier, base in enumerate(PACKS, 1):
        icon = ('bro' + typ.lower()) if tier == 1 and typ in ('FW', 'MF', 'DF', 'GK') else base['icon']
        ALL_PACKS.append({**base, 'recruitid': 100 + i * 10 + tier, 'position': typ,
                          'icon': icon, 'staffpack_name': label + ' - ' + ('Basic', 'Advanced', 'Elite')[tier - 1]})
PACKS = tuple(ALL_PACKS)
for pack in PACKS:
    pack['icon'] = 'staffpack/' + pack['icon']


def normalize_team(team):
    """Migrate legacy ALL staff and relocate appointments without losing owned cards."""
    staffs = team.setdefault('staffs', [])
    for staff in staffs:
        info = CATALOG.get(str(staff.get('stfid')))
        if info is not None:
            staff['commonname'] = info['name']
            staff['position'] = info['position']
            staff['material'] = info['material']
        elif staff.get('position') not in SLOT_TYPES.values():
            staff['position'] = 'FRONT'
        if str(staff.get('stfid')) in ('9502', '9505'):
            staff['commonname'] = 'Staff #' + str(staff['stfid']) + ' (unverified)'
    by_id = {p['_id']: p for p in staffs}
    old = team.get('staffroles') or []
    roles = [{'roleidx': 1, 'slotidx': i, 'open': True, 'staffid': None} for i in SLOT_TYPES]
    for previous in old:
        staff = by_id.get(previous.get('staffid'))
        if staff is None:
            continue
        target = next(r for r in roles if SLOT_TYPES[r['slotidx']] == staff['position'])
        if target['staffid'] is None:
            target['staffid'] = staff['_id']
    active = {r['staffid'] for r in roles if r['staffid']}
    for staff in staffs:
        staff['status'] = 'appointed' if staff['_id'] in active else 'idle'
    team['staffroles'] = roles
    team['staffroleidx'] = 1
    team['maxstaff'] = max(30, team.get('maxstaff') or 0)


def team_state(st):
    slot = hc._default_slot(st)
    team = st["teams"][str(slot)]
    normalize_team(team)
    return slot, team


def reply(st, slot, **extra):
    return hc._json({"result": True, **extra, "resources": hc.coach_me_resources(st, slot)})


def fail(reason):
    return hc._json({"result": False, "reason": reason})


def recruit_list(query, body):
    return hc._json([{k: v for k, v in p.items() if k != "grades"} for p in PACKS])


def recruit(recruitid, query, body):
    pack = next((p for p in PACKS if p["recruitid"] == int(recruitid)), None)
    if pack is None:
        return fail("INVALID_STAFF_PACK")
    req = json.loads(body or b"{}")
    if req.get("feetype", "ep") != "ep" or req.get("eventtype"):
        return fail("INVALID_STAFF_PAYMENT")
    st = hc._state()
    slot, team = team_state(st)
    if len(team["staffs"]) >= team["maxstaff"]:
        return fail("STAFF_LIMIT_EXCEEDED")
    coach = hc.my_coach(st)
    if coach.get("ep", hc.START_EP) < pack["ep"]:
        return fail("STAFF_EP_NOTENOUGH")
    category = next((r for r in TYPES if r[0] == pack.get('position')), None) or random.choice(TYPES)
    typ, label, pool, effects_pool = category
    portraits = [p for p in pool if os.path.isfile(os.path.join(hc.ASSETS, "externalAssets", "staffs", str(p) + ".png"))]
    if not portraits:
        return fail("STAFF_PORTRAITS_MISSING")
    grade, stfid = random.choice(pack["grades"]), random.choice(portraits)
    info = CATALOG[str(stfid)]
    effects = recruit_effects(info, grade)
    staff = {"_id": hc.new_iid(), "stfid": stfid, "commonname": info['name'],
             "position": typ, "grade": grade, "exp": 0, "gradeupto": 1000,
             "life": 100, "status": "idle", "effect": effects, "study": None,
             "material": False, "contractfee": 0, "new": True}
    team["staffs"].append(staff)
    coach["ep"] = coach.get("ep", hc.START_EP) - pack["ep"]
    hc._save(st)
    return reply(st, slot, staff=staff)


def appoint(staffid, query, body):
    req = json.loads(body or b"{}")
    idx, role = req.get("slot"), req.get("staffrole", 1)
    if type(idx) is not int or not 1 <= idx <= 7 or type(role) is not int or role != 1:
        return fail("INVALID_STAFF_SLOT")
    st = hc._state()
    slot, team = team_state(st)
    staff = next((p for p in team["staffs"] if p["_id"] == staffid), None)
    if staff is None or staff.get("life", 0) <= 0:
        return fail("INVALID_STAFF")
    target = next((r for r in team["staffroles"] if r["roleidx"] == role and r["slotidx"] == idx), None)
    if target is None or not target.get("open"):
        return fail("INVALID_STAFF_SLOT")
    if staff['position'] != SLOT_TYPES[idx]:
        return fail('STAFF_POSITION_MISMATCH')
    previous_id = target.get('staffid')
    for r in team["staffroles"]:
        if r.get("staffid") == staffid:
            r["staffid"] = None
    target["staffid"] = staffid
    active = {r.get("staffid") for r in team["staffroles"] if r.get("open")}
    for p in team["staffs"]:
        p["status"] = "appointed" if p["_id"] in active else "idle"
    hc._save(st)
    previous = next((p for p in team['staffs'] if p['_id'] == previous_id), None)
    return reply(st, slot, appointed={'appointedstaff': staff, 'prevstaff': previous})


def unappoint(staffid, query, body):
    st = hc._state()
    slot, team = team_state(st)
    staff = next((p for p in team["staffs"] if p["_id"] == staffid), None)
    if staff is None:
        return fail("INVALID_STAFF")
    for r in team["staffroles"]:
        if r.get("staffid") == staffid:
            r["staffid"] = None
    staff["status"] = "idle"
    hc._save(st)
    return reply(st, slot)


def install(module):
    global hc
    hc = module
    hc.ENDPOINTS["/staff/recruit"] = recruit_list
    hc.ROUTES[:0] = [
        (re.compile(r"/staff/recruit/(\d+)"), recruit),
        (re.compile(r"/staff/appoint/([0-9a-f]{24})"), appoint),
        (re.compile(r"/staff/unappoint/([0-9a-f]{24})"), unappoint),
    ]

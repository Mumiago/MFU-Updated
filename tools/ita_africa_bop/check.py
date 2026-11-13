import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
ON00 = 'common/on_actions/00_on_actions.txt'
TRIG = 'common/scripted_triggers/MFU_ITA_africa_bop_triggers.txt'
EFF = 'common/scripted_effects/MFU_ITA_africa_bop_effects.txt'
ONA = 'common/on_actions/MFU_ITA_africa_bop_on_actions.txt'
FOCUS = 'common/national_focus/italy.txt'
IDEAS = 'common/ideas/germany.txt'
TRAITS = 'common/country_leader/00_traits.txt'
BOP = 'common/bop/ITA.txt'
LOC = 'localisation/english/MFU_ITA_africa_bop_l_english.yml'
TOUCHED = [ON00, TRIG, EFF, ONA, FOCUS, IDEAS, TRAITS, BOP]


def raw(p):
    fp = os.path.join(ROOT, p)
    return open(fp, 'rb').read() if os.path.exists(fp) else b''


def text(p):
    return raw(p).decode('utf-8-sig', errors='replace')


def code(t):
    return '\n'.join(l.split('#')[0] for l in t.split('\n'))


def block(t, start):
    i = t.index('{', start)
    d = 0
    for j in range(i, len(t)):
        if t[j] == '{':
            d += 1
        elif t[j] == '}':
            d -= 1
            if d == 0:
                return t[i:j + 1]
    raise AssertionError('unbalanced block')


def named(t, name):
    m = re.search(r'(?m)^\s*' + re.escape(name) + r'\s*=\s*\{', t)
    assert m, name + ' not found'
    return block(t, m.start())


def focus(fid):
    t = code(text(FOCUS))
    m = re.search(r'\bid\s*=\s*' + fid + r'\b', t)
    assert m, fid
    return block(t, t.rfind('focus', 0, m.start()))


def reward(fid):
    f = focus(fid)
    return block(f, f.index('completion_reward'))


def test_old_blocks_removed():
    assert 'id = ITA_power_balance' not in code(text(ON00))


def test_state_list():
    b = named(code(text(TRIG)), 'ITA_africa_bop_state')
    assert sorted(map(int, re.findall(r'state\s*=\s*(\d+)', b))) == [448, 449, 450, 451, 458]


def test_effects_defined():
    t = code(text(EFF))
    for n in ('ITA_africa_bop_apply_loss', 'ITA_africa_bop_apply_refund', 'ITA_africa_bop_step_down', 'ITA_africa_bop_end'):
        named(t, n)
    loss = named(t, 'ITA_africa_bop_apply_loss')
    gain = named(t, 'ITA_africa_bop_apply_refund')
    for v in ('-0.2', '-0.15', '-0.1'):
        assert re.search(r'value\s*=\s*' + re.escape(v) + r'\b', loss), v
    for v in ('0.2', '0.15', '0.1'):
        assert re.search(r'value\s*=\s*' + re.escape(v) + r'\b', gain), v


def test_on_action():
    t = code(text(ONA))
    assert 'on_state_control_changed' in t
    assert 'set_state_flag = ITA_africa_bop_lost' in t
    assert 'clr_state_flag = ITA_africa_bop_lost' in t
    assert 'ITA_africa_bop_apply_loss = yes' in t
    assert 'ITA_africa_bop_apply_refund = yes' in t
    assert 'has_power_balance' in t


def test_focus_hooks():
    for fid, key, eff in (('ITA_bend_the_bars', 'ITA_africa_bop_tier_1_tt', 'ITA_africa_bop_step_down'),
                          ('ITA_castello_di_sabbia', 'ITA_africa_bop_tier_1_tt', 'ITA_africa_bop_step_down'),
                          ('ITA_victory_in_the_desert', 'ITA_africa_bop_tier_2_tt', 'ITA_africa_bop_step_down'),
                          ('ITA_viva_il_duce', 'ITA_africa_bop_off_tt', 'ITA_africa_bop_end')):
        r = reward(fid)
        assert r.count(eff + ' = yes') == 1, (fid, eff)
        assert r.count(key) == 1, (fid, key)


def test_flat_bop():
    for fid, n in (('ITA_bend_the_bars', 0), ('ITA_castello_di_sabbia', 1), ('ITA_victory_in_the_desert', 1)):
        assert reward(fid).count('ITA_bop_low_increase_effect') == n, fid


def test_no_german_output_in_ita():
    for fid in ('ITA_bend_the_bars', 'ITA_castello_di_sabbia', 'ITA_victory_in_the_desert'):
        f = focus(fid)
        assert 'GER_arbeitseinsatz_industrial_capacity_factory' not in f, fid
        assert 'GER_elalamein_tt' not in f, fid


def test_plunder_levels():
    t = code(text(IDEAS))
    for n, v in zip(range(1, 7), ('0.06', '0.11', '0.17', '0.23', '0.28', '0.34')):
        b = named(t, 'GER_economy_of_plunder_%d' % n)
        got = re.findall(r'\bindustrial_capacity_factory\s*=\s*([\d.]+)', b)
        assert got == [v], (n, got)


def test_speer():
    b = named(code(text(TRAITS)), 'GERminister_of_armament_and_war_production')
    assert re.findall(r'\bindustrial_capacity_factory\s*=\s*([\d.]+)', b) == ['0.30']


def test_no_collapse():
    t = code(text(BOP))
    m = re.search(r'id\s*=\s*ITA_grand_council_total_control_range', t)
    rng = block(t, t.rfind('range', 0, m.start()))
    act = block(rng, rng.index('on_activate'))
    for k in ('remove_power_balance', 'add_war_support', 'add_stability'):
        assert k not in act, k


def test_loc():
    b = raw(LOC)
    assert b.startswith(b'\xef\xbb\xbf'), 'BOM'
    t = b.decode('utf-8-sig')
    assert t.lstrip().startswith('l_english:')
    allloc = ''
    d = os.path.join(ROOT, 'localisation/english')
    for f in os.listdir(d):
        if f.endswith('.yml'):
            allloc += open(os.path.join(d, f), 'rb').read().decode('utf-8', errors='replace') + '\n'
    for k in ('ITA_africa_bop_tier_1_tt', 'ITA_africa_bop_tier_2_tt', 'ITA_africa_bop_off_tt'):
        assert len(re.findall(r'(?m)^\s*' + k + r':', allloc)) == 1, k


def test_bop_desc():
    t = code(text('common/scripted_localisation/MFU_ITA_africa_bop_scripted_loc.txt'))
    b = named(t, 'defined_text')
    assert 'name = GetITAAfricaBopRule' in b
    keys = re.findall(r'localization_key\s*=\s*(\w+)', b)
    assert keys == ['ITA_africa_bop_rule_off', 'ITA_africa_bop_rule_10', 'ITA_africa_bop_rule_15', 'ITA_africa_bop_rule_20'], keys
    loc = raw(LOC).decode('utf-8-sig')
    assert re.search(r'(?m)^\s*ITA_balance_of_power_category_desc:\d*\s*"\[ITA\.GetITAAfricaBopRule\]"', loc)
    for k, pct in (('ITA_africa_bop_rule_20', '20%'), ('ITA_africa_bop_rule_15', '15%'), ('ITA_africa_bop_rule_10', '10%'), ('ITA_africa_bop_rule_off', None)):
        m = re.search(r'(?m)^\s*' + k + r':\d*\s*"(.*)"', loc)
        assert m, k
        if pct:
            assert pct in m.group(1), k


def test_braces():
    for p in TOUCHED:
        t = raw(p)
        if not t:
            continue
        d = 0
        for line in t.decode('utf-8-sig', errors='replace').split('\n'):
            c = re.sub(r'"[^"]*"', '', line).split('#')[0]
            d += c.count('{') - c.count('}')
            assert d >= 0, p
        assert d == 0, p


def test_crlf():
    for p in TOUCHED + [LOC]:
        b = raw(p)
        if b:
            assert b.count(b'\r\n') == b.count(b'\n'), p


if __name__ == '__main__':
    fails = 0
    for name, fn in sorted((k, v) for k, v in globals().items() if k.startswith('test_')):
        try:
            fn()
            print('PASS', name)
        except Exception as e:
            fails += 1
            print('FAIL', name, '-', repr(e)[:160])
    print('%d failed' % fails)
    sys.exit(1 if fails else 0)

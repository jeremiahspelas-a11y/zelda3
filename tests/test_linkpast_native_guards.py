#!/usr/bin/env python3
"""Static integration guards for the native LinkPast prototype.

These are structural regressions only. They DO NOT substitute for an
Emscripten build, gameplay tests, or 60-Hz collision verification.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
anc = (ROOT / "src/ancilla.c").read_text()
player = (ROOT / "src/player.c").read_text()
sprite = (ROOT / "src/sprite.c").read_text()
patch = (ROOT / "browser_patch.py").read_text()
browser = (ROOT / "browser/index.html").read_text()

def required(source, fragments, name):
    for fragment in fragments:
        assert fragment in source, f"{name}: missing {fragment!r}"

required(anc, [
    "LinkPast_SpawnZeldaWandPulse(bool charged)",
    "LinkPast_OrbitPosition(",
    "Boomerang_Draw(k);",
    "Ancilla_CheckSpriteCollision(k)",
    "g_linkpast_wand_ticks[j] = 0;",
    "g_linkpast_wand_ticks[k] = 0;",
], "native ancilla")

assert anc.index("static const uint8 kAncilla_Pflags") < anc.index("static void LinkPast_SpawnWandBolt"), (
    "Wand helper must follow original ancilla sprite flag declaration"
)

required(player, [
    "LinkPast_SpawnZeldaWandPulse(false)",
    "LinkPast_SpawnZeldaWandPulse(true)",
    "link_spin_attack_step_counter = 0;",
    "void Link_CheckForSwordSwing()",
    "void Player_Sword_SpinAttackJerks_HoldDown()",
], "player")

a = player.index("void HandleSwordControls()")
b = player.index("void Link_ResetSwordAndItemUsage()", a)
controller = player[a:b]
zelda = controller[controller.index("if (g_browser_zelda_skin)") : controller.index("#endif")]
assert "Player_Sword_SpinAttackJerks_HoldDown()" not in zelda, "Zelda must not use Link spin state"
assert "CalculateSwordHitBox()" not in zelda, "Zelda must not use Link sword hitbox"
assert "if (charged)" in zelda

required(sprite, [
    "g_browser_zelda_skin /* Zelda never inherits Link's frontal shield */",
    "The player B timer is reused for Zelda's wand",
    "uint8 Sprite_CheckDamageFromLink(int k)",
], "native sprite collision")

required(patch, [
    "ZeldaBrowserSwitchCharacter(int target)",
    "LinkPast_SetZeldaOrbitBoomerangEnabled(g_browser_zelda_skin)",
    "g_coop_spawned_zelda",
], "native browser bridge")
required(browser, [
    'id="linkpast-pair"',
    'id="linkpast-switch"',
    "_ZeldaBrowserSwitchCharacter",
], "Android controls")

print("PASS native structural regression guards (not a runtime build)")

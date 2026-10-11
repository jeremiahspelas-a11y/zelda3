#!/usr/bin/env python3
"""Rewrite the privately extracted US dialogue to swap Zelda and Link roles.

USAGE
  python3 browser/rewrite_roles.py --rom /private/zelda.sfc \
      --assets /private/zelda3_assets.dat --out /private/zelda3_roles.dat

All ROM bytes and generated assets stay on the user's computer. NEVER commit
generated .dat files or a ROM to a public repository.

The editor preserves every non-dialogue asset, glyph font, animation directive,
and message count. It changes on-screen dialogue but does NOT yet rewrite every
visual graphic, name-entry tilemap, or ending-credit picture.
"""
import argparse
from pathlib import Path
import re
import struct
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "assets"))
import util
import text_compression


def unpack_array(data):
    if len(data) < 2:
        raise ValueError("Invalid packed array")
    end = len(data) - 2
    mx, = struct.unpack_from("<H", data, end)
    use32 = mx >= 8192
    count = mx - 8192 if use32 else mx
    step, fmt = (4, "<I") if use32 else (2, "<H")
    if count * step > end:
        raise ValueError("Invalid array index")
    cuts = [0] + [struct.unpack_from(fmt, data, i * step)[0]
                  for i in range(count)] + [end-count*step]
    if cuts != sorted(cuts):
        raise ValueError("Array offsets out of order")
    return [data[count*step+cuts[i]:count*step+cuts[i+1]]
            for i in range(count+1)]


def pack_array(blobs):
    blobs = list(blobs)
    offset = 0
    cuts = []
    for blob in blobs[:-1]:
        offset += len(blob)
        cuts.append(offset)
    if offset < 65536 and len(blobs) <= 8192:
        return b"".join(struct.pack("<H", cut) for cut in cuts) + \
            b"".join(blobs) + struct.pack("<H", len(blobs)-1)
    return b"".join(struct.pack("<I", cut) for cut in cuts) + \
        b"".join(blobs) + struct.pack("<H", 8192+len(blobs)-1)


def rewrite_message(text, num):
    # The imprisoned Princess Zelda becomes Prince Link. The playable
    # protagonist, formerly [Name], is now permanently called Zelda.
    # Do not edit bracketed control tokens such as [Waitkey] and [Scroll].
    changed = text.replace("Princess Zelda", "Prince Link")
    changed = re.sub(r"\bPrincess\b", "Prince", changed)
    changed = re.sub(r"\bZelda\b", "Link", changed)
    changed = re.sub(r"(?<!Prince )\bLink\b", "Prince Link", changed)
    changed = changed.replace("[Name]", "Zelda")

    # Some English pronouns require context, not global replacement.
    if num == 44:
        changed = changed.replace("young[3]man", "young[3]woman")
    elif num == 48:
        changed = changed.replace("wanted man!", "wanted woman!")
    elif num == 51:
        changed = changed.replace("young[Scroll]man", "young[Scroll]woman")
    elif num == 58:
        changed = changed.replace("young man!", "young woman!")
        changed = changed.replace("young[Waitkey]man", "young[Waitkey]woman")
    elif num == 182:
        changed = changed.replace("his form", "their form")
    elif num == 28:
        changed = changed.replace("abducted her", "abducted him")
        changed = changed.replace("taken her", "taken him")
        changed = changed.replace("find her", "find him")
    elif num == 32:
        changed = changed.replace("other missing[Scroll]girls",
                                  "other missing[Scroll]heirs")
    elif num == 60:
        changed = changed.replace("see him!", "see her!")
        changed = changed.replace("[LinkL][LinkR]", "")  # remove wrong face portrait
    elif num == 167:
        changed = changed.replace("bad[Scroll]guy", "bad[Scroll]person")
    elif num == 309:
        changed = changed.replace("he alone must face",
                                  "she alone must face")
    return changed


def assets_to_parts(data):
    if data[:9] != b"Zelda3_v0":
        raise ValueError("Not a Zelda3 extracted-assets container")
    n, = struct.unpack_from("<I", data, 80)
    if n != 165:
        raise ValueError("Unexpected asset count")
    header_len = 88 + 4*n + struct.unpack_from("<I", data, 84)[0]
    if header_len > len(data):
        raise ValueError("Corrupt asset header")
    parts, pos = [], header_len
    for i in range(n):
        pos = (pos + 3) & ~3
        size, = struct.unpack_from("<I", data, 88 + 4*i)
        if pos + size > len(data):
            raise ValueError(f"Asset {i} overruns file")
        parts.append(data[pos:pos+size])
        pos += size
    return header_len, parts


def rewrite_assets(rom, data):
    messages = [s for s, raw in
                text_compression.decode_strings_generic(rom.get_byte, "us")]
    if len(messages) != 397:
        raise ValueError("Expected 397 original US dialogue messages")
    rewritten = [rewrite_message(s, i+1) for i, s in enumerate(messages)]
    modified = sum(a != b for a, b in zip(messages, rewritten))
    if not modified:
        raise ValueError("Nothing changed")

    header_len, parts = assets_to_parts(data)
    languages = unpack_array(parts[94])
    chunks = unpack_array(languages[0])
    old_messages = unpack_array(chunks[1])
    if len(old_messages) != 397:
        raise ValueError("Asset dialogue count does not match the ROM")

    new_messages = list(map(bytes, text_compression.compress_strings(rewritten, "us")))
    for i, (orig, new, oldbytes) in enumerate(zip(messages, rewritten, old_messages)):
        if orig == new and new_messages[i] != oldbytes:
            raise ValueError(f"Untouched message {i+1} changed during encoding")

    chunks[1] = pack_array(new_messages)
    languages[0] = pack_array(chunks)
    parts[94] = pack_array(languages)

    out = bytearray(data[:header_len])
    for i, block in enumerate(parts):
        while len(out) % 4:
            out.append(0)
        struct.pack_into("<I", out, 88 + 4*i, len(block))
        out += block

    _, check = assets_to_parts(out)
    assert len(unpack_array(unpack_array(unpack_array(check[94])[0])[1])) == 397
    assert all(parts[i] == check[i] for i in range(165))
    return bytes(out), modified


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom", type=Path, required=True)
    parser.add_argument("--assets", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    src = args.assets.resolve()
    dest = args.out.resolve()
    if src == dest:
        parser.error("--out must not overwrite the original extracted assets")
    rom = util.load_rom(str(args.rom), True)
    result, count = rewrite_assets(rom, args.assets.read_bytes())
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(result)
    print(f"PASS: rewrote {count} of 397 US messages")
    print("PASS: unchanged assets preserved, all 397 dialogue slots retained")
    print(f"PRIVATE OUTPUT: {dest}")


if __name__ == "__main__":
    main()

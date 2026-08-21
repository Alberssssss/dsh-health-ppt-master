# Icon Availability Guide

> Prevents the #1 icon pitfall: writing icon names into `spec_lock.md` that don't exist in the library directory, causing `finalize_svg.py` to silently drop them (icons vanish from the PPTX with only a `[WARN]` in stderr).

## How to verify any icon name

```bash
# Verify a batch of names against the chosen library
ls <skill-dir>/templates/icons/chunk-filled/ | grep -E 'brain|stethoscope|gear'
# No output = name doesn't exist — find an alternative below or ls | grep <semantic keyword>
```

## chunk-filled: common missing → available alternatives

Discovered in a 20-page medical-tech deck session where 16/30 locked icon names didn't exist. The left column names are intuitive but **do not exist** as filenames; use the right column instead.

| Missing name (hallucinated) | Available alternative | Semantic match |
|---|---|---|
| `brain` | `microchip` | AI / intelligence |
| `stethoscope` | `heart` | medical examination |
| `gear` | `cog` | settings / mechanism |
| `network` | `share-nodes` | connectivity / graph |
| `atom` | `label` | science / tag |
| `lock` | `key` | security / access |
| `check-circle` | `circle-checkmark` | validation / success |
| `award` | `badge` | achievement / recognition |
| `growth` | `arrow-trend-up` | upward trend / growth |
| `file-text` | `file` | document |
| `pulse` | `waveform` | vital signs / signal |
| `hand-heart` | `hand` | care / support |
| `flow-arrow` | `arrow-right` | directional flow |
| `flask` | `(use tabler-filled: flask)` | chemistry / lab |
| `cross` | `(use tabler-filled: cross)` | medical cross |
| `medical-shield` | `shield` | medical protection |

## Search strategy when an alternative isn't listed

1. `ls <skill-dir>/templates/icons/<library>/ | grep <semantic-keyword>` — try multiple keywords (`heart`, `medical`, `health`, `pulse`)
2. If the stylistic library truly lacks a needed icon, consider whether a broader semantic icon works (`shield` instead of `medical-shield`)
3. **Never** cross stylistic libraries to fill a gap (per icons README). `simple-icons` is brand-logo-only.
4. If no alternative exists, omit the icon — a missing icon is better than a hallucinated one that silently disappears

## Post-generation check

After `finalize_svg.py`, scan its output for `[WARN]`:

```bash
python3 <skill-dir>/scripts/finalize_svg.py <project_path> 2>&1 | grep -i 'warn\|not found\|missing'
```

Any match = an icon name was wrong. Fix the `data-icon` value in the SVG, re-run finalize.

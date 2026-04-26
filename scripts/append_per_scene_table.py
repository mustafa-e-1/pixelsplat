"""Append a per-scene metrics table to SUMMARY.md, computed from the
authoritative per_scene_metrics.json (saved by patched MetricComputer).
"""
import json
from pathlib import Path

PER_SCENE = Path("outputs/full_eval/per_scene_metrics.json")
SUMMARY = Path("report/session2_repro/SUMMARY.md")
PER_SCENE_DIR = Path("report/session2_repro/per_scene")

with PER_SCENE.open() as f:
    data = json.load(f)

# Sort by PSNR descending so best scenes are at the top.
rows = sorted(
    data.items(),
    key=lambda kv: -kv[1]["psnr_ours"],
)

mean_psnr = sum(v["psnr_ours"] for v in data.values()) / len(data)
mean_lpips = sum(v["lpips_ours"] for v in data.values()) / len(data)
mean_ssim = sum(v["ssim_ours"] for v in data.values()) / len(data)

# Build the markdown.
table_lines = [
    "\n---\n",
    f"## Per-Scene Metrics ({len(data)} scenes)\n",
    "Computed by pixelSplat's `compute_metrics.py` on the rendered novel "
    "views vs. dataset ground truth at 256×256. Each scene's row also "
    "links to its asset folder under `per_scene/<scene_id>/`, which "
    "contains the two input frames and the rendered novel views.\n",
    "| # | Scene ID | PSNR (dB) ↑ | LPIPS ↓ | SSIM ↑ | Assets |",
    "|---|---|---:|---:|---:|---|",
]
for i, (scene, m) in enumerate(rows, 1):
    asset_link = f"[`per_scene/{scene}/`](per_scene/{scene}/)"
    table_lines.append(
        f"| {i} | `{scene}` | {m['psnr_ours']:.3f} "
        f"| {m['lpips_ours']:.3f} | {m['ssim_ours']:.3f} "
        f"| {asset_link} |"
    )

table_lines.append("")
table_lines.append("### Aggregate (mean across all scenes above)")
table_lines.append("")
table_lines.append("| Metric | Mine | Paper | Δ |")
table_lines.append("|---|---:|---:|---:|")
table_lines.append(
    f"| PSNR ↑ | **{mean_psnr:.3f}** | 26.090 "
    f"| {mean_psnr - 26.09:+.3f} |"
)
table_lines.append(
    f"| LPIPS ↓ | **{mean_lpips:.3f}** | 0.136 "
    f"| {mean_lpips - 0.136:+.3f} |"
)
table_lines.append(
    f"| SSIM ↑ | **{mean_ssim:.3f}** | 0.863 "
    f"| {mean_ssim - 0.863:+.3f} |"
)
table_lines.append("")

# Append to SUMMARY.md (don't overwrite existing content).
with SUMMARY.open("a") as f:
    f.write("\n".join(table_lines))

print(f"Appended {len(data)}-row per-scene table to {SUMMARY}")
print(f"Mean: PSNR={mean_psnr:.3f}, LPIPS={mean_lpips:.3f}, SSIM={mean_ssim:.3f}")
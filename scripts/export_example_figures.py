"""Generate deterministic documentation figures from package APIs."""

from __future__ import annotations

from contextlib import suppress
from html import escape
from pathlib import Path

from rubin_subshifts.symbolic.sft import OneStepSFT
from rubin_subshifts.visualization.export import export_figure
from rubin_subshifts.visualization.subshifts import counts_figure, transition_graph_figure


def fallback_line_svg(x: list[int], y: list[int], title: str) -> bytes:
    """Render a deterministic accessible SVG when Kaleido is unavailable."""
    width, height = 1200, 675
    left, right, top, bottom = 110, 1140, 100, 570
    maximum = max(y) * 1.08
    points = [
        (
            left + index * (right - left) / max(len(x) - 1, 1),
            bottom - value * (bottom - top) / maximum,
        )
        for index, value in enumerate(y)
    ]
    polyline = " ".join(f"{px:.1f},{py:.1f}" for px, py in points)
    circles = "".join(
        f'<circle cx="{px:.1f}" cy="{py:.1f}" r="6" fill="#0F766E" />' for px, py in points
    )
    labels = "".join(
        f'<text x="{px:.1f}" y="610" text-anchor="middle">{value}</text>'
        for px, value in zip((point[0] for point in points), x, strict=True)
    )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title><desc id="desc">Exact periodic-point counts by period.</desc>
<rect width="100%" height="100%" fill="white"/>
<text x="60" y="52" font-family="sans-serif" font-size="30" font-weight="700" fill="#132238">{escape(title)}</text>
<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="#64748B" stroke-width="2"/>
<line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" stroke="#64748B" stroke-width="2"/>
<polyline points="{polyline}" fill="none" stroke="#0F766E" stroke-width="5"/>{circles}{labels}
<text x="625" y="652" text-anchor="middle" font-family="sans-serif" font-size="20" fill="#334155">Period n</text>
<text x="28" y="340" transform="rotate(-90 28 340)" text-anchor="middle" font-family="sans-serif" font-size="20" fill="#334155">Periodic points</text>
</svg>'''
    return svg.encode()


def main() -> None:
    """Write idempotent HTML figures and best-effort static images."""
    output = Path("docs/assets/figures")
    output.mkdir(parents=True, exist_ok=True)
    shift = OneStepSFT.golden_mean()
    periods = list(range(1, 11))
    figures = {
        "golden-mean-transition": transition_graph_figure(
            shift.transition_graph(), title=shift.name
        ),
        "golden-mean-periodic-points": counts_figure(
            periods,
            [shift.periodic_point_count(period) for period in periods],
            title="Golden mean periodic points",
            x_title="Period",
            y_title="Points",
        ),
    }
    for stem, figure in figures.items():
        (output / f"{stem}.html").write_bytes(export_figure(figure, "html"))
        with suppress(Exception):
            (output / f"{stem}.png").write_bytes(export_figure(figure, "png"))
    svg_path = output / "golden-mean-periodic-points.svg"
    try:
        svg_path.write_bytes(export_figure(figures["golden-mean-periodic-points"], "svg"))
    except Exception:
        svg_path.write_bytes(
            fallback_line_svg(
                periods,
                [shift.periodic_point_count(period) for period in periods],
                "Golden mean periodic points",
            )
        )


if __name__ == "__main__":
    main()

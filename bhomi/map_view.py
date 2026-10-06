"""Create a schematic, explicitly unsurveyed field illustration."""
from html import escape


def polygon_svg(field: dict, width: int = 640, height: int = 220, language: str = "gu") -> str:
    points = field.get("polygon", [])
    if len(points) < 3:
        return '<div class="map-fallback">No sample field boundary is available.</div>' if language == "en" else '<div class="map-fallback">નમૂના ખેતરની સીમા ઉપલબ્ધ નથી.</div>'
    lats, lons = [p[0] for p in points], [p[1] for p in points]
    min_x, max_x, min_y, max_y = min(lons), max(lons), min(lats), max(lats)
    span_x, span_y = max(max_x - min_x, 0.0001), max(max_y - min_y, 0.0001)
    coords = []
    for lat, lon in points:
        x = 42 + ((lon - min_x) / span_x) * (width - 84)
        y = 35 + ((max_y - lat) / span_y) * (height - 70)
        coords.append(f"{x:.1f},{y:.1f}")
    joined = " ".join(coords)
    title = escape(field.get("name_en", field["name_gu"]) if language == "en" else field["name_gu"])
    sample_label = "sample shape" if language == "en" else "નમૂના આકાર"
    boundary_label = "not surveyed" if language == "en" else "સર્વે કરેલી સીમા નથી"
    map_aria = f"{title}, illustrative map" if language == "en" else f"{title}, કલ્પિત નકશો"
    return f'''<svg viewBox="0 0 {width} {height}" role="img" aria-label="{map_aria}" xmlns="http://www.w3.org/2000/svg">
      <rect width="{width}" height="{height}" rx="18" fill="#eef1e5"/>
      <path d="M0 155 Q140 115 270 145 T640 110 V220 H0Z" fill="#dfe9d4"/>
      <path d="M0 182 Q180 142 330 172 T640 139" fill="none" stroke="#c5d5ba" stroke-width="2"/>
      <polygon points="{joined}" fill="#a9c58d" fill-opacity=".65" stroke="#4f6f3a" stroke-width="4" stroke-linejoin="round"/>
      <text x="24" y="30" font-size="15" fill="#52634e" font-family="sans-serif">{title} · {sample_label}</text>
      <text x="{width-175}" y="{height-18}" font-size="12" fill="#68756b" font-family="sans-serif">{boundary_label}</text>
    </svg>'''

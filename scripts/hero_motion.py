"""Self-contained SVG motion: preprojected 3D geometry, SMIL and internal CSS.

The result works as an image; it needs no JavaScript, external font or library.
"""
import math

FRAMES = 49  # Includes the identical loop endpoint.
DURATION = '24s'


def project(point, phase):
    """Orthographic projection of a rotating, gently pitching computation cube."""
    x, y, z = point
    angle = .58 + math.tau * phase
    tilt = .43 + .07 * math.sin(math.tau * phase)
    xr = x * math.cos(angle) + z * math.sin(angle)
    zr = -x * math.sin(angle) + z * math.cos(angle)
    yr = y * math.cos(tilt) - zr * math.sin(tilt)
    return 948 + xr * 82, 241 + yr * 82 + 4 * math.sin(math.tau * phase)


def path_for(lines, phase):
    chunks = []
    for points, closed in lines:
        coords = [project(p, phase) for p in points]
        chunks.append('M' + 'L'.join(f'{x:.2f} {y:.2f}' for x, y in coords) + ('Z' if closed else ''))
    return ''.join(chunks)


def animated_path(lines, attrs, live):
    first = path_for(lines, 0)
    if not live:
        return f'<path d="{first}" {attrs}/>'
    values = ';'.join(path_for(lines, i / (FRAMES - 1)) for i in range(FRAMES))
    return f'<path d="{first}" {attrs}><animate attributeName="d" dur="{DURATION}" values="{values}" calcMode="linear" repeatCount="indefinite"/></path>'


def cube_edges(size):
    vertices = [(x * size, y * size, z * size) for x in [-1, 1] for y in [-1, 1] for z in [-1, 1]]
    return [(tuple([a, b]), False) for i, a in enumerate(vertices) for b in vertices[i + 1:] if sum(abs(u - v) > .001 for u, v in zip(a, b)) == 1]


def node(point, color, index, live):
    coords = [project(point, i / (FRAMES - 1)) for i in range(FRAMES)]
    x, y = coords[0]
    motion = ''
    if live:
        for axis, values in [('cx', [v[0] for v in coords]), ('cy', [v[1] for v in coords])]:
            motion += f'<animate attributeName="{axis}" values="{";".join(f"{v:.2f}" for v in values)}" dur="{DURATION}" repeatCount="indefinite"/>'
    return (f'<circle cx="{x:.2f}" cy="{y:.2f}" r="8" fill="{color}" opacity=".17" class="core-node-halo" style="animation-delay:-{index * 1.1}s">{motion}</circle>'
            f'<circle cx="{x:.2f}" cy="{y:.2f}" r="2.8" fill="{color}">{motion}</circle>')


def scene(t, live):
    mint, violet, cyan = t['accent'], t['violet'], '#75DAF2'
    parts = []
    # Transparent faces preserve the wireframe's depth without occluding routes.
    for face in [((-1,-1,-1),(1,-1,-1),(1,-1,1),(-1,-1,1)),
                 ((-1,-1,-1),(-1,1,-1),(1,1,-1),(1,-1,-1))]:
        parts.append(animated_path([(face, True)], f'fill="{mint}" fill-opacity=".025" stroke="none"', live))
    parts.append(animated_path(cube_edges(1), f'fill="none" stroke="{t["muted"]}" stroke-opacity=".6" stroke-width=".9"', live))

    for level, color in [(-.65, cyan), (0, mint), (.65, violet)]:
        corners = ((-.88,level,-.88),(.88,level,-.88),(.88,level,.88),(-.88,level,.88))
        parts.append(animated_path([(corners, True)], f'fill="{color}" fill-opacity=".045" stroke="{color}" stroke-opacity=".5" stroke-width=".8"', live))
        grid = []
        for step in [-.44, 0, .44]:
            grid += [(((-.88,level,step),(.88,level,step)),False), (((step,level,-.88),(step,level,.88)),False)]
        parts.append(animated_path(grid, f'fill="none" stroke="{color}" stroke-opacity=".16" stroke-width=".65"', live))

    route = ((-.76,.65,.42),(-.12,.65,.42),(-.12,0,.42),(.7,0,.42),(.7,0,-.64),(.7,-.65,-.64),(-.25,-.65,-.64))
    parts.append(animated_path([(route, False)], f'fill="none" stroke="{mint}" stroke-opacity=".27" stroke-width="1.1"', live))
    if live:
        parts.append(animated_path([(route, False)], f'class="core-data-glow" pathLength="100" fill="none" stroke="{mint}" stroke-opacity=".15" stroke-width="6" stroke-dasharray="14 86" stroke-linecap="round"', live))
        parts.append(animated_path([(route, False)], f'class="core-data" pathLength="100" fill="none" stroke="{mint}" stroke-width="1.8" stroke-dasharray="14 86" stroke-linecap="round"', live))
        # A luminous plane sweeps vertically through the rotating volume.
        scan_values = []
        for i in range(FRAMES):
            p = i / (FRAMES - 1)
            level = .82 * math.cos(math.tau * p * 2)
            corners = ((-.92,level,-.92),(.92,level,-.92),(.92,level,.92),(-.92,level,.92))
            scan_values.append(path_for([(corners, True)], p))
        parts.append(f'<path d="{scan_values[0]}" fill="{cyan}" fill-opacity=".045" stroke="{cyan}" stroke-opacity=".22" stroke-width=".8"><animate attributeName="d" values="{";".join(scan_values)}" dur="{DURATION}" repeatCount="indefinite"/></path>')

    parts.append(animated_path(cube_edges(.24), f'fill="none" stroke="{mint}" stroke-opacity=".9" stroke-width="1.1"', live))
    for index, point in enumerate([route[0], route[2], route[4], route[6]]):
        parts.append(node(point, [mint, cyan, violet, mint][index], index, live))
    return ''.join(parts)


def animated_core(t, reduced=False):
    mint, cyan, violet = t['accent'], '#75DAF2', t['violet']
    if reduced:
        return f'''<defs><pattern id="core-dots" width="16" height="16" patternUnits="userSpaceOnUse"><circle cx="8" cy="8" r=".7" fill="{mint}" opacity=".18"/></pattern></defs>
    <rect x="784" y="109" width="328" height="266" fill="url(#core-dots)" opacity=".6"/>
    <g transform="translate(948 241)" fill="none" stroke="{t['line']}">
      <circle r="148" stroke-width=".75" stroke-dasharray="1 9"/>
      <path d="M-154-108V-125H-137M137-125H154V-108M-154 108V125H-137M137 125H154V108"/>
    </g>{scene(t, False)}'''
    return f'''<defs>
      <radialGradient id="core-ambient"><stop stop-color="{mint}" stop-opacity=".14"/><stop offset=".5" stop-color="{cyan}" stop-opacity=".035"/><stop offset="1" stop-color="{t['bg']}" stop-opacity="0"/></radialGradient>
      <pattern id="core-dots" width="16" height="16" patternUnits="userSpaceOnUse"><circle cx="8" cy="8" r=".7" fill="{mint}" opacity=".18"/></pattern>
      <linearGradient id="core-rim"><stop stop-color="{mint}"/><stop offset=".55" stop-color="{cyan}"/><stop offset="1" stop-color="{violet}"/></linearGradient>
    </defs>
    <style>
      .core-static{{display:none}}
      .hero-live{{animation:core-status 4s ease-in-out infinite}}
      .core-ambient{{animation:core-breathe 8s ease-in-out infinite}}
      .core-orbit-a{{animation:core-spin 12s linear infinite;transform-origin:0 0}}
      .core-orbit-b{{animation:core-spin 24s linear infinite reverse;transform-origin:0 0}}
      .core-data,.core-data-glow{{animation:core-stream 6s linear infinite}}
      .core-node-halo{{animation:core-nodepulse 4.8s ease-in-out infinite}}
      .core-rim{{animation:core-stream 24s linear infinite}}
      @keyframes core-spin{{to{{transform:rotate(360deg)}}}}
      @keyframes core-stream{{to{{stroke-dashoffset:-100}}}}
      @keyframes core-status{{0%,100%{{opacity:.35}}50%{{opacity:.95}}}}
      @keyframes core-nodepulse{{0%,100%{{opacity:.08}}50%{{opacity:.3}}}}
      @keyframes core-breathe{{0%,100%{{opacity:.5}}50%{{opacity:1}}}}
      @media(prefers-reduced-motion:reduce){{
        .core-live,.motion-only{{display:none}}
        .core-static{{display:inline}}
        .hero-live,.core-node-halo{{animation:none}}
      }}
    </style>
    <ellipse cx="948" cy="241" rx="205" ry="164" fill="url(#core-ambient)" class="core-ambient motion-only"/>
    <rect x="784" y="109" width="328" height="266" fill="url(#core-dots)" opacity=".6"/>
    <g transform="translate(948 241)" fill="none">
      <circle r="148" stroke="{t['line']}" stroke-width=".75" stroke-dasharray="1 9"/>
      <path d="M-154-108V-125H-137M137-125H154V-108M-154 108V125H-137M137 125H154V108" stroke="{t['line']}" stroke-width="1"/>
      <g class="core-orbit-a motion-only">
        <circle r="148" stroke="{mint}" stroke-opacity=".1" stroke-width=".7"/>
        <path d="M148 0A148 148 0 0 0 113.37-95.13" stroke="{mint}" stroke-width="1.4" stroke-opacity=".65" stroke-linecap="round"/>
        <circle cx="148" cy="0" r="7" fill="{mint}" opacity=".12"/>
        <circle cx="148" cy="0" r="2.7" fill="{mint}"/>
      </g>
      <g class="core-orbit-b motion-only">
        <path d="M-139 0A139 139 0 0 0-120.38 69.5" stroke="{violet}" stroke-width="1" stroke-opacity=".55" stroke-linecap="round"/>
        <circle cx="-139" cy="0" r="6" fill="{violet}" opacity=".12"/>
        <circle cx="-139" cy="0" r="2.4" fill="{violet}"/>
      </g>
    </g>
    <g class="core-static">{scene(t, False)}</g>
    <g class="core-live">{scene(t, True)}</g>
    <rect x="1" y="1" width="1198" height="468" rx="24" fill="none" stroke="url(#core-rim)" stroke-width="1.1" stroke-opacity=".6" pathLength="100" stroke-dasharray="4 96" class="core-rim motion-only"/>
    '''.rstrip()

#!/usr/bin/env python3
"""Render a GitHub-native profile. Python standard library only."""
import argparse
import copy
import datetime as dt
import hashlib
import html
import json
import math
import os
from pathlib import Path
import urllib.request
from hero_motion import animated_core

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
THEMES = {
    "dark": dict(bg="#0D171D", panel="#13232B", ink="#EDF8F4", muted="#9DB5B5", accent="#9BE8C4", line="#284249", violet="#B7BAEF"),
    "light": dict(bg="#F1F7F5", panel="#FFFFFF", ink="#142F32", muted="#526D70", accent="#107D64", line="#CBDDD8", violet="#6560AD"),
}


def txt(x, y, value, size=20, fill="currentColor", weight=400, extra=""):
    return f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" font-weight="{weight}" {extra}>{html.escape(str(value))}</text>'


def svg(w, h, content, title):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title">
<title id="title">{html.escape(title)}</title>
<g font-family="{FONT}">{content}</g></svg>\n'''


def hero(t, animated=False, reduced=False):
    c = f'''<defs>
      <radialGradient id="halo"><stop stop-color="{t['accent']}" stop-opacity=".16"/><stop offset="1" stop-color="{t['bg']}" stop-opacity="0"/></radialGradient>
      <linearGradient id="edge"><stop stop-color="{t['accent']}"/><stop offset="1" stop-color="{t['violet']}"/></linearGradient>
    </defs>
    <rect x="1" y="1" width="1198" height="468" rx="24" fill="{t['bg']}" stroke="{t['line']}"/>
    <circle cx="950" cy="226" r="239" fill="url(#halo)"/>
    <path d="M56 91H1144" stroke="{t['line']}"/>
    <circle cx="64" cy="53" r="5" fill="{t['accent']}"{' class="hero-live"' if animated and not reduced else ''}/>
    {txt(82,59,'CHAO QIN / WIN4R',17,t['muted'],600,extra='letter-spacing="3"')}
    {txt(1144,60,'AI超元域',23,t['ink'],600,extra='text-anchor="end"')}
    {txt(56,184,'Build with AI.',66,t['ink'],700,extra='letter-spacing="-2.5"')}
    {txt(56,265,'Share what works.',66,t['accent'],700,extra='letter-spacing="-2.5"')}
    {txt(59,313,'Agents. Memory. AI coding.',23,t['muted'])}
    <path d="M58 368H615" stroke="{t['line']}"/>
    {txt(58,411,'OPEN SOURCE × HANDS-ON AI',16,t['muted'],500,extra='letter-spacing="2.3"')}
    '''
    if animated:
        c += animated_core(t, reduced=reduced)
    else:
        c += f'''<g transform="translate(948 241)" fill="none" stroke="{t['line']}">
      <circle r="139"/><circle r="107" stroke-dasharray="2 10"/><circle r="66"/>
      <ellipse rx="139" ry="52" transform="rotate(-35)" stroke="{t['accent']}" stroke-opacity=".65"/>
      <ellipse rx="139" ry="52" transform="rotate(35)" stroke="{t['violet']}" stroke-opacity=".65"/>
      <ellipse rx="139" ry="52" transform="rotate(90)"/>
      <path d="M-139 0H139M0-139V139" stroke-dasharray="3 8"/>
    </g>'''
        for i in range(28):
            a = i * math.tau / 28
            x, y = 948 + math.cos(a)*139, 241+math.sin(a)*139
            c += f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{3 if i%7==0 else 1.5}" fill="{t["accent"]}" opacity="{1 if i%7==0 else .5}"/>'
        c += f'''<g transform="translate(948 241)">
      <rect x="-38" y="-38" width="76" height="76" rx="20" fill="{t['panel']}" stroke="url(#edge)"/>
      <path d="M-13 8L0-15 13 8M-8 0H8M-16 17H16" stroke="{t['accent']}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
      <circle cx="-111" cy="-82" r="6" fill="{t['accent']}"/>
      <circle cx="119" cy="72" r="6" fill="{t['violet']}"/>
    </g>'''
    c += f'''
    {txt(948,418,'EXPLORE → BUILD → SHARE',12,t['muted'],500,extra='text-anchor="middle" letter-spacing="1.5"')}
    <path d="M56 468H1144" stroke="url(#edge)" stroke-width="2"/>
    '''
    return svg(1200,470,c,'Chao Qin · AI超元域 — Build with AI. Share what works.')


def metrics(t, data):
    total = sum(p['stars'] for p in data['projects'])
    youtube = f"{data['youtube']['minimum_subscribers'] // 1000}K+"
    bilibili = f"{data['bilibili']['followers'] // 1000}K+"
    c = f'<rect x="1" y="1" width="1198" height="156" rx="20" fill="{t["panel"]}" stroke="{t["line"]}"/>'
    for x in [302,602,902]:
        c += f'<path d="M{x} 32V126" stroke="{t["line"]}"/>'
    values = [(f'{total:,}', 'Stars across featured projects'), (youtube, 'YouTube subscribers'), (bilibili, 'Bilibili followers'), (str(len(data['projects'])), 'Featured open-source projects')]
    for i,(number,label) in enumerate(values):
        x = 34 + i*300
        c += txt(x,82,number,45,t['ink'],650,extra='letter-spacing="-1.5"')
        c += txt(x,118,label,15,t['muted'])
        c += f'<circle cx="{x+236}" cy="55" r="4" fill="{t["accent"]}"/>'
    return svg(1200,158,c,f"{total:,} stars across {len(data['projects'])} featured projects · {youtube} YouTube subscribers · {bilibili} Bilibili followers")


def flagship(t, stars):
    c = f'''<rect x="1" y="1" width="1198" height="258" rx="22" fill="{t['bg']}" stroke="{t['line']}"/>
    <rect x="1" y="36" width="4" height="186" rx="2" fill="{t['accent']}"/>
    {txt(40,49,'FLAGSHIP / CREATOR & LEAD MAINTAINER',14,t['accent'],600,extra='letter-spacing="1.8"')}
    {txt(40,114,'memory-lancedb-pro',45,t['ink'],650,extra='letter-spacing="-1.5"')}
    {txt(42,161,'Long-term memory for OpenClaw agents.',23,t['muted'])}
    {txt(43,214,'VECTOR + BM25',13,t['accent'],500,extra='letter-spacing="1"')}
    {txt(237,214,'RERANKING',13,t['muted'],500,extra='letter-spacing="1"')}
    {txt(398,214,'MULTI-SCOPE ISOLATION',13,t['muted'],500,extra='letter-spacing="1"')}
    <g transform="translate(949 135)" fill="none" stroke="{t['line']}" stroke-width="1.5">
      <path d="M-63-53L0 0 68-44M0 0L-63 53M0 0L68 44"/>
      <circle r="24" fill="{t['panel']}" stroke="{t['accent']}"/>
      <circle cx="-63" cy="-53" r="10" fill="{t['panel']}" stroke="{t['accent']}"/>
      <circle cx="-63" cy="53" r="10" fill="{t['panel']}" stroke="{t['violet']}"/>
      <circle cx="68" cy="-44" r="10" fill="{t['panel']}" stroke="{t['violet']}"/>
      <circle cx="68" cy="44" r="10" fill="{t['panel']}" stroke="{t['accent']}"/>
    </g>
    {txt(949,143,'M',20,t['accent'],600,extra='text-anchor="middle"')}
    {txt(1147,48,f'★ {stars:,}',18,t['muted'],500,extra='text-anchor="end"')}
    {txt(1147,222,'EXPLORE PROJECT ↗',13,t['muted'],500,extra='text-anchor="end" letter-spacing="1"')}
    '''
    return svg(1200,260,c,'memory-lancedb-pro — Long-term memory for OpenClaw agents. Creator and lead maintainer: Chao Qin.')


def badge(stars):
    c = f'<rect x=".5" y=".5" width="127" height="27" rx="7" fill="#172A30" stroke="#345057"/>{txt(12,19,"★",14,"#9BE8C4")}{txt(32,19,f"{stars:,} stars",12,"#DFEEE9",500)}'
    return svg(128,28,c,f'{stars:,} GitHub stars')


def button(label, kind):
    icons = {
        'youtube':'<rect x="16" y="14" width="24" height="17" rx="5" fill="#FF6477"/><path d="M26 18L33 22.5 26 27Z" fill="#0D171D"/>',
        'bilibili':'<g fill="none" stroke="#73D5EC" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10L25 14M34 10L30 14"/><rect x="16" y="14" width="24" height="19" rx="4"/><path d="M22 21L24 23M34 21L32 23M25 28H31"/></g>',
        'x':'<path d="M18 13L35 32H31L14 13ZM33 13H36L17 32H14Z" fill="#E5F2ED"/>',
        'blog':'<circle cx="27" cy="22.5" r="10" stroke="#9BE8C4" fill="none"/><ellipse cx="27" cy="22.5" rx="4" ry="10" stroke="#9BE8C4" fill="none"/><path d="M17 22.5H37" stroke="#9BE8C4"/>',
    }
    c=f'<rect x=".5" y=".5" width="169" height="45" rx="10" fill="#13232B" stroke="#345057"/>{icons[kind]}{txt(52,28,label,15,"#E5F2ED",600)}'
    return svg(170,46,c,label)


def versioned_asset(stem):
    digest = hashlib.sha256((ASSETS/f'{stem}.svg').read_bytes()).hexdigest()[:12]
    return f'{stem}-{digest}.svg'


def picture(name, alt, width="100%"):
    reduced_source = (f'  <source media="(prefers-reduced-motion: reduce) and (prefers-color-scheme: dark)" srcset="./assets/{versioned_asset("hero-dark-static")}">\n' if name == 'hero' else '')
    dark_source = (f'./assets/{versioned_asset(name+"-dark")}' if name in ['hero','metrics'] else f'./assets/{name}-dark.svg')
    light_source = (f'./assets/{versioned_asset("metrics-light")}' if name == 'metrics' else f'./assets/{name}-light.svg')
    return f'''<picture>
{reduced_source}  <source media="(prefers-color-scheme: dark)" srcset="{dark_source}">
  <source media="(prefers-color-scheme: light)" srcset="{light_source}">
  <img src="{light_source}" alt="{html.escape(alt,quote=True)}" width="{width}">
</picture>'''


def readme(data):
    stars = {p['repo']:p['stars'] for p in data['projects']}
    youtube = f"{data['youtube']['minimum_subscribers'] // 1000}K+"
    bilibili = f"{data['bilibili']['followers'] // 1000}K+"
    cards = [
      ('AISuperDomain','MULTI-MODEL WORKSPACE','Ask once. Compare answers from multiple AI models in one desktop workspace.',''),
      ('ClawTeam-OpenClaw','MULTI-AGENT COORDINATION','Bring CLI coding agents together with OpenClaw as the default agent.','OpenClaw adaptation of <a href="https://github.com/HKUDS/ClawTeam">HKUDS/ClawTeam</a>.'),
      ('cc-notebook','CLAUDE CODE FIELD NOTES','Explore notes on context, memory, model switching and multi-agent architecture.',''),
      ('GraphRAG4OpenWebUI','KNOWLEDGE & RETRIEVAL','Connect Microsoft GraphRAG to Open WebUI with local, global and web search.',''),
      ('openclaw-a2a-gateway','AGENT INTEROPERABILITY','Let OpenClaw agents discover and communicate with each other across servers.',''),
      ('OpenClaw-Skill','REUSABLE AGENT SKILL','Install, configure, operate and troubleshoot OpenClaw with an AI coding assistant.',''),
    ]
    rows=[]
    display_names = {
      'AISuperDomain': 'AISuper&#8203;Domain',
      'ClawTeam-OpenClaw': 'ClawTeam-&#8203;OpenClaw',
      'cc-notebook': 'cc-&#8203;notebook',
      'GraphRAG4OpenWebUI': 'GraphRAG4&#8203;OpenWebUI',
      'openclaw-a2a-gateway': 'openclaw-&#8203;a2a-&#8203;gateway',
      'OpenClaw-Skill': 'OpenClaw-&#8203;Skill',
    }
    for i in range(0,len(cards),2):
        cells=[]
        for name,category,desc,note in cards[i:i+2]:
            n=stars['win4r/'+name]
            cells.append(f'''<td width="50%" valign="top">
<sub>{category}</sub>
<h3><a href="https://github.com/win4r/{name}">{display_names[name]}</a></h3>
<p>{desc}</p>
<a href="https://github.com/win4r/{name}/stargazers"><img src="./assets/stars-{name.lower()}.svg" alt="{n:,} GitHub stars" height="24"></a>
{'<p><sub>'+note+'</sub></p>' if note else ''}
</td>''')
        rows.append('<tr>\n'+'\n'.join(cells)+'\n</tr>')
    return f'''<!-- Generated by scripts/render_profile.py. Edit the source, then render. -->
{picture('hero','Chao Qin · AI超元域 — Build with AI. Share what works.')}

<p align="center">
  <b>AI builder, open-source maintainer & creator of AI超元域.</b><br>
  I build agent tools, test AI in real projects, and share the process.<br>
  <sub>AI 技术 · 开源项目 · 实践笔记</sub>
</p>

<p align="center">
  <a href="https://www.youtube.com/@AIsuperdomain"><img src="./assets/youtube.svg" alt="Watch AI超元域 on YouTube" width="138"></a>
  <a href="https://space.bilibili.com/3493277319825652"><img src="./assets/bilibili.svg" alt="Watch AI超元域 on Bilibili" width="138"></a>
  <a href="https://x.com/AISuperDomain"><img src="./assets/x.svg" alt="Follow @AISuperDomain on X" width="138"></a>
  <a href="https://www.aivi.fyi/"><img src="./assets/blog.svg" alt="Read AI超元域's technical blog" width="138"></a>
</p>

{picture('metrics',f"{sum(stars.values()):,} GitHub stars across {len(data['projects'])} featured projects · {youtube} YouTube subscribers · {bilibili} Bilibili followers")}

<p align="center">
  <a href="#selected-open-source">Projects</a> &nbsp; / &nbsp;
  <a href="#watch--build">Watch & build</a> &nbsp; / &nbsp;
  <a href="#currently-exploring">Exploring</a> &nbsp; / &nbsp;
  <a href="https://www.aivi.fyi/">Writing ↗</a>
</p>

## Selected open source

<a href="https://github.com/CortexReach/memory-lancedb-pro">
{picture('flagship','memory-lancedb-pro — Long-term memory for OpenClaw agents. Creator & lead maintainer: Chao Qin.')}
</a>

**Give agents memory that carries across sessions.** I created and lead-maintain [memory-lancedb-pro](https://github.com/CortexReach/memory-lancedb-pro): hybrid vector + BM25 retrieval, cross-encoder reranking, and memory isolation across agents, users and projects. [Watch the walkthrough ↗](https://youtu.be/bhuGrjuCM_g)

<table>
{chr(10).join(rows)}
</table>

<sub>**Contributing upstream:** CJK token estimation and CJK trigram search from [lossless-claw-enhanced](https://github.com/win4r/lossless-claw-enhanced) were merged into [lossless-claw](https://github.com/Martian-Engineering/lossless-claw). The original fork is retired; use upstream for new installs.</sub>

## Watch & build

Hands-on AI tests, agent workflows and tutorials — with the projects and implementation details to explore for yourself.

<table>
<tr>
<td width="50%" valign="top">
<a href="https://youtu.be/bhuGrjuCM_g"><img src="https://i.ytimg.com/vi/bhuGrjuCM_g/hqdefault.jpg" alt="memory-lancedb-pro video tutorial on AI超元域" width="480"></a>
<p><b><a href="https://youtu.be/bhuGrjuCM_g">Give your agent long-term memory ↗</a></b></p>
<sub>From installation to hybrid retrieval.</sub>
</td>
<td width="50%" valign="top">
<a href="https://youtu.be/aZT9d8qrirY"><img src="https://i.ytimg.com/vi/aZT9d8qrirY/hqdefault.jpg" alt="ClawTeam-OpenClaw video tutorial on AI超元域" width="480"></a>
<p><b><a href="https://youtu.be/aZT9d8qrirY">Build with a team of agents ↗</a></b></p>
<sub>Explore ClawTeam and OpenClaw in practice.</sub>
</td>
</tr>
</table>

**More from the lab:** [Unlimited-OCR-2 deployment & document tests](https://youtu.be/W7lSIikNJBI) · [YouTube videos](https://www.youtube.com/@AIsuperdomain/videos) · [Bilibili videos](https://space.bilibili.com/3493277319825652) · [Technical articles](https://www.aivi.fyi/)

## Currently exploring

- **Agent systems** — long-term memory, multi-agent coordination and interoperability.
- **AI coding** — Claude Code, Codex, context engineering and reusable workflows.
- **Applied AI** — RAG, model fine-tuning, multimodal tools and local deployment.

<br>

<p align="center">
  <b>Build something useful. Share what you learn.</b><br>
  <sub>Find me on <a href="https://www.youtube.com/@AIsuperdomain">YouTube</a>, <a href="https://space.bilibili.com/3493277319825652">Bilibili</a>, <a href="https://x.com/AISuperDomain">X</a> or <a href="https://www.aivi.fyi/">the blog</a> · Away from the keyboard: archery.</sub>
</p>

<!-- GitHub stars refreshed {data['github_verified_on']}. YouTube {youtube} is a manually verified lower bound as of {data['youtube']['verified_on']}; it is not a live subscriber counter. Bilibili {data['bilibili']['followers']:,} (displayed as {bilibili}) was provided by the owner on {data['bilibili']['provided_on']}; it is not a live follower counter. Stars sum only the {len(data['projects'])} featured repositories, including the attributed ClawTeam adaptation. -->
'''


def refresh(data):
    updated = copy.deepcopy(data)
    for p in updated['projects']:
        headers={'Accept':'application/vnd.github+json','User-Agent':'win4r-profile','X-GitHub-Api-Version':'2022-11-28'}
        if os.environ.get('GITHUB_TOKEN'):
            headers['Authorization']='Bearer '+os.environ['GITHUB_TOKEN']
        request=urllib.request.Request('https://api.github.com/repos/'+p['repo'],headers=headers)
        with urllib.request.urlopen(request,timeout=30) as response:
            repo=json.load(response)
        count=repo['stargazers_count']
        if not isinstance(count,int) or count<0 or repo['full_name'].lower()!=p['repo'].lower() or repo.get('private'):
            raise ValueError('Unexpected public repository metadata: '+p['repo'])
        p['stars']=count
    updated['github_verified_on']=dt.datetime.now(dt.timezone.utc).date().isoformat()
    return updated


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh',action='store_true',help='Fetch current public GitHub star counts before rendering')
    args=parser.parse_args()
    config=ROOT/'profile.json'
    data=json.loads(config.read_text())
    if args.refresh:
        data=refresh(data)  # Complete all requests before changing any files.
        config.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
    ASSETS.mkdir(exist_ok=True)
    for name,t in THEMES.items():
        for filename,content in [('hero',hero(t, animated=name=='dark')),('metrics',metrics(t,data)),('flagship',flagship(t,data['projects'][0]['stars']))]:
            (ASSETS/f'{filename}-{name}.svg').write_text(content)
    (ASSETS/'hero-dark-static.svg').write_text(hero(THEMES['dark'], animated=True, reduced=True))
    for stem in ['hero-dark', 'hero-dark-static', 'metrics-dark', 'metrics-light']:
        (ASSETS/versioned_asset(stem)).write_bytes((ASSETS/f'{stem}.svg').read_bytes())
    for p in data['projects']:
        (ASSETS/f"stars-{p['repo'].split('/')[1].lower()}.svg").write_text(badge(p['stars']))
    for kind,label in [('youtube','YouTube'),('bilibili','Bilibili'),('x','Follow on X'),('blog','Read the blog')]:
        (ASSETS/f'{kind}.svg').write_text(button(label,kind))
    (ROOT/'README.md').write_text(readme(data))
    print(f"Rendered profile with {sum(p['stars'] for p in data['projects']):,} featured-project stars.")


if __name__=='__main__':
    main()

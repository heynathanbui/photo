#!/usr/bin/env python3
"""Builds index.html from template.html and the photo lists below.

Add a photo: drop name.jpg (1800px long edge) and name-sm.jpg (800px) into
assets/img, add a line to the right list, then run:  python3 build.py
Each line is (file name without .jpg, caption, camera settings, filter tag).
Add the name to ROLL as well to put it on the 3D film roll.
"""
import html, json, re, struct
from pathlib import Path

ROOT = Path(__file__).parent
IMG = ROOT / "assets/img"

SCENERY = [
    ("sydney-4407", "Opera House after sunset · Sydney", "f/3.6 · 1/26s · ISO 6400 · 16mm", "sydney"),
    ("ninhbinh-9334", "Pagoda reflected in the pond · Ninh Bình", "f/5.6 · 1/80s · ISO 80 · 22mm", "vietnam"),
    ("hoian-4516", "Lantern shop · Hội An", "f/5.6 · 1/60s · ISO 4000 · 21mm", "vietnam"),
    ("harbour-5341", "Harbour at golden hour · Sydney", "f/4.5 · 1/105s · ISO 320 · 21mm", "sydney"),
    ("sydney-4376", "Office towers · Sydney CBD", "f/5 · 1/125s · ISO 2000 · 16mm", "sydney"),
    ("ninhbinh-9301", "Temple gate · Ninh Bình", "f/5.6 · 1/250s · ISO 200 · 45mm", "vietnam"),
    ("harbour-5284", "Afternoon sun on the water · Sydney", "f/13 · 1/400s · ISO 320 · 45mm", "sydney"),
    ("sydney-4417", "Harbour Bridge at night · Sydney", "f/4.7 · 1/7s · ISO 6400 · 30mm", "sydney"),
    ("elsewhere-4649", "Towers in Lujiazui · Shanghai", "f/4.4 · 1/125s · ISO 200 · 26mm", "abroad"),
    ("hoian-4536", "Old town at night · Hội An", "f/5.6 · 1/60s · ISO 8000 · 45mm", "vietnam"),
    ("harbour-5313", "Harbour Bridge from the rocks · Sydney", "f/13 · 1/120s · ISO 640 · 40mm", "sydney"),
    ("ninhbinh-9316", "Walkway between the cliffs · Ninh Bình", "f/5.6 · 1/80s · ISO 80 · 15mm", "vietnam"),
    ("harbour-5355", "Harbour after sunset · Sydney", "f/4.9 · 1/100s · ISO 2500 · 32mm", "sydney"),
    ("elsewhere-4629", "Skyline · Shanghai", "f/4.5 · 1/180s · ISO 80 · 28mm", "abroad"),
    ("sydney-4412", "City skyline at dusk · Sydney", "f/5.2 · 1/17s · ISO 6400 · 38mm", "sydney"),
    ("ninhbinh-9326", "Temple by the lake · Ninh Bình", "f/5.6 · 1/80s · ISO 80 · 40mm", "vietnam"),
    ("harbour-5287", "Climbing the rocks · Sydney", "f/13 · 1/100s · ISO 320 · 20mm", "sydney"),
    ("hoian-4521", "Lantern stall · Hội An", "f/5.6 · 1/60s · ISO 2000 · 15mm", "vietnam"),
    ("sydney-4251", "Opera House at midday · Sydney", "f/5.6 · 1/250s · ISO 500 · 37mm", "sydney"),
    ("elsewhere-4670", "Canal in a water town · near Shanghai", "f/4.4 · 1/125s · ISO 400 · 24mm", "abroad"),
    ("ninhbinh-9347", "Looking out at the pagoda · Ninh Bình", "f/4.5 · 1/180s · ISO 200 · 15mm", "vietnam"),
    ("harbour-5357", "The city at dusk · Sydney", "f/5.6 · 1/85s · ISO 12800 · 45mm", "sydney"),
    ("sydney-4236", "Harbour Bridge on a clear day · Sydney", "f/5.6 · 1/250s · ISO 500 · 23mm", "sydney"),
    ("ninhbinh-9351", "Temple rooftops · Ninh Bình", "f/4.9 · 1/180s · ISO 400 · 33mm", "vietnam"),
    ("harbour-5334", "Last light on the harbour · Sydney", "f/5.6 · 1/320s · ISO 320 · 26mm", "sydney"),
    ("elsewhere-4745", "Feeding the koi · near Shanghai", "f/5.6 · 1/60s · ISO 1000 · 44mm", "abroad"),
    ("elsewhere-4558", "Tree-lined street · Shanghai", "f/5.6 · 1/60s · ISO 250 · 35mm", "abroad"),
    ("harbour-5286", "The tower at Barangaroo · Sydney", "f/13 · 1/100s · ISO 640 · 22mm", "sydney"),
    ("harbour-5337", "Apartments across the water, late light · Sydney", "f/4.5 · 1/100s · ISO 160 · 28mm", "sydney"),
    ("harbour-5346", "People on the rocks under the bridge · Sydney", "f/4.5 · 1/100s · ISO 320 · 29mm", "sydney"),
]
PEOPLE = [
    ("ivy-5378", "Sitting on the ledge · USyd", "f/7.1 · 1/170s · ISO 320 · 15mm", "concept"),
    ("grad-4198", "Graduation day in áo dài · USyd", "f/18 · 1/125s · ISO 160 · 58mm", "graduation"),
    ("ivy-5413", "On the steps · USyd", "f/5.6 · 1/140s · ISO 1600 · 45mm", "portrait"),
    ("mqgrad-4761", "Graduation portrait · Macquarie", "f/22 · 1/125s · ISO 2000 · 35mm", "graduation"),
    ("ivy-5414", "Chin on hand, close · USyd", "f/5.6 · 1/140s · ISO 2000 · 45mm", "portrait"),
    ("ivy-5450", "On the lawn · USyd", "f/7.1 · 1/150s · ISO 320 · 21mm", "concept"),
    ("grad-4310", "On the bench · USyd graduation", "f/22 · 1/125s · ISO 12800 · 86mm", "graduation"),
    ("ivy-5400", "In the courtyard · USyd", "f/5.6 · 1/125s · ISO 800 · 42mm", "portrait"),
    ("mqgrad-5091", "By the fountain · Macquarie", "f/5.6 · 1/240s · ISO 320 · 42mm", "graduation"),
    ("ivy-5385", "In front of the Quad · USyd", "f/7.1 · 1/150s · ISO 320 · 23mm", "concept"),
    ("grad-4422", "Flowers and sunglasses · USyd graduation", "f/20 · 1/60s · ISO 160 · 55mm", "graduation"),
    ("ivy-5389", "Sitting in the sun · USyd", "f/6.4 · 1/160s · ISO 320 · 23mm", "portrait"),
    ("ivy-5493", "Under the arch · USyd", "f/5.6 · 1/160s · ISO 320 · 16mm", "concept"),
    ("mqgrad-4889", "Celebrating · Macquarie", "f/22 · 1/125s · ISO 1600 · 33mm", "graduation"),
    ("ivy-5420", "By the railing · USyd", "f/5.6 · 1/140s · ISO 800 · 45mm", "portrait"),
    ("grad-4549", "Celebrating · USyd graduation", "f/5.6 · 1/1250s · ISO 320 · 58mm", "graduation"),
    ("ivy-5504", "On the path to the Quad · USyd", "f/6.4 · 1/160s · ISO 320 · 17mm", "concept"),
    ("mqgrad-5123", "The stole, from behind · Macquarie", "f/5.6 · 1/150s · ISO 160 · 30mm", "graduation"),
    ("grad-4232", "In front of the Quad · USyd graduation", "f/22 · 1/125s · ISO 320 · 55mm", "graduation"),
    ("ivy-5426", "By the stair rail · USyd", "f/5.6 · 1/140s · ISO 800 · 45mm", "portrait"),
    ("ivy-5411", "Sitting on the stairs · USyd", "f/5.6 · 1/140s · ISO 2000 · 45mm", "concept"),
    ("grad-4386", "In the Quad · USyd graduation", "f/22 · 1/100s · ISO 400 · 58mm", "graduation"),
    ("ivy-5488", "Arch and tower · USyd", "f/6.4 · 1/150s · ISO 320 · 15mm", "concept"),
    ("mqgrad-4605", "Surrounded by flowers · Macquarie", "f/16 · 1/60s · ISO 320 · 32mm", "graduation"),
    ("grad-4459", "Group photo · USyd graduation", "f/14 · 1/60s · ISO 320 · 58mm", "graduation"),
    ("ivy-5393", "Close-up in the sun · USyd", "f/5.6 · 1/160s · ISO 320 · 29mm", "portrait"),
    ("mqgrad-4985", "Group photo · Macquarie", "f/22 · 1/125s · ISO 3200 · 41mm", "graduation"),
    ("grad-4327", "On the bench · USyd graduation", "f/22 · 1/125s · ISO 12800 · 90mm", "graduation"),
    ("ivy-5425", "On the stairs · USyd", "f/4.5 · 1/110s · ISO 320 · 19mm", "concept"),
    ("ivy-5484", "In the shade · USyd", "f/7.1 · 1/150s · ISO 320 · 15mm", "concept"),
    ("ivy-5521", "By the lamppost · USyd", "f/7.1 · 1/160s · ISO 320 · 18mm", "concept"),
]
EVENTS = [
    ("stage-4156", "Dance performance · Serenade '24", "f/5.6 · 1/250s · ISO 4000 · 45mm", "stage"),
    ("sydneygo-1023", "All the teams · Sydney Go 2026", "f/3.5 · 1/100s · ISO 400 · 15mm", "community"),
    ("daihoi-4066", "Delegates with certificates · Đại hội 2026", "f/3.5 · 1/100s · ISO 2500 · 15mm", "conference"),
    ("events-0320", "Volleyball · UAVS Sports Day 2026", "f/4 · 1/250s · ISO 3200 · 50mm", "sport"),
    ("hack-9590", "Presenting · Hackathon 2026", "f/4.2 · 1/160s · ISO 2000 · 122mm", "conference"),
    ("cultural-8478", "Making rice paper rolls · Cultural Day 2025", "f/4.4 · 1/60s · ISO 1250 · 26mm", "community"),
    ("events-3138", "With the sponsor · Sydney Go 2026", "f/4 · 1/500s · ISO 1250 · 32mm", "community"),
    ("stage-4146", "On stage · Serenade '24", "f/5.6 · 1/250s · ISO 4000 · 45mm", "stage"),
    ("hack-9596", "Taking a break · Hackathon 2026", "f/3.8 · 1/160s · ISO 2000 · 78mm", "conference"),
    ("sydneygo-1087", "Solving a clue · Sydney Go 2026", "f/5.6 · 1/60s · ISO 1000 · 36mm", "community"),
    ("cultural-8460", "Rolling gỏi cuốn · Cultural Day 2025", "f/5.6 · 1/80s · ISO 2500 · 43mm", "community"),
    ("events-0297", "Basketball · UAVS Sports Day 2026", "f/4 · 1/250s · ISO 3200 · 50mm", "sport"),
    ("daihoi-4020", "Group photo · Đại hội 2026", "f/4.2 · 1/40s · ISO 3200 · 22mm", "conference"),
    ("stage-4166", "The finale · Serenade '24", "f/5.2 · 1/250s · ISO 4000 · 38mm", "stage"),
    ("events-3155", "Everyone at the end · Sydney Go 2026", "f/7.1 · 1/125s · ISO 1250 · 18mm", "community"),
    ("hack-9616", "A team at their table · Hackathon 2026", "f/3.5 · 1/250s · ISO 1250 · 55mm", "conference"),
    ("cultural-8315", "The ingredients · Cultural Day 2025", "f/5 · 1/160s · ISO 2500 · 35mm", "community"),
    ("sydneygo-1041", "Reading the clue · Sydney Go 2026", "f/5.6 · 1/60s · ISO 800 · 33mm", "community"),
    ("daihoi-4090", "Award photo · Đại hội 2026", "f/3.8 · 1/100s · ISO 5000 · 17mm", "conference"),
    ("hack-9578", "Working · Hackathon 2026", "f/3.5 · 1/160s · ISO 1600 · 55mm", "conference"),
    ("events-3059", "Building the challenge · Sydney Go 2026", "f/3.6 · 1/250s · ISO 500 · 18mm", "community"),
    ("cultural-8403", "Rolling · Cultural Day 2025", "f/5.6 · 1/60s · ISO 1600 · 45mm", "community"),
    ("sydneygo-1005", "Mid-challenge · Sydney Go 2026", "f/4 · 1/240s · ISO 640 · 19mm", "community"),
    ("daihoi-4035", "Group photo on stage · Đại hội 2026", "f/3.5 · 1/100s · ISO 4000 · 15mm", "conference"),
    ("events-2428", "Team photo · Sydney Go 2026", "f/4 · 1/320s · ISO 640 · 27mm", "community"),
    ("events-3062", "Hands-on challenge · Sydney Go 2026", "f/3.6 · 1/250s · ISO 1000 · 18mm", "community"),
]

# 24 frames for the 3D film roll, in order
ROLL = [
    "sydney-4407", "hoian-4516", "ivy-5413", "stage-4156", "ninhbinh-9334", "grad-4198",
    "sydney-4417", "ivy-5493", "harbour-5341", "mqgrad-5091", "hoian-4536", "ivy-5504",
    "stage-4146", "ninhbinh-9301", "ivy-5378", "sydney-4376", "mqgrad-4761", "harbour-5355",
    "events-0320", "ninhbinh-9347", "ivy-5450", "elsewhere-4649", "hoian-4521", "harbour-5313",
]
# behind the lens aperture in the hero
HERO = ["sydney-4407", "ivy-5413", "stage-4156", "ninhbinh-9334", "grad-4198", "hoian-4516"]

FILTERS = {
    "SCENERY": [("all", "All"), ("sydney", "Sydney"), ("vietnam", "Vietnam"), ("abroad", "Shanghai")],
    "PEOPLE": [("all", "All"), ("portrait", "Portraits"), ("graduation", "Graduation"), ("concept", "Concepts")],
    "EVENTS": [("all", "All"), ("community", "Community"), ("stage", "Stage"), ("conference", "Conferences"), ("sport", "Sport")],
}

# Albums: each one gets its own page at albums/<slug>/ with its own look ("theme").
# title uses *stars* for the italic part. "times" (optional) labels each photo, in order.
ALBUMS = [
    dict(slug="harbour", cover="harbour-5313", kind="SCENERY", theme="horizon", title="The harbour, *one evening*",
         where="Sydney Harbour", when="Sunday 11 October 2026", accent="#e2a85a",
         intro="I went for a walk around the harbour and kept shooting for about an hour, from just after six until the sun went down. They're in the order I took them, so you can watch the light change as you scroll.",
         photos=["harbour-5284", "harbour-5286", "harbour-5287", "harbour-5313", "harbour-5334", "harbour-5337", "harbour-5341", "harbour-5346", "harbour-5355", "harbour-5357"],
         times=["6:09 pm", "6:10 pm", "6:10 pm", "6:32 pm", "6:46 pm", "6:47 pm", "6:48 pm", "6:49 pm", "7:04 pm", "7:06 pm"]),
    dict(slug="sydney", cover="sydney-4407", kind="SCENERY", theme="skyline", title="Around *the city*",
         where="Sydney CBD", when="2024", accent="#e2c77a",
         intro="Walking around the city in 2024. The Opera House and the bridge at midday, then the same area again once it got dark.",
         photos=["sydney-4236", "sydney-4251", "sydney-4376", "sydney-4412", "sydney-4407", "sydney-4417"]),
    dict(slug="ninh-binh", cover="ninhbinh-9334", kind="SCENERY", theme="ink", title="Ninh *Bình*",
         where="Ninh Bình, Vietnam", when="July 2026", accent="#3f5b4b",
         intro="A trip with friends in July. Temples, a pagoda sitting on the pond, and the walkway between the limestone cliffs.",
         photos=["ninhbinh-9301", "ninhbinh-9316", "ninhbinh-9326", "ninhbinh-9334", "ninhbinh-9347", "ninhbinh-9351"]),
    dict(slug="hoi-an", kind="SCENERY", theme="lantern", title="Hội An *after dark*",
         where="Hội An, Vietnam", when="July 2025", accent="#e8742c",
         intro="The old town at night, once the lanterns are on. Everything here was shot handheld at ISO 2000 to 8000.",
         photos=["hoian-4516", "hoian-4521", "hoian-4536"]),
    dict(slug="shanghai", kind="SCENERY", theme="blinds", title="*Shanghai*",
         where="Shanghai & a water town nearby", when="July 2025", accent="#b3262d",
         intro="The towers in Lujiazui, a quiet tree-lined street, and one of the old water towns outside the city.",
         photos=["elsewhere-4649", "elsewhere-4629", "elsewhere-4558", "elsewhere-4670", "elsewhere-4745"]),
    dict(slug="usyd-portraits", cover="ivy-5413", kind="PEOPLE", theme="contact", title="Portraits *at USyd*",
         where="University of Sydney", when="2026", accent="#7d5ba6",
         intro="A styled portrait session around the Quad: the arches, the stairs, the lawn and a lot of afternoon sun. These are my own colour edits.",
         photos=["ivy-5378", "ivy-5385", "ivy-5389", "ivy-5393", "ivy-5400", "ivy-5411", "ivy-5413", "ivy-5414", "ivy-5420", "ivy-5425", "ivy-5426", "ivy-5450", "ivy-5484", "ivy-5488", "ivy-5493", "ivy-5504", "ivy-5521"]),
    dict(slug="usyd-graduation", kind="PEOPLE", theme="arches", title="Graduation *at USyd*",
         where="University of Sydney", when="2026", accent="#b48a3c",
         intro="Grad day at USyd, in gowns and áo dài. The Quad, the flowers, the bench, and the group photo at the end.",
         photos=["grad-4198", "grad-4232", "grad-4310", "grad-4327", "grad-4386", "grad-4422", "grad-4459", "grad-4549"]),
    dict(slug="macquarie-graduation", cover="mqgrad-4761", kind="PEOPLE", theme="album", title="Graduation *at Macquarie*",
         where="Macquarie University", when="October 2026", accent="#c9a43f",
         intro="A grad shoot at Macquarie. The fountain, a lot of flowers, and the group photos with everyone who came.",
         photos=["mqgrad-4605", "mqgrad-4761", "mqgrad-4889", "mqgrad-4985", "mqgrad-5091", "mqgrad-5123"]),
    dict(slug="sydney-go", cover="sydneygo-1023", kind="EVENTS", theme="route", title="Sydney Go *2026*",
         where="UAVS · around Sydney", when="2026", accent="#6b1f24",
         intro="UAVS's day of clues and challenges around the city. I followed the teams from the first clue to the group photo at the end.",
         photos=["sydneygo-1005", "sydneygo-1023", "sydneygo-1041", "sydneygo-1087", "events-2428", "events-3059", "events-3062", "events-3138", "events-3155"]),
    dict(slug="hackathon", cover="hack-9590", kind="EVENTS", theme="terminal", title="Hackathon *2026*",
         where="Sydney", when="2026", accent="#e2c77a",
         intro="Teams at their tables, a few breaks, and the presentations, which I shot from the back on a long lens.",
         photos=["hack-9578", "hack-9616", "hack-9596", "hack-9590"]),
    dict(slug="dai-hoi", kind="EVENTS", theme="curtain", title="Đại hội *2026*",
         where="Delegates' congress", when="2026", accent="#c9a43f",
         intro="Our delegates' congress. Certificates and awards on stage, and the group photos once it was all done.",
         photos=["daihoi-4066", "daihoi-4090", "daihoi-4035", "daihoi-4020"]),
    dict(slug="cultural-day", cover="cultural-8460", kind="EVENTS", theme="ricepaper", title="Cultural Day *2025*",
         where="Sydney", when="2025", accent="#6f8f3a",
         intro="Making rice paper rolls at Cultural Day. Here it is step by step, from the ingredients to the finished roll.",
         photos=["cultural-8315", "cultural-8460", "cultural-8403", "cultural-8478"]),
    dict(slug="serenade", cover="stage-4156", kind="EVENTS", theme="spotlight", title="Serenade *'24*",
         where="Stage show", when="2024", accent="#e2c77a",
         intro="A stage show with dance performances, shot at ISO 4000 under the stage lights. Move your mouse to light up the stage.",
         photos=["stage-4146", "stage-4156", "stage-4166"]),
]
KIND_LABEL = {"SCENERY": ("Landscape", "landscape"), "PEOPLE": ("Portrait", "portrait"), "EVENTS": ("Events", "events")}


def jpeg_size(path):
    """Width and height from a JPEG's SOF marker (no Pillow needed)."""
    with open(path, "rb") as f:
        f.read(2)
        while True:
            marker, length = struct.unpack(">2sH", f.read(4))
            if marker[1] in (0xC0, 0xC1, 0xC2):
                h, w = struct.unpack(">xHH", f.read(5))
                return w, h
            f.seek(length - 2, 1)


ALL = {p[0]: p for p in SCENERY + PEOPLE + EVENTS}
counter = iter(range(1, len(ALL) + 1))


def figure(name, cap, exif, tag):
    w, h = jpeg_size(IMG / f"{name}.jpg")
    cls = "ph ph--land" if w > h else "ph"
    cap, exif = html.escape(cap), html.escape(exif)
    alt = cap.split(" · ")[0]
    n = next(counter)
    return f"""          <figure class="{cls}" data-tag="{tag}" data-n="{n:03d}">
            <a href="assets/img/{name}.jpg" data-cap="{cap}" data-exif="{exif}"><img src="assets/img/{name}-sm.jpg" srcset="assets/img/{name}-sm.jpg 800w, assets/img/{name}.jpg 1800w" sizes="(max-width: 700px) 50vw, 33vw" width="{w}" height="{h}" alt="{alt}" loading="lazy" decoding="async"></a>
            <figcaption>{alt}</figcaption>
          </figure>"""


def chips(key):
    return "\n".join(
        f'            <button class="chip{" is-on" if v == "all" else ""}" data-filter="{v}" aria-pressed="{str(v == "all").lower()}">{label}</button>'
        for v, label in FILTERS[key])


def frames(names):
    out = []
    for n in names:
        _, cap, exif, _ = ALL[n]
        w, h = jpeg_size(IMG / f"{n}-sm.jpg")
        out.append({"src": f"assets/img/{n}-sm.jpg", "full": f"assets/img/{n}.jpg", "cap": cap, "exif": exif, "w": w, "h": h})
    return out


# ---------- album pages ----------
def stars(t):
    return re.sub(r"\*(.+?)\*", r"<em>\1</em>", html.escape(t))


def plain(t):
    return t.replace("*", "")


def album_card(a, i):
    cover = a.get("cover", a["photos"][0])
    thumbs = [f"assets/img/{n}-sm.jpg" for n in [cover] + [p for p in a["photos"] if p != cover]]
    return f"""          <a class="acard" href="albums/{a['slug']}/" style="--acc:{a['accent']}" data-thumbs='{json.dumps(thumbs[:6])}'>
            <span class="acard__stack"><img src="{thumbs[2 % len(thumbs)]}" alt="" loading="lazy"><img src="{thumbs[1]}" alt="" loading="lazy"><img class="acard__cover" src="{thumbs[0]}" alt="" loading="lazy"></span>
            <span class="acard__meta"><small>Album {i:02d} · {len(a['photos'])} photos</small><b>{stars(a['title'])}</b><span>{html.escape(a['where'])} · {html.escape(a['when'])}</span></span>
            <span class="acard__go" aria-hidden="true">Open album →</span>
          </a>"""


def album_photo(n, i, time=None):
    _, cap, exif, _ = ALL[n]
    w, h = jpeg_size(IMG / f"{n}.jpg")
    alt = cap.split(" · ")[0]
    t = f' data-time="{time}"' if time else ""
    return f"""      <figure class="ap{' ap--land' if w > h else ''}" data-i="{i:02d}"{t}>
        <a class="ap__a" href="../../assets/img/{n}.jpg" data-cap="{html.escape(cap)}" data-exif="{html.escape(exif)}"><img src="../../assets/img/{n}-sm.jpg" srcset="../../assets/img/{n}-sm.jpg 800w, ../../assets/img/{n}.jpg 1800w" sizes="(max-width: 760px) 100vw, 60vw" width="{w}" height="{h}" alt="{html.escape(alt)}" decoding="async"></a>
        <figcaption><span class="ap__n">{i:02d}</span><b>{html.escape(alt)}</b><small>{html.escape(exif)}</small></figcaption>
      </figure>"""


out = (ROOT / "template.html").read_text()
for key, items in (("SCENERY", SCENERY), ("PEOPLE", PEOPLE), ("EVENTS", EVENTS)):
    out = out.replace(f"{{{{{key}}}}}", "\n".join(figure(*p) for p in items))
    out = out.replace(f"{{{{CHIPS_{key}}}}}", chips(key))
    out = out.replace(f"{{{{N_{key}}}}}", f"{len(items):02d}")
for key in ("SCENERY", "PEOPLE", "EVENTS"):
    out = out.replace(f"{{{{ALBUMS_{key}}}}}", "\n".join(album_card(a, i + 1) for i, a in enumerate(ALBUMS) if a["kind"] == key))
out = out.replace("{{N_ALL}}", f"{len(ALL):03d}")
data = json.dumps({"roll": frames(ROLL), "hero": frames(HERO)}, ensure_ascii=False)
out = out.replace("{{SCENE_DATA}}", data.replace("</", "<\\/"))
assert not re.search(r"\{\{\w+\}\}", out), "unfilled placeholder"
(ROOT / "index.html").write_text(out)
print("index.html built:", len(SCENERY), "scenery,", len(PEOPLE), "people,", len(EVENTS), "events;", len(ROLL), "on the roll")

atpl = (ROOT / "album.html").read_text()
(ROOT / "albums").mkdir(exist_ok=True)
for i, a in enumerate(ALBUMS):
    nxt = ALBUMS[(i + 1) % len(ALBUMS)]
    label, anchor = KIND_LABEL[a["kind"]]
    times = a.get("times") or [None] * len(a["photos"])
    page = atpl
    for k, v in {
        "TITLE": html.escape(plain(a["title"])), "TITLE_HTML": stars(a["title"]), "THEME": a["theme"],
        "ACCENT": a["accent"], "WHERE": html.escape(a["where"]), "WHEN": html.escape(a["when"]),
        "INTRO": html.escape(a["intro"]), "COUNT": str(len(a["photos"])), "KIND": label, "ANCHOR": anchor,
        "NO": f"{i + 1:02d}", "TOTAL": f"{len(ALBUMS):02d}", "SLUG": a["slug"], "COVER": a.get("cover", a["photos"][0]),
        "PHOTOS": "\n".join(album_photo(n, j + 1, t) for j, (n, t) in enumerate(zip(a["photos"], times))),
        "NEXT_SLUG": nxt["slug"], "NEXT_TITLE": stars(nxt["title"]), "NEXT_ACCENT": nxt["accent"],
        "NEXT_COVER": nxt.get("cover", nxt["photos"][0]), "NEXT_META": html.escape(f"{nxt['where']} · {nxt['when']} · {len(nxt['photos'])} photos"),
    }.items():
        page = page.replace("{{" + k + "}}", v)
    assert not re.search(r"\{\{\w+\}\}", page), "unfilled placeholder in album"
    d = ROOT / "albums" / a["slug"]
    d.mkdir(exist_ok=True)
    (d / "index.html").write_text(page)
print(len(ALBUMS), "album pages built")

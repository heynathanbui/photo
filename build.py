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
    ("mcmahons-9550", "By the water, the Bridge behind · McMahons Point", "f/6.3 · 1/160s · ISO 100 · 19mm", "portrait"),
    ("mcmahons-9562", "On the bench in the Henry Lawson shelter · McMahons Point", "f/5.6 · 1/160s · ISO 160 · 50mm", "portrait"),
    ("mcmahons-9565", "Beside the shelter, the Bridge and the Opera House behind · McMahons Point", "f/5.6 · 1/320s · ISO 100 · 50mm", "portrait"),
    ("mcmahons-9585", "Wind in her hair, the Opera House behind · McMahons Point", "f/9 · 1/160s · ISO 100 · 28mm", "portrait"),
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
    ("grad-4282", "With family under the ivy arch · USyd graduation", "f/6.4 · 1/125s · ISO 320 · 55mm", "graduation"),
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
ALBUMS_RAW = [
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
    dict(slug="usyd-graduation", cover="grad-4282", kind="PEOPLE", theme="arches", title="Graduation *at USyd*",
         where="University of Sydney", when="2026", accent="#b48a3c",
         intro="Grad day at USyd, in gowns and áo dài. The Quad, the flowers, the bench, and the group photo at the end.",
         photos=["grad-4282", "grad-4198", "grad-4232", "grad-4310", "grad-4327", "grad-4386", "grad-4422", "grad-4459", "grad-4549"]),
    dict(slug="macquarie-graduation", cover="mqgrad-4761", kind="PEOPLE", theme="album", title="Graduation *at Macquarie*",
         where="Macquarie University", when="October 2026", accent="#c9a43f",
         intro="A grad shoot at Macquarie. The fountain, a lot of flowers, and the group photos with everyone who came.",
         photos=["mqgrad-4605", "mqgrad-4761", "mqgrad-4889", "mqgrad-4985", "mqgrad-5091", "mqgrad-5123"]),
    dict(slug="mcmahons-point", cover="mcmahons-9550", kind="PEOPLE", theme="postcard", title="Portraits *at McMahons Point*",
         where="McMahons Point, North Sydney", when="November 2026", accent="#b5523a", camera="Sony a6400",
         intro="An afternoon portrait shoot at McMahons Point: the Harbour Bridge, the Opera House across the water, and the old Henry Lawson shelter by the wharf.",
         photos=["mcmahons-9550", "mcmahons-9562", "mcmahons-9565", "mcmahons-9585"]),
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
ALBUMS = [a for k in ("PEOPLE", "SCENERY", "EVENTS") for a in ALBUMS_RAW if a["kind"] == k]
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


# ---------- place stamps: my own line drawings of each uni's / place's landmark (not official logos) ----------
_WAVES = '<path d="M6 54q4-3 8 0t8 0t8 0t8 0t8 0t8 0t8 0"/>'
MARK_ART = {
    # USyd: the Quadrangle gate tower (twin turrets, flag, Gothic window, arched gateway)
    "quad": '<path d="M15 31V16h9v15M40 31V16h9v15M14 16h11M39 16h11M15 16l4.5-10L24 16M40 16l4.5-10L49 16M19.5 6V2.5M18.2 3.8h2.6M44.5 6V2.5M43.2 3.8h2.6M24 31l8-9 8 9M32 22v-7l4.5 1.6-4.5 1.6M30.5 26.5v3M33.5 26.5v3M13 31h38v27H13zM25 46v-6a7 7 0 0 1 14 0v6zM29.7 46v-9.5M34.3 46v-9.5M25 42h14M27 58v-6a5 5 0 0 1 10 0v6M2 58V40h11M51 40h11v18M2 40v-2.5h2.5V40h2.5v-2.5h2.5V40M54.5 40v-2.5h2.5V40h2.5v-2.5h2.5V40M8 40v-8h3v8M53 40v-8h3v8M5.5 53v-5a1.5 1.5 0 0 1 3 0v5M55.5 53v-5a1.5 1.5 0 0 1 3 0v5M1 58h62"/>',
    # Macquarie: simplified shield, lighthouse and seven-point star (from the university's logo, at the user's request)
    "mq": '<path class="pstamp__fill" d="M13 5h38v28c0 13-8 21-19 27-11-6-19-14-19-27z"/><path d="M13 5h38v28c0 13-8 21-19 27-11-6-19-14-19-27zM13 5l20 18L51 5M33 23l18 13"/><path d="M19.5 55l2.6-20h7.8L32.5 55M18.5 35h15M19.5 35v-3h13v3M22.5 32v-7h7v7M22.5 25l7 7M29.5 25l-7 7M22.5 25q3.5-4.5 7 0M26 21v-2.2M24.6 55v-4a1.4 1.4 0 0 1 2.8 0v4"/><path class="pstamp__solid" d="M44.50 16.00L45.45 19.02L48.41 17.88L46.64 20.51L49.37 22.11L46.22 22.37L46.67 25.50L44.50 23.20L42.33 25.50L42.78 22.37L39.63 22.11L42.36 20.51L40.59 17.88L43.55 19.02Z"/>',
    # harbour: the bridge arch, deck and pylons
    "bridge": '<path d="M7 42Q32 6 57 42M11 42Q32 16 53 42M2 42h60M4 42V29h6v13M54 42V29h6v13M18 42V27M25 42V21M32 42V18M39 42V21M46 42V27"/>' + _WAVES,
    # city: the Opera House sails
    "sails": '<path d="M9 44q4-20 16-26-3 14-1 26M21 44q6-24 21-28-5 16-3 28M36 44q8-19 21-20-5 11-3 20M4 44h56v4H4z"/>' + _WAVES,
    # Ninh Binh: limestone peaks over the river, a rowing boat
    "karst": '<path d="M2 44q5-28 11-14 3-16 9-4 4-12 8 2 5-22 12-6 4-8 8 4 4-10 12 18M24 50q8 4 16 0l-2-2H26zM34 48l4-9"/><path d="M6 56q4-3 8 0t8 0M42 56q4-3 8 0t8 0"/>',
    # Hoi An: a silk lantern
    "lantern": '<path d="M32 3v7M26 10h12M26 12q-9 17 0 34h12q9-17 0-34zM32 12v34M29 12q-5 17 0 34M35 12q5 17 0 34M27 46h10v3H27zM32 49v9M29.5 58h5"/>',
    # Shanghai: the Oriental Pearl Tower among the towers of Lujiazui
    "pearl": '<circle cx="32" cy="40" r="7"/><circle cx="32" cy="20" r="4.5"/><circle cx="32" cy="9" r="2"/><path d="M32 7V1M30 33v-8.6M34 33v-8.6M31 15.6V11M33 15.6V11M26 58l3-12M38 58l-3-12M32 58V47M8 58h48M12 58V34h6v24M46 58V28h6v24M41 58V40h4v18"/>',
}
MARKS = {
    "usyd-portraits": ("quad", "THE UNIVERSITY OF SYDNEY · THE QUADRANGLE ·"),
    "usyd-graduation": ("quad", "THE UNIVERSITY OF SYDNEY · GRADUATION ·"),
    "macquarie-graduation": ("mq", "MACQUARIE UNIVERSITY · GRADUATION ·"),
    "harbour": ("bridge", "SYDNEY HARBOUR · 11 OCTOBER 2026 ·"),
    "mcmahons-point": ("bridge", "McMAHONS POINT · NORTH SYDNEY · 2026 ·"),
    "sydney": ("sails", "SYDNEY · OPERA HOUSE · THE CITY ·"),
    "ninh-binh": ("karst", "NINH BÌNH · VIỆT NAM · JULY 2026 ·"),
    "hoi-an": ("lantern", "HỘI AN · VIỆT NAM · OLD TOWN ·"),
    "shanghai": ("pearl", "上海 · SHANGHAI · LUJIAZUI ·"),
}


def seal(slug, cls="pstamp"):
    if slug not in MARKS:
        return ""
    art, ring = MARKS[slug]
    rid = f"ring-{slug}"
    return (f'<svg class="{cls}" viewBox="0 0 120 120" aria-hidden="true" focusable="false">'
            f'<defs><path id="{rid}" d="M60 60m-46 0a46 46 0 1 1 92 0a46 46 0 1 1-92 0"/></defs>'
            f'<circle class="pstamp__bg" cx="60" cy="60" r="58"/><circle class="pstamp__o" cx="60" cy="60" r="56"/><circle class="pstamp__i" cx="60" cy="60" r="37"/>'
            f'<g class="pstamp__spin"><text class="pstamp__t"><textPath href="#{rid}" textLength="286" lengthAdjust="spacing">{html.escape(ring)}</textPath></text></g>'
            f'<g class="pstamp__m" transform="translate(34 34) scale(.8125)">{MARK_ART[art]}</g></svg>')


# small print on each card frame: film edge code (landscape) / slide mount label (events)
FRAME_LEFT = {"SCENERY": "NB 400", "PEOPLE": "NB 160", "EVENTS": "NB 800"}



# ---------- floating grad + Sydney line drawings behind the graduation albums ----------
FLOAT_ART = {
    "cap": '<path d="M32 14 60 25 32 36 4 25Z"/><path d="M16 30v12c0 7 32 7 32 0V30"/><path d="M32 25l20 5v14"/><path d="M52 44l-2.5 9h5z"/>',
    "diploma": '<path d="M10 26h40a6 6 0 0 1 0 12H10a6 6 0 0 1 0-12Z"/><path d="M10 26a6 6 0 0 0 0 12"/><path d="M30 26v12M34 26v12"/><path d="M32 38l-6 13M32 38l6 13"/>',
    "bridge": '<path d="M2 44h60"/><path d="M10 54V35h7v19M47 54V35h7v19"/><path d="M17 52Q32 10 47 52"/><path d="M19 52Q32 22 45 52"/><path d="M24 44v-9M28 44v-13M32 44v-14M36 44v-13M40 44v-9"/><path d="M2 58h60" opacity=".5"/>',
    "sails": '<path d="M4 48h56"/><path d="M10 48c2-14 10-24 22-28-4 10-6 20-4 28"/><path d="M24 48c4-12 12-18 22-20-3 8-4 14-3 20"/><path d="M38 48c3-7 8-10 16-11-2 5-2 8-2 11"/><path d="M8 54h48" opacity=".5"/>',
    "laurel": '<path d="M22 58C16 42 20 24 36 8"/><path d="M20 48c-8-1-11-7-10-12 7 1 10 7 10 12Z"/><path d="M19 38c-7-3-8-9-6-13 6 2 8 8 6 13Z"/><path d="M22 28c-5-4-5-10-2-13 5 3 5 9 2 13Z"/><path d="M21 48c6-5 13-5 16-2-5 5-11 5-16 2Z"/><path d="M22 37c6-5 12-6 15-3-4 5-10 6-15 3Z"/><path d="M26 26c5-5 11-6 14-4-3 5-9 7-14 4Z"/>',
    "gumleaf": '<path d="M14 54C10 34 26 14 52 8c-2 22-16 40-38 46Z"/><path d="M14 54C26 40 38 26 52 8"/><path d="M10 59l4-5"/>',
    "blossom": '<circle cx="32" cy="32" r="4"/>' + "".join(f'<ellipse cx="32" cy="19" rx="6" ry="11" transform="rotate({r} 32 32)"/>' for r in (0, 72, 144, 216, 288)),
    "quad": '<path d="M4 58h56"/><path d="M22 58V24h20v34"/><path d="M22 24V14l3-6 3 6v10M36 24V14l3-6 3 6v10"/><path d="M28 24v-5h8v5"/><path d="M28 58V49a4 4 0 0 1 8 0v9"/><path d="M29 39v-6a3 3 0 0 1 6 0v6Z"/><path d="M8 58V40h14M42 40h14v18"/><path d="M8 40v-3h3v3M14 40v-3h3v3M45 40v-3h3v3M51 40v-3h3v3"/>',
    "lighthouse": '<path d="M26 56l2-34h8l2 34Z"/><path d="M26 22h12M28 22v-6h8v6M30 16l2-5 2 5"/><path d="M27 41h10M27.6 31h8.8"/><path d="M18 56h28"/><path d="M38 17l16-6M38 20l16 6" opacity=".6"/>',
    "tassel": '<path d="M32 4v28"/><circle cx="32" cy="35" r="3.5"/><path d="M28.5 38l-4 20h15l-4-20"/><path d="M29 44v13M32 44v14M35 44v13"/>',
    "bouquet": '<path d="M21 33l11 27 11-27Z"/><path d="M26 47h12"/><circle cx="23" cy="25" r="7"/><circle cx="41" cy="25" r="7"/><circle cx="32" cy="17" r="7"/><circle cx="32" cy="30" r="5"/>',
    "star": '<path d="M32.0,10.0 L35.9,23.9 L49.2,18.3 L40.8,30.0 L53.4,36.9 L39.0,37.6 L41.5,51.8 L32.0,41.0 L22.5,51.8 L25.0,37.6 L10.6,36.9 L23.2,30.0 L14.8,18.3 L28.1,23.9Z"/>',
}
FLOAT_POOLS = {
    "home-portrait": ["cap", "diploma", "tassel", "laurel", "blossom", "bouquet", "quad", "cap", "lighthouse", "star", "class", "bridge", "cap", "blossom"],
    "usyd-graduation": ["cap", "quad", "blossom", "diploma", "bridge", "laurel", "tassel", "sails", "cap", "bouquet", "gumleaf", "class", "blossom", "cap"],
    "macquarie-graduation": ["cap", "lighthouse", "star", "diploma", "bridge", "laurel", "tassel", "bouquet", "cap", "gumleaf", "star", "class", "sails", "cap"],
}
# (count of drawings, falling petals or confetti, sparkles, petal colours)
FLOAT_MIX = {
    "home-portrait": (30, 22, 12, ["#9d7fcc", "#b79ad9", "#8466b8"]),
    "usyd-graduation": (34, 26, 14, ["#9d7fcc", "#b79ad9", "#8466b8"]),
    "macquarie-graduation": (34, 26, 14, ["#c8384a", "#e2c77a", "#f6e3cb"]),
}


def floaters(key):
    """grad + Sydney line drawings drifting at different depths; some caps get tossed now and then; petals (or confetti) fall; sparkles twinkle"""
    pool = FLOAT_POOLS.get(key)
    if not pool:
        return ""
    n, n_petal, n_spark, colours = FLOAT_MIX[key]
    seed = sum(map(ord, key))
    rnd = lambda k, lo, hi: lo + (hi - lo) * (((seed * 9301 + k * 49297) % 233280) / 233280)
    out = []
    for k in range(n):
        name = pool[(k * 5 + seed) % len(pool)]
        side = k % 3  # 0 left edge, 1 right edge, 2 anywhere
        x = rnd(k, 0, 14) if side == 0 else rnd(k, 84, 96) if side == 1 else rnd(k, 15, 82)
        y = 1 + 95 * k / n + rnd(k + 50, -2, 2)
        depth = round(rnd(k + 99, .25, 1), 2)
        size = round(46 + 70 * depth)
        cls = f"fl fl--{name}"
        if k % 5 == 2: cls += " fl--acc"
        if name == "cap" and k % 2 == 0: cls += " fl--toss"
        if name == "class":
            art = '<svg viewBox="0 0 132 34"><path d="M6 4h120l-8 13 8 13H6l8-13Z"/><text x="66" y="21.5" text-anchor="middle">CLASS OF 2026</text></svg>'
            size = round(size * 1.9)
        else:
            art = f'<svg viewBox="0 0 64 64">{FLOAT_ART[name]}</svg>'
        out.append(f'<span class="{cls}" style="--x:{x:.1f}%;--y:{y:.1f}%;--s:{size}px;--d:{depth};--t:{rnd(k + 7, 7, 13):.1f}s;--dl:-{rnd(k + 3, 0, 12):.1f}s;--rot:{rnd(k + 11, -18, 18):.0f}deg">{art}</span>')
    for k in range(n_petal):
        out.append(f'<i class="petal" style="--x:{rnd(k + 300, 0, 100):.1f}%;--s:{rnd(k + 301, 9, 17):.0f}px;--t:{rnd(k + 302, 16, 30):.1f}s;--dl:-{rnd(k + 303, 0, 30):.1f}s;--sw:{rnd(k + 304, -70, 70):.0f}px;--c:{colours[k % len(colours)]}"></i>')
    for k in range(n_spark):
        out.append(f'<i class="spark" style="--x:{rnd(k + 500, 2, 98):.1f}%;--y:{rnd(k + 501, 2, 97):.1f}%;--s:{rnd(k + 502, 8, 18):.0f}px;--t:{rnd(k + 503, 2.4, 5):.1f}s;--dl:-{rnd(k + 504, 0, 5):.1f}s"></i>')
    return '<div class="floaters" aria-hidden="true">' + "".join(out) + "</div>"


def side_strips(thumbs, lead):
    """two more frames from the album, cut as their own strips, tucked behind the card; they fan out side to side on hover"""
    picks = (thumbs[3:5] + thumbs[1:3])[:2] if len(thumbs) > 1 else thumbs * 2
    sizes = "(max-width: 900px) 70vw, 34vw" if lead else "(max-width: 900px) 40vw, 24vw"
    out = ""
    for side, src in zip(("l", "r"), picks):
        big = src.replace("-sm.jpg", ".jpg")
        out += f'<span class="acard__side acard__side--{side}" aria-hidden="true"><img src="{src}" srcset="{src} 800w, {big} 1800w" sizes="{sizes}" alt="" loading="lazy" decoding="async"></span>'
    return out


UNI = {  # each uni's own gradient for the mat behind its film strip
    "usyd": "linear-gradient(155deg, #f4cf96 0%, #dd9a6e 40%, #9a7bc6 100%)",      # sandstone to jacaranda
    "mq": "linear-gradient(155deg, #f5e7d4 0%, #de8676 42%, #8f1d2c 100%)",        # sand to Macquarie red
    "harbour": "linear-gradient(155deg, #f6dba4 0%, #e2925f 40%, #3d6f9f 100%)",   # afternoon sun to harbour blue
}
UNI_OF = {"usyd-portraits": "usyd", "usyd-graduation": "usyd", "macquarie-graduation": "mq", "mcmahons-point": "harbour"}


def album_card(a, i, lead=False):
    cover = a.get("cover", a["photos"][0])
    thumbs = [f"assets/img/{n}-sm.jpg" for n in [cover] + [p for p in a["photos"] if p != cover]]
    exif = html.escape(ALL[cover][2])
    n = list(ALL).index(cover) + 1
    cls = "acard acard--lead" if lead else "acard"
    return f"""          <a class="{cls}" href="albums/{a['slug']}/" style="--acc:{a['accent']}{(';--uni:' + UNI[UNI_OF[a['slug']]]) if a['slug'] in UNI_OF else ''}"{' data-uni="' + UNI_OF[a['slug']] + '"' if a['slug'] in UNI_OF else ''} data-thumbs='{json.dumps(thumbs[:6])}' data-exif="{exif}" data-n="{n:03d}">
            <span class="acard__fan"><span class="acard__stack"><img src="{thumbs[2 % len(thumbs)]}" alt="" loading="lazy"><img src="{thumbs[1]}" alt="" loading="lazy"><img class="acard__cover" src="{thumbs[0]}" srcset="{thumbs[0]} 800w, {thumbs[0].replace('-sm.jpg', '.jpg')} 1800w" sizes="{'(max-width: 900px) 92vw, 46vw' if lead else '(max-width: 560px) 92vw, (max-width: 900px) 46vw, 30vw'}" alt="" loading="lazy" decoding="async"><i class="flash"></i><span class="acard__frame" aria-hidden="true"><b>{FRAME_LEFT[a["kind"]]}</b><i>{i:02d}A ▸</i><em>{html.escape(plain(a["title"]))}</em><u>▸ {i + 1:02d}</u></span></span>{side_strips(thumbs, lead)}</span>
            <span class="acard__meta"><small>Album {i:02d} · {len(a['photos'])} photos</small><b>{stars(a['title'])}</b><span>{html.escape(a['where'])} · {html.escape(a['when'])}</span><span class="acard__intro">{html.escape(a['intro'])}</span></span>
            <span class="acard__go" aria-hidden="true">Open album →</span>{('<template class="stamp-tpl">' + seal(a['slug']) + '</template>') if a['slug'] in MARKS else ''}
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
for key in ("SCENERY", "PEOPLE", "EVENTS"):
    mine = [(i + 1, a) for i, a in enumerate(ALBUMS) if a["kind"] == key]
    # 5 albums -> two big lead cards, then three; 3 albums -> one even row
    leads = 2 if len(mine) % 3 == 2 else 0
    out = out.replace(f"{{{{ALBUMS_{key}}}}}", "\n".join(album_card(a, i, j < leads) for j, (i, a) in enumerate(mine)))
    out = out.replace(f"{{{{N_ALBUMS_{key}}}}}", str(len(mine)))
out = out.replace("{{FLOATERS_PEOPLE}}", floaters("home-portrait"))
# behind the Portrait album cards: two long film strips of every portrait frame drifting in opposite directions
def reel_backdrop(kind):
    shots = [n for a in ALBUMS if a["kind"] == kind for n in a["photos"]]
    half = (len(shots) + 1) // 2
    rows = [shots[:half], shots[half:] + shots[:max(0, half - (len(shots) - half))]]
    html_rows = ""
    for r, row in enumerate(rows):
        frames = "".join(f'<img src="assets/img/{n}-sm.jpg" alt="" loading="lazy" decoding="async">' for n in row)
        html_rows += f'<div class="bgreel__row bgreel__row--{"ab"[r]}"><div class="bgreel__track">{frames}{frames}</div></div>'
    return f'<div class="bgreel" aria-hidden="true">{html_rows}</div>'
out = out.replace("{{BGREEL_PEOPLE}}", reel_backdrop("PEOPLE"))

# the side margins: two vertical film strips down the left and right of the Portrait section (wide screens),
# and on phones one swipeable strip; every frame opens its album
def portrait_frames(kind):
    # newest album first, so the latest shoot is the first thing on the roll
    return [(a["slug"], n, html.escape(plain(a["title"]))) for a in reversed(ALBUMS) if a["kind"] == kind for n in a["photos"]]


def frame_link(slug, n, title, cls):
    return f'<a class="{cls}" href="albums/{slug}/" tabindex="-1" aria-hidden="true" title="{title}"><img src="assets/img/{n}-sm.jpg" alt="" loading="lazy" decoding="async"></a>'


def side_rails(kind):
    fr = portrait_frames(kind)
    left, right = fr[0::2], fr[1::2][::-1]
    out = ""
    for side, row in (("l", left), ("r", right)):
        frames = "".join(frame_link(*f, "srail__f") for f in row)
        out += f'<div class="srail srail--{side}" aria-hidden="true"><div class="srail__track">{frames}{frames}</div></div>'
    return out


def phone_strip(kind):
    fr = portrait_frames(kind)
    frames = "".join(f'<a class="mstrip__f" href="albums/{slug}/"><img src="assets/img/{n}-sm.jpg" alt="From {title}" loading="lazy" decoding="async"><small>{title}</small></a>' for slug, n, title in fr)
    return f'<div class="mstrip"><p class="mstrip__k"><span>{len(fr)} frames</span><small>Swipe the roll, tap one to open its album</small></p><div class="mstrip__track">{frames}</div></div>'


out = out.replace("{{RAILS_PEOPLE}}", side_rails("PEOPLE")).replace("{{MSTRIP_PEOPLE}}", phone_strip("PEOPLE"))
out = out.replace("{{N_ALBUMS}}", str(len(ALBUMS)))
out = out.replace("{{N_ALBUM_PHOTOS}}", str(sum(len(a["photos"]) for a in ALBUMS)))
out = out.replace("{{N_ALL}}", f"{len(ALL):03d}")
data = json.dumps({"roll": frames(ROLL), "hero": frames(HERO)}, ensure_ascii=False)
out = out.replace("{{SCENE_DATA}}", data.replace("</", "<\\/"))
assert not re.search(r"\{\{\w+\}\}", out), "unfilled placeholder"
(ROOT / "index.html").write_text(out)
print("index.html built:", len(ALBUMS), "album cards;", len(ROLL), "on the roll")

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
        "NO": f"{i + 1:02d}", "TOTAL": f"{len(ALBUMS):02d}", "SLUG": a["slug"], "SEAL": seal(a["slug"]), "FLOATERS": floaters(a["slug"]), "CAMERA": a.get("camera", "Fujifilm X-T30 II"), "NEXT_SEAL": seal(nxt["slug"]), "COVER": a.get("cover", a["photos"][0]),
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

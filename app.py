





from flask import Flask, render_template_string, request
import requests
import re
from urllib.parse import urlparse
from collections import Counter, defaultdict
from serpapi import GoogleSearch

app = Flask(__name__)

API_KEY = "d24b186a1ec0672bac703f57b1e9707beee4b29b71fce9e5301c77c1fac58178"


def domain(link):
    return urlparse(link).netloc.replace("www.", "")


def get_logo_url(website_link):
    d = domain(website_link)
    clearbit_logo = f"https://logo.clearbit.com/{d}"
    google_logo = f"https://www.google.com/s2/favicons?domain={d}&sz=256"
    try:
        r = requests.get(clearbit_logo, timeout=10)
        if r.status_code == 200 and len(r.content) > 500:
            return clearbit_logo
        return google_logo
    except:
        return google_logo


def clean_title(title):
    parts = re.split(r'[-–—|:]', title)
    name = parts[0].strip()
    name = re.sub(r'^(Top\s*\d+[:\s]*)|(Best\s+for\s+)|(Best[:\s]*)', '', name, flags=re.I).strip()
    return name


def valid(link):
    BAD_DOMAINS = [
        "reddit.com", "quora.com", "facebook.com", "youtube.com",
        "pinterest.com", "twitter.com", "linkedin.com", "medium.com"
    ]
    d = domain(link)
    return not any(bad in d for bad in BAD_DOMAINS)


def search(q):
    try:
        return GoogleSearch({
            "engine": "google",
            "q": q,
            "api_key": API_KEY,
            "num": 10
        }).get_dict()
    except Exception as e:
        print("Search Error:", e)
        return {}


def get_one_tool(problem):
    SEARCH_QUERIES = [
        "best software for {}",
        "best websites for {}",
        "top tools for {}",
        "apps for {}"
    ]

    names = Counter()
    samples = defaultdict(list)

    for q in SEARCH_QUERIES:
        result = search(q.format(problem))

        for item in result.get("organic_results", [])[:5]:
            link = item.get("link", "")
            if not valid(link):
                continue

            title = item.get("title", "")
            snippet = item.get("snippet", "")
            name = clean_title(title) or domain(link)

            names[name] += 1
            samples[name].append((title, link, snippet))

    if not names:
        return None

    top_name, _ = names.most_common(1)[0]
    sample = samples[top_name][0]

    return {
        "name": top_name,
        "link": sample[1],
        "title": sample[0],
        "snippet": sample[2][:220],
        "logo": get_logo_url(sample[1])
    }


# ----------------------------
# Route
# ----------------------------
@app.route("/", methods=["GET", "POST"])
def home():
    result = None

    if request.method == "POST":
        problem = request.form["query"]
        result = get_one_tool(problem)

    html = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TV | Tele Verse</title>

<style>
*{
    margin:0;
    padding:0;
    box-sizing:border-box;
}

body{
    font-family:'Segoe UI',sans-serif;
    min-height:100vh;
    background:
        radial-gradient(circle at top left,#14304f 0%,transparent 35%),
        radial-gradient(circle at bottom right,#00bcd4 0%,transparent 28%),
        linear-gradient(135deg,#0f1720,#15202d,#1b2735);
    color:white;
    display:flex;
    justify-content:center;
    align-items:center;
    overflow:hidden;
}

body::before{
    content:"";
    position:absolute;
    width:200%;
    height:200%;
    background:
        linear-gradient(rgba(255,255,255,0.015) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.015) 1px, transparent 1px);
    background-size:45px 45px;
    animation:gridMove 18s linear infinite;
}

@keyframes gridMove{
    0%{transform:translate(0,0);}
    100%{transform:translate(-45px,-45px);}
}

.container{
    position:relative;
    z-index:10;
    width:90%;
    max-width:950px;
    padding:55px;
    border-radius:30px;
    background:rgba(255,255,255,0.06);
    backdrop-filter:blur(22px);
    border:1px solid rgba(255,255,255,0.08);
    box-shadow:
        0 0 40px rgba(0,180,255,0.08),
        inset 0 0 20px rgba(255,255,255,0.03);
    text-align:center;
}

.brand{
    font-size:34px;
    font-weight:700;
    letter-spacing:4px;
    color:#ffffff;
    margin-bottom:10px;
}

.subtitle{
    color:#87dfff;
    font-size:14px;
    letter-spacing:3px;
    margin-bottom:40px;
    text-transform:uppercase;
}

.logo{
    width:130px;
    height:130px;
    margin:0 auto 35px;
    border-radius:28px;
    background:rgba(255,255,255,0.05);
    display:flex;
    justify-content:center;
    align-items:center;
    border:1px solid rgba(0,255,255,0.15);
    transition:0.4s ease;
}

.logo:hover{
    transform:translateY(-6px);
}

.logo img{
    width:80px;
    height:80px;
    border-radius:18px;
}

.tool-name{
    font-size:28px;
    font-weight:600;
    margin-bottom:20px;
    color:#ffffff;
}

.output{
    background:rgba(255,255,255,0.04);
    border:1px solid rgba(255,255,255,0.06);
    border-radius:22px;
    padding:28px;
    line-height:1.8;
    color:#d9f8ff;
    margin-bottom:35px;
}

.output a{
    color:#58e6ff;
    text-decoration:none;
}

.output a:hover{
    color:white;
}

.input-box{
    width:100%;
}

.input-box input{
    width:100%;
    padding:18px 24px;
    border:none;
    border-radius:18px;
    background:rgba(255,255,255,0.06);
    color:white;
    font-size:17px;
    outline:none;
    border:1px solid rgba(255,255,255,0.08);
    transition:0.35s;
}

.input-box input:focus{
    border:1px solid rgba(0,255,255,0.35);
    box-shadow:0 0 20px rgba(0,255,255,0.08);
}

::placeholder{
    color:#8caec7;
}

.empty{
    color:#8fa6b7;
    font-size:17px;
    margin-bottom:35px;
}

@media(max-width:768px){
    .container{
        padding:35px;
    }

    .brand{
        font-size:24px;
    }

    .tool-name{
        font-size:22px;
    }
}
</style>
</head>

<body>

<div class="container">

<div class="brand">TELE VERSE</div>
<div class="subtitle">AI Tool Discovery Engine</div>

<div class="logo">
{% if result %}
<img src="{{result['logo']}}" alt="Logo">
{% endif %}
</div>

{% if result %}
<div class="tool-name">{{result['name']}}</div>

<div class="output">
<p><strong>{{result['title']}}</strong></p>
<br>
<p>{{result['snippet']}}</p>
<br>
<a href="{{result['link']}}" target="_blank">{{result['link']}}</a>
</div>
{% else %}
<div class="empty">
Describe your problem statement and Tele Verse will identify the most relevant tool.
</div>
{% endif %}

<form method="POST" class="input-box">
<input type="text" name="query" placeholder="Enter your problem statement..." required>
</form>

</div>

</body>
</html>
'''

    return render_template_string(html, result=result)


# ----------------------------
# Run App
# ----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

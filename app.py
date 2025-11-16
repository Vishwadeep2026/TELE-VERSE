





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
        else:
            return google_logo
    except:
        return google_logo

def clean_title(title):
    parts = re.split(r'[-–—|:]', title)
    name = parts[0].strip()
    name = re.sub(r'^(Top\s*\d+[:\s]*)|(Best\s+for\s+)|(Best[:\s]*)', '', name, flags=re.I).strip()
    return name

def valid(link):
    BAD_DOMAINS = ["reddit.com","quora.com","facebook.com","youtube.com","pinterest.com","twitter.com","linkedin.com","medium.com"]
    d = domain(link)
    return not any(bad in d for bad in BAD_DOMAINS)

def search(q):
    try:
        return GoogleSearch({"engine": "google", "q": q, "api_key": API_KEY, "num": 10}).get_dict()
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
    logo_url = get_logo_url(sample[1])

    return {
        "name": top_name,
        "link": sample[1],
        "title": sample[0],
        "snippet": sample[2][:180],
        "logo": logo_url
    }

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
        <title>TV(Tele Verse)</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                background: #212121;
                color: #212121;
                font-family: 'Poppins', 'Segoe UI', sans-serif;
                height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                overflow: hidden;
            }
            .container {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                width: 100%;
                height: 100%;
                text-align: center;
                gap: 50px;
            }

            .logo {
            width: 160px;
            height: 160px;
            border-radius: 50%;
            background: rgb(23, 23, 23); /* transparent layer */
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .logo img {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            transition: transform 0.5s ease;
        }

        .logo img:hover {
            transform: scale(1.05);
        }




            .title {
    font-size: 22px;
    font-weight: 700;
    font-style: italic;
    color: white;
    letter-spacing: 1.2px;
    font-family: 'Poppins', 'Segoe UI', 'Roboto', sans-serif;
}

            .output {
    font-size: 17px;
    max-width: 800px;
    color: rgba(255, 255, 255, 0.9);
    line-height: 1.6;
    backdrop-filter: blur(25px);
    padding: 25px;
    border-radius: 20px;
    background: rgba(255, 255, 255, 0.03);
    font-family: 'Poppins', 'Segoe UI', 'Roboto', sans-serif;
    font-style: italic;
    transition: all 0.5s ease;
}

.output a {
    color: white;
    text-decoration: none;
    font-weight: 600;
    font-style: italic;
}

.output a:hover {
    color: cyan;
    text-shadow: 0 0 10px cyan;
}

            .input-box input {
    width: 420px;
    padding: 14px 20px;
    border: none;
    border-radius: 40px;
    font-size: 18px;
    font-family: 'Poppins', 'Segoe UI', 'Roboto', sans-serif;
    background: rgba(48, 48, 48, 0.03);
    color: white;
    outline: none;
    text-align: center;
    backdrop-filter: blur(20px);
    transition: transform 0.3s ease;
}

.input-box input:focus {
    transform: scale(1.02);
}
.input-box input:hover {
    transform: scale(1.02);
}

        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">
                {% if result %}
                    <img src="{{result['logo']}}" alt="Logo">
                {% else %}
                    <img src="https://cdn-icons-png.flaticon.com/512/2490/2490456.png" alt="Logo">
                {% endif %}
            </div>

            {% if result %}
                <div class="title">{{result['name']}}</div>
                <div class="output">
                    <p>{{result['title']}}</p>
                    <p>{{result['snippet']}}</p>
                    <p><a href="{{result['link']}}" target="_blank">{{result['link']}}</a></p>
                </div>
            {% else %}
                <div class="output" style="color:gray;">Enter a problem statement to find matching the best tool...</div>
            {% endif %}

            <form method="POST" class="input-box">
                <input type="text" name="query" placeholder="Enter your problem statement..." required>
            </form>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html, result=result)

if __name__ == "__main__":
    app.run(debug=True)

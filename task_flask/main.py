from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/scrape", methods=["POST"])
def scrape():
    query = request.form["query"]
    save_folder = "static/Images"
    
    ''' Clear previous images'''

    if os.path.exists(save_folder):
        for file in os.listdir(save_folder):
            os.remove(os.path.join(save_folder, file))
    else:
        os.makedirs(save_folder)

    
    headers = {
        "User-Agent": "Mozilla/5.0"
    }


    search_url = f"https://www.google.com/search?q={query}&tbm=isch"
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    img_tags = soup.find_all("img")[1:10]  # skip the first 

    image_files = []
    for idx, img in enumerate(img_tags):
        img_url = img.get("src")
        if img_url:
            img_data = requests.get(img_url).content
            file_name = f"{idx}.jpg"
            with open(os.path.join(save_folder, file_name), "wb") as f:
                f.write(img_data)
            image_files.append(file_name)

    return render_template("result.html", images=image_files, query=query)

if __name__ == "__main__":
    app.run(debug=True)

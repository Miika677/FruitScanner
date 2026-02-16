#Fruit Scanner Demo - AI-powered automatic pricetags
#Author: Miika677

import os
from flask import Flask, render_template, request, url_for, redirect
from labels import possiblefruits
from ai import fruit_agent
from sticker import create_price_sticker

app = Flask(__name__)

#Folders ----------------------------------------------
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

STICKER_FOLDER = "stickers"
os.makedirs(os.path.join(app.static_folder, STICKER_FOLDER), exist_ok=True)
app.config["STICKER_FOLDER"] = STICKER_FOLDER


#Routes ----------------------------------------------
@app.route("/")
def home ():
    return render_template("index.html",  fruitlist=possiblefruits)

@app.route("/sticker", methods=["GET", "POST"])
def sticker ():
    #Get image and weight from POST request.
    #In real world application the image's origin would be from a camera-equipped scale.
    #The customer presses a button to initiate the price tag sticker creation process.
    #The same button would capture an image for this route along with the weight from the scale.

    if request.method == "GET":
        return redirect(url_for("home"))

    uploaded_file = request.files["image"]
    str_weight = request.form.get("weight_grams", "").strip()

    #Initial error checks
    if not uploaded_file or not str_weight:
        return render_template("index.html", error=True, errormsg="Error: Missing information.", fruitlist=possiblefruits)
    
    if int(str_weight) >10000:
        return render_template("index.html", error=True, errormsg="Error: Weight limit of 10kg exceeded.", fruitlist=possiblefruits)
    try:
        weight = int(str_weight)
    except ValueError:
        return render_template("index.html", error=True, errormsg="Error: Weight must be a number.", fruitlist=possiblefruits)
        
    #Save uploaded image
    file_path_upload = os.path.join(app.config["UPLOAD_FOLDER"], uploaded_file.filename)
    uploaded_file.save(file_path_upload)

    #Pass image to AI function
    ai_fruitchoice = fruit_agent(file_path_upload)
    if ai_fruitchoice == "unknown":
         return render_template("index.html", error=True, errormsg="Error: Fruit could not be identified or not in selection.", fruitlist=possiblefruits)
    
    #Create the final price sticker
    file_path_sticker = os.path.join(app.static_folder, STICKER_FOLDER, "sticker.png")
    create_price_sticker("Mike's Shop", ai_fruitchoice, weight, file_path_sticker)

    sticker_url = url_for("static", filename="stickers/sticker.png")
    return render_template("sticker.html", fruit=ai_fruitchoice, template_sticker=sticker_url) 

if __name__ == "__main__":
    with app.app_context():
        app.run(debug=False)
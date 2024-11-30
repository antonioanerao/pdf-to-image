import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
from slugify import slugify
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('APP_SECRET')
UPLOAD_FOLDER = os.path.join("pdfs")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def pdf_to_image(pdf_path, output_folder):
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"O arquivo {pdf_path} não foi encontrado.")

    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    folder_name = slugify(pdf_name)
    folder_path = os.path.join(output_folder, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    pages = convert_from_path(pdf_path)
    for i, page in enumerate(pages, start=1):
        page_name = f"{i:02}.png"
        page_path = os.path.join(folder_path, page_name)
        page.save(page_path, "PNG")

    return folder_name


@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            flash("Nenhum arquivo selecionado.")
            return redirect(request.url)

        file = request.files["file"]

        if file.filename == "":
            flash("Nenhum arquivo foi enviado.")
            return redirect(request.url)

        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)

            try:
                folder_name = pdf_to_image(file_path, "images")
                flash(f"PDF processado com sucesso. Imagens salvas na pasta '{folder_name}'.")
                return redirect(url_for("upload_file"))
            except Exception as e:
                flash(f"Erro ao processar o PDF: {e}")
                return redirect(request.url)

    return render_template("upload.html")


if __name__ == "__main__":
    app.run(host=os.getenv('APP_HOST'), port=os.getenv('APP_PORT'), debug=True)

from flask import Flask, render_template, request
import requests
import random

app = Flask(__name__)

API_KEY = "27dba43fd51bea661d24a1efce2e9647"
BASE_URL = "https://api.themoviedb.org/3"

def obter_generos():
    url = f"{BASE_URL}/genre/movie/list?api_key={API_KEY}&language=pt-BR"
    resposta = requests.get(url)
    if resposta.status_code == 200:
        return resposta.json().get("genres", [])
    return []

def buscar_filmes_por_genero(genero_id):
    url = f"{BASE_URL}/discover/movie?api_key={API_KEY}&with_genres={genero_id}&sort_by=vote_average.desc&vote_count.gte=100&language=pt-BR"
    resposta = requests.get(url)
    if resposta.status_code == 200:
        return resposta.json().get("results", [])
    return []

def buscar_trailer(filme_id):
    url = f"{BASE_URL}/movie/{filme_id}/videos?api_key={API_KEY}&language=pt-BR"
    resposta = requests.get(url)
    if resposta.status_code == 200:
        videos = resposta.json().get("results", [])
        for video in videos:
            if video["type"] == "Trailer" and video["site"] == "YouTube":
                return f"https://www.youtube.com/watch?v={video['key']}"
    return None

@app.route("/", methods=["GET", "POST"])
def index():
    recomendacoes = []
    generos = obter_generos()

    if request.method == "POST":
        genero_nome = request.form.get("genero")
        genero_id = next((g["id"] for g in generos if g["name"].lower() == genero_nome.lower()), None)

        if genero_id:
            filmes = buscar_filmes_por_genero(genero_id)
            if filmes:
                filmes_escolhidos = random.sample(filmes, min(3, len(filmes)))
                for filme in filmes_escolhidos:
                    recomendacoes.append({
                        "titulo": filme["title"],
                        "nota": filme["vote_average"],
                        "sinopse": filme["overview"],
                        "ano": filme["release_date"][:4] if filme["release_date"] else "N/A",
                        "poster": f"https://image.tmdb.org/t/p/w500{filme['poster_path']}" if filme["poster_path"] else None,
                        "trailer": buscar_trailer(filme["id"])
                    })

    return render_template("index.html", generos=generos, recomendacoes=recomendacoes)

if __name__ == "__main__":
    app.run(debug=True)

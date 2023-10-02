import os
import requests
import json

# Função para baixar imagens usando a DuckDuckGo Instant Answer API
def download_images(search_query, limit):
    # URL da API do DuckDuckGo
    api_url = "https://api.duckduckgo.com/"

    # Parâmetros da consulta
    params = {
        "q": search_query,
        "format": "json",
        "iax": "images",
        "ia": "images",
        "no_html": "1",
        "no_redirect": "1",
        "skip_disambig": "1",
        "callback": "",
    }

    try:
        # Faz a solicitação à API
        response = requests.get(api_url, params=params)
        data = response.json()

        # Verifica se há resultados de imagens
        if "Results" in data and data["Results"]:
            images = data["Results"]

            # Crie uma pasta para salvar as imagens
            folder_name = search_query.replace(" ", "_")
            os.makedirs(folder_name, exist_ok=True)

            # Baixe as imagens
            for i, image in enumerate(images[:limit], 1):
                image_url = image["Image"]
                image_data = requests.get(image_url).content
                with open(f"{folder_name}/{i}.jpg", "wb") as img_file:
                    img_file.write(image_data)
                print(f"Downloaded image {i}/{limit}")

            print(f"Downloaded {len(images)} images for {search_query}")
        else:
            print(f"No image results found for {search_query}")

    except Exception as e:
        print(f"Error: {e}")

# Pedir ao usuário as pesquisas desejadas
search_terms = input("Digite as palavras-chave para pesquisa: ")
limit = int(input("Digite o número máximo de imagens a serem baixadas: "))

# Divida os termos de pesquisa e processe cada um
search_terms_list = search_terms.split(",")
for term in search_terms_list:
    download_images(term.strip(), limit)

print("Todas as pesquisas foram concluídas.")

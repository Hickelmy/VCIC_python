import os
import requests
import urllib.request
from urllib.request import urlopen
from bs4 import BeautifulSoup
from user_agent import generate_user_agent

# Função para baixar imagens de um URL
def download_images(url, keywords, limit):
    try:
        main_folder = 'objetos'
        folder_name = '_'.join(keywords.split()[:3]).lower()  # Converta o termo para minúsculas
        main_folder_path = os.path.join(os.getcwd(), main_folder)
        os.makedirs(main_folder_path, exist_ok=True)
        folder_path = os.path.join(main_folder_path, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        headers = {"User-Agent": generate_user_agent()}
        response = requests.get(url, headers=headers)
        page_soup = BeautifulSoup(response.text, 'html.parser')
        img_items = page_soup.find_all('img')
        
        i = 1
        downloaded_images = set()
        for img in img_items:
            img_src = img.get('src')
            if img_src and (img_src.startswith('http') or img_src.startswith('https')):
                if img_src in downloaded_images:
                    continue
                image = img_src
                print(f'Downloading image {i}/{limit} from {keywords}')
                file_name = os.path.join(folder_path, f'{i}.jpeg')
                urllib.request.urlretrieve(image, file_name)
                downloaded_images.add(img_src)
                if is_valid_image(file_name):
                    i += 1
                if i > limit:
                    break

        # Verifica se a pasta está vazia
        if not os.listdir(folder_path):
            print(f'A pasta {folder_name} está vazia. Removendo...')
            os.rmdir(folder_path)
        else:
            print(f'As imagens foram baixadas com sucesso para {folder_name}')

        print(f'Downloaded {i - 1} images for {keywords}')
    except Exception as e:
        print(f'Error: {e}')

# Função para verificar se a imagem é válida (não é um ícone ou imagem pequena)
def is_valid_image(file_name):
    try:
        with open(file_name, 'rb') as img_file:
            img_data = img_file.read()
        if len(img_data) >= 100:
            return True
        else:
            os.remove(file_name)
            return False
    except Exception as e:
        os.remove(file_name)
        return False

# Pedir ao usuário as pesquisas desejadas
search_terms = input("Digite as palavras-chave para pesquisa (separadas por vírgulas): ")
limit = min(int(input("Digite o número máximo de imagens a serem baixadas por pesquisa (limite máximo é 20): ")), 20)

search_terms_list = search_terms.split(',')
for term in search_terms_list:
    url = f'https://www.google.com/search?q={term}&tbm=isch'
    download_images(url, term.strip(), limit)

print("Todas as pesquisas foram concluídas.")

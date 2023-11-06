from pymongo import MongoClient
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt
from pymongo import MongoClient

# Conecte ao servidor MongoDB
client = MongoClient("localhost", 27017)

# Acesse o banco de dados
db = client["user_data"]

# Acesse a coleção
colecao = db["sr cat"]

# Defina o critério de pesquisa, por exemplo, encontrar todos os documentos com imagens
criterio = {"image": {"$exists": True}}

# Realize a pesquisa na coleção
documentos_encontrados = colecao.find(criterio)

# Itere sobre os documentos encontrados
for documento in documentos_encontrados:
    # Recupere o campo de imagem
    imagem_codificada = documento["image"]

    # Decodifique a imagem
    imagem_bytes = BytesIO(imagem_codificada)
    imagem = Image.open(imagem_bytes)

    # Exiba a imagem
    plt.imshow(imagem)
    plt.axis("off")
    plt.show()

import os
import aiohttp
import asyncio
from tqdm import tqdm
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup
import re


async def baixar_imagem(sem, session, url, destino):
    headers = {
        'User-Agent': 'User agent aqui'
        'Cookie': 'Cookie aqui'
    }

    try:
        async with sem, session.get(url, headers=headers) as response:
            if response.status == 200:
                soup = BeautifulSoup(await response.text(), 'html.parser')
                foto_zoom_div = soup.find('div', {'id': 'foto_zoom'})

                if foto_zoom_div:
                    # Usando expressão regular para extrair a URL da imagem do estilo CSS
                    style = foto_zoom_div['style']
                    match = re.search(r'url\((.*?)\)', style)
                    if match:
                        request_url = match.group(1)
                        content = await baixar_imagem_real(session, request_url, destino)
                        if content:
                            salvar_imagem_original(content, destino)
                            print(f'Imagem de {url} baixada com sucesso para {destino}')
                        else:
                            print(f'Falha ao baixar imagem de {url}. Conteúdo da imagem vazio')
                    else:
                        print(f'Nenhuma URL de imagem encontrada em {url}')
                else:
                    print(f'Div com ID "foto_zoom" não encontrada em {url}')
            else:
                print(f'Falha ao baixar imagem de {url}. Status: {response.status}')
    except Exception as e:
        print(f'Erro ao processar {url}: {str(e)}')


async def baixar_imagem_real(session, request_url, destino):
    try:
        async with session.get(request_url) as response:
            if response.status == 200:
                return await response.read()
    except Exception as e:
        print(f'Erro ao baixar imagem real: {str(e)}')
    return None


def salvar_imagem_original(content, destino):
    with open(destino, 'wb') as arquivo:
        arquivo.write(content)

    imagem = Image.open(BytesIO(content))
    imagem_jpg = imagem.convert('RGB')
    caminho_jpg = destino.replace('.gif', '.jpg')
    imagem_jpg.save(caminho_jpg)
    os.remove(destino)


async def processar_faixa(sem, session, inicio, fim):
    tasks = []
    for numero in tqdm(range(inicio, fim + 1), desc="Baixando imagens", unit="imagem", position=1):
        url = f'URL/{numero}'
        tasks.append(baixar_imagem(sem, session, url, f'{pasta_download}/imagem_{numero}.gif'))

    await asyncio.gather(*tasks)


pasta_download = 'download'
if not os.path.exists(pasta_download):
    os.makedirs(pasta_download)

inicio_total = 647032001
fim_total = 647044000
passo = 5000


async def main():
    async with aiohttp.ClientSession() as session:
        sem = asyncio.Semaphore(500)
        for inicio in range(inicio_total, fim_total, passo):
            fim = min(inicio + passo - 1, fim_total)
            await processar_faixa(sem, session, inicio, fim)


if __name__ == "__main__":
    asyncio.run(main())

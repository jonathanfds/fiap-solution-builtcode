import cv2
import pytesseract
import os
import Funcoes.func_images as fi
import Funcoes.func_extraction as ext;
import json

SHOW_IMAGE = False
pasta_cupons = input("Insira o caminho para a Pasta dos cupons: \n")
cupons_diretorio = os.listdir(pasta_cupons)

caminho_imagens = []

for caminho_imagem in cupons_diretorio:
    if caminho_imagem.lower().endswith(".jpg"):
        caminho = [pasta_cupons, '\\', caminho_imagem]
        caminho_imagens.append("".join(caminho))
pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

for image_path in caminho_imagens:
    img_name = os.path.basename(image_path)
    img = fi.processar_imagem(image_path)

    if SHOW_IMAGE:
        fi.exibir_img(image_path, img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    ocr = pytesseract.image_to_string(img, lang="por", config="--psm 3")

    text_lines = []
    # Remove linhas com menos de 3 caracteres
    text_lines = [line for line in ocr.splitlines() if line.strip() and len(line) > 3]

    nome_empresa = ext.encontra_nome_empresa(text_lines)
    idx_ini_itens, cnpj_empresa = ext.encontra_cnpj_empresa(text_lines)
    consumidor = ext.encontra_consumidor(text_lines)
    idx_final_itens, valor_nota = ext.encontra_valor_total(text_lines, idx_ini_itens)
    itens = ext.encontra_itens_nota(text_lines, idx_ini_itens, idx_final_itens)
    dado_nota = {'nome_empresa': nome_empresa, 'cnpj_empresa': cnpj_empresa, 'consumidor': consumidor, 'valor_nota': valor_nota, 'itens': itens, 'ocr_lines': text_lines}
    jsonString = json.dumps(dado_nota, indent=4, ensure_ascii=False)

    file = open(image_path.lower().replace(".jpg", ".json"), "w", encoding="utf-8")
    file.write(jsonString)
    file.close()
    print(img_name + ' processed !')

print('--- Finish ---')

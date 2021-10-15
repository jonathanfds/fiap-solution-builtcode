import regex
import locale

NOT_FOUND = "Não encontrado"
locale.setlocale(locale.LC_ALL, 'pt_Br')


def encontra_nome_empresa(nota_strings):
    # Busca nas 5 primeiras linhas alguma linha que contenha LTDA ou SA
    for i in range(5):
        if regex.search("(LTDA){e<=1}", nota_strings[i], flags=regex.BESTMATCH | regex.IGNORECASE):
            match_nome = regex.search(r"[a-zA-Z].*(LTDA){e<=1}", nota_strings[i],
                                      flags=regex.BESTMATCH | regex.IGNORECASE)
            if match_nome:
                return match_nome.group()
    for i in range(5):
        if regex.search("(SA)", nota_strings[i], flags=regex.IGNORECASE):
            match_nome = regex.search(r"[a-zA-Z].*(SA)", nota_strings[i], flags=regex.BESTMATCH | regex.IGNORECASE)
            if match_nome and len(match_nome.group().replace(" ", "")) >= 5:
                return match_nome.group()
    #Caso não encontre, retorna a primeira linha
    return nota_strings[0]


def encontra_cnpj_empresa(nota_strings):
    # Busca nas 7 primeiras linhas a expressão CNPJ e algum valor que atenda a Regex de CNPJ
    for i in range(7):
        if regex.search("(CNPJ){e<=1}", nota_strings[i], flags=regex.BESTMATCH | regex.IGNORECASE):
            match_cnpj = regex.search(r'(\d{2}.\d{3}.\d{3}/\d{4}-\d{2})|(\d{14})', fix_ocr_numbers(nota_strings[i]),
                                      flags=regex.BESTMATCH)
            if match_cnpj:
                cnpj = match_cnpj.group()
                return i, limpar_cnpj_cpf(cnpj)
    # Caso Não encontre com a label, retorna o primeiro CNPJ encontrado
    for i in range(5):
        match_cnpj = regex.search(r'(\d{2}.\d{3}.\d{3}/\d{4}-\d{2})|(\d{14})', fix_ocr_numbers(nota_strings[i]),
                                  flags=regex.BESTMATCH)
        if match_cnpj:
            cnpj = match_cnpj.group()
            return i, limpar_cnpj_cpf(cnpj)
    return 0, NOT_FOUND


def fix_ocr_numbers(text):
    # Corrigi alguns erros comuns do OCR para números
    return text.upper().replace("O", "0").replace("I", "1").replace("L", "1").replace("º", "")


def limpar_cnpj_cpf(text):
    # Limpa caracters do CNPJ ou CPF
    return text.upper().replace("-", "").replace("/", "").replace(".", "")


def encontra_consumidor(nota_strings):
    # Busca nas linhas a expressão CONSUMIDOR e algum valor que atenda a Regex de CPF ou CNPJ
    for i in range(len(nota_strings)):
        if regex.search("(CONSUMIDOR){e<=3}", nota_strings[i], flags=regex.BESTMATCH | regex.IGNORECASE):
            match_cnpj = regex.search(r'(\d{2}.\d{3}.\d{3}/\d{4}-\d{2})|(\d{14})', fix_ocr_numbers(nota_strings[i]))
            if match_cnpj:
                return limpar_cnpj_cpf(match_cnpj.group())
            match_cpf = regex.search(r'(^(\d{3}.\d{3}.\d{3}-\d{2})|(\d{11}))', fix_ocr_numbers(nota_strings[i]))
            if match_cpf:
                return match_cpf.group()
    return NOT_FOUND


def encontra_valor_total(nota_strings, linha_inicial):
    # Busca nas linhas a expressão VALOR TOTAL e algum valor que atenda a Regex
    idx, value = encontra_valor_total_regex("(VALOR TOTAL){e<=3}", nota_strings, linha_inicial)
    if idx == -1:
        # Caso não encontre tenta usar somente a palavra TOTAL
        idx, value = encontra_valor_total_regex("(TOTAL){e<=1}", nota_strings, linha_inicial)
        if idx == -1:
            idx = len(nota_strings)
            value = NOT_FOUND

    return idx, value


def encontra_valor_total_regex(pattern, nota_strings, linha_inicial):
    candidates = []
    candidates_text = []
    for i in range(linha_inicial, len(nota_strings)):
        if regex.search(pattern, nota_strings[i], flags=regex.BESTMATCH | regex.IGNORECASE):
            for j in range(3):
                l = i + j
                # [0-9]+((\,|\.)[0-9][0-9])
                regex_valor = r'([0-9]+((\,|\.)[0-9][0-9]))?[0-9]+((\,|\.)[0-9][0-9])'
                match_valor = regex.search(regex_valor, fix_ocr_numbers(nota_strings[l]),
                                           flags=regex.BESTMATCH | regex.IGNORECASE)
                if match_valor:
                    valor = match_valor.group().replace(",", ".")
                    if valor.count(".") > 1:
                        valor = valor.replace(".", "", 1)
                    candidates_text.append([l, valor])
                    candidates.append([l, float(valor)])

    if len(candidates) >= 1:
        idx, max_value = max(candidates, key=lambda item: item[1])
        valor_dec = "{:.2f}".format(max_value)
        valor_txt = find_item(candidates_text, idx)
        if valor_txt == NOT_FOUND:
            valor_txt = valor_dec.replace(".", ",")
        return idx, valor_txt

    return -1, NOT_FOUND


def find_item(list, item):
    for i in range(len(list)):
        if list[i][0] == item:
            return list[i][1]
    return NOT_FOUND


def encontra_itens_nota(nota_strings, linha_inicial, linha_final):
    # Busca o numero da linha de cabeçalho da lista de Produtos,
    # caso nao encontre usar a linha do CNPJ da empresa como inicial
    lista_itens = []
    for i in range(linha_inicial, linha_final):
        if regex.search("CODIGO|DESCR|QTD{e<=2}", nota_strings[i], flags=regex.BESTMATCH | regex.IGNORECASE):
            linha_inicial = i
            break
    for i in range(linha_inicial, linha_final):
        match_item = regex.search(r'^([a-zA-Z]{1})?([0-9]{2,4})( )([0-9]+)( )(.+)', nota_strings[i])
        match_item2 = regex.search(r'^([a-zA-Z]{1})?([0-9]{2,13})( )(.+)', nota_strings[i])
        # A Regex '.*[a-zA-Z].*' ignora linha que tenha somente numeros
        match_letras = regex.match(r'.*[a-zA-Z].*', nota_strings[i])

        if match_item and match_letras:
            lista_itens.append(match_item.group())
            continue

        if match_item2 and match_letras:
            lista_itens.append(match_item2.group())

    return lista_itens

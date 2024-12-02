import pickle
import matplotlib.pyplot as plt
import numpy as np

def apurar_votos_e_gerar_resultados(arquivo_votos='votos.bin', candidatos=None):
    # Função principal para apurar votos e gerar resultados
    resultado_votos = apurar_votos(arquivo_votos)
    if resultado_votos:
        # Se houver votos, gera o boletim e os gráficos
        gerar_boletim_urna(resultado_votos)
        gera_graficos_por_cargo(resultado_votos, candidatos)
    else:
        print("Não foram encontrados votos para apuração.")

def gera_graficos_por_cargo(resultado_votos, candidatos):
    # Função para gerar gráficos dos votos agrupados por cargo
    cargo_referencia = {"F": "Deputado Federal", "E": "Deputado Estadual", "S": "Senador", "G": "Governador", "P": "Presidente"}
    votos_por_cargo = {}
    for (uf, cargo, numero), total in resultado_votos.items():
        # Agrupa os votos por cargo e número do candidato
        votos_por_cargo.setdefault(cargo, {}).setdefault(numero, 0)
        votos_por_cargo[cargo][numero] += total

    for cargo, votos in votos_por_cargo.items():
        # Mapeia os números dos candidatos para os nomes
        nomes_candidatos = {numero: candidatos.get(f"{numero}{cargo}{uf}", {}).get('nome', numero) 
                            for numero in votos.keys()}
        # Substitui a sigla do cargo pelo nome completo
        nome_completo_cargo = cargo_referencia.get(cargo, cargo)
        # Gera um gráfico para cada cargo
        gera_grafico(f"Resultados para {nome_completo_cargo}", votos, nomes_candidatos)

def gera_grafico(titulo, votos, nomes_candidatos, salvar=False, arquivo_grafico='grafico.png'):
    # Função para criar um gráfico de barras dos votos
    nomes = [nomes_candidatos.get(numero, numero) for numero in votos.keys()]
    valores = list(votos.values())
    
    plt.figure(figsize=(10, 5))
    barras = plt.bar(nomes, valores, color=np.random.rand(len(nomes), 3))  # Cores aleatórias para cada barra

    # Adiciona o valor dos votos em cima de cada barra
    for barra in barras:
        yval = barra.get_height()
        plt.text(barra.get_x() + barra.get_width()/2.0, yval, int(yval), va='bottom')  # centraliza o texto

    plt.xlabel('Candidatos')
    plt.ylabel('Votos')
    plt.title(titulo)
    plt.xticks(rotation=45)
    plt.tight_layout()

    if salvar:
        # Salva o gráfico em um arquivo, se solicitado
        plt.savefig(arquivo_grafico)
        print(f"Gráfico salvo como '{arquivo_grafico}'")
    else:
        plt.show()

def gerar_boletim_urna(resultado_votos, arquivo_boletim='boletim_urna.txt'):
    # Função para gerar um boletim de urna em formato de texto
    try:
        with open(arquivo_boletim, 'w') as arquivo:
            arquivo.write("Boletim de Urna\n\n")
            # Escreve os resultados de votos no arquivo
            for (uf, cargo, numero), total in sorted(resultado_votos.items()):
                arquivo.write(f"UF: {uf}, Cargo: {cargo}, Número: {numero}, Votos: {total}\n")
        print(f"Boletim de urna gerado com sucesso em {arquivo_boletim}.")
    except Exception as e:
        print(f"Erro ao gerar boletim de urna: {e}")

def apurar_votos(arquivo_votos='votos.bin', arquivo_resultado='resultado_votos.txt'):
    # Função para apurar os votos de um arquivo binário e gerar um arquivo de texto com os resultados
    try:
        with open(arquivo_votos, 'rb') as arquivo:
            votos = []
            try:
                while True:
                    votos.append(pickle.load(arquivo))
            except EOFError:
                pass  # Fim do arquivo alcançado

        if not votos:
            print("Nenhum voto para apurar.")
            return None

        contagem_votos = {}
        votos_por_eleitor = set()

        for voto in votos:
            uf = voto['UF']
            titulo_eleitor = voto['titulo_eleitor']

            if (uf, titulo_eleitor) in votos_por_eleitor:
                continue
            votos_por_eleitor.add((uf, titulo_eleitor))

            for cargo, numero in voto.items():
                if cargo not in ["UF", "titulo_eleitor"]:
                    chave = (uf, cargo, numero)
                    contagem_votos.setdefault(chave, 0)
                    contagem_votos[chave] += 1

        # Contagem de votos nominais, nulos e brancos
        total_votos = sum(contagem_votos.values())
        votos_nominais = sum(total for (uf, cargo, numero), total in contagem_votos.items() if numero not in ["Nulo", "Branco"])
        votos_nulos = sum(total for (uf, cargo, numero), total in contagem_votos.items() if numero == "Nulo")
        votos_brancos = sum(total for (uf, cargo, numero), total in contagem_votos.items() if numero == "Branco")

        # Gerar arquivo de texto com os resultados
        with open(arquivo_resultado, 'w') as arquivo_res:
            arquivo_res.write(f"Eleitores Aptos: {total_votos}\n")
            arquivo_res.write(f"Total de Votos Nominais: {votos_nominais}\n")
            arquivo_res.write(f"Brancos: {votos_brancos}\n")
            arquivo_res.write(f"Nulos: {votos_nulos}\n\n")

            for cargo in set(cargo for (uf, cargo, numero) in contagem_votos):
                total_votos_cargo = sum(total for (uf, cargo_iter, numero), total in contagem_votos.items() if cargo_iter == cargo)
                for (uf, cargo_iter, numero), total in sorted(contagem_votos.items()):
                    if cargo_iter == cargo:
                        percentual = (total / total_votos_cargo) * 100 if total_votos_cargo > 0 else 0
                        arquivo_res.write(f"Candidato: {numero} | Cargo: {cargo} | Estado: {uf} | Votos: {total} ({percentual:.2f}%)\n")

        print(f"Resultado da apuração salvo em {arquivo_resultado}")
        return contagem_votos
    except FileNotFoundError:
        print(f"Erro: O arquivo '{arquivo_votos}' não foi encontrado.")
        return None
    except Exception as e:
        print(f"Erro ao apurar votos: {e}")
        return None

def ler_arquivo_candidatos(nome_arquivo):
    # Função para ler e processar um arquivo de texto contendo informações dos candidatos
    candidatos = {}
    try:
        with open(nome_arquivo, 'r') as arquivo:
            for linha in arquivo:
                # Divide cada linha para obter dados do candidato
                dados = linha.strip().split(',')
                if len(dados) == 5:
                    nome, numero, partido, estado, cargo = dados
                    # Cria uma chave única para cada candidato
                    chave = f"{numero}{cargo}" if cargo == "P" else f"{numero}{cargo}{estado}"
                    candidatos[chave] = {
                        "nome": nome,
                        "partido": partido,
                        "estado": estado,
                        "cargo": cargo
                    }
                else:
                    print(f"Formato inválido de linha: {linha}")

        return candidatos
    except FileNotFoundError:
        # Erro caso o arquivo especificado não seja encontrado
        print(f"Erro: O arquivo '{nome_arquivo}' não foi encontrado.")
        return None
    except Exception as e:
        # Outros erros ao ler o arquivo
        print(f"Erro ao ler o arquivo: {e}")
        return None

def ler_arquivo_eleitores(nome_arquivo):
    # Função para ler e processar um arquivo de texto contendo informações dos eleitores
    eleitores = {}
    try:
        with open(nome_arquivo, 'r') as arquivo:
            linhas = arquivo.readlines()

        for linha in linhas:
            try:
                # Divide cada linha para obter dados do eleitor
                nome, rg, titulo_eleitor, municipio, estado = linha.strip().split(',')
                eleitores[titulo_eleitor] = {
                    "nome": nome,
                    "rg": rg,
                    "municipio": municipio,
                    "estado": estado
                }
            except ValueError:
                # Erro caso a linha não esteja no formato correto
                print(f"Erro na linha: {linha}. Formato incorreto.")

        return eleitores if eleitores else None
    except FileNotFoundError:
        # Erro caso o arquivo especificado não seja encontrado
        print(f"Erro: O arquivo '{nome_arquivo}' não foi encontrado.")
        return None
    except Exception as e:
        # Outros erros ao ler o arquivo
        print(f"Erro ao ler o arquivo: {e}")
        return None

def salvar_voto(voto, arquivo_votos='votos.bin'):
    # Função para salvar um voto no arquivo binário
    if not voto:
        # Caso não haja voto para salvar
        print("Nenhum voto para salvar.")
        return

    try:
        with open(arquivo_votos, 'ab') as arquivo:  # 'ab' para anexar em modo binário
            pickle.dump(voto, arquivo)
            print("Voto salvo com sucesso.")
    except Exception as e:
        # Trata erros ao salvar o voto
        print(f"Erro ao salvar o voto: {e}")

def coletar_voto(eleitores, candidatos, uf_urna):
    # Função para coletar um voto do eleitor
    titulo_eleitor = input("Informe o Título de Eleitor: ").strip()
    if titulo_eleitor not in eleitores or eleitores[titulo_eleitor]['estado'] != uf_urna:
        # Verifica se o eleitor está habilitado a votar na UF especificada
        print("Título não encontrado ou UF de voto do eleitor é diferente do da urna!")
        return None

    eleitor = eleitores[titulo_eleitor]
    # Exibe informações do eleitor
    print(f"Eleitor: {eleitor['nome']}, Documento(rg): {eleitor['rg']}, Endereço: {eleitor['municipio']} - {eleitor['estado']}")

    votos = {"UF": uf_urna, "titulo_eleitor": titulo_eleitor}
    # Mapeamento de códigos para cargos eleitorais
    cargo_referencia = {"F": "Deputado Federal", "E": "Deputado Estadual", "S": "Senador", "G": "Governador", "P": "Presidente"}

    for cargo in cargo_referencia:
        while True:
            # Coleta voto para cada cargo
            voto = input(f"Informe o voto para {cargo_referencia[cargo]} (ou digite 'B' para branco): ").strip().upper()

            if voto == "B":
                # Se o eleitor optar por voto em branco
                votos[cargo] = "Branco"
                break

            chave_candidato = f"{voto}{cargo}" if cargo == "P" else f"{voto}{cargo}{uf_urna}"

            # Verifica se o voto é válido (se o candidato existe)
            if chave_candidato not in candidatos:
                # Opção para voto nulo se o candidato não for encontrado
                print("Candidato não encontrado! Deseja votar nulo? (S ou N)")
                confirmar_nulo = input().strip().upper()
                if confirmar_nulo == "S":
                    votos[cargo] = "Nulo"
                    break
                else:
                    print("Por favor, informe um candidato válido.")
            else:
                # Se o candidato for encontrado, confirma o voto
                candidato = candidatos[chave_candidato]
                print(f"Candidato: {candidato['nome']}")
                confirmar = input("Confirma (S ou N)? ").strip().upper()
                if confirmar == "S":
                    votos[cargo] = voto
                    break
    return votos


def main():
    # Função principal que executa o sistema de votação
    candidatos = {}
    eleitores = {}
    candidatos_carregados = False
    eleitores_carregados = False

    while True:
        # Exibe o menu do sistema e aguarda a escolha do usuário
        print("Sistema de Urna Eletrônica Simplificada 💻🗳️")
        print("1 - Ler arquivo de candidatos 🧑‍💼")
        print("2 - Ler arquivo de eleitores 👥")
        print("3 - Iniciar votação 🗳️")
        print("4 - Apurar votos 📊")
        print("5 - Mostrar resultados 📈")
        print("6 - Fechar programa ❌")

        escolha = input("Escolha uma opção: ").strip()

        if escolha == "1":
            # Opção para carregar arquivo de candidatos
            nome_arquivo = input("Informe a localização dos dados dos candidatos: 📂 ")
            candidatos_temp = ler_arquivo_candidatos(nome_arquivo)
            if candidatos_temp is not None:
                candidatos = candidatos_temp
                candidatos_carregados = True
                print("Arquivo de candidatos carregado com sucesso! ✅")

        elif escolha == "2":
            # Opção para carregar arquivo de eleitores
            nome_arquivo = input("Informe a localização dos dados dos eleitores: 📂 ")
            eleitores_temp = ler_arquivo_eleitores(nome_arquivo)
            if eleitores_temp is not None:
                eleitores = eleitores_temp
                eleitores_carregados = True
                print("Arquivo de eleitores carregado com sucesso! ✅")

        elif escolha == "3":
            # Opção para iniciar o processo de votação
            if not candidatos_carregados or not eleitores_carregados:
                print("É necessário carregar os arquivos de candidatos e eleitores primeiro! ⚠️")
            else:
                # Inicia a coleta e salvamento dos votos
                uf_urna = input("UF onde está localizada a urna: ")
                while True:
                    voto = coletar_voto(eleitores, candidatos, uf_urna)
                    salvar_voto(voto)
                    continuar = input("Registrar novo voto (S ou N)? ")
                    if continuar.upper() != "S":
                        break

        elif escolha == "4":
            # Opção para apurar os votos coletados
            if not candidatos_carregados or not eleitores_carregados:
                print("É necessário carregar os arquivos de candidatos e eleitores e realizar a votação primeiro! ⚠️")
            else:
                resultado_votos = apurar_votos()
                if resultado_votos:
                    print("Resultados da Apuração:")
                    for (uf, cargo, numero), total in resultado_votos.items():
                        print(f"UF: {uf}, Cargo: {cargo}, Número: {numero}, Votos: {total}")
                else:
                    print("Não foi possível apurar os votos! 🚫")

        elif escolha == "5":
            # Opção para exibir os resultados da votação
            if not candidatos_carregados or not eleitores_carregados:
                print("É necessário carregar os arquivos de candidatos e eleitores e realizar a votação primeiro! ⚠️")
            else:
                apurar_votos_e_gerar_resultados(candidatos=candidatos)

        elif escolha == "6":
            # Opção para encerrar o programa
            print("Programa encerrado.")
            break

        else:
            print("Opção inválida. Tente novamente! 🚫")

if __name__ == "__main__":
    main()

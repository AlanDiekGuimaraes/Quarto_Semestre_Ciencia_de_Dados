
'''
Configuração Automática do Ambiente Virtual e Instalação de Bibliotecas

Execute este arquivo Python na pasta raiz do seu projeto para criar e configurar
um ambiente virtual (.venv) e instalar automaticamente as bibliotecas listadas
na variável 'lista_de_bibliotecas'.

Certifique-se de adicionar os nomes das bibliotecas desejadas (separados por vírgula e entre aspas)
na variável 'lista_de_bibliotecas' dentro do script.
'''

import subprocess
import sys
import os

# Lista de bibliotecas a serem instaladas
lista_de_bibliotecas = ["numpy", "pandas", "matplotlib", "seaborn", "nltk", "Spacy", "scikit-learn", "tensorflow", "keras", "xgboost", "lightgbm", "catboost"]
# Nome da pasta do ambiente virtual
pasta_venv = ".venv"

def criar_e_instalar_bibliotecas(bibliotecas):
    """
    Cria um ambiente virtual na pasta atual, atualiza o pip e instala as bibliotecas especificadas.
    """
    # Criação do ambiente virtual
    if not os.path.exists(pasta_venv):
        print(f"Criando ambiente virtual em '{pasta_venv}'...")
        try:
            subprocess.check_call([sys.executable, "-m", "venv", pasta_venv])
            print(f"Ambiente virtual criado com sucesso em '{pasta_venv}'.")
        except subprocess.CalledProcessError as e:
            print(f"Erro ao criar o ambiente virtual: {e}")
            return
    else:
        print(f"Ambiente virtual já existe em '{pasta_venv}'.")

    # Define os executáveis do Python e do pip dentro do ambiente virtual
    python_executavel = os.path.join(pasta_venv, "Scripts", "python.exe") if sys.platform == "win32" else os.path.join(pasta_venv, "bin", "python")
    pip_executavel = os.path.join(pasta_venv, "Scripts", "pip.exe") if sys.platform == "win32" else os.path.join(pasta_venv, "bin", "pip")

    # Atualização do pip no ambiente virtual
    print("Atualizando pip no ambiente virtual...")
    try:
        subprocess.check_call([python_executavel, "-m", "pip", "install", "--upgrade", "pip"])
        print("pip atualizado com sucesso no ambiente virtual.")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao atualizar o pip: {e}")

    # Instalação das bibliotecas
    print("Instalando bibliotecas...")
    try:
        for biblioteca in bibliotecas:
            print(f"Instalando {biblioteca} no ambiente virtual...")
            subprocess.check_call([pip_executavel, "install", biblioteca])
            print(f"{biblioteca} instalada com sucesso no ambiente virtual.")
        print("Todas as bibliotecas foram instaladas no ambiente virtual.")

        # Geração do arquivo requirements.txt dentro da pasta do projeto
        arquivo_requirements = "requirements.txt"
        subprocess.check_call([pip_executavel, "freeze", ">", arquivo_requirements], shell=True)
        print(f"\nArquivo {arquivo_requirements} gerado.")
        print(f"Para instalar as dependências em outro ambiente, use: pip install -r {arquivo_requirements}")

        print("\nConfiguração concluída!")
        print("Para usar as bibliotecas, ative o ambiente virtual:")
        if sys.platform == "win32":
            print(f"  {pasta_venv}\\Scripts\\activate")
        else:
            print(f"  source {pasta_venv}/bin/activate")

        # Tentativa de ativar o ambiente virtual (pode não funcionar diretamente em todos os terminais)
        print("\nTentando ativar o ambiente virtual...")
        if sys.platform == "win32":
            subprocess.run([os.path.join(pasta_venv, "Scripts", "activate.bat")], shell=True, check=False)
            print("Ambiente virtual (talvez) ativado. Verifique o prompt do seu terminal.")
        else:
            # Em sistemas Unix, a ativação geralmente requer 'source' que é um comando do shell
            # e não pode ser diretamente executado por subprocess.run dessa forma.
            print("Em sistemas Unix, você precisa usar o comando 'source .venv/bin/activate' no seu terminal.")

    except subprocess.CalledProcessError as e:
        print(f"Erro ao instalar uma biblioteca ou gerar {arquivo_requirements}: {e}")
    except FileNotFoundError:
        print(f"Erro: O executável do pip no ambiente virtual ('{pip_executavel}') não foi encontrado.")

if __name__ == "__main__":
    criar_e_instalar_bibliotecas(lista_de_bibliotecas)
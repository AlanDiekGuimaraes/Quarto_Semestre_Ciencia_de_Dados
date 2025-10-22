# Conjunto de imports
import os
import logging
import json
import numpy as np
import tensorflow as tf
import keras

def init():
    '''
    Esse método é executado na inicialização do modelo
    '''
    logging.info("Iniciando o Init do script.")
    global modelo
    AZUREML_MODEL_DIR = os.getenv("AZUREML_MODEL_DIR")

    # Fazendo um tratamento de erro básico
    if AZUREML_MODEL_DIR is None:
        raise EnvironmentError(
            "O camiminho do AZUREML_MODEL_DIR não está configurado!!")
    
    model_path = os.path.join(AZUREML_MODEL_DIR, "churn.h5")
    logging.info(f"Carregando o modelo em: {model_path}")

    modelo = keras.models.load_model(model_path)
    logging.info("Modelo carregado com sucesso!!")

def run(raw_data):
    '''
    Método chamado na invocação do endpoint para fazer a predição
    '''
    try:
        logging.info("Requisição recebida")
        dados = json.loads(raw_data)["dados"]
        dados = np.array(dados)
        predicao = modelo.predict(dados)
        logging.info("Execução da predição com sucesso")
        return {"previsao": predicao.tolist()}
    except Exception as e:
        logging.error(f"Erro na predição: {str(e)}")
        return {"error": str(e)}

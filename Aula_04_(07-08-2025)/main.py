import hashlib
import json
import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime
import os


VALORES = {
    "Hora Extra": 1000,
    "Licitação": 0,  # valor para Licitação será perguntado ao usuário
    "Workshop": 50000,
    "Convênio": -5000,
    "Contratação": -100000,
    "Demissão": 0,
    "Multa": 0
}

class Block:
    def __init__(self, index, previous_hash, classificacao, valor, integrantes, empresa, cnpj,
                 detalhes_valor="", timestamp=None, status="Pendente", hash_value=None,
                 class_values=None, hashes_classificacao=None):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.classificacao = classificacao
        self.valor = valor  # inteiro total
        self.detalhes_valor = detalhes_valor  # descrição legível
        self.status = status
        self.integrantes = integrantes
        self.empresa = empresa
        self.cnpj = cnpj

        # valores por classificação (dict: {"Hora Extra": 2000, ...})
        self.class_values = class_values or {}

        # hash geral do bloco
        if hash_value is None:
            self.hash = self.generate_hash()
        else:
            self.hash = hash_value

        # hashes individuais por classificação (preservar se vier do JSON)
        if hashes_classificacao is None:
            self.hashes_classificacao = self.generate_hashes_classificacao()
        else:
            self.hashes_classificacao = hashes_classificacao

    def generate_hash(self):
        # Inclui class_values serializado para garantir determinismo
        class_values_json = json.dumps(self.class_values, sort_keys=True, ensure_ascii=False)
        content = f"{self.index}{self.previous_hash}{self.timestamp}{self.classificacao}{self.valor}{self.detalhes_valor}{self.status}{self.integrantes}{self.empresa}{self.cnpj}{class_values_json}"
        return hashlib.sha256(content.encode()).hexdigest()

    def generate_hashes_classificacao(self):
        hashes = {}
        for item in self.classificacao:
            # valor específico desta classificação (0 se não existir)
            valor_item = int(self.class_values.get(item, 0))
            # conteúdo específico para cada classificação
            content = f"{self.index}|{self.previous_hash}|{self.timestamp}|{item}|{valor_item}|{self.status}|{self.integrantes}|{self.empresa}|{self.cnpj}"
            hashes[item] = hashlib.sha256(content.encode()).hexdigest()
        return hashes

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "classificacao": self.classificacao,
            "valor": self.valor,
            "detalhes_valor": self.detalhes_valor,
            "class_values": self.class_values,
            "hashes_classificacao": self.hashes_classificacao,
            "status": self.status,
            "integrantes": self.integrantes,
            "empresa": self.empresa,
            "cnpj": self.cnpj,
            "previous_hash": self.previous_hash,
            "hash": self.hash
        }

    @staticmethod
    def from_dict(data):
        return Block(
            index=data["index"],
            previous_hash=data.get("previous_hash", "0"),
            classificacao=data.get("classificacao", []),
            valor=data.get("valor", 0),
            integrantes=data.get("integrantes", []),
            empresa=data.get("empresa", ""),
            cnpj=data.get("cnpj", ""),
            detalhes_valor=data.get("detalhes_valor", ""),
            timestamp=data.get("timestamp"),
            status=data.get("status", "Pendente"),
            hash_value=data.get("hash"),
            class_values=data.get("class_values", {}),
            hashes_classificacao=data.get("hashes_classificacao")
        )

def create_genesis_block():
    # genesis com valor inteiro e class_values para Workshop
    return Block(
        0,
        "0",
        ["Workshop"],
        50000,
        ["Admin"],
        "Empresa Gênesis",
        "00.000.000/0000-00",
        detalhes_valor="Workshop: +50000 DNX",
        hash_value="0",
        class_values={"Workshop": 50000}
    )

def calcular_valor(classificacao, integrantes):
    """
    Retorna: total (int), detalhes (str), class_values (dict)
    """
    total = 0
    detalhes = []
    class_values = {}

    for item in classificacao:
        if item == "Hora Extra":
            valor_item = VALORES[item] * len(integrantes)
            detalhes.append(f"{item}: {valor_item:+} DNX")
            class_values[item] = valor_item
            total += valor_item

        elif item == "Licitação":
            valor_item = simpledialog.askinteger("Licitação", "Informe o valor total da Licitação (inteiro):")
            valor_item = int(valor_item) if valor_item is not None else 0
            detalhes.append(f"{item}: {valor_item:+} DNX")
            class_values[item] = valor_item
            total += valor_item

        elif item == "Workshop":
            valor_item = VALORES[item] * 1
            detalhes.append(f"{item}: {valor_item:+} DNX (por empresa)")
            class_values[item] = valor_item
            total += valor_item

        elif item == "Convênio":
            qtd = simpledialog.askinteger("Convênio", "Quantos integrantes pegaram convênio?")
            qtd = int(qtd) if qtd is not None else 0
            valor_item = VALORES[item] * qtd
            detalhes.append(f"{item}: {valor_item:+} DNX (para {qtd} integrante(s))")
            class_values[item] = valor_item
            total += valor_item

        elif item == "Contratação":
            qtd = simpledialog.askinteger("Contratação", "Quantos integrantes foram contratados (novos)?")
            qtd = int(qtd) if qtd is not None else 0
            valor_item = VALORES[item] * qtd
            detalhes.append(f"{item}: {valor_item:+} DNX (para {qtd} integrante(s) novo(s))")
            class_values[item] = valor_item
            total += valor_item

        elif item == "Demissão":
            qtd_justa = simpledialog.askinteger("Demissão", "Quantos ex-integrantes saíram com justa causa?")
            qtd_justa = int(qtd_justa) if qtd_justa is not None else 0
            qtd_sem_justa = simpledialog.askinteger("Demissão", "Quantos ex-integrantes saíram sem justa causa?")
            qtd_sem_justa = int(qtd_sem_justa) if qtd_sem_justa is not None else 0
            # 10.000 para justa causa (pedido de demissão), 20.000 para sem justa causa
            valor_item = 10000 * qtd_justa + 20000 * qtd_sem_justa
            detalhes.append(f"{item}: {valor_item:+} DNX ({qtd_justa} justa causa, {qtd_sem_justa} sem justa causa)")
            class_values[item] = valor_item
            total += valor_item

        elif item == "Multa":
            valor_multa = simpledialog.askinteger("Multa", "Informe o valor da multa para subtrair (valor positivo):")
            valor_multa = int(valor_multa) if valor_multa is not None else 0
            valor_item = -valor_multa
            detalhes.append(f"{item}: {valor_item:+} DNX")
            class_values[item] = valor_item
            total += valor_item

        else:
            valor = VALORES.get(item, 0)
            valor_item = valor * len(integrantes)
            detalhes.append(f"{item}: {valor_item:+} DNX")
            class_values[item] = valor_item
            total += valor_item

    return total, " | ".join(detalhes), class_values

def next_block(previous_block, classificacao, integrantes, empresa, cnpj):
    valor, detalhes, class_values = calcular_valor(classificacao, integrantes)
    return Block(previous_block.index + 1, previous_block.hash, classificacao, valor, integrantes, empresa, cnpj,
                 detalhes_valor=detalhes, class_values=class_values)

def carregar_blockchain():
    if os.path.exists("blockchain.json"):
        try:
            with open("blockchain.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            # Suporta tanto {"data": [...]} quanto lista direta [...]
            if isinstance(data, dict) and "data" in data:
                data_list = data["data"]
            elif isinstance(data, list):
                data_list = data
            else:
                raise ValueError("Formato de blockchain.json não reconhecido")
            blockchain = [Block.from_dict(b) for b in data_list]
            return blockchain
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar blockchain.json: {e}")
            return [create_genesis_block()]
    else:
        return [create_genesis_block()]

def exportar_json_local(blockchain):
    try:
        # Salva como objeto com chave "data" para compatibilidade
        with open("blockchain.json", "w", encoding="utf-8") as f:
            json.dump({"data": [b.to_dict() for b in blockchain]}, f, indent=4, ensure_ascii=False)
        messagebox.showinfo("Exportado", "Blockchain exportada para arquivo 'blockchain.json' com sucesso!")
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao exportar JSON: {e}")

# Inicia blockchain (carrega arquivo se existir)
blockchain = carregar_blockchain()

def adicionar_bloco():
    classificacao = [c for c, v in classificacao_vars.items() if v.get()]
    integrantes = [i.strip() for i in integrantes_entry.get().split(",") if i.strip()]
    empresa = empresa_entry.get().strip()
    cnpj = cnpj_entry.get().strip()

    if not classificacao or not integrantes or not empresa or not cnpj:
        messagebox.showerror("Erro", "Preencha todos os campos.")
        return

    bloco = next_block(blockchain[-1], classificacao, integrantes, empresa, cnpj)
    blockchain.append(bloco)

    # Mostra total e detalhes; você pode também exibir os hashes por classificação se quiser
    messagebox.showinfo("Bloco Adicionado", f"Valor total: {bloco.valor} DNX\nDetalhes: {bloco.detalhes_valor}")
    print(json.dumps(bloco.to_dict(), indent=2, ensure_ascii=False))

def exportar_json():
    exportar_json_local(blockchain)

# Interface Tkinter
root = tk.Tk()
root.title("Blockchain DNX")

tk.Label(root, text="Nome da Empresa:").pack()
empresa_entry = tk.Entry(root, width=40)
empresa_entry.pack()

tk.Label(root, text="CNPJ:").pack()
cnpj_entry = tk.Entry(root, width=40)
cnpj_entry.pack()

tk.Label(root, text="Classificação:").pack()
classificacao_vars = {}
for item in VALORES.keys():
    var = tk.BooleanVar()
    classificacao_vars[item] = var
    tk.Checkbutton(root, text=item, variable=var).pack(anchor="w")

tk.Label(root, text="Integrantes (separados por vírgula):").pack()
integrantes_entry = tk.Entry(root, width=50)
integrantes_entry.pack()

tk.Button(root, text="Adicionar Bloco", command=adicionar_bloco).pack(pady=10)
tk.Button(root, text="Exportar JSON localmente", command=exportar_json).pack(pady=5)

root.mainloop()
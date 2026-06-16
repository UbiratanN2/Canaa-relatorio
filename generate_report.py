import json
import re
from datetime import datetime
from pathlib import Path

DATA_FILE = Path("occurrences.json")

def parse_message(text: str):
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    occ = {
        "id": "",
        "data": "",
        "acionamento_cgr": "",
        "acionamento_equipe": "",
        "os": "",
        "caixa": "",
        "impacto": "",
        "obs": "",
        "regiao": "",
        "deslocamento": "",
        "rfo": "",
        "etr": "",
        "status": "Em andamento",
        "validacao_cgr": "",
        "historico": [],
        "last_update": datetime.now().isoformat()
    }

    for line in lines:
        upper = line.upper()
        
        if "DATA:" in upper:
            m = re.search(r'DATA:\s*(\d{2}/\d{2}/\d{4})', line)
            if m: occ["data"] = m.group(1)
        
        elif "ACIONAMENTO GRUPO CGR HORA" in upper:
            m = re.search(r'HORA\s*:\s*(\d{2}:\d{2})', line)
            if m: occ["acionamento_cgr"] = m.group(1)
        
        elif "ACIONAMENTO EQUIPE DATA HORA" in upper:
            m = re.search(r'HORA:\s*(\d{2}:\d{2})', line)
            if m: occ["acionamento_equipe"] = m.group(1)
        
        elif "OS Nº" in upper:
            m = re.search(r'OS Nº\s*-\s*(\S+)', line)
            if m: occ["os"] = m.group(1)
        
        elif "CAIXA:" in upper:
            m = re.search(r'CAIXA:\s*(\S+)', line)
            if m: occ["caixa"] = m.group(1).strip()
        
        elif "IMPACTO:" in upper:
            occ["impacto"] = line.split(":", 1)[1].strip()
        
        elif "OBS:" in upper:
            occ["obs"] = line.split(":", 1)[1].strip()
        
        elif "REGIÃO:" in upper or "REGIAO:" in upper:
            occ["regiao"] = line.split(":", 1)[1].strip()
        
        elif "DESLOCAMENTO:" in upper:
            occ["deslocamento"] = line.split(":", 1)[1].strip()
        
        elif "RFO:" in upper:
            occ["rfo"] = line.split(":", 1)[1].strip()
        
        elif "ETR" in upper:
            occ["etr"] = line.split(":", 1)[1].strip()
        
        elif any(x in upper for x in ["VALIDAR", "RESTABELECIMENTO", "VALIDAÇÃO"]):
            occ["status"] = "Resolvido"
            occ["validacao_cgr"] = datetime.now().strftime("%d/%m/%Y %H:%M")

    if occ["caixa"] and occ["data"]:
        occ["id"] = f"{occ['caixa']}-{occ['data'].replace('/', '-')}"
    
    occ["historico"].append(text)
    return occ


def load_data():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"occurrences": []}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def update_occurrence(text: str):
    new_occ = parse_message(text)
    if not new_occ["id"]:
        return "❌ Erro: Não consegui identificar Caixa + Data na mensagem."
    
    data = load_data()
    for existing in data["occurrences"]:
        if existing["id"] == new_occ["id"]:
            for k, v in new_occ.items():
                if v and k not in ["historico", "last_update"]:
                    existing[k] = v
            existing["historico"].extend(new_occ.get("historico", []))
            existing["last_update"] = datetime.now().isoformat()
            save_data(data)
            return f"✅ Ocorrência atualizada: {new_occ['id']}"
    
    data["occurrences"].append(new_occ)
    save_data(data)
    return f"✅ Nova ocorrência criada: {new_occ['id']}"


if __name__ == "__main__":
    print("✅ Script carregado com sucesso!")

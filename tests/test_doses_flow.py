from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

FUSO = ZoneInfo("America/Sao_Paulo")
MED = {"nome": "Losartana", "dosagem": "50mg", "observacao": ""}
CONTATO = {"nome": "Cuidador", "telefone": "11988880000", "parentesco": "Filho"}


def _hoje():
    return datetime.now(FUSO).strftime("%Y-%m-%d")


def _criar_stack(client, headers, frequencia="diario"):
    """Cria medicamento + contato + agendamento. Retorna (med_id, contato_id, agend_id)."""
    med_id = client.post("/api/medicamentos", json=MED, headers=headers).json()["id"]
    contato_id = client.post("/api/contatos", json=CONTATO, headers=headers).json()["id"]
    agend = {
        "id_medicamento": med_id,
        "horario": "08:00",
        "frequencia": frequencia,
        "data_inicio": _hoje(),
    }
    agend_id = client.post("/api/agendamentos", json=agend, headers=headers).json()["id"]
    return med_id, contato_id, agend_id


# ---------- Fluxo diário completo ----------

def test_fluxo_diario_completo(client, headers_a):
    _criar_stack(client, headers_a)

    doses = client.get("/api/doses/hoje", headers=headers_a).json()
    assert len(doses) == 1
    dose = doses[0]
    assert dose["status"] == "PENDENTE"

    r = client.put(f"/api/confirmacoes/{dose['confirmacao_id']}/confirmar", headers=headers_a)
    assert r.status_code == 200
    assert r.json()["status"] == "CONFIRMADO"


def test_doses_nao_duplicadas(client, headers_a):
    _criar_stack(client, headers_a)
    client.get("/api/doses/hoje", headers=headers_a)
    client.get("/api/doses/hoje", headers=headers_a)

    doses = client.get("/api/doses/hoje", headers=headers_a).json()
    assert len(doses) == 1


# ---------- Frequência semanal ----------

def test_agendamento_semanal_dia_correto(client, headers_a):
    """data_inicio = hoje → geração no mesmo dia da semana → gera dose."""
    _criar_stack(client, headers_a, frequencia="semanal")
    doses = client.get("/api/doses/hoje", headers=headers_a).json()
    assert len(doses) == 1


def test_agendamento_semanal_dia_errado(client, headers_a):
    """data_inicio = ontem → dia da semana diferente → não gera dose hoje."""
    med_id = client.post("/api/medicamentos", json=MED, headers=headers_a).json()["id"]
    ontem = (datetime.now(FUSO) - timedelta(days=1)).strftime("%Y-%m-%d")
    agend = {
        "id_medicamento": med_id,
        "horario": "08:00",
        "frequencia": "semanal",
        "data_inicio": ontem,
    }
    client.post("/api/agendamentos", json=agend, headers=headers_a)
    doses = client.get("/api/doses/hoje", headers=headers_a).json()
    assert len(doses) == 0


# ---------- Dose vencida gera notificação ----------

def test_dose_vencida_gera_notificacao(client, headers_a):
    from app.services.monitor_service import varrer_e_notificar

    _med_id, _contato_id, agend_id = _criar_stack(client, headers_a)

    # Cria confirmação com horário 1 hora atrás no timezone do usuário
    prevista = (datetime.now(FUSO) - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
    payload = {
        "id_agendamento": agend_id,
        "data_hora_prevista": prevista,
        "status": "PENDENTE",
    }
    r = client.post("/api/confirmacoes", json=payload, headers=headers_a)
    assert r.status_code == 201
    confirmacao_id = r.json()["id"]

    resultado = varrer_e_notificar()
    assert resultado["notificacoes_criadas"] >= 1
    assert resultado["confirmacoes_atualizadas"] >= 1

    r2 = client.get(f"/api/confirmacoes/{confirmacao_id}", headers=headers_a)
    assert r2.json()["status"] == "ATRASADO"

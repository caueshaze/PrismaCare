MED = {"nome": "Paracetamol", "dosagem": "500mg", "observacao": "Após refeição"}


def test_criar_medicamento_retorna_201(client, headers_a):
    r = client.post("/api/medicamentos", json=MED, headers=headers_a)
    assert r.status_code == 201
    body = r.json()
    assert body["nome"] == MED["nome"]
    assert body["dosagem"] == MED["dosagem"]


def test_listar_medicamentos(client, headers_a):
    client.post("/api/medicamentos", json=MED, headers=headers_a)
    r = client.get("/api/medicamentos", headers=headers_a)
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_buscar_medicamento_por_id(client, headers_a):
    med_id = client.post("/api/medicamentos", json=MED, headers=headers_a).json()["id"]
    r = client.get(f"/api/medicamentos/{med_id}", headers=headers_a)
    assert r.status_code == 200
    assert r.json()["id"] == med_id


def test_atualizar_medicamento(client, headers_a):
    med_id = client.post("/api/medicamentos", json=MED, headers=headers_a).json()["id"]
    atualizado = {**MED, "dosagem": "1000mg"}
    r = client.put(f"/api/medicamentos/{med_id}", json=atualizado, headers=headers_a)
    assert r.status_code == 200
    assert r.json()["dosagem"] == "1000mg"


def test_deletar_medicamento(client, headers_a):
    med_id = client.post("/api/medicamentos", json=MED, headers=headers_a).json()["id"]
    r = client.delete(f"/api/medicamentos/{med_id}", headers=headers_a)
    assert r.status_code == 200
    r2 = client.get(f"/api/medicamentos/{med_id}", headers=headers_a)
    assert r2.status_code == 404


def test_medicamento_inexistente_retorna_404(client, headers_a):
    r = client.get("/api/medicamentos/99999", headers=headers_a)
    assert r.status_code == 404

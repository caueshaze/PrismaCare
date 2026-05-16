CONTATO_VALIDO = {
    "nome": "Cuidador",
    "telefone": "11988880000",
    "parentesco": "Filho",
}


def test_criar_contato_com_telefone_invalido_retorna_422(client, headers_a):
    payload = {
        **CONTATO_VALIDO,
        "telefone": "abc",
    }

    r = client.post("/api/contatos", json=payload, headers=headers_a)

    assert r.status_code == 422
    assert "telefone" in r.text.lower()

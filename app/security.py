import bcrypt


def hash_senha(senha: str) -> str:
    """Criptografa a senha antes de salvar no banco."""
    senha_bytes = senha.encode("utf-8")
    hashed = bcrypt.hashpw(senha_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verificar_senha(senha: str, senha_hash: str) -> bool:
    """Verifica se a senha digitada bate com a senha salva no banco."""
    return bcrypt.checkpw(
        senha.encode("utf-8"),
        senha_hash.encode("utf-8")
    )
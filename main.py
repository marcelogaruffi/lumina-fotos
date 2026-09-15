from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import shutil
import os
import json
import numpy as np
import jwt
import hashlib
from datetime import datetime, timedelta, timezone
from database import supabase
from watermark import apply_watermark
from face_engine import extract_face_encoding, compare_faces

# Configurações de Segurança
SECRET_KEY = "paula_caldas_art_photography_super_secret"
ALGORITHM = "HS256"

app = FastAPI(title="Paula Caldas Fotografia")

os.makedirs("temp", exist_ok=True)
os.makedirs("static", exist_ok=True)

# Servindo as telas HTML
app.mount("/site", StaticFiles(directory="static", html=True), name="static")
import os
os.makedirs("biometria", exist_ok=True)
app.mount("/biometria", StaticFiles(directory="biometria"), name="biometria")

# ==========================================
# UTILITÁRIOS
# ==========================================
def hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode()).hexdigest()

def gerar_token(cliente_id: str) -> str:
    payload = {
        "sub": cliente_id,
        "exp": datetime.now(timezone.utc) + timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verificar_token(auth_header: str) -> str:
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Não autorizado")
    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")


# ==========================================
# ROTAS DE AUTENTICAÇÃO E CADASTRO
# ==========================================

class PayloadCadastro(BaseModel):
    nome: str
    cpf: str
    telefone: str
    email: str
    senha: str
    foto_frente: str
    foto_esquerda: str
    foto_direita: str

@app.post("/api/auth/cadastro-completo")
async def cadastro_completo(dados: PayloadCadastro):
    """Cria a conta do cliente e extrai os 3 ângulos do rosto da Base64"""
    import base64
    
    # 1. Checar se e-mail ou CPF já existem
    check = supabase.table("clientes").select("id").eq("email", dados.email).execute()
    if len(check.data) > 0:
        return {"sucesso": False, "erro": "E-mail já cadastrado."}
        
    # 2. Decodificar imagens Base64 e extrair faces (Isso vai ser pesado, mas é feito 1 vez)
    angulos = [dados.foto_frente, dados.foto_esquerda, dados.foto_direita]
    vetores = []
    
    for i, b64 in enumerate(angulos):
        try:
            # Remover cabeçalho 'data:image/jpeg;base64,'
            if "," in b64:
                b64 = b64.split(",")[1]
            img_data = base64.b64decode(b64)
            temp_path = f"temp/cad_{dados.cpf}_{i}.jpg"
            with open(temp_path, "wb") as f:
                f.write(img_data)
            
            # Extrair rosto
            vetor = extract_face_encoding(temp_path)
            if vetor:
                vetores.append(vetor)
            os.remove(temp_path)
        except Exception as e:
            print(f"Erro na extração facial: {e}")
            pass
            
    if not vetores:
        return {"sucesso": False, "erro": "Não encontramos nenhum rosto nítido nas fotos. Tente novamente em um local iluminado."}

    # 3. Salvar no banco
    db_data = {
        "nome": dados.nome,
        "email": dados.email,
        "telefone": dados.telefone,
        "cpf": dados.cpf,
        "senha_hash": hash_senha(dados.senha),
        "termos_aceitos_em": datetime.now(timezone.utc).isoformat(),
        "face_encodings": json.dumps(vetores)
    }
    
    try:
        supabase.table("clientes").insert(db_data).execute()
        return {"sucesso": True}
    except Exception as e:
        print(f"Erro interno: {e}")
        return {"sucesso": False, "erro": "Ocorreu um erro inesperado ao salvar seus dados. (Cód: ERR-CAD-02)"}


from fastapi import Header
from datetime import datetime, timedelta

def verificar_token_admin(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token admin ausente")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Acesso negado")
        return payload.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="Token admin invalido")

@app.post("/api/auth/admin-login")
def admin_login(email: str = Form(...), senha: str = Form(...)):
    res = supabase.table("admins").select("*").eq("email", email).execute()
    if not res.data: return {"sucesso": False, "erro": "Credenciais invalidas"}
    admin = res.data[0]
    if admin["senha"] != senha:
        return {"sucesso": False, "erro": "Credenciais invalidas"}
        
    token = jwt.encode({"sub": admin["id"], "role": "admin", "exp": datetime.utcnow() + timedelta(hours=12)}, SECRET_KEY, algorithm=ALGORITHM)
    return {"sucesso": True, "token": token}

@app.post("/api/auth/login")
async def login(email: str = Form(...), senha: str = Form(...)):
    senha_hasheada = hash_senha(senha)
    res = supabase.table("clientes").select("id").eq("email", email).eq("senha_hash", senha_hasheada).execute()
    
    if res.data and len(res.data) > 0:
        token = gerar_token(res.data[0]["id"])
        return {"sucesso": True, "token": token}
    return {"sucesso": False, "erro": "Usuário ou senha incorretos."}


# ==========================================
# ROTAS DO CLIENTE (MÁGICAS E CARRINHO)
# ==========================================

from fastapi import Header

@app.get("/api/cliente/eventos")
def listar_eventos_cliente():
    res = supabase.table("eventos").select("id, nome, data").order("data", desc=True).execute()
    return {"sucesso": True, "eventos": res.data}

@app.get("/api/cliente/fotos-evento/{evento_id}")
def fotos_evento(evento_id: str, authorization: str = Header(None)):
    verificar_token(authorization)
    res = supabase.table("fotos").select("id, url_marcada, preco").eq("evento_id", evento_id).execute()
    return {"sucesso": True, "fotos": res.data}

@app.get("/api/cliente/buscar-fotos-magica/{evento_id}")
def buscar_fotos_magica(evento_id: str, authorization: str = Header(None)):
    cliente_id = verificar_token(authorization)
    
    # 1. Pega os 3 vetores faciais do cliente no banco
    cliente = supabase.table("clientes").select("face_encodings").eq("id", cliente_id).execute()
    if not cliente.data or not cliente.data[0].get("face_encodings"):
        return {"sucesso": False, "erro": "Biometria não encontrada."}
        
    vetores_cliente = json.loads(cliente.data[0]["face_encodings"])
    
    # 2. Pega TODAS as fotos do evento que possuem rosto
    fotos_evento = supabase.table("fotos").select("id, url_marcada, face_encoding, preco").eq("evento_id", evento_id).execute()
    if not fotos_evento.data:
        return {"sucesso": True, "fotos": []}
        
    # 3. Cruzeamento em Memória (Rápido)
    known_encodings = []
    lista_fotos = []
    
    for f in fotos_evento.data:
        if f.get("face_encoding"):
            known_encodings.append(json.loads(f["face_encoding"]))
            lista_fotos.append(f)
            
    fotos_encontradas = []
    
    # Vamos testar cada ângulo do cliente contra o banco
    for vetor_angulo in vetores_cliente:
        if not known_encodings: break
        
        # Tolerância relaxada para 0.65 devido às luzes de palco (teatro)
        resultados = compare_faces(known_encodings, np.array(vetor_angulo), tolerance=0.65)
        for i, match in enumerate(resultados):
            if match and lista_fotos[i] not in fotos_encontradas:
                fotos_encontradas.append(lista_fotos[i])

    # Remover os vetores pesados do retorno JSON
    for f in fotos_encontradas:
        f.pop("face_encoding", None)

    return {"sucesso": True, "fotos": fotos_encontradas}

class Pedido(BaseModel):
    fotos_ids: list

@app.post("/api/cliente/pedido")
def criar_pedido(pedido: Pedido, authorization: str = Header(None)):
    cliente_id = verificar_token(authorization)
    
    # Pega preço total real das fotos
    total = 0
    for fid in pedido.fotos_ids:
        f = supabase.table("fotos").select("preco").eq("id", fid).execute()
        if f.data:
            total += float(f.data[0]["preco"])
            
    # Cria o pedido
    db_data = {
        "cliente_id": cliente_id,
        "fotos_ids": pedido.fotos_ids,
        "total": total,
        "status": "pendente"
    }
    supabase.table("pedidos").insert(db_data).execute()
    return {"sucesso": True}


@app.get("/api/cliente/perfil")
def ver_perfil(authorization: str = Header(None)):
    cliente_id = verificar_token(authorization)
    res = supabase.table("clientes").select("nome, email, telefone, cpf").eq("id", cliente_id).execute()
    return {"sucesso": True, "cliente": res.data[0]}

class PayloadPerfil(BaseModel):
    nome: str
    telefone: str

@app.put("/api/cliente/perfil")
def atualizar_perfil(dados: PayloadPerfil, authorization: str = Header(None)):
    cliente_id = verificar_token(authorization)
    supabase.table("clientes").update({"nome": dados.nome, "telefone": dados.telefone}).eq("id", cliente_id).execute()
    return {"sucesso": True}

class PayloadBio(BaseModel):
    foto_frente: str
    foto_esquerda: str
    foto_direita: str

@app.post("/api/cliente/atualizar-biometria")
def atualizar_biometria(dados: PayloadBio, authorization: str = Header(None)):
    cliente_id = verificar_token(authorization)
    import base64
    res_cpf = supabase.table("clientes").select("cpf").eq("id", cliente_id).execute()
    cpf_cliente = res_cpf.data[0]["cpf"]
    
    angulos = [dados.foto_frente, dados.foto_esquerda, dados.foto_direita]
    vetores = []
    
    for i, b64 in enumerate(angulos):
        try:
            if "," in b64: b64 = b64.split(",")[1]
            img_data = base64.b64decode(b64)
            temp_path = f"temp/upd_{cliente_id}_{i}.jpg"
            with open(temp_path, "wb") as f:
                f.write(img_data)
            
            vetor = extract_face_encoding(temp_path)
            if vetor: vetores.append(vetor)
            try:
                shutil.copy(temp_path, f"biometria/{cpf_cliente}_{i}.jpg")
            except: pass
            os.remove(temp_path)
        except: pass
            
    if not vetores:
        return {"sucesso": False, "erro": "Não encontramos rostos nítidos. (Cód: ERR-BIO-01)"}

    supabase.table("clientes").update({"face_encodings": json.dumps(vetores)}).eq("id", cliente_id).execute()
    return {"sucesso": True}

# ==========================================
# ROTAS DA ADMINISTRAÇÃO (FOTÓGRAFA PAULA)
# ==========================================

@app.post("/admin/eventos")
async def criar_evento_admin(nome: str = Form(...), data: str = Form(...), authorization: str = Header(None)):
    verificar_token_admin(authorization)
    try:
        res = supabase.table("eventos").insert({"nome": nome, "data": data}).execute()
        return {"sucesso": True, "evento": res.data}
    except Exception as e:
        print(f"Erro ao criar evento: {e}")
        return {"sucesso": False, "erro": "Falha ao registrar o evento no sistema. (Cód: ERR-EVT-01)"}

def process_and_upload_photo(evento_id: str, temp_path: str, filename: str):
    """Fila indiana: Processa IA e sobe para o banco (Síncrono para evitar deadlocks)"""
    watermark_path = f"temp/watermarked_{filename}"
    
    try:
        # 1. Aplicar Marca d'Água
        apply_watermark(temp_path, watermark_path)
        
        # 2. Extrair IA
        vector = extract_face_encoding(temp_path)
        
        # 3. Upload Original (Sem expor)
        with open(temp_path, "rb") as f:
            supabase.storage.from_("fotos-originais").upload(f"eventos/{evento_id}/{filename}", f, file_options={"content-type": "image/jpeg"})
        url_original = supabase.storage.from_("fotos-originais").get_public_url(f"eventos/{evento_id}/{filename}")
        
        # 4. Upload com Marca (Pública)
        with open(watermark_path, "rb") as f:
            supabase.storage.from_("fotos-marcadas").upload(f"eventos/{evento_id}/wm_{filename}", f, file_options={"content-type": "image/jpeg"})
        url_marcada = supabase.storage.from_("fotos-marcadas").get_public_url(f"eventos/{evento_id}/wm_{filename}")
        
        # 5. Salvar no Banco
        data = {
            "evento_id": evento_id,
            "url_original": url_original,
            "url_marcada": url_marcada,
            "face_encoding": json.dumps(vector) if vector else None,
            "preco": 15.00
        }
        supabase.table("fotos").insert(data).execute()
        
    except Exception as e:
        print(f"Erro no processamento da foto {filename}: {e}")
    finally:
        # Limpar lixo
        if os.path.exists(temp_path): os.remove(temp_path)
        if os.path.exists(watermark_path): os.remove(watermark_path)

@app.get("/api/admin/clientes")
def listar_clientes_admin(authorization: str = Header(None)):
    verificar_token_admin(authorization)
    res = supabase.table("clientes").select("id, nome, email, telefone, cpf").execute()
    return {"sucesso": True, "clientes": res.data}

@app.get("/api/admin/pedidos")
def listar_pedidos_admin(authorization: str = Header(None)):
    verificar_token_admin(authorization)
    res = supabase.table("pedidos").select("id, cliente_id, fotos_ids, total, status").execute()
    return {"sucesso": True, "pedidos": res.data}

@app.post("/admin/upload-foto")
async def upload_foto(evento_id: str = Form(...), foto: UploadFile = File(...)):
    temp_path = f"temp/{foto.filename}"
    with open(temp_path, "wb") as f:
        shutil.copyfileobj(foto.file, f)
    
    process_and_upload_photo(evento_id, temp_path, foto.filename)
    return {"mensagem": f"Foto processada com sucesso!"}


@app.get("/api/admin/eventos/{evento_id}/fotos")
def listar_fotos_evento_admin_nova(evento_id: str, authorization: str = Header(None)):
    verificar_token_admin(authorization)
    res = supabase.table("fotos").select("*").eq("evento_id", evento_id).execute()
    return {"sucesso": True, "fotos": res.data}

@app.delete("/api/admin/foto/{foto_id}")
def deletar_foto_admin_nova(foto_id: str, authorization: str = Header(None)):
    verificar_token_admin(authorization)
    supabase.table("fotos").delete().eq("id", foto_id).execute()
    return {"sucesso": True}

@app.get("/api/admin/pedido/{pedido_id}")
def detalhes_pedido_admin_nova(pedido_id: str, authorization: str = Header(None)):
    verificar_token_admin(authorization)
    res = supabase.table("pedidos").select("*").eq("id", pedido_id).execute()
    if not res.data: return {"sucesso": False}
    pedido = res.data[0]
    cliente_res = supabase.table("clientes").select("*").eq("id", pedido["cliente_id"]).execute()
    fotos_res = supabase.table("fotos").select("*").in_("id", pedido["fotos_ids"]).execute()
    return {"sucesso": True, "pedido": pedido, "cliente": cliente_res.data[0] if cliente_res.data else {}, "fotos": fotos_res.data}

@app.get("/api/cliente/minhas-compras")
def minhas_compras(authorization: str = Header(None)):
    cliente_id = verificar_token(authorization)
    res = supabase.table("pedidos").select("*").eq("cliente_id", cliente_id).execute()
    if not res.data: return {"sucesso": True, "pedidos": []}
    
    pedidos_com_fotos = []
    for p in res.data:
        f_res = supabase.table("fotos").select("*").in_("id", p["fotos_ids"]).execute()
        p["fotos"] = f_res.data
        pedidos_com_fotos.append(p)
        
    return {"sucesso": True, "pedidos": pedidos_com_fotos}


from fastapi import Query, Response

@app.get("/api/admin/foto/{foto_id}/original")
def ver_foto_original(foto_id: str, authorization: str = Query(None)):
    verificar_token_admin(f"Bearer {authorization}")
    res = supabase.table("fotos").select("url_original").eq("id", foto_id).execute()
    if not res.data: raise HTTPException(404)
    url_orig = res.data[0].get("url_original")
    if not url_orig: raise HTTPException(404)
    try:
        path = url_orig.split("/fotos-originais/")[1]
        file_data = supabase.storage.from_("fotos-originais").download(path)
        return Response(content=file_data, media_type="image/jpeg")
    except Exception as e:
        raise HTTPException(404, str(e))


@app.get("/api/cliente/eventos/{evento_id}/fotos")
def listar_fotos_evento_publico(evento_id: str):
    res = supabase.table("fotos").select("id, url_marcada, preco").eq("evento_id", evento_id).execute()
    return {"sucesso": True, "fotos": res.data}


@app.delete("/api/admin/pedido/{pedido_id}")
def deletar_pedido_admin(pedido_id: str, authorization: str = Header(None)):
    verificar_token_admin(authorization)
    try:
        supabase.table("pedidos").delete().eq("id", pedido_id).execute()
        return {"sucesso": True}
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}

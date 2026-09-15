import os
import re

print("Adicionando rota no backend...")
with open('main.py', 'r', encoding='utf-8') as f:
    main_py = f.read()

delete_evento_endpoint = """
@app.delete("/api/admin/evento/{evento_id}")
def deletar_evento_admin(evento_id: str, authorization: str = Header(None)):
    verificar_token_admin(authorization)
    try:
        supabase.table("eventos").delete().eq("id", evento_id).execute()
        return {"sucesso": True}
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}
"""
if "def deletar_evento_admin" not in main_py:
    with open('main.py', 'a', encoding='utf-8') as f:
        f.write("\n" + delete_evento_endpoint)

print("Modificando frontend admin.html...")
with open('static/admin.html', 'r', encoding='utf-8') as f:
    html = f.read()

js_delete_evento = """
        async function apagarEvento(id, nome) {
            if(!confirm(Tem certeza que deseja apagar o evento '' permanentemente?)) return;
            try {
                const res = await fetch(/api/admin/evento/, { method: "DELETE", headers: { "Authorization": "Bearer " + adminToken }});
                const data = await res.json();
                if(data.sucesso) {
                    carregarListaEventos();
                } else {
                    alert("Erro ao apagar evento.");
                }
            } catch(e) { alert(e); }
        }
"""
if "async function apagarEvento" not in html:
    html = html.replace('async function apagarPedido(id)', js_delete_evento + '\n        async function apagarPedido(id)')

# Adicionar o botao de lixeira no card
old_card = '''<div class="bg-white p-6 rounded-xl shadow-sm border border-[#EBEBEB] hover:shadow-md cursor-pointer transition flex flex-col justify-between" onclick="abrirEvento('', '')">
                            <h4 class="font-serif text-xl font-bold mb-2"></h4>
                            <p class="text-sm text-gray-400 mb-4"></p>
                            <button class="w-full py-2 bg-gray-50 text-[#C48B5D] font-bold rounded-lg hover:bg-[#F4EBE3] transition">Gerenciar Fotos</button>
                        </div>'''

new_card = '''<div class="bg-white p-6 rounded-xl shadow-sm border border-[#EBEBEB] hover:shadow-md cursor-pointer transition flex flex-col justify-between relative" onclick="abrirEvento('', '')">
                            <button onclick="event.stopPropagation(); apagarEvento('', '')" class="absolute top-4 right-4 w-8 h-8 flex items-center justify-center bg-red-50 text-red-500 rounded-full hover:bg-red-500 hover:text-white transition shadow-sm z-10" title="Apagar Evento">???</button>
                            <h4 class="font-serif text-xl font-bold mb-2 pr-6"></h4>
                            <p class="text-sm text-gray-400 mb-4"></p>
                            <button class="w-full py-2 bg-gray-50 text-[#C48B5D] font-bold rounded-lg hover:bg-[#F4EBE3] transition">Gerenciar Fotos</button>
                        </div>'''

html = html.replace(old_card, new_card)

with open('static/admin.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Sucesso!")

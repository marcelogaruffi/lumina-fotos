import os

with open('static/eventos.html', 'r', encoding='utf-8') as f:
    html = f.read()

lightbox_html = """
    <!-- Lightbox Cliente -->
    <div id="lightbox-cliente" class="fixed inset-0 bg-black/95 z-[100] hidden flex items-center justify-center backdrop-blur-sm">
        <button onclick="fecharLightboxCliente()" class="absolute top-6 right-8 text-white text-5xl hover:text-[#C48B5D] transition drop-shadow-lg">&times;</button>
        
        <button onclick="mudarFotoCliente(-1)" class="absolute left-4 md:left-12 top-1/2 -translate-y-1/2 text-white text-5xl hover:text-[#C48B5D] transition drop-shadow-lg">&#10094;</button>
        
        <img id="lightbox-cliente-img" src="" class="max-h-[90vh] max-w-[90vw] object-contain rounded-lg shadow-2xl transition-transform">
        
        <button onclick="mudarFotoCliente(1)" class="absolute right-4 md:right-12 top-1/2 -translate-y-1/2 text-white text-5xl hover:text-[#C48B5D] transition drop-shadow-lg">&#10095;</button>
        
        <!-- Carrinho Toggle no Lightbox -->
        <button onclick="toggleCartLightbox()" id="lightbox-cart-btn" class="absolute bottom-8 left-1/2 -translate-x-1/2 px-8 py-3 bg-white text-[#C48B5D] font-bold rounded-full shadow-xl hover:scale-105 transition flex items-center gap-2">
            ?? Adicionar
        </button>
    </div>
"""

if 'id="lightbox-cliente"' not in html:
    html = html.replace('</body>', lightbox_html + '\n</body>')

with open('static/eventos.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("HTML do Lightbox adicionado!")

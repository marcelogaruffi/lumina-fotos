import os

with open('static/eventos.html', 'r', encoding='utf-8') as f:
    html = f.read()

swipe_js = """
        // Swipe Logic
        let touchstartX = 0;
        let touchendX = 0;
        
        function handleGesture() {
            if (touchendX < touchstartX - 40) mudarFotoCliente(1); // Swipe left
            if (touchendX > touchstartX + 40) mudarFotoCliente(-1); // Swipe right
        }
        
        document.getElementById('lightbox-cliente').addEventListener('touchstart', e => {
            touchstartX = e.changedTouches[0].screenX;
        });
        
        document.getElementById('lightbox-cliente').addEventListener('touchend', e => {
            touchendX = e.changedTouches[0].screenX;
            handleGesture();
        });
"""

if "let touchstartX" not in html:
    html = html.replace('function tecladoLightboxCliente(e) {', swipe_js + '\n        function tecladoLightboxCliente(e) {')
    with open('static/eventos.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Swipe do Cliente adicionado!")

import os

with open('static/admin.html', 'r', encoding='utf-8') as f:
    html = f.read()

swipe_js = """
        let touchstartX = 0;
        let touchendX = 0;
        
        function handleGesture() {
            if (touchendX < touchstartX - 40) mudarFoto(1);
            if (touchendX > touchstartX + 40) mudarFoto(-1);
        }
        
        document.getElementById('lightbox').addEventListener('touchstart', e => {
            touchstartX = e.changedTouches[0].screenX;
        });
        
        document.getElementById('lightbox').addEventListener('touchend', e => {
            touchendX = e.changedTouches[0].screenX;
            handleGesture();
        });
"""

if "let touchstartX" not in html:
    html = html.replace('function fecharLightbox() {', swipe_js + '\n        function fecharLightbox() {')
    with open('static/admin.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Swipe do Admin adicionado!")

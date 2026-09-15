import os
import re

with open('static/cadastro_facial.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Make the page fit 100vh with no scrollbar
html = html.replace('<body class="min-h-screen flex items-center justify-center p-4">', '<body class="h-[100dvh] overflow-hidden flex flex-col items-center justify-center p-2 md:p-4">')
html = html.replace('<div class="glass-panel max-w-lg w-full p-8 text-center">', '<div class="glass-panel max-w-lg w-full p-4 md:p-6 text-center flex flex-col h-full max-h-full">')
# Adjust container spacing and video scaling
html = html.replace('<div class="camera-container mb-6 relative">', '<div class="camera-container flex-1 min-h-0 relative mb-4">')
html = html.replace('<video id="video" autoplay playsinline class="camera-video"></video>', '<video id="video" autoplay playsinline class="w-full h-full object-cover transform scale-x-[-1] rounded-lg"></video>')

# Update style.css overrides
with open('static/css/style.css', 'a', encoding='utf-8') as f:
    f.write('''
/* Mobile Opt - Camera */
.camera-container {
    height: 100%;
}
.oval-overlay {
    width: 60vw;
    height: 80vw;
    max-width: 200px;
    max-height: 280px;
}
''')

with open('static/cadastro_facial.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Camera facial arrumada!")

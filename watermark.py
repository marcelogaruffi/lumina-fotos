from PIL import Image, ImageDraw, ImageFont
import os

def apply_watermark(input_image_path: str, output_image_path: str, text: str = "PAULA CALDAS FOTOGRAFIA"):
    """
    Abre uma imagem, adiciona uma marca d'água enorme na horizontal e nas diagonais,
    e salva o resultado no caminho de destino.
    """
    try:
        # Abre a imagem original
        image = Image.open(input_image_path).convert("RGBA")
        width, height = image.size
        
        # Cria uma camada transparente para a marca d'agua
        txt_layer = Image.new("RGBA", image.size, (255, 255, 255, 0))
        
        # Calcula o tamanho da fonte para preencher 90% da largura
        try:
            # Aproximacao: a largura do texto em Arial e cerca de 55% do tamanho da fonte por caractere
            font_size = int((width * 0.95) / (len(text) * 0.55))
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()
            
        # Cria um canvas apenas para o texto (com margem para poder rotacionar sem cortar)
        temp_draw = ImageDraw.Draw(txt_layer)
        bbox = temp_draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        
        # Tamanho do canvas de texto
        text_canvas_w = int(text_w * 1.5)
        text_canvas_h = int(text_h * 3.0)
        text_img = Image.new("RGBA", (text_canvas_w, text_canvas_h), (255, 255, 255, 0))
        text_draw = ImageDraw.Draw(text_img)
        
        # Desenha o texto no canvas de texto (transparente e centralizado)
        # 128 = 50% de opacidade
        text_x = (text_canvas_w - text_w) / 2
        text_y = (text_canvas_h - text_h) / 2
        text_draw.text((text_x, text_y), text, font=font, fill=(255, 255, 255, 128))
        
        # --- 1. Horizontal (Centro) ---
        txt_layer.paste(text_img, (int((width - text_canvas_w) / 2), int((height - text_canvas_h) / 2)), text_img)
        
        # --- 2. Diagonal 1 (Top-Left para Bottom-Right) ---
        diag1 = text_img.rotate(45, expand=1)
        txt_layer.paste(diag1, (int((width - diag1.width) / 2), int((height - diag1.height) / 2)), diag1)
        
        # --- 3. Diagonal 2 (Bottom-Left para Top-Right) ---
        diag2 = text_img.rotate(-45, expand=1)
        txt_layer.paste(diag2, (int((width - diag2.width) / 2), int((height - diag2.height) / 2)), diag2)
        
        # Mescla a imagem original com a camada de texto
        watermarked = Image.alpha_composite(image, txt_layer)
        
        # Converte para RGB para salvar como JPEG (com boa qualidade)
        watermarked.convert("RGB").save(output_image_path, "JPEG", quality=90)
        
        print(f"Marca d'agua enorme e diagonal aplicada com sucesso: {output_image_path}")
        return True
        
    except Exception as e:
        print(f"Erro ao aplicar marca d'agua na imagem {input_image_path}: {e}")
        return False

if __name__ == "__main__":
    print("O script de marca d'agua está pronto para ser importado pela API.")

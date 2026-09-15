from PIL import Image, ImageDraw, ImageFont
import os

def apply_watermark(input_image_path: str, output_image_path: str, text: str = "PAULA CALDAS FOTOGRAFIA"):
    """
    Abre uma imagem, adiciona uma marca d'água de texto semitransparente centralizada
    e salva o resultado no caminho de destino.
    """
    try:
        # Abre a imagem original
        image = Image.open(input_image_path).convert("RGBA")
        width, height = image.size
        
        # Cria uma camada transparente para a marca d'água
        txt_layer = Image.new("RGBA", image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt_layer)
        
        # Tenta carregar a fonte Arial. O tamanho da fonte é dinâmico (proporcional à foto)
        font_size = int(height / 15)
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()
            
        # Calcula o tamanho do texto para centralizar
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        
        x = (width - text_w) / 2
        y = (height - text_h) / 2
        
        # Desenha o texto (Cor branca com 50% de transparência / alpha=128)
        draw.text((x, y), text, font=font, fill=(255, 255, 255, 128))
        
        # Mescla a imagem original com a camada de texto
        watermarked = Image.alpha_composite(image, txt_layer)
        
        # Converte para RGB para salvar como JPEG
        watermarked.convert("RGB").save(output_image_path, "JPEG")
        
        print(f"Marca d'água aplicada com sucesso: {output_image_path}")
        return True
        
    except Exception as e:
        print(f"Erro ao aplicar marca d'água na imagem {input_image_path}: {e}")
        return False

if __name__ == "__main__":
    print("O script de marca d'água está pronto para ser importado pela API.")

import face_recognition

def extract_face_encoding(image_path: str):
    """
    Recebe o caminho de uma imagem (Ex: a selfie do cliente ou uma foto tirada pela Paula),
    detecta o rosto e retorna o vetor numérico (face encoding) com 128 dimensões.
    """
    try:
        # Carrega a imagem do disco
        image = face_recognition.load_image_file(image_path)
        
        # Encontra as "assinaturas" de todos os rostos na foto
        encodings = face_recognition.face_encodings(image)
        
        if len(encodings) > 0:
            # Retorna o vetor numérico do primeiro rosto encontrado (convertido para lista normal do Python)
            print(f"Rosto detectado com sucesso em: {image_path}")
            return encodings[0].tolist()
        else:
            print(f"Nenhum rosto humano detectado na imagem: {image_path}")
            return None
            
    except Exception as e:
        print(f"Erro ao processar a imagem {image_path}: {e}")
        return None

def compare_faces(known_encodings: list, face_encoding_to_check: list, tolerance=0.6):
    """
    Compara o rosto enviado pelo cliente (face_encoding_to_check) com uma lista de 
    rostos salvos no banco de dados (known_encodings).
    
    Retorna uma lista de Verdadeiro/Falso. 
    A tolerância define o rigor: 0.6 é o padrão, menor = mais rigoroso.
    """
    return face_recognition.compare_faces(known_encodings, face_encoding_to_check, tolerance)

if __name__ == "__main__":
    print("O Motor de IA está pronto. Ele usa face_recognition (dlib) nos bastidores.")

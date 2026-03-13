import os
from PIL import Image

# Tamaño máximo permitido (10 KB)
MAX_SIZE = 10 * 1024 

def compress_images():
    # Obtener todas las imágenes de la carpeta actual
    for filename in os.listdir('.'):
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue
            
        filepath = os.path.join('.', filename)
        
        # Si ya pesa menos de 10kb, la ignoramos
        if os.path.getsize(filepath) <= MAX_SIZE:
            print(f"Ok: {filename} ya pesa menos de 10KB.")
            continue
            
        print(f"Comprimiendo {filename}...")
        try:
            with Image.open(filepath) as img:
                # Convertir a RGB por si tienen transparencias (en caso de guardarlas como JPG internamente o tratarlas)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                    
                temp_filename = filepath + ".tmp"
                
                scale = 1.0
                success = False
                
                # Intentar reducir progresivamente
                while not success and scale > 0.05:
                    new_w = max(int(img.width * scale), 1)
                    new_h = max(int(img.height * scale), 1)
                    
                    # Redimensionar la imagen
                    resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                    
                    if filename.lower().endswith('.png'):
                        # En PNG no hay nivel de calidad como tal, dependemos de reducir la resolución
                        resized.save(temp_filename, "PNG", optimize=True)
                        if os.path.getsize(temp_filename) <= MAX_SIZE:
                            success = True
                    else:
                        # En JPG podemos jugar con la compresión por calidad
                        for q in range(85, 4, -15):
                            resized.save(temp_filename, "JPEG", quality=q, optimize=True)
                            if os.path.getsize(temp_filename) <= MAX_SIZE:
                                success = True
                                break
                    
                    # Si no tuvimos éxito, reducimos la escala a la próxima iteración
                    if not success:
                        scale -= 0.15
                
                # Reemplazar el archivo original si logramos la meta
                if success:
                    os.replace(temp_filename, filepath)
                    print(f"  -> ¡Éxito! Nuevo tamaño: {os.path.getsize(filepath) / 1024:.2f} KB")
                else:
                    if os.path.exists(temp_filename):
                        os.remove(temp_filename)
                    print(f"  -> No se pudo reducir {filename} a menos de 10KB sin destruirla.")
        except Exception as e:
            print(f"Error procesando {filename}: {e}")

if __name__ == "__main__":
    print("Iniciando compresión de imágenes al límite de 10KB...")
    compress_images()
    print("¡Proceso finalizado!")

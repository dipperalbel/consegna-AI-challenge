from PIL import Image, ImageDraw, ImageFont
import json
import math

# --- Colori delle entità ---
entity_colors = {
    "VendorName": (255, 255, 0),
    "Address": (0, 191, 255),
    "PostalCode": (65, 105, 225),
    "Residence": (50, 205, 50),
    "PhoneNumber": (255, 20, 147),
    "FiscalCode": (255, 140, 0),
    "Category": (138, 43, 226),
    "IssueDate": (255, 215, 0),
    "Time": (0, 255, 255),
    "Total": (220, 20, 60),
    "TotalCashPayment": (255, 69, 0),
    "TermsOfPayment": (0, 128, 0),
    "Currency": (0, 0, 255),
    "default": (169, 169, 169)
}


# Funzione che colora i bounding box delle OCR in base alla confidenza
def get_confidence_color(confidence):
    if confidence >= 90:
        return (0, 255, 0, 255)
    elif confidence >= 70:
        return (255, 215, 0, 255)
    else:
        return (255, 0, 0, 255)



image_path = 'receipt_challenge_image.jpg'
json_path = 'receipt_challenge_response.json'

# Apre l'immagine della ricevuta e la converte in formato RGBA
image = Image.open(image_path).convert("RGBA")
w, h = image.size

# Definisce una larghezza extra da aggiungere a destra (per mostrare legenda)
extra_width = 800

# Crea una nuova immagine più larga, bianca, in formato RGBA
# La larghezza è quella originale più lo spazio extra
base_image = Image.new("RGBA", (w + extra_width, h), (255, 255, 255, 255))

# Incolla l'immagine originale nella parte sinistra della nuova immagine
base_image.paste(image, (0, 0))

# Crea un'immagine trasparente (overlay) della stessa dimensione della base_image
# Ha canale alpha = 0, quindi è completamente trasparente inizialmente
overlay = Image.new("RGBA", (w + extra_width, h), (255, 255, 255, 0))

# Crea uno strumento per disegnare sull'immagine trasparente (overlay)
draw_overlay = ImageDraw.Draw(overlay)

# Crea uno strumento per disegnare sull'immagine di base (base_image)
draw_base = ImageDraw.Draw(base_image)


# Carica due font (grande e piccolo) da usare per disegnare il testo sulle immagini.
try:
    font_big = ImageFont.truetype("arial.ttf", size=22)
    font_small = ImageFont.truetype("arial.ttf", size=12)
except:
    font_big = ImageFont.load_default()
    font_small = ImageFont.load_default()

# Apre il file JSON contenente i risultati OCR e le entità estratte e li slava in due variabili, entities ed ocr_data.
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)
    
entities = data['Pages'][0]['Entities']
ocr_data = data['Pages'][0]['Ocr']

# Creo dizionario per raccogliere le informazioni grafiche delle entità (colore, confidenza, posizione, coordinate), da usare per la legenda e il rendering
entity_render_info = {}

# La funzione crea una stella a 5 punte in una posizione specificata.
def draw_star(draw, cx, cy, size, color, opacity=160):
    points = []
    for i in range(10):
        angle = math.pi / 5 * i
        r = size if i % 2 == 0 else size * 0.4
        x = cx + r * math.sin(angle)
        y = cy - r * math.cos(angle)
        points.append((x, y))
    draw.polygon(points, fill=color + (opacity,))

# Nel loop, gestiamo il rendering delle entità
for key, entity in entities.items():
    # Verifica che l'entità esista e abbia una bounding box
    if entity and 'BoundingBox' in entity and entity['BoundingBox']:
        # Ottiene il colore associato al tipo di entità (o colore di default)
        color = entity_colors.get(key, entity_colors['default'])
        
        # Ottiene la confidenza e la arrotonda a 1 decimale
        confidence = round(entity.get("Confidence", 100.0), 1)

        # Estrae tutti i punti dei bounding box (alcune entità possono avere più box)
        all_points = [pt for box in entity['BoundingBox'] for pt in box]

        # Estrae le coordinate x e y separatamente
        x_coords = [pt[0] for pt in all_points]
        y_coords = [pt[1] for pt in all_points]

        # Calcoliamo gli estremi ed il centro del bounding box
        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)
        center_x = (min_x + max_x) // 2
        center_y = (min_y + max_y) // 2

        # Calcola larghezza, altezza e una dimensione di riferimento
        width = max_x - min_x
        height = max_y - min_y
        size = int(min(width, height) * 0.5)

        # Disegna forma diversa in base alla confidenza
        # Rettangolo semi-trasparente per confidenza sopra il 90 percento
        if confidence >= 90:
            draw_overlay.rectangle([min_x, min_y, max_x, max_y], fill=color + (100,))

        # Rombo per confidenza tra il 70 ed il 90 percento
        elif confidence >= 70:
            diamond = [
                (center_x, min_y),
                (max_x, center_y),
                (center_x, max_y),
                (min_x, center_y)
            ]
            draw_overlay.polygon(diamond, fill=color + (100,))

        # Stella per bassa confidenza (< 70%)
        else:
            draw_star(draw_overlay, center_x, center_y, size, color)
            
        # Salva info utili per legenda
        entity_render_info[key] = {
            "color": color,
            "confidence": confidence,
            "y": min_y,
            "x": min_x,
            "all_x": x_coords,
            "all_y": y_coords
        }

# Nel loop gestiamo le singole parole OCR
for ocr in ocr_data:
    # Estrae il bounding box e il testo riconosciuto
    box = ocr['BoundingBox']
    text = ocr['Text']

    # Estrae la confidenza del riconoscimento OCR (default 100 se non presente)
    confidence = ocr.get('Confidence', 0)

    # Determina il colore del bordo in base alla confidenza
    color = get_confidence_color(confidence)

    # Crea un poligono chiuso con i punti del bounding box
    polygon = [tuple(p) for p in box] + [tuple(box[0])]

    # Disegna il contorno della parola rilevata (linea chiusa)
    draw_overlay.line(polygon, fill=color, width=2)

    # Posizione e sfondo del testo OCR 
    # Coord. punto iniziale (in alto a sinistra del bounding box)
    x, y = box[0]

    # Calcola le dimensioni del testo da disegnare
    padding = 2
    text_bbox = font_small.getbbox(text)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    # Definisce il rettangolo di sfondo per il testo OCR (leggermente sopra la parola)
    background_box = [
        x - padding,
        y - 10 - padding,
        x + text_width + padding,
        y - 10 + text_height + padding
    ]

    # Disegna uno sfondo bianco semi-trasparente dietro al testo OCR
    draw_overlay.rectangle(background_box, fill=(255, 255, 255, 80))

    # Disegna il testo OCR in blu sopra lo sfondo
    draw_overlay.text((x, y - 10), text, fill=(0, 0, 255, 255), font=font_small)

# --- Composizione finale ---
# Uniamo l'immagine base e l'overlay trasparente in un'unica immagine finale
result = Image.alpha_composite(base_image, overlay)

# Crea uno strumento per disegnare sulla nuova immagine composita
draw_result = ImageDraw.Draw(result)


# Inizio X della legenda (nel margine bianco a destra)
legend_start_x = w + 10

# Larghezza della colonna della legenda
legend_width = 360

# Distanza dal bordo alto dell’immagine
legend_top_y = 20

# Spazio verticale tra sezioni della legenda
section_spacing = 40

# Funzione di utilità per "snappare" le posizioni verticali a una griglia ogni 10 pixel. Utile per l’allineamento visivo.
def round_to_grid(y, grid=10):
    return round(y / grid) * grid


# Ordina le entità per posizione: prima verticale (y), poi orizzontale (x)
sorted_entities = sorted(
    entity_render_info.items(),
    key=lambda item: (
        round_to_grid(sum(item[1]["all_y"]) / len(item[1]["all_y"])),
        sum(item[1]["all_x"]) / len(item[1]["all_x"])
    )
)

# --- LEGENDA ENTITÀ ---
# Calcola l'altezza totale della sezione legenda entità
legend_entity_height = 30 * len(sorted_entities) + 50
legend_entity_bottom = legend_top_y + legend_entity_height

# Disegna il contenitore della legenda (rettangolo bianco con bordo nero)
draw_result.rectangle(
    [legend_start_x, legend_top_y, legend_start_x + legend_width, legend_entity_bottom],
    fill=(255, 255, 255),     # Sfondo bianco
    outline=(0, 0, 0),        # Bordo nero
    width=2
)


# Scrive il titolo della sezione "Entità riconosciute"
draw_result.text(
    (legend_start_x + 10, legend_top_y + 10),
    "Entità (con confidenza):",
    fill=(0, 0, 0),
    font=font_big
)

# Posizione iniziale per il primo elemento della lista
current_y = legend_top_y + 40

# Cicla attraverso le entità ordinate per visualizzarle una per una
for key, info in sorted_entities:
    color = info['color']
    confidence = info['confidence']

    # Posizione dove disegnare la forma (es. rettangolo, rombo, stella)
    shape_x = legend_start_x + 10
    shape_y = current_y
    center_x = shape_x + 10
    center_y = shape_y + 10

    # Disegna la forma in base alla confidenza:
    if confidence >= 90:
        # Rettangolo pieno per alta confidenza
        draw_result.rectangle([shape_x, shape_y, shape_x + 20, shape_y + 20], fill=color + (255,))
    elif confidence >= 70:
        # Romba per confidenza media
        diamond = [
            (center_x, shape_y),
            (shape_x + 20, center_y),
            (center_x, shape_y + 20),
            (shape_x, center_y)
        ]
        draw_result.polygon(diamond, fill=color + (255,))
    else:
        # Stella per bassa confidenza
        draw_star(draw_result, center_x, center_y, 10, color, opacity=255)

    # Scrive il nome dell'entità e la confidenza accanto alla forma
    draw_result.text(
        (legend_start_x + 40, current_y),
        f"{key} ({confidence}%)",
        fill=(0, 0, 0),
        font=font_big
    )

    # Passa alla riga successiva
    current_y += 30



# --- LEGENDA OCR ---

# Posizione verticale di partenza della sezione OCR (dopo la legenda entità)
legend_ocr_y = legend_entity_bottom + section_spacing

# Altezza della sezione legenda OCR
legend_ocr_height = 130

# Disegna un rettangolo per contenere la legenda OCR (sfondo bianco, bordo nero)
draw_result.rectangle(
    [legend_start_x, legend_ocr_y, legend_start_x + legend_width, legend_ocr_y + legend_ocr_height],
    fill=(255, 255, 255),      # Sfondo bianco
    outline=(0, 0, 0),         # Bordo nero
    width=2
)

# Titolo della sezione OCR
draw_result.text(
    (legend_start_x + 10, legend_ocr_y + 10),
    "Confidenza OCR:",
    fill=(0, 0, 0),
    font=font_big
)

# Posizione iniziale per i simboli della legenda OCR
y = legend_ocr_y + 40

# --- Confidenza ≥ 90% (verde) ---
draw_result.rectangle([legend_start_x + 10, y, legend_start_x + 30, y + 20], fill=(0, 255, 0))
draw_result.text((legend_start_x + 40, y), "≥ 90%", fill=(0, 0, 0), font=font_big)

# Sposta verso il basso
y += 30

# --- Confidenza tra 70% e 90% (giallo oro) ---
draw_result.rectangle([legend_start_x + 10, y, legend_start_x + 30, y + 20], fill=(255, 215, 0))
draw_result.text((legend_start_x + 40, y), "70–90%", fill=(0, 0, 0), font=font_big)

# Sposta verso il basso
y += 30

# --- Confidenza < 70% (rosso) ---
draw_result.rectangle([legend_start_x + 10, y, legend_start_x + 30, y + 20], fill=(255, 0, 0))
draw_result.text((legend_start_x + 40, y), "< 70%", fill=(0, 0, 0), font=font_big)


# Salvataggio
result.convert("RGB").save("output.png")
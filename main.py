import io
import os
from PIL import Image, ImageDraw, ImageFont
import segno
from fpdf import FPDF
from qrjson import QRJsonGenerator

OUTPUT_PDF = "./_out/qrcodes_table.pdf"
DPI = 300
MM_TO_PX = 300 / 25.4
# to pod tym to jest  generuje jsony
#opcje generowania można zobaczyć w qrjson.py
generator = QRJsonGenerator()

generator.add_type(
    "shelf",
    ["shelf:MGZ/01/01", "shelf:MGZ/01/02", "shelf:MGZ/01/03"],
    width=30,
    height=60,
    margin_up=0.3,
    margin_down=0.3,
    margin_left=0.1,
    margin_right=0.1,
    text_size=0.1
)

generator.add_type(
    "mode",
    {"insert": "mode:insert", "remove": "mode:remove"},
    repeat=2
)

qr_config = generator.generate()


def generate_qr_images_from_json(config):
    result_files = []

    for qr_type, params in config.items():
        width_mm = params["width"]
        height_mm = params["height"]
        width_px = int(width_mm * MM_TO_PX)
        height_px = int(height_mm * MM_TO_PX)

        margin_top = int(params["margin_up"] * height_px)
        margin_bottom = int(params["margin_down"] * height_px)
        margin_left = int(params["margin_left"] * width_px)
        margin_right = int(params["margin_right"] * width_px)

        text_pos = params.get("text", "under")
        text_size_ratio = params.get("text_size", 0.15)

        for item in params["items"]:
            label = item["label"]
            qr_value = item["value"]

            qr = segno.make_qr(qr_value)
            qr_buffer = io.BytesIO()
            qr.save(qr_buffer, kind="png", scale=10, border=0)
            qr_buffer.seek(0)
            qr_img = Image.open(qr_buffer).convert("RGBA")

            canvas = Image.new("RGB", (width_px, height_px), "white")
            draw = ImageDraw.Draw(canvas)

            available_width = width_px - margin_left - margin_right
            available_height = height_px - margin_top - margin_bottom

            base_font = ImageFont.load_default()
            text_scale = int(text_size_ratio * min(available_width, available_height))
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", text_scale)

            bbox = draw.textbbox((0, 0), label, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]


            qr_side_px = int(min(available_width, available_height - text_h))
            qr_img = qr_img.resize((qr_side_px, qr_side_px), Image.Resampling.LANCZOS)

            qr_x = margin_left + (available_width - qr_side_px) // 2
            qr_y = margin_top if text_pos == "under" else margin_top + text_h
            canvas.paste(qr_img, (qr_x, qr_y))

            text_x = (width_px - text_w) // 2
            if text_pos == "under":
                text_y = height_px - margin_bottom + (margin_bottom - text_h) // 2
            else:
                text_y = (margin_top - text_h) // 2
            draw.text((text_x, text_y), label, font=font, fill="black")

            img_buffer = io.BytesIO()
            canvas.save(img_buffer, "PNG", dpi=(DPI, DPI))
            img_buffer.seek(0)

            result_files.append((label, img_buffer, (width_mm, height_mm)))

    return result_files


def generate_pdf(qr_items):
    pdf = FPDF("P", "mm", "A4")
    pdf.add_page()

    x, y = 10, 10
    row_height = 0
    current_size = None

    for label, img_buffer, size_mm in qr_items:
        w, h = size_mm

        if current_size != size_mm:
            x = 10
            y += row_height
            row_height = 0
            current_size = size_mm

        if x + w > 200:
            x = 10
            y += row_height
            row_height = 0

        if y + h > 280:
            pdf.add_page()
            x, y = 10, 10
            row_height = 0

        pdf.image(img_buffer, x=x, y=y, w=w, h=h)
        pdf.rect(x, y, w, h)

        x += w
        row_height = max(row_height, h)

    os.makedirs(os.path.dirname(OUTPUT_PDF), exist_ok=True)
    pdf.output(OUTPUT_PDF)
    print(f"{OUTPUT_PDF} generated")


if __name__ == "__main__":
    qr_imgs = generate_qr_images_from_json(qr_config)
    generate_pdf(qr_imgs)

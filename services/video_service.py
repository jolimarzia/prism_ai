from pathlib import Path
from core.config import DATA_DIR

# Video tmp folder
_video_tmp = DATA_DIR / "video_tmp"
_video_tmp.mkdir(exist_ok=True)


def _make_text_image(text: str, path: Path, size=(1280, 720)):
    """Render a scene as a 1280x720 image with centered wrapped text."""
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new("RGB", size, (12, 20, 38))
    draw = ImageDraw.Draw(img)

    # Try common fonts
    font = None
    for font_name in ["arial.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf"]:
        try:
            font = ImageFont.truetype(font_name, 48)
            break
        except Exception:
            continue
    if font is None:
        font = ImageFont.load_default()

    # Word-wrap
    words = text.split()
    lines, current = [], ""
    for w in words:
        test = (current + " " + w).strip()
        try:
            width = draw.textlength(test, font=font)
        except Exception:
            width = len(test) * 24
        if width < size[0] - 120:
            current = test
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)

    # Center vertically
    line_height = 60
    total_h = len(lines) * line_height
    y = (size[1] - total_h) // 2

    for line in lines:
        try:
            line_w = draw.textlength(line, font=font)
        except Exception:
            line_w = len(line) * 24
        x = (size[0] - line_w) / 2
        draw.text((x, y), line, font=font, fill=(230, 240, 255))
        y += line_height

    img.save(path)


def build_video(script_lines, out_name: str = "video.mp4",
                seconds_per_line: int = 3) -> Path:
    """Build an MP4 slideshow from a list of text lines."""
    from moviepy.editor import ImageClip, concatenate_videoclips

    clips = []
    for i, line in enumerate(script_lines):
        img_path = _video_tmp / f"scene_{i}.png"
        _make_text_image(line, img_path)
        clips.append(ImageClip(str(img_path)).set_duration(seconds_per_line))

    final = concatenate_videoclips(clips, method="compose")
    out_path = DATA_DIR / out_name
    final.write_videofile(
        str(out_path),
        fps=24,
        codec="libx264",
        audio=False,
        logger=None,
    )
    final.close()
    return out_path
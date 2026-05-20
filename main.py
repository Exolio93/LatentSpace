from datetime import datetime
from pathlib import Path

from src.schema import LatentSpace
from src.core import generate_newsletter
from src.render import render_newsletter


# def main():
#     unique_id = datetime.now().strftime("%Y%m%d_%H%M%S")
#     output_dir = Path(f"./outputs/{unique_id}")
#     output_dir.mkdir(parents=True, exist_ok=True)

#     newsletter_object = generate_newsletter()

#     with open(output_dir / "archive.json","w", encoding="utf-8") as f : 
#         f.write(newsletter_object.model_dump_json())

#     markdown_text = render_newsletter(newsletter_object)
#     with open(output_dir / "newsletter.md", "w", encoding="utf-8") as f : 
#         f.write(markdown_text)

def main():
    # 1. On cible précisément le dossier où se trouve ton archive
    output_dir = Path("./outputs/20260520_183237")
    archive_path = output_dir / "archive.json"
    
    with open(archive_path, "r", encoding="utf-8") as f:
        json_data = f.read()

    newsletter_object = LatentSpace.model_validate_json(json_data)
    markdown_text = render_newsletter(newsletter_object)

    output_file = output_dir / "newsletter.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(markdown_text)


if __name__ == "__main__":
    main()
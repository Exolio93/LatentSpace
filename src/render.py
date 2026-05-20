from jinja2 import Environment, FileSystemLoader
from src.schema import LatentSpace

def render_newsletter(newsletter_data: LatentSpace) -> str:

    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template("template_newsletter.md")
    rendered_text = template.render(
        data=newsletter_data
    )
    
    return rendered_text
# app/utils/pdf_generator.py

from jinja2 import Template
from pathlib import Path

# PDF生成にWeasyPrintを利用
from weasyprint import HTML

TEMPLATE = """
<h2>ペットレポート</h2>
<ul>
  <li><b>名前:</b> {{ pet_name }}</li>
  <li><b>種別:</b> {{ species }}</li>
  <li><b>品種:</b> {{ breed }}</li>
  <li><b>年齢:</b> {{ age }}</li>
  <li><b>要約:</b> {{ summary }}</li>
</ul>
"""

def generate_pdf_report(pet_name, species, breed, age, summary, report_id) -> str:
    """
    Jinja2でテンプレートをレンダリングし、WeasyPrintでPDF出力。
    ファイルパスを返す。
    """
    html_content = Template(TEMPLATE).render(
        pet_name=pet_name,
        species=species,
        breed=breed,
        age=age,
        summary=summary
    )

    output_path = f"./reports/{report_id}.pdf"
    Path("./reports").mkdir(exist_ok=True)
    HTML(string=html_content).write_pdf(output_path)

    return output_path

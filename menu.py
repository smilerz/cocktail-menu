import os

from reportlab.graphics import renderPDF, renderPM
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from svglib.svglib import svg2rlg

from utils import printable_date


# Function to load an SVG file, execute getStrings() method, find and replace text, and save as PNG
def convert_svg(input_file=None, output_file=None, file_format=None, options=None):
    # Load the SVG file as a ReportLab graphics object
    filetypes = ['gif', 'jpg', 'png', 'pdf']
    template_dir = os.path.join(os.getcwd(), 'templates')
    input_file = 'CocktailMenu.svg'
    output_file = 'CocktailMenu'
    output_type = 'svg'
    fonts = [
        {'name': 'DrawveticaMini', 'file': 'DrawveticaMini.ttf'},
        {'name': 'GrutchShaded', 'file': 'GrutchShaded.ttf'},
        {'name': 'Heavyweight', 'file': 'HEAVYWEI.TTF'},
        {'name': 'vtksnoise', 'file': 'vtksnoise.ttf'}
    ]

    date_text = {'date': 'Sept 20', 'superscript': 'txxh'}
    date, ordinal = printable_date(options.mp_date)
    text = []

    # Open file and read contents
    with open(os.path.join(template_dir, input_file)) as f:
        source = f.read()
        # update dates if they exist
    if d := date_text.get('date', None):
        source.replace(d, date)
    if d := date_text.get('superscript', None):
        source.replace(d, ordinal)
    with open(os.path.join(template_dir, 'temp.svg'), 'w') as f:
        f.write(source)

    # Register font files
    for f in fonts:
        pdfmetrics.registerFont(TTFont(f['name'], os.path.join(template_dir, f['file'])))

    # Import SVG
    drawing = svg2rlg(os.path.join(template_dir, 'temp.svg'))

    # find and replace text

    if output_type.lower() == 'pdf':
        renderPDF.drawToFile(drawing, os.path.join(template_dir, f'{output_file}.{output_type}'))
    else:
        renderPM.drawToFile(drawing, os.path.join(template_dir, f'{output_file}.{output_type}'), fmt=output_type)

    pass


# import fitz
# from svglib import svglib
# from reportlab.graphics import renderPDF

# # Convert svg to pdf in memory with svglib+reportlab
# # directly rendering to png does not support transparency nor scaling
# drawing = svglib.svg2rlg(path="input.svg")
# pdf = renderPDF.drawToString(drawing)

# # Open pdf with fitz (pyMuPdf) to convert to PNG
# doc = fitz.Document(stream=pdf)
# pix = doc.load_page(0).get_pixmap(alpha=True, dpi=300)
# pix.save("output.png")

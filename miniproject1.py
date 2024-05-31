import warnings
import re
import ebooklib
from ebooklib import epub
import requests
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


warnings.filterwarnings("ignore", message="In the future version we will turn default option ignore_ncx to True.")
warnings.filterwarnings("ignore", message="This search incorrectly ignores the root element, and will be fixed in a future version.")


def read_epub_file(file_path):
    book = epub.read_epub(file_path)
    return book


def get_book_info(book):
    title = ""
    authors = []

    for metadata in book.get_metadata('DC', 'title'):
        title = f'{metadata[0]}'

    for metadata in book.get_metadata('DC', 'creator'):
        authors.append(f'{metadata[0]}')

    return title, authors


def get_first_chapter(book, start_pattern, end_pattern):
    first_chapter_content = None
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            content = item.get_body_content()
            break

    text = content.decode('utf-8') if content else None

    pattern = re.compile(
        rf'{re.escape(start_pattern)}(.*?)\s*{re.escape(end_pattern)}',
        re.DOTALL)
    match = pattern.search(text)
    if match:
        return match.group(1)
    else:
        return None


def decode_paragraphs(text):
    paragraphs = text.replace("\n", " ").split('</p>')
    clean_paragraphs = [re.sub(r'<[^>]*>', '', paragraph).strip()
                        for paragraph in paragraphs
                        if paragraph.strip()]
    return clean_paragraphs


def evaluate_paragraph_lengths(paragraphs):
    paragraph_lengths = [len(paragraph.split()) for paragraph in paragraphs]
    return paragraph_lengths


def download_image(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return Image.open(BytesIO(response.content))
    except requests.exceptions.RequestException as e:
        print(f"Error downloading the image: {e}")
        return None
    except IOError as e:
        print(f"Error opening the image: {e}")
        return None


def combine_images(img_url, img_path):
    img1 = download_image(img_url)
    if img1 is None:
        raise SystemExit("Failed to download Picture #1")

    original_width, original_height = img1.size
    new_width, new_height = 1000, 700

    left = (original_width - new_width) / 2
    top = (original_height - new_height) / 2
    right = (original_width + new_width) / 2
    bottom = (original_height + new_height) / 2

    crop_box = (left, top, right, bottom)
    img1_cropped = img1.crop(crop_box)

    resize_dimensions = (800, 700)
    img1_resized = img1_cropped.resize(resize_dimensions)

    img2 = Image.open(img_path)

    angle = 45
    img2_rotated = img2.rotate(angle, expand=True)

    offset_x = 150
    offset_y = 150
    position = ((img1_cropped.width - img2_rotated.width) // 2 + offset_x,
                (img1_cropped.height - img2_rotated.height) // 2 + offset_y)

    final_image = img1_resized.copy()
    final_image.paste(img2_rotated, position, img2_rotated)

    final_image.save("final_image.png")

    return final_image


def plot_paragraph_lengths(paragraph_lengths, output_path):
    plt.figure(figsize=(10, 6))
    plt.hist(paragraph_lengths, bins=range(1, max(paragraph_lengths) + 2), edgecolor='black')
    plt.title('Distribution of Paragraph Lengths')
    plt.xlabel('Number of Words')
    plt.ylabel('Number of Paragraphs')
    plt.grid(True)
    plt.savefig(output_path)
    plt.close()


def create_word_document(title, authors, report_author, img1_path, paragraph_lengths, num_paragraphs, num_words, min_words, max_words, avg_words, output_path):
    document = Document()

    # Title page
    document.add_heading('Title Page', level=1)

    document.add_heading('Title of the Book', level=2)
    document.add_paragraph(title, style='IntenseQuote')

    document.add_heading('Author(s) of the Book', level=2)
    for author in authors:
        document.add_paragraph(author, style='IntenseQuote')

    document.add_heading('Author of the Report', level=2)
    document.add_paragraph(report_author, style='IntenseQuote')

    document.add_heading('Picture #1', level=2)
    document.add_picture(img1_path, width=Inches(6))

    document.add_page_break()

    # Info page
    document.add_heading('Info Page', level=1)

    plot_path = "paragraph_lengths_distribution.png"
    plot_paragraph_lengths(paragraph_lengths, plot_path)
    document.add_picture(plot_path, width=Inches(6))
    document.add_paragraph('Figure 1: Distribution of Paragraph Lengths', style='Caption')

    document.add_heading('Description of the Plot', level=2)
    document.add_paragraph(
        f'The plot above shows the distribution of paragraph lengths in the first chapter of the book. '
        f'There are {num_paragraphs} paragraphs, with a total of {num_words} words. '
        f'The shortest paragraph contains {min_words} words, and the longest paragraph contains {max_words} words. '
        f'The average paragraph length is {avg_words:.2f} words.'
    )

    document.save(output_path)


def main():
    file_path = 'book.epub'  # Path to your ePub file
    start_pattern = '<p class="ph1">'
    end_pattern = '<hr class="chap"/>'
    img_url = "https://cdn.thecollector.com/wp-content/uploads/2023/04/hp-lovecraft-cthulhu-mythos.jpg"
    img_path = "img2.png"
    report_author = "Jakub Moszyński"
    output_doc_path = "report.docx"

    book = read_epub_file(file_path)

    title, authors = get_book_info(book)

    first_chapter_text = get_first_chapter(book, start_pattern, end_pattern)

    first_chapter_paragraphs = decode_paragraphs(first_chapter_text)

    paragraph_lengths = evaluate_paragraph_lengths(first_chapter_paragraphs)

    num_paragraphs = len(first_chapter_paragraphs)
    num_words = sum(paragraph_lengths)
    min_words = min(paragraph_lengths) if paragraph_lengths else 0
    max_words = max(paragraph_lengths) if paragraph_lengths else 0
    avg_words = num_words / num_paragraphs if num_paragraphs > 0 else 0

    final_image = combine_images(img_url, img_path)

    create_word_document(title, authors, report_author, "final_image.png", paragraph_lengths, num_paragraphs, num_words, min_words, max_words, avg_words, output_doc_path)

    print(title)
    print(authors)
    print(paragraph_lengths)


if __name__ == '__main__':
    main()

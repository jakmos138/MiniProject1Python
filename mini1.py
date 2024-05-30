import warnings
import re
import ebooklib
from ebooklib import epub

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
            # Assuming the first chapter is the first document in the ePub
            first_chapter_content = item.get_body_content()
            break
    
    text = first_chapter_content.decode('utf-8') if first_chapter_content else None

    pattern = re.compile(rf'{re.escape(start_pattern)}(.*?)\s*{re.escape(end_pattern)}', re.DOTALL)
    match = pattern.search(text)
    if match:
        return match.group(1)
    else:
        return None


def decode_paragraphs(text):
    paragraphs = text.replace("\n", " ").split('</p>')
    clean_paragraphs = [re.sub(r'<[^>]*>', '', paragraph).strip() for paragraph in paragraphs if paragraph.strip()]
    return clean_paragraphs


def evaluate_paragraph_lengths(paragraphs):
    paragraph_lengths = [len(paragraph.split()) for paragraph in paragraphs]
    return paragraph_lengths


def main():
    file_path = 'book.epub'  # Path to your ePub file
    start_pattern = '<p class="ph1">'
    end_pattern = '<hr class="chap"/>'
    # Read the ePub file
    book = read_epub_file(file_path)
    
    # Display the structure of the book
    title, authors = get_book_info(book)

    first_chapter_text = get_first_chapter(book, start_pattern, end_pattern)

    first_chapter_paragraphs = decode_paragraphs(first_chapter_text)

    # Evaluate paragraph lengths
    paragraph_lengths = evaluate_paragraph_lengths(first_chapter_paragraphs)

    print(title)
    print(authors)
    print(paragraph_lengths)


if __name__ == '__main__':
    main()

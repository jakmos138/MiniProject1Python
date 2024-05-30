import warnings
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

warnings.filterwarnings("ignore", message="In the future version we will turn default option ignore_ncx to True.")
warnings.filterwarnings("ignore", message="This search incorrectly ignores the root element, and will be fixed in a future version.")


def read_epub_file(file_path):
    book = epub.read_epub(file_path)
    return book


def display_book_structure(book):
    # Print Metadata
    print("\nTitle:")
    for metadata in book.get_metadata('DC', 'title'):
        print(f'{metadata[0]}')

    print("\nAuthors:")
    for metadata in book.get_metadata('DC', 'creator'):
        print(f'{metadata[0]}')


def main():
    file_path = 'book.epub'  # Path to your ePub file
    
    # Read the ePub file
    book = read_epub_file(file_path)
    
    # Display the structure of the book
    display_book_structure(book)


if __name__ == '__main__':
    main()

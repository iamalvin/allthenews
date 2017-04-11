from bs4 import BeautifulSoup

def normalise(text):
    no_html = BeautifulSoup(text).get_text()
    return no_html
    

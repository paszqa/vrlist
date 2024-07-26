import requests
from bs4 import BeautifulSoup

def wipe_file(filename):
    with open(filename, 'w') as file:
        file.write("")

def scrape_gg_deals(filename):
    base_url = "https://gg.deals/search/?platform=1&tag=146&type=1&page="
    pages = 99
    
    with open(filename, 'a') as file:
        for page in range(1, pages + 1):
            url = base_url + str(page)
            try:
                response = requests.get(url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                game_titles = soup.find_all('a', class_='game-info-title title')
                
                for title in game_titles:
                    game_name = title.get_text(strip=True)
                    game_link = title.get('href', 'N/A')
                    file.write(f"{game_name};{game_link}\n")
                
                print(f"Page {page} processed.")
            except requests.exceptions.RequestException as e:
                print(f"An error occurred while processing page {page}: {e}")

if __name__ == "__main__":
    filename = "gglist"
    
    # Wipe the content of the file
    wipe_file(filename)
    
    # Scrape the data and write to the file
    scrape_gg_deals(filename)
    
    print("Scraping completed.")

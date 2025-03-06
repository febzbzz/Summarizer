from newspaper import Article
import nltk

nltk.download('punkt')

def summarize_and_save(url, filename="news_summary.txt"):
    try:
        article = Article(url)
        article.download()
        article.parse()
        article.nlp()  # Summarize the article

        with open(filename, "w", encoding="utf-8") as file:
            file.write(f"Title: {article.title}\n\n")
            file.write(f"Summary:\n{article.summary}\n")

        print("\nTitle:", article.title)
        print("\nSummary:\n", article.summary)
        print(f"\nSummary saved as {filename}")

    except Exception as e:
        print("\nError:", e)
        print("❌ The article could not be downloaded. Please try another URL.")

# Ask user to enter a news article URL
url = input("Enter a news article URL: ")
summarize_and_save(url)

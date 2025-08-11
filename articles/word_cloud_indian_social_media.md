---
title: Visualizing Indian Social Media Text with Word Clouds
seo_description: Build meaningful word clouds from UPI, IRCTC and cricket chatter using Python.
suggested_tags:
  - WordCloud
  - Python
  - Data Visualization
  - Social Media Analytics
  - Indian Data
canonical_url: ""
author: Praveen
---
# Visualizing Indian Social Media Text with Word Clouds

*Inspired by best practices on Medium such as [Building Resilient Data Systems: Key Lessons from Veronika Durgin](https://medium.com/@odsc/building-resilient-data-systems-key-lessons-from-veronika-durgin-675032360d9b).* 

> **Series Note:** This tutorial is part of my "Indian Data Viz" series. Make sure to read [Part 1: Collecting Indian Social Media Text](https://medium.com/python-in-plain-english/zero-to-hero-in-python-in-30-days-day-15-list-methods-5d221bdbf3a6) to follow the flow.

## TL;DR

- Word clouds turn text frequency into a visual summary.
- `wordcloud` and `matplotlib` make generation easy.
- Real Indian scenarios: UPI payments, IRCTC reviews, cricket commentary.
- Mini projects help you practice with Mumbai weather and UPI feedback data.
- Carefully chosen stopwords and preprocessing yield clearer visuals.

---

## Why Word Clouds Matter for Indian Social Media Data

India's digital ecosystem – from **UPI** transactions to **IRCTC** ticket reviews – generates enormous text streams daily. Visualizing this text as a word cloud instantly surfaces trends like popular destinations, payment issues or cricketer mentions. The approach mirrors story-driven articles on Medium, giving readers context before code.

---

## Mini Project 1: Mumbai Weather Tweets

### GOAL
Turn a week of Mumbai weather tweets into a quick, colourful word cloud.

### PREREQS
- Python 3
- Libraries: `wordcloud`, `matplotlib`, `pandas`
- CSV file `mumbai_weather_tweets.csv` with column `tweet_text`

### STEP-BY-STEP
1. Load tweets with pandas.
2. Combine them into one string.
3. Remove stopwords (`rt`, `https`, `co`).
4. Generate the cloud.
5. Display with matplotlib.

### CODE
```python
import pandas as pd
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

df = pd.read_csv('mumbai_weather_tweets.csv')
text = ' '.join(df.tweet_text)
stopwords = set(STOPWORDS)
stopwords.update(['rt', 'https', 'co'])
wordcloud = WordCloud(width=800, height=400,
                      background_color='white',
                      stopwords=stopwords,
                      min_font_size=10).generate(text)
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.show()
```

### SAMPLE INPUT
`"Mumbai weather is humid today, heavy rains expected."`
`"Stay safe Mumbai! Rain alert for the next 3 days."`

### SAMPLE OUTPUT
Word cloud highlighting "Mumbai", "rain", "humid" and other keywords.

### What could go wrong?
- Wrong CSV path → FileNotFoundError
- Over-aggressive stopwords → Empty or sparse cloud
- Too little text → Uninformative visual

---

## Mini Project 2: UPI Transaction Feedback Cloud

### GOAL
Spot common sentiments from UPI payment feedback.

### PREREQS
- Python 3
- Libraries: `wordcloud`, `matplotlib`
- Text file `upi_feedback.txt`

### STEP-BY-STEP
1. Read the text file.
2. Add payment-domain stopwords ("transaction", "payment", "upi", "app").
3. Generate and display the cloud.

### CODE
```python
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

with open('upi_feedback.txt', 'r', encoding='utf-8') as file:
    text = file.read()
stopwords = set(STOPWORDS)
stopwords.update(['transaction', 'payment', 'upi', 'app'])
wordcloud = WordCloud(width=800, height=800,
                      background_color='white',
                      stopwords=stopwords,
                      min_font_size=10).generate(text)
plt.figure(figsize=(8, 8))
plt.imshow(wordcloud)
plt.axis('off')
plt.tight_layout(pad=0)
plt.show()
```

### SAMPLE INPUT
`"UPI app crashes during payment"`
`"Successful transaction but delayed confirmation"`

### SAMPLE OUTPUT
Prominent words like "crashes", "delayed" and "confirmation".

### What could go wrong?
- Encoding issues → `UnicodeDecodeError`
- Excess stopwords → Missing useful terms
- Small dataset → Bland visuals

---

## Deep Dive: Cleaning Text for Better Clouds

Quality word clouds rely on smart preprocessing:

- **Lowercase text** for uniformity.
- **Strip URLs, mentions and hashtags** that clutter the cloud.
- **Remove numbers and punctuation** unless they carry meaning.
- **Extend stopwords** with domain-specific terms like `{"upi", "transaction", "co", "rt", "india", "pay"}`.

This approach keeps the visual focused on actionable words rather than noise – a technique often highlighted in leading Medium tutorials.

---

## Troubleshooting & FAQ

- **Few or no words?** Ensure your text isn't empty and stopwords aren't overly broad.
- **Unicode errors?** Read files with `encoding='utf-8'`.
- **Hindi or other languages?** Provide language-specific stopwords and fonts.
- **Too cluttered?** Increase `min_font_size` or cap words with `max_words`.

---

## Keep Exploring

This post is part of a larger journey into Indian data visualization. For the next installment and more real-world guides, follow along.

**Connect with me**: [LinkedIn](https://www.linkedin.com/in/iampraveenkr/) | [GitHub](https://github.com/krpraveen0)

---

*Praveen's Checklist*
- Clean and preprocess text
- Tailor stopwords to the domain
- Start small, then scale
- Iterate visuals for clarity
- Keep projects reproducible

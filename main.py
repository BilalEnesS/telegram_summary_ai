import requests
import feedparser
import openai
import telegram
from telegram import Bot
import schedule
import time
from datetime import datetime, timedelta
import json
import os
from bs4 import BeautifulSoup
import re
import dotenv

class AILiteratureScanner:
    def __init__(self, telegram_token, telegram_chat_id, openai_api_key):
        self.telegram_bot = Bot(token=telegram_token)
        self.chat_id = telegram_chat_id
        openai.api_key = openai_api_key
        
        # Akademik kaynak RSS feeds
        self.academic_feeds = [
            "http://export.arxiv.org/rss/cs.AI",  # ArXiv AI
            "http://export.arxiv.org/rss/cs.CL",  # Computational Linguistics
            "http://export.arxiv.org/rss/cs.CV",  # Computer Vision
            "http://export.arxiv.org/rss/cs.LG",  # Machine Learning
            "http://export.arxiv.org/rss/cs.NE"   # Neural Networks
        ]
        
        # News Sources
        self.news_sources = [
            {"name": "AI News", "url": "https://www.artificialintelligence-news.com/feed/"},
            {"name": "VentureBeat AI", "url": "https://venturebeat.com/ai/feed/"},
            {"name": "The Batch", "url": "https://www.deeplearning.ai/the-batch/feed/"}
        ]
        
        # Blog Sources
        self.blog_sources = [
            {"name": "OpenAI Blog", "url": "https://openai.com/blog/rss.xml"},
            {"name": "Google AI Blog", "url": "https://ai.googleblog.com/feeds/posts/default"},
            {"name": "DeepMind Blog", "url": "https://deepmind.com/blog/rss.xml"},
            {"name": "Anthropic Blog", "url": "https://www.anthropic.com/news/rss.xml"}
        ]

    def get_today_papers(self):
        """Fetch today's AI papers from ArXiv"""
        today = datetime.now().strftime("%Y-%m-%d")
        papers = []
        
        for feed_url in self.academic_feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries:
                    # Filter for papers published today
                    pub_date = datetime(*entry.published_parsed[:6]).strftime("%Y-%m-%d")
                    if pub_date == today:
                        papers.append({
                            "title": entry.title,
                            "authors": entry.author if hasattr(entry, 'author') else "Bilinmeyen",
                            "abstract": entry.summary,
                            "link": entry.link,
                            "source": "ArXiv",
                            "category": self.get_category_from_url(feed_url)
                        })
            except Exception as e:
                print(f"Feed okuma hatası {feed_url}: {e}")
                
        return papers

    def get_today_news(self):
        """Fetch AI news"""
        today = datetime.now().date()
        news_items = []
        
        all_sources = self.news_sources + self.blog_sources
        
        for source in all_sources:
            try:
                feed = feedparser.parse(source["url"])
                for entry in feed.entries:
                    # Get news from the last 24 hours
                    if hasattr(entry, 'published_parsed'):
                        pub_date = datetime(*entry.published_parsed[:6]).date()
                        if pub_date >= today - timedelta(days=1):
                            news_items.append({
                                "title": entry.title,
                                "summary": entry.summary if hasattr(entry, 'summary') else entry.title,
                                "link": entry.link,
                                "source": source["name"],
                                "date": pub_date.strftime("%Y-%m-%d")
                            })
            except Exception as e:
                print(f"Haber kaynağı okuma hatası {source['name']}: {e}")
                
        return news_items

    def get_category_from_url(self, url):
        """Extract category from URL"""
        if "cs.AI" in url:
            return "Artificial Intelligence"
        elif "cs.CL" in url:
            return "Natural Language Processing"
        elif "cs.CV" in url:
            return "Computer Vision"
        elif "cs.LG" in url:
            return "Machine Learning"
        elif "cs.NE" in url:
            return "Neural Networks"
        return "AI General"

    def summarize_with_llm(self, content, content_type="paper"):
        """Summarize content using LLM"""
        if content_type == "paper":
            prompt = f"""
            Summarize the following academic paper in Turkish:
            
            Title: {content['title']}
            Authors: {content['authors']}
            Abstract: {content['abstract']}
            
            Please summarize in this format:
            - Main topic and novelty
            - Used methods
            - Results obtained
            - Practical applications
            
            Maximum 150 words.
            """
        else:  # news
            prompt = f"""
            Summarize the following AI news in Turkish:
            
            Title: {content['title']}
            Content: {content['summary']}
            
            Highlight the main points and importance for the AI world.
            Maximum 100 words.
            """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"LLM summarization error: {e}")
            return content.get('abstract', content.get('summary', ''))[:200] + "..."

    def create_daily_report(self):
        """Create daily report"""
        papers = self.get_today_papers()
        news = self.get_today_news()
        
        report = f"🤖 **AI Daily Report - {datetime.now().strftime('%d.%m.%Y')}**\n\n"
        
        # Papers section
        if papers:
            report += f"📚 **New Academic Papers ({len(papers)} papers)**\n\n"
            for i, paper in enumerate(papers[:5], 1):  # Max 5 papers
                summary = self.summarize_with_llm(paper, "paper")
                report += f"**{i}. {paper['title']}**\n"
                report += f"👥 Authors: {paper['authors']}\n"
                report += f"📂 Category: {paper['category']}\n"
                report += f"📄 Abstract: {summary}\n"
                report += f"🔗 [Read Paper]({paper['link']})\n\n"
        else:
            report += "📚 **No new academic papers today**\n\n"
        
        # News section
        if news:
            report += f"📰 **AI News ({len(news)} articles)**\n\n"
            for i, article in enumerate(news[:8], 1):  # Max 8 news
                summary = self.summarize_with_llm(article, "news")
                report += f"**{i}. {article['title']}**\n"
                report += f"📰 Source: {article['source']}\n"
                report += f"📝 Summary: {summary}\n"
                report += f"🔗 [Read News]({article['link']})\n\n"
        else:
            report += "📰 **No AI news today**\n\n"
        
        # Footer
        report += f"⏰ Report generation time: {datetime.now().strftime('%H:%M')}\n"
        report += "🔄 Next report will be sent tomorrow at the same time...\n"
        
        return report

    def send_to_telegram(self, message):
        """Send message to Telegram"""
        try:
            # Split message into parts (Telegram 4096 character limit)
            max_length = 4000
            if len(message) <= max_length:
                result = self.telegram_bot.send_message(
                    chat_id=self.chat_id, 
                    text=message, 
                    parse_mode=telegram.ParseMode.MARKDOWN,
                    disable_web_page_preview=True
                )
                print(f"✅ Message sent (ID: {result.message_id})")
            else:
                # Split long messages
                parts = []
                current_part = ""
                lines = message.split('\n')
                
                for line in lines:
                    if len(current_part + line + '\n') <= max_length:
                        current_part += line + '\n'
                    else:
                        parts.append(current_part)
                        current_part = line + '\n'
                
                if current_part:
                    parts.append(current_part)
                
                for i, part in enumerate(parts):
                    header = f"📋 Report Section {i+1}/{len(parts)}\n\n" if i > 0 else ""
                    result = self.telegram_bot.send_message(
                        chat_id=self.chat_id, 
                        text=header + part, 
                        parse_mode=telegram.ParseMode.MARKDOWN,
                        disable_web_page_preview=True
                    )
                    print(f"✅ Report part {i+1} sent (ID: {result.message_id})")
                    time.sleep(1)  # Rate limiting
                    
        except telegram.error.BadRequest as e:
            if "can't parse entities" in str(e).lower():
                print("⚠️ Markdown parse error, sending as plain text...")
                # Retry without markdown
                self.telegram_bot.send_message(
                    chat_id=self.chat_id, 
                    text=message,
                    disable_web_page_preview=True
                )
            else:
                print(f"❌ Telegram BadRequest error: {e}")
        except Exception as e:
            print(f"❌ Telegram sending error: {e}")
            # Chat ID check
            if "chat not found" in str(e).lower():
                print("💡 Chat ID might be incorrect. Send /start to the bot and check your chat ID.")

    def daily_scan(self):
        """Daily scanning function"""
        print(f"Daily scan started: {datetime.now()}")
        try:
            report = self.create_daily_report()
            self.send_to_telegram(report)
            print("Daily report successfully sent!")
        except Exception as e:
            print(f"Daily scan error: {e}")
            error_msg = f"❌ Error creating daily report: {str(e)}"
            self.send_to_telegram(error_msg)

    def start_scheduler(self):
        """Start the scheduler"""
        # Run once immediately
        self.daily_scan()

        # Schedule to run every 12 hours (e.g., at 09:00 and 21:00)
        schedule.every().day.at("09:00").do(self.daily_scan)
        schedule.every().day.at("21:00").do(self.daily_scan)

        print("AI Literatür Tarayıcısı başlatıldı!")
        print("Günlük raporlar her gün 09:00 ve 21:00'da gönderilecek.")

        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    def test_telegram_connection(self):
        """Test Telegram connection"""
        try:
            # Get bot info
            bot_info = self.telegram_bot.get_me()
            print(f"✅ Bot connection successful: {bot_info.username}")
            
            # Send test message
            test_message = f"🔧 Test message - {datetime.now().strftime('%H:%M:%S')}"
            result = self.telegram_bot.send_message(
                chat_id=self.chat_id, 
                text=test_message
            )
            print(f"✅ Test message sent: {result.message_id}")
            return True
        except telegram.error.Unauthorized:
            print("❌ Bot token invalid!")
            return False
        except telegram.error.BadRequest as e:
            if "chat not found" in str(e).lower():
                print(f"❌ Chat ID not found: {self.chat_id}")
                print("💡 Solution: Send /start to the bot and use the correct chat ID")
            else:
                print(f"❌ Telegram API error: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False

    def get_chat_id(self):
        """Get the chat ID of the user interacting with the bot"""
        try:
            url = f"https://api.telegram.org/bot{self.telegram_bot.token}/getUpdates"
            response = requests.get(url)
            data = response.json()
            
            if data["ok"] and data["result"]:
                # Get chat ID from the last message
                last_update = data["result"][-1]
                chat_id = last_update["message"]["chat"]["id"]
                user_name = last_update["message"]["from"].get("first_name", "Unknown")
                print(f"💬 Chat ID found: {chat_id} (User: {user_name})")
                return str(chat_id)
            else:
                print("❌ No conversation with the bot yet.")
                print("💡 Solution: Go to t.me/ainewssum_bot and send /start")
                return None
        except Exception as e:
            print(f"❌ Error getting chat ID: {e}")
            return None

def main():
    # Load .env file
    dotenv.load_dotenv()
    
    # Configuration
    config = {
        "telegram_token": os.getenv("TELEGRAM_BOT_TOKEN"),
        "telegram_chat_id": os.getenv("TELEGRAM_CHAT_ID"),
        "openai_api_key": os.getenv("OPENAI_API_KEY")
    }
    
    # Auto-detect chat ID
    if config["telegram_chat_id"] == "AUTO_DETECT":
        temp_bot = Bot(token=config["telegram_token"])
        temp_scanner = AILiteratureScanner(
            telegram_token=config["telegram_token"],
            telegram_chat_id="0",
            openai_api_key=config["openai_api_key"]
        )
        chat_id = temp_scanner.get_chat_id()
        if chat_id:
            config["telegram_chat_id"] = chat_id
            print(f"✅ Chat ID auto-detected: {chat_id}")
        else:
            print("❌ Chat ID not found. Please send a message to the bot and try again.")
            return
    
    # Start scanner
    scanner = AILiteratureScanner(
        telegram_token=config["telegram_token"],
        telegram_chat_id=config["telegram_chat_id"], 
        openai_api_key=config["openai_api_key"]
    )
    
    scanner.start_scheduler()

if __name__ == "__main__":
    main()
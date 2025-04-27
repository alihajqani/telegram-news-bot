from dotenv import load_dotenv; load_dotenv()
from app.flows.newsflow import NewsFlow

if __name__ == "__main__":
    flow = NewsFlow()
    flow.kickoff()

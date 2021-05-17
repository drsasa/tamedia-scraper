from datetime import datetime
from celery.utils.log import get_task_logger
from worker import app
from utils import get_url_content, generate_sql_upsert


logger = get_task_logger(__name__)


@app.task(name="fetch_source", queue="scraping", priority=0)
def fetch_source():
    """
    Task for getting list of article - we will fetch list of today articles
    """
    year = datetime.now().year
    month = str(datetime.now().month).zfill(2)
    day = str(datetime.now().day).zfill(2)

    url = f"https://feed-prod.unitycms.io/2/categoryHistory/6/{year}/{month}/{day}"

    result = get_url_content(url)
    if result["status"] == "error":
        error_log.s(result["data"]).apply_async()
        return

    map_source.s(result["data"]).apply_async()


@app.task(name="map_source", queue="mapping", priority=0)
def map_source(data):
    """
    Task for handling list of articles
    we will check list of articles and send to scrape only missing, updated or new one
    """
    from worker import db_conn

    def get_article_info(article_data):
        """
        Get basic info about article:
        id - uniq indetificator
        updated - last time article was updated (i saw article can be updated even if published before)
        """
        return {
            "id": article_data.get("id", None),
            "updated": article_data.get("content", {}).get("updated", None),
        }

    def check_article(article_info):
        """
        Before we send to scrape, we need to decide is this article new or maybe updated in mean time

        INFO: Since this is test we will query here, but in some normal casses this should be some kind of repositorium
        """
        cur = db_conn.cursor()
        new_id = article_info["id"]
        new_updated = article_info["updated"]

        cur.execute(
            "SELECT count(*) as cnt FROM articles "
            f"WHERE id={new_id} AND updated='{new_updated}'::timestamp;"
        )
        result = cur.fetchone()
        cur.close()
        return True if result[0] == 0 else False

    articles = data.get("content", {}).get("elements", None)
    if not articles:
        return

    articles = filter(lambda x: x["type"] == "articles", articles)
    for article in articles:
        info = get_article_info(article)
        need_scrape = check_article(info)

        if need_scrape:
            fetch_article.s(info["id"]).apply_async()


@app.task(name="fetch_article", queue="scraping", priority=9)
def fetch_article(data):
    """
    Task for scraping article - scrape article for it's content
    """
    url = f"https://feed-prod.unitycms.io/2/content/{data}"

    result = get_url_content(url)
    if result["status"] == "error":
        error_log.s(result["data"]).apply_async()
        return

    map_article.s(result["data"]).apply_async()


@app.task(name="map_article", queue="mapping", priority=9)
def map_article(data):
    """
    Task for handling article data - we will transform data and store in DB
    """

    def get_article_content(article_data):
        """
        Get content text of article
        """
        content = ""
        for item in article_data:
            if item["type"] == "textBlockArray":
                sub_content = ""
                for part in item["items"]:
                    sub_content += part["htmlText"]
                content += f"{sub_content}\n"
            elif item["type"] == "crosshead":
                content += f"\n\n{item['htmlText']}\n\n"
        return content.strip()

    def check_is_covid_related(article_data):
        """
        Check is article covid related
        """
        for check in ["title_header", "title", "lead"]:
            check_text = article_data[check].lower().strip()
            if (
                check_text.startswith("corona")
                or " corona" in check_text
                or "covid-19" in check_text
            ):
                return True
        return False

    def insert_or_update_article(article_data):
        """
        Insert data into table
        """
        from worker import db_conn

        cur = db_conn.cursor()
        sql_text = generate_sql_upsert(
            "public", "articles", article_data.keys(), ["id"]
        )
        cur.execute(sql_text, article_data)
        cur.close()
        db_conn.commit()

    article = {
        "id": data["id"],
        "published": data["content"]["meta"]["published"],
        "updated": data["content"]["meta"]["updated"],
        "title_header": data["content"]["article"]["titleHeader"],
        "title": data["content"]["article"]["title"],
        "lead": data["content"]["article"]["lead"],
        "content": get_article_content(data["content"]["article"]["elements"]),
        "covid_related": False,
    }

    article["covid_related"] = check_is_covid_related(article)
    insert_or_update_article(article)


@app.task(name="error_log", queue="mapping", priority=9)
def error_log(data):
    """
    Task for handling error log

    INFO: for now, we will just put to stdout - this should go to DB or some other log consumer
    """
    print(data)

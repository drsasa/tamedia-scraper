def get_covid_articles_count(articles_date, conn):
    """
    Get count of covid related articles for specific date
    """

    cur = conn.cursor()
    cur.execute(
        "SELECT count(*) as cnt FROM articles "
        f"WHERE published::date = '{articles_date}' AND covid_related = true;"
    )
    result = cur.fetchone()
    cur.close()

    return result[0]

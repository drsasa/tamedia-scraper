from requests import Session


def get_url_content(url):
    result = {}

    with Session() as session:
        try:
            resp = session.get(url, allow_redirects=True)
            if resp.status_code != 200:
                result = {"status": "error", "data": f"URL returned status {resp.status_code}"}
            result = {"status": "ok", "data": resp.json()}
        except Excpetion as ex:
            result = {"status": "error", "data": str(ex)}

    return result


def generate_sql_upsert(schema, table, all_fields, uniq_fields):
    sql_text = """
        INSERT INTO {schema}.{table}({fields})
        VALUES ({value_fields})
        ON CONFLICT ({conflict_fields})
        DO UPDATE SET {update_fields};
    """

    fields = ",".join(all_fields)
    conflict_fields = ",".join(uniq_fields)

    value_fields = ",".join(
        map(lambda x: "%({name})s".format(name=x)
            if "updated" not in x and "published" not in x
            else "%({name})s::timestamp".format(name=x),
            all_fields)
    )

    all_fields_update = [x for x in all_fields if x not in uniq_fields]
    update_fields = ",".join(
        map(lambda x: "{name} = EXCLUDED.{name}".format(name=x),
            all_fields_update)
    )

    return sql_text.format(
        schema=schema,
        table=table,
        fields=fields,
        value_fields=value_fields,
        conflict_fields=conflict_fields,
        update_fields=update_fields
    )

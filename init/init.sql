--- init SQL

CREATE TABLE IF NOT EXISTS public.articles
(
	id bigint not null,
	published timestamp,
	updated timestamp,
	title_header text,
	title text,
	lead text,
	content text,
    covid_related bool,
	created_at timestamp default current_timestamp
);

create unique index articles_id_uindex
	on public.articles (id);

alter table public.articles
	add constraint articles_pk
		primary key (id);

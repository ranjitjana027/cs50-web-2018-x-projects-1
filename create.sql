create table books
(isbn varchar(20) primary key,
title varchar(50) not null,
author varchar(50) not null,
year integer not null,
avg_rating integer,
rating_count integer
);

create table reviews
(
isbn varchar(20) references books(isbn) on delete cascade,
user_id integer references user_login_details(id) on delete cascade,
rating integer,
review varchar(40));
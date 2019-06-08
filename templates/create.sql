create table user_login_details
(id serial primary key,
email varchar(25) unique not null,
username varchar(25) not null,
password varchar(25) not null
);
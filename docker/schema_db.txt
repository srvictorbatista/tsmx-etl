begin;

create table tbl_oscar (
    id bigserial not null,
    ceremony int4 not null,
    year int4 not null,
    primary key (id),
    unique(ceremony)
);

create table tbl_class (
    id bigserial not null,
    description varchar(255) not null,
    primary key (id),
    unique (description)
);

create table tbl_category (
    id bigserial not null,
    description varchar(500) not null,
    primary key (id),
    unique (description)
);

create table tbl_movie (
    id bigserial not null,
    title varchar(500) not null,
    primary key (id),
    unique (title)
);

create table tbl_nominees (
    id bigserial not null,
    oscar_id bigint not null,
    class_id bigint not null,
    category_id bigint not null,
    movie_id bigint not null,
    name varchar(500) null,
    nominees varchar(500) null,
    winner boolean not null default false,
    detail text null,
    note text null,
    primary key (id),
    foreign key (oscar_id) references tbl_oscar (id) on update cascade on delete cascade,
    foreign key (class_id) references tbl_class (id) on update cascade on delete cascade,
    foreign key (category_id) references tbl_category (id) on update cascade on delete cascade,
    foreign key (movie_id) references tbl_movie (id) on update cascade on delete cascade
);

commit;

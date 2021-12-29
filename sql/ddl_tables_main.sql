"""
Таблицы для сайтов-источников
"""

create table src_gs_calendar (
	event_id     INT not null auto_increment primary key,
 	name         varchar(255),
 	event_date   varchar(50),
 	place        varchar(255),
 	site         varchar(255),
 	descr        text          not null
);

create table src_gs_startups (
	event_id     INT           not null auto_increment primary key,
 	name         varchar(255)  not null,
 	site         varchar(255)  not null,
 	event_type   varchar(50)   not null
);

create table src_rvc (
	event_id     INT           not null auto_increment primary key,
 	name         varchar(255)  not null,
 	event_date   varchar(50)   not null,
 	place        varchar(255)  not null,
 	site         varchar(255)  not null,
 	descr        text          not null
);

create table src_changellenge (
	event_id     INT           not null auto_increment primary key,
 	name         varchar(255)  not null,
 	event_date   varchar(50)   not null,
 	site         varchar(255)  not null,
 	status       varchar(50)   not null
);

create table src_rb (
	event_id     INT           not null auto_increment primary key,
 	name         varchar(255)  not null,
 	event_date   varchar(50)   not null,
 	site         varchar(255)  not null,
 	event_type   varchar(50)   not null
);



create table src_info_letter (
	file_id      int auto_increment PRIMARY KEY,
	file_name    varchar(255),
	link         varchar(255)
);


"""
Спровочники
"""

create table d_tag (
	tag_id      int auto_increment PRIMARY KEY,
	name        varchar(10),
	link        varchar(255)
);

create table d_tag_array (
	tag_id      int,
	key_word    varchar(50)
);


create table d_event_type (
	type_id     int auto_increment PRIMARY KEY,
	name        varchar(10),
	link        varchar(255)
);


create table d_src (
	src_id      int auto_increment PRIMARY KEY,
	table_name  varchar(20),
	link        varchar(255)
);

"""
Факты
"""

create table f_information (
	event_id      int auto_increment PRIMARY KEY,
	name          varchar(255),
	site          varchar(255),
	post_link     varchar(255),
	date_from     date,
	date_to       date,
	event_type    varchar(255),
	status        varchar(255),
	is_published  bool,
	is_deleted    bool,
	src_id        int,
	
	FOREIGN KEY (src_id) REFERENCES d_src (src_id)
);


create table f_post (
	event_id      int auto_increment PRIMARY KEY,
	name          varchar(255),
	place         varchar(255),
	site          varchar(255),
	post_link     varchar(255),
	date_from     date,
	date_to       date,
	descr         text,
	is_published  bool,
	is_deleted    bool,
	src_id        int,
	
	FOREIGN KEY (src_id) REFERENCES d_src (src_id)
);

"""
Маппинги
"""

create table m_tag_event (
	tag_event_id int auto_increment PRIMARY KEY,
	tag_id       int,
	event_id     int,
	
	FOREIGN KEY (tag_id)REFERENCES d_tag (tag_id),
	FOREIGN KEY (event_id) REFERENCES f_post (event_id)
);


create table m_event_type_event (
	type_event_id int auto_increment PRIMARY KEY,
	type_id       int,
	event_id      int,
	
	FOREIGN KEY (type_id) REFERENCES d_event_type (type_id),
	FOREIGN KEY (event_id) REFERENCES f_post (event_id)
);
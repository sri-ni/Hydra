drop table if exists entries;

create table entries (
	id integer primary key autoincrement,
	timestamp string not null,
	liquid string not null,
	qty string not null,
	username string not null
	);
	
create table accounts (
	username string primary key not null,
	password string not null
	);

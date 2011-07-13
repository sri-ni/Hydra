drop table if exists entries;
create table entries (
	id integer primary key autoincrement,
	liquid string not null,
	qty string not null
	);
create table accounts (
	username string primary key not null,
	password string not null
	);

drop table if exists entries;
create table entries (
	id integer primary key autoincrement,
	liquid string not null,
	qty string not null
	);
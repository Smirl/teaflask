drop table if exists pots;
create table pots (
  id integer primary key autoincrement,
  datetime text not null,
  tea text not null,
  brewer text not null,
  drinkable integer not null
);
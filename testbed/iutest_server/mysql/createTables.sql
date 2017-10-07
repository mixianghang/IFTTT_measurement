--create log databses for polling/action request/real time api request
create Table log (id int not null auto_increment primary key, time datetime, requestDetail varchar(32000), responseDetail varchar(32000), type smallint);

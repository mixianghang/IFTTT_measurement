--device table
Create Table device (id INT auto_increment not null primary key, name varchar(256), userId int, createdTime datetime, deviceType varchar(128), deviceState smallint);
insert into device (name, deviceType, createdTime, userId) values("Wemo Switch 1", "switch", "2017-02-27 13:30:03", 1);
insert into device (name, deviceType, createdTime, userId) values("Hue Light 1 Living Room", "light", "2017-02-27 13:30:03", 1);
insert into device (name, deviceType, createdTime, userId) values("Hue Light 1 Bed Room", "light", "2017-02-27 13:30:03", 1);


--event table
Create Table event (id int auto_increment not null primary key,  deviceId int, deviceState smallint, userId int, eventTime datetime);

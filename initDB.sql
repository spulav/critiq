drop table if exists listcredits;
drop table if exists readinglists;
drop table if exists history;
drop table if exists reviews;
drop table if exists prefs;
drop table if exists commentCredits;
drop table if exists comments;
drop table if exists taglink;
drop table if exists tags;
drop table if exists chapters;
drop table if exists works;
drop table if exists users;

create table users (
    uid int not null auto_increment primary key,
    username varchar(30), 
    passhash char(60),
    unique(username),
    index(username),
    commentscore DECIMAL,
    bio varchar(3000),
    email varchar(200)
);

create table works (
    sid int not null auto_increment primary key,
    uid int not null,
    title VARCHAR(200),
    updated date,
    summary varchar(2000),
    stars float,
    avgRating decimal(10),
    index(uid),
    foreign key (uid) references users(uid)
        on UPDATE cascade
        on delete cascade
)

ENGINE = InnoDB;

create table chapters (
    cnum int not null,
    sid int not NULL,
    filename varchar(100),

    PRIMARY KEY (sid,cnum),
    index(sid),
    foreign key (sid) references works(sid)
        on update cascade
        on delete cascade
)

ENGINE = InnoDB;

create table tags (
    tid int not null auto_increment primary key,
    ttype varchar(20) not null,
    tname varchar(50) not null unique
)

ENGINE = InnoDB;

create table taglink (
    tid int not null,
    sid int not null,

    foreign key(sid) references works(sid)
        on update cascade
        on delete cascade,
    foreign key(tid) references tags(tid)
        on update cascade
        on delete cascade
)

ENGINE = InnoDB;

create table comments (
    commid int not null auto_increment primary key,
    commenter int not null,
    reviewText varchar(2000),
    foreign key(commenter) references users(uid)
)

ENGINE = InnoDB;

create table commentCredits ( 
    commid int not null,
    cid int not null,

    primary key(commid, cid),

    foreign key(commid) references comments(commid)
        on update cascade
        on delete cascade,
    foreign key(cid) references chapters(cid)
        on update cascade
        on delete cascade
)

ENGINE = InnoDB;

create table prefs (
    uid int not null,
    tid int not null,
    isWarning boolean, 
    primary key (uid, tid),

    foreign key(uid) references users(uid)
        on update cascade
        on delete cascade,
    foreign key (tid) references tags(tid)
        on update cascade
        on delete cascade
)
ENGINE = InnoDB;

create table reviews (
    uid int not null,
    sid int not null,
    filename varchar(200),
    rating int not null,
    primary key (uid, sid),
    
    foreign key(uid) references users(uid)
        on update cascade
        on delete cascade,
    foreign key (sid) references works(sid)
        on update cascade
        on delete cascade
)

ENGINE = InnoDB;

create table history (
    uid int not null,
    sid int not null,
    cid int not null,
    visited datetime,
    primary key (uid, sid, cid),
    foreign key(uid) references users(uid)
        on update cascade
        on delete cascade,
    foreign key (sid) references works(sid)
        on update cascade
        on delete cascade,
    foreign key (cid) references chapters(cid)
        on update CASCADE
        on delete cascade
)

ENGINE = InnoDB;

create table readinglists (
    lid int auto_increment not null primary key,
    uid int not null,
    listname varchar(50) not null,

    index(uid)

    foreign key(uid) references users(uid)
        on update CASCADE
        on delete cascade,
)

create table listcredits (
    lid int not null,
    sid int not null, 
    primary key (lid, sid),
    foreign key(lid) references readinglists(lid)
        on update CASCADE
        on delete cascade,
    foreign key(sid) references works(sid)
        on update CASCADE
        on delete cascade
)

ENGINE = InnoDB;

insert into tags values (null, 'genre', 'Romance'), (null, 'genre', 'Fantasy'), 
    (null, 'genre', 'Horror'), (null, 'genre', 'Sci-Fi'), (null, 'genre', 'Historical'),
    (null, 'genre', 'Mystery'), (null, 'genre', 'Humor'), (null, 'genre', 'Literary'),
    (null, 'genre', 'Thriller'), (null, 'genre', 'Suspense'), (null, 'genre', 'Poetry');

insert into tags values (null, 'audience', 'General'), (null, 'audience', 'Young Adult'),
    (null, 'audience', '18+');

insert into tags values (null, 'warnings', 'Violence'), (null, 'warnings', 'Gore'), 
    (null, 'warnings', 'Rape or Sexual Assault'), (null, 'warnings', 'Sexual Content'),  
    (null, 'warnings', 'Racism'), (null, 'warnings', 'Homophobia'), 
    (null, 'warnings', 'Suicidal Content'), (null, 'warnings', 'Abuse'), 
    (null, 'warnings', 'Animal Cruelty'), (null, 'warnings', 'Self-Harm'),
    (null, 'warnings', 'Eating Disorder'), (null, 'warnings', 'Incest'),
    (null, 'warnings', 'Child Abuse or Pedophilia'), (null, 'warnings', 'Death or Dying'),
    (null, 'warnings', 'Pregnancy or Childbirth'),(null, 'warnings', 'Miscarriages orAbortion'),
    (null, 'warnings', 'Mental Illness');

insert into tags values (null, 'isFin', 'Finished'), (null, 'isFin', 'Work in Progress');
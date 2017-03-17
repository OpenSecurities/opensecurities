CREATE TABLE stocks (
    symbol      varchar(8) PRIMARY KEY,
    name        varchar(255) NOT NULL,
    cik         integer NOT NULL,
    city        varchar(75),
    state       char(2),
    zip         char(11),
    street1     varchar(255),
    street2     varchar(255)
);

CREATE TABLE prices (
    symbol      varchar(8) references stocks(symbol),
    date        date,
    open        money,
    high        money,
    low         money,
    close       money,
    adj_open    money,
    adj_high    money,
    adj_low     money,
    adj_close   money,
    volume      integer,
    adj_volume  integer,
    ex_dividend decimal,
    split_ratio decimal,
    PRIMARY KEY(symbol, date)
);

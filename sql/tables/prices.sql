CREATE TABLE prices (
    symbol      varchar(8) references stocks(symbol),
    date        date,
    open        decimal,
    high        decimal,
    low         decimal,
    close       decimal,
    adj_open    decimal,
    adj_high    decimal,
    adj_low     decimal,
    adj_close   decimal,
    volume      integer,
    adj_volume  integer,
    ex_dividend decimal,
    split_ratio decimal,
    PRIMARY KEY(symbol, date)
);

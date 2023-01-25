create table gene_expression
(
    ensembl_id varchar(22),
    gtex_id    varchar(30),
    level      integer
);

create table ensembl2symbol
(
    alias      varchar(32),
    ensembl_id varchar(22),
    symbol     varchar(25),
    entrez_id  integer
);

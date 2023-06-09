create table data_dictionary
(
    varname varchar(10),
    vardesc varchar(310),
    varmeta varchar(10),
    vartype varchar(25)
);

create table ensembl2symbol
(
    alias      varchar(32),
    ensembl_id varchar(22),
    symbol     varchar(25),
    entrez_id  integer
);

create table expression_correlation
(
    gene_a      varchar(15),
    gene_b      varchar(15),
    tissue      varchar(40),
    correlation real
);

create table gene_expression
(
    ensembl_id varchar(22),
    gtex_id    varchar(30),
    level      integer
);

create table gsea
(
    pathway      text,
    pvalue       real,
    padj         real,
    lod2err      real,
    es           real,
    nes          real,
    size         integer,
    ranks        real[],
    leading_edge varchar(25)[],
    varname      varchar(10),
    tissue       varchar(40)
);

create table metadata
(
    gtex_id varchar(30),
    tissue  varchar(40),
    varname varchar(10),
    value   text
);

create table metadata2expression
(
    varname        varchar(10),
    ensembl_id     varchar(25),
    tissue         varchar(40),
    test           varchar(20),
    test_statistic real,
    pvalue         double precision
);

create table metadata2metadata
(
    category_a     varchar(10),
    category_b     varchar(10),
    tissue         varchar(40),
    test           varchar(20),
    test_statistic real,
    pvalue         double precision
);

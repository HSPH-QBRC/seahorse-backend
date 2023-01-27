create table annotations
(
    gtex_id   varchar(42),
    smatsscr  real,
    smcenter  varchar(10),
    smpthnts  text,
    smrin     real,
    smts      varchar(20),
    smtsd     varchar(45),
    smubrid   varchar(12),
    smtsisch  real,
    smtspax   real,
    smnabtch  varchar(40),
    smnabtcht varchar(55),
    smnabtchd date,
    smgebtch  varchar(35),
    smgebtchd date,
    smgebtcht varchar(40),
    smafrze   varchar(10),
    smgtc     varchar(20),
    sme2mprt  real,
    smchmprs  real,
    smntrart  real,
    smnumgps  integer,
    smmaprt   real,
    smexncrt  real,
    sm550nrm  integer,
    smgnsdtc  real,
    smunmprt  real,
    sm350nrm  integer,
    smrdlgth  real,
    smmncpb   integer,
    sme1mmrt  real,
    smsflgth  real,
    smestlbs  real,
    smmppd    real,
    smnterrt  real,
    smrrnanm  real,
    smrdttl   real,
    smvqcfl   real,
    smmncv    integer,
    smtrscpt  real,
    smmppdpr  real,
    smcglgth  integer,
    smgappct  integer,
    smunpdrd  real,
    smntrnrt  real,
    smmpunrt  real,
    smexpeff  real,
    smmppdun  real,
    sme2mmrt  real,
    sme2anti  real,
    smaltalg  real,
    sme2snse  real,
    smmflgth  real,
    sme1anti  real,
    smspltrd  real,
    smbsmmrt  real,
    sme1snse  real,
    sme1pcts  real,
    smrrnart  real,
    sme1mprt  real,
    smnum5cd  integer,
    smdpmprt  real,
    sme2pcts  real,
    sex       integer,
    age       varchar(5),
    dthhrdy   real
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

create table metadata2expression
(
    metadata       varchar(10),
    ensembl_id     varchar(25),
    test           varchar(20),
    test_statistic real,
    pvalue         double precision
);

create table metadata2metadata
(
    metadata1      varchar(10),
    metadata2      varchar(10),
    test           varchar(20),
    test_statistic real,
    pvalue         double precision
);

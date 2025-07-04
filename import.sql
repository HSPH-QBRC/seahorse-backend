CREATE EXTENSION aws_commons;
CREATE EXTENSION aws_s3;

select aws_commons.create_s3_uri(
    'seahorse-data-jq',
    'db_tables/data_dictionary.tsv.gz',
    'us-east-2'
) as s3_uri \gset
select aws_s3.table_import_from_s3(
    'data_dictionary',
    '',
    '(format csv, delimiter E''\t'', header)',
    :'s3_uri'
);

select aws_commons.create_s3_uri(
    'seahorse-data-jq',
    'db_tables/human_ensembl2symbol_map.tsv.gz',
    'us-east-2'
) as s3_uri \gset
select aws_s3.table_import_from_s3(
    'ensembl2symbol',
    '',
    '(format csv, delimiter E''\t'', header)',
    :'s3_uri'
);
create index on ensembl2symbol (ensembl_id);

select aws_commons.create_s3_uri(
    'seahorse-data-jq',
    'db_tables/geneexpression_data.tsv.gz',
    'us-east-2'
) as s3_uri \gset
select aws_s3.table_import_from_s3(
    'gene_expression',
    '',
    '(format csv, delimiter E''\t'', header)',
    :'s3_uri'
);
create index on gene_expression (ensembl_id);

select aws_commons.create_s3_uri(
    'seahorse-data-jq',
    'db_tables/geneexpression2geneexpression.tsv.gz',
    'us-east-2'
) as s3_uri \gset
select aws_s3.table_import_from_s3(
    'expression_correlation',
    '',
    '(format csv, delimiter E''\t'', header)',
    :'s3_uri'
);
alter table expression_correlation add primary key (gene_a, gene_b, tissue);

select aws_commons.create_s3_uri(
    'seahorse-data-jq',
    'db_tables/all_gsea_results.tsv.gz',
    'us-east-2'
) as s3_uri \gset
select aws_s3.table_import_from_s3(
    'gsea',
    '',
    '(format csv, delimiter E''\t'', header)',
    :'s3_uri'
);
create index on gsea (varname);

select aws_commons.create_s3_uri(
    'seahorse-data-jq',
    'db_tables/metadata.tsv.gz',
    'us-east-2'
) as s3_uri \gset
select aws_s3.table_import_from_s3(
    'metadata',
    '',
    '(format csv, delimiter E''\t'', header)',
    :'s3_uri'
);

select aws_commons.create_s3_uri(
    'seahorse-data-jq',
    'db_tables/metadata2expression.tsv.gz',
    'us-east-2'
) as s3_uri \gset
select aws_s3.table_import_from_s3(
    'metadata2expression',
    '',
    '(format csv, delimiter E''\t'', header)',
    :'s3_uri'
);
create index on metadata2expression (varname);
create index on metadata2expression (ensembl_id);

select aws_commons.create_s3_uri(
    'seahorse-data-jq',
    'db_tables/metadata2metadata.tsv.gz',
    'us-east-2'
) as s3_uri \gset
select aws_s3.table_import_from_s3(
    'metadata2metadata',
    '',
    '(format csv, delimiter E''\t'', header)',
    :'s3_uri'
);

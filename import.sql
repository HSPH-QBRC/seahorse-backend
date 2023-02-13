select aws_commons.create_s3_uri(
    'seahorse-data',
    'db_tables/metadata_data.tsv.gz',
    'us-east-2'
) as s3_uri \gset
select aws_s3.table_import_from_s3(
    'annotations',
    '',
    '(format csv, delimiter E''\t'', header)',
    :'s3_uri'
);

select aws_commons.create_s3_uri(
    'seahorse-data',
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
    'seahorse-data',
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
    'seahorse-data',
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
    'seahorse-data',
    'db_tables/metadata_desc.tsv.gz',
    'us-east-2'
) as s3_uri \gset
select aws_s3.table_import_from_s3(
    'metadata',
    '',
    '(format csv, delimiter E''\t'', header)',
    :'s3_uri'
);

select aws_commons.create_s3_uri(
    'seahorse-data',
    'db_tables/metadata2geneexpression.tsv.gz',
    'us-east-2'
) as s3_uri \gset
select aws_s3.table_import_from_s3(
    'metadata2expression',
    '',
    '(format csv, delimiter E''\t'', header)',
    :'s3_uri'
);

select aws_commons.create_s3_uri(
    'seahorse-data',
    'db_tables/metadata2metadata.tsv.gz',
    'us-east-2'
) as s3_uri \gset
select aws_s3.table_import_from_s3(
    'metadata2metadata',
    '',
    '(format csv, delimiter E''\t'', header)',
    :'s3_uri'
);

select aws_commons.create_s3_uri(
    'seahorse-data',
    'db_tables/geneexpression_data.tsv.gz',
    'us-east-2'
) as s3_uri \gset

select aws_s3.table_import_from_s3(
    'expression',
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

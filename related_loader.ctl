LOAD CSV  
   FROM 'related_numbered.tsv' WITH ENCODING 'utf-8'
   HAVING FIELDS (id, like_type,  product_id, like_product_id) 
   INTO postgresql://ford@:/amazon?like_product_association
   TARGET COLUMNS (id, like_type, product_id, like_product_id)
   WITH fields terminated by '\t';


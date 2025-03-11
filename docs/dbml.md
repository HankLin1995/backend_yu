Table customers {
  line_id varchar [pk]
  line_name varchar
  line_pic_url varchar
  phone varchar
  email varchar
  address text
  create_date datetime
}

Table products {
  product_id int [pk]
  product_name varchar
  price decimal
  specail_price decimal [null]
  stock_quantity int
  description text
  create_time datetime
}

Table products_categories{

  id int [pk]
  product_id int [ref: > products.product_id]
  categories_id int [ref: > categories.category_id]
}

Table categories {
  category_id int [pk]
  category_name varchar
}

Table orders {
  order_id int [pk]
  line_id int [ref: > customers.line_id]
  product_id int [ref: > products.product_id]
  order_date datetime
  order_station varchar
  order_status varchar
  total_amount decimal
}

Table order_details {
  order_detail_id int [pk]  // 新增的唯一識別符作為主鍵
  order_id int [ref: > orders.order_id]
  product_id int [ref: > products.product_id]
  quantity int
  unit_price decimal
  subtotal decimal
}

Table product_photos {
  photo_id int [pk]
  product_id int [ref: > products.product_id]
  photo_url varchar
  description varchar
  created_date datetime
}

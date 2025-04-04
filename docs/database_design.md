# 濠鮮資料庫設計文件

## 資料表概覽

本資料庫包含以下資料表：
1. customers (客戶資料)
2. products (商品資料)
3. categories (商品類別)
4. products_categories (商品與類別關聯)
5. orders (訂單主表)
6. order_details (訂單明細)
7. product_photos (商品照片)

## 詳細資料表結構

### 1. customers (客戶資料)
| 欄位名稱 | 資料型態 | 說明 | 備註 |
|---------|----------|------|------|
| line_id | varchar | LINE ID | 主鍵 |
| name | varchar | 客戶名稱 | |
| line_name | varchar | LINE 名稱 | |
| line_pic_url | varchar | LINE 頭像 URL | |
| phone | varchar | 電話號碼 | |
| email | varchar | 電子郵件 | |
| address | text | 地址 | |
| create_date | datetime | 建立日期 | |

### 2. products (商品資料)
| 欄位名稱 | 資料型態 | 說明 | 備註 |
|---------|----------|------|------|
| product_id | int | 商品編號 | 主鍵 |
| product_name | varchar | 商品名稱 | |
| price | decimal | 單價 | |
| unit | varchar | 單位 | |
| one_set_price | decimal | 一組價格 | |
| one_set_quantity | int | 一組數量 | |
| stock_quantity | int | 庫存數量 | |
| description | text | 商品描述 | |
| create_time | datetime | 建立時間 | |

### 3. categories (商品類別)
| 欄位名稱 | 資料型態 | 說明 | 備註 |
|---------|----------|------|------|
| category_id | int | 類別編號 | 主鍵 |
| category_name | varchar | 類別名稱 | |

### 4. products_categories (商品與類別關聯)
| 欄位名稱 | 資料型態 | 說明 | 備註 |
|---------|----------|------|------|
| id | int | 關聯編號 | 主鍵 |
| product_id | int | 商品編號 | 外鍵參考 products.product_id |
| categories_id | int | 類別編號 | 外鍵參考 categories.category_id |

### 5. product_photos (商品照片)
| 欄位名稱 | 資料型態 | 說明 | 備註 |
|---------|----------|------|------|
| photo_id | int | 照片編號 | 主鍵 |
| product_id | int | 商品編號 | 外鍵參考 products.product_id |
| photo_url | varchar | 照片 URL | |
| description | varchar | 照片描述 | |
| created_date | datetime | 建立日期 | |

### 6. orders (訂單主表)
| 欄位名稱 | 資料型態 | 說明 | 備註 |
|---------|----------|------|------|
| order_id | int | 訂單編號 | 主鍵 |
| line_id | int | LINE ID | 外鍵參考 customers.line_id |
| product_id | int | 商品編號 | 外鍵參考 products.product_id |
| order_date | datetime | 訂單日期 | |
| order_station | varchar | 訂單狀態 | |
| order_status | varchar | 訂單狀態 | |
| total_amount | decimal | 訂單總金額 | |

### 7. order_details (訂單明細)
| 欄位名稱 | 資料型態 | 說明 | 備註 |
|---------|----------|------|------|
| order_detail_id | int | 明細編號 | 主鍵 |
| order_id | int | 訂單編號 | 外鍵參考 orders.order_id |
| product_id | int | 商品編號 | 外鍵參考 products.product_id |
| quantity | int | 數量 | |
| unit_price | decimal | 單價 | |
| subtotal | decimal | 小計 | |

## 資料表關聯說明

1. 一個商品可以屬於多個類別，一個類別可以包含多個商品 (多對多關係，透過 products_categories 表實現)
2. 一個訂單對應一個客戶 (一對多關係)
3. 一個訂單可以包含多個商品項目 (一對多關係，透過 order_details 表實現)
4. 一個商品可以有多張照片 (一對多關係)

## 注意事項

1. 所有金額相關欄位使用 decimal 型態以確保精確計算
2. 時間相關欄位統一使用 datetime 型態
3. 主要的識別欄位都設置為主鍵 (Primary Key)
4. 適當的外鍵關聯確保資料完整性
5. 商品特價欄位允許空值，表示該商品目前沒有特價

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
8. pickup_locations (取貨地點)
9. schedules (日程表)

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
| line_id | varchar | LINE ID | 外鍵參考 customers.line_id |
| schedule_id | int | 取貨時段編號 | 外鍵參考 schedules.schedule_id |
| order_date | datetime | 訂單日期 | |
| order_status | varchar | 訂單狀態 | * |   
| payment_method | varchar | 付款方式 | |
| payment_status | varchar | 付款狀態 | * |
| total_amount | decimal | 訂單總金額 | |
| create_time | datetime | 建立時間 | |
| update_time | datetime | 更新時間 | |

* order_status 說明：
  - pending: 訂單未付款
  - paid: 訂單已付款
  - preparing: 訂單備貨中
  - ready_for_pickup: 訂單已備貨
  - completed: 訂單已完成
  - cancelled: 訂單已取消

* payment_status 說明：
  - pending: 付款未完成
  - paid: 付款完成
  - refunded: 退款完成

### 7. order_details (訂單明細)
| 欄位名稱 | 資料型態 | 說明 | 備註 |
|---------|----------|------|------|
| order_detail_id | int | 明細編號 | 主鍵 |
| order_id | int | 訂單編號 | 外鍵參考 orders.order_id |
| product_id | int | 商品編號 | 外鍵參考 products.product_id |
| quantity | int | 數量 | |
| unit_price | decimal | 單價 | |
| subtotal | decimal | 小計 | |
| discount_id | int | 折扣編號 | 外鍵參考 product_discounts.discount_id，可為空 |

### 8. pickup_locations (取貨地點)
| 欄位名稱 | 資料型態 | 說明 | 備註 |
|---------|----------|------|------|
| location_id | int | 地點編號 | 主鍵 |
| district | varchar | 鄉鎮市 | |
| name | varchar | 地點名稱 | |
| address | text | 地址 | 可為空 |
| coordinate_x | decimal(10,6) | 座標X | 可為空 |
| coordinate_y | decimal(10,6) | 座標Y | 可為空 |
| photo_path | varchar | 照片路徑 | 可為空 |
| create_time | datetime | 建立時間 | |

### 9. schedules (日程表)
| 欄位名稱 | 資料型態 | 說明 | 備註 |
|---------|----------|------|------|
| schedule_id | int | 日程編號 | 主鍵 |
| date | date | 日期 | 與 location_id 共同構成唯一索引 |
| location_id | int | 取貨地點編號 | 外鍵參考 pickup_locations.location_id，與 date 共同構成唯一索引 |
| pickup_start_time | time | 取貨時間起 | |
| pickup_end_time | time | 取貨時間迄 | |
| status | varchar | 狀態 | 預設為 ACTIVE |
| create_time | datetime | 建立時間 | |

## 資料表關聯說明

1. 一個商品可以屬於多個類別，一個類別可以包含多個商品 (多對多關係，透過 products_categories 表實現)
2. 一個訂單對應一個客戶 (一對多關係)
3. 一個訂單可以包含多個商品項目 (一對多關係，透過 order_details 表實現)
4. 一個商品可以有多張照片 (一對多關係)
5. 取貨地點為獨立資料表，可供訂單參考使用
6. 一個日期可以對應多個取貨地點，但同一天同一地點不能重複排程 (透過 date 和 location_id 的複合索引確保)

## 注意事項

1. 所有金額相關欄位使用 decimal 型態以確保精確計算
2. 時間相關欄位統一使用 datetime 型態
3. 主要的識別欄位都設置為主鍵 (Primary Key)
4. 適當的外鍵關聯確保資料完整性
5. 商品特價欄位允許空值，表示該商品目前沒有特價

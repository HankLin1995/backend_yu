-- 修改 orders 表，允許 schedule_id 為 NULL 並添加配送相關欄位
ALTER TABLE orders MODIFY COLUMN schedule_id INT NULL;
ALTER TABLE orders ADD COLUMN delivery_address VARCHAR(255) NULL;
ALTER TABLE orders ADD COLUMN delivery_method VARCHAR(50) NULL;

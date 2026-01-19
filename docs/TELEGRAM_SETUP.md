# Telegram 通知設定指南

本指南說明如何設定 Telegram Bot 以接收價格警報通知。

## 1. 建立 Telegram Bot

1. 在 Telegram 搜尋 `@BotFather` 並開始對話
2. 發送 `/newbot` 指令
3. 依照提示設定：
   - Bot 名稱（顯示名稱，如：PChome Price Tracker）
   - Bot username（唯一識別碼，需以 `bot` 結尾，如：pchome_price_bot）
4. 建立成功後，BotFather 會回傳 **Bot Token**
   - 格式：`123456789:ABCdefGHIjklMNOpqrsTUVwxyz`
   - **請妥善保管此 Token，不要外洩**

## 2. 取得你的 Chat ID

Chat ID 是你的 Telegram 帳號識別碼，Bot 需要此 ID 才能發送訊息給你。

### 方法一：使用 @userinfobot（推薦）

1. 在 Telegram 搜尋 `@userinfobot`
2. 發送任意訊息（如 `/start` 或 `hi`）
3. Bot 會回傳你的資訊，包含 `Id: 123456789`
4. 這個數字就是你的 Chat ID

### 方法二：使用 @raw_data_bot

1. 在 Telegram 搜尋 `@raw_data_bot`
2. 發送任意訊息
3. Bot 會回傳 JSON 格式的資料
4. 找到 `"from": { "id": 123456789 }` 中的數字

## 3. 啟用 Bot 對話

**重要**：在設定環境變數之前，你必須先與 Bot 對話。

1. 在 Telegram 搜尋你剛建立的 Bot（用 @username）
2. 點擊 `Start` 或發送 `/start`
3. 這樣 Bot 才有權限發送訊息給你

## 4. 設定環境變數

### 本地執行

在 `.env` 檔案中新增：

```bash
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=987654321
```

### Docker / Kubernetes

參考 `k8s/secret.example.yaml` 或在 docker run 時加入環境變數：

```bash
podman run --rm \
  -e TELEGRAM_BOT_TOKEN=your-token \
  -e TELEGRAM_CHAT_ID=your-chat-id \
  ...
```

## 5. 測試通知

執行追蹤程式，確認看到以下輸出：

```
📢 Telegram notifications: Enabled
```

當有商品達到歷史新低時，你會收到 Telegram 通知。

## 常見問題

### Q: 設定後沒有收到通知？

1. 確認已與 Bot 對話（發送 `/start`）
2. 確認 `TELEGRAM_BOT_TOKEN` 和 `TELEGRAM_CHAT_ID` 都有設定
3. 檢查程式輸出是否有錯誤訊息

### Q: 收到 "chat not found" 錯誤？

這表示 Bot 無法發送訊息給指定的 Chat ID。請確認：
1. Chat ID 正確
2. 已與 Bot 開始對話

### Q: Token 外洩了怎麼辦？

1. 到 @BotFather 發送 `/revoke`
2. 選擇要撤銷 Token 的 Bot
3. 取得新 Token 並更新環境變數

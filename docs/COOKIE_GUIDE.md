# PChome Cookie 獲取指南

本工具需要 PChome 的 `ECWEBSESS` cookie 來存取追蹤清單 API。由於此 cookie 標記為 `httpOnly`，無法透過 JavaScript 直接讀取，需要手動從瀏覽器獲取。

## 必要的 Cookie

| Cookie 名稱 | 說明 | 有效期 |
|-------------|------|--------|
| `ECWEBSESS` | PChome 會員登入 session | 約 2 年 |

## 獲取方法

### 方法一：從 Application 面板獲取（推薦）

1. 開啟 Chrome 瀏覽器，前往 [PChome 24h](https://24h.pchome.com.tw/)
2. 登入您的 PChome 帳號
3. 按 `F12` 開啟 DevTools
4. 點擊上方的 **Application** 標籤
5. 左側選擇 **Cookies** > `https://24h.pchome.com.tw`
6. 找到 **ECWEBSESS**，雙擊 **Value** 欄位複製值

```
範例值格式：2812f3bc8a.4137ae74eba95caa2f1d736b7db2ee034c0f8db9.1768830861
```

### 方法二：從 Network 請求獲取

1. 開啟 Chrome 瀏覽器，前往 [PChome 24h](https://24h.pchome.com.tw/)
2. 登入您的 PChome 帳號
3. 按 `F12` 開啟 DevTools
4. 點擊上方的 **Network** 標籤
5. 在搜尋框輸入 `trace/list` 過濾請求
6. 前往 [追蹤清單頁面](https://24h.pchome.com.tw/vip/wishlist/trace)
7. 點擊任一請求，在 **Headers** 標籤找到 **Request Headers** > **cookie**
8. 從 cookie 字串中找到 `ECWEBSESS=xxx` 部分，複製 `xxx` 的值

### 方法三：使用 Console Script 快速複製

在 DevTools 的 **Console** 標籤中貼上以下程式碼：

```javascript
// PChome Cookie Extractor
// 由於 ECWEBSESS 是 httpOnly，此 script 會引導您從 Application 面板複製

(async () => {
  console.log('%c=== PChome Cookie Extractor ===', 'color: #e24c1f; font-size: 16px; font-weight: bold;');
  console.log('');
  console.log('%c📋 請按照以下步驟獲取 ECWEBSESS cookie:', 'color: #333; font-size: 14px;');
  console.log('');
  console.log('1. 點擊上方的 "Application" 標籤');
  console.log('2. 左側展開 "Cookies" > 選擇 "https://24h.pchome.com.tw"');
  console.log('3. 找到 "ECWEBSESS" 這一列');
  console.log('4. 雙擊 "Value" 欄位，按 Ctrl+C 複製');
  console.log('');
  console.log('%c💡 提示：ECWEBSESS 是 httpOnly cookie，無法透過 JavaScript 讀取', 'color: #666; font-style: italic;');
  console.log('');

  // 測試當前登入狀態
  try {
    const response = await fetch('https://ecvip.pchome.com.tw/fsapi/member/products/trace/list?page=1&limit=1', {
      credentials: 'include',
      headers: { 'accept': 'application/json' }
    });
    if (response.ok) {
      const data = await response.json();
      console.log('%c✅ 登入狀態：已登入', 'color: green; font-weight: bold;');
      console.log(`   追蹤商品數量：${data.TotalProducts} 件`);
    } else {
      console.log('%c❌ 登入狀態：未登入或 Session 已過期', 'color: red; font-weight: bold;');
    }
  } catch (e) {
    console.log('%c⚠️ 無法檢查登入狀態', 'color: orange;');
  }
})();
```

## 驗證 Cookie 是否有效

獲取 cookie 後，可以使用以下命令驗證是否有效：

```bash
# 將 YOUR_COOKIE_VALUE 替換為實際的 ECWEBSESS 值
curl -s "https://ecvip.pchome.com.tw/fsapi/member/products/trace/list?page=1&limit=1" \
  -H "cookie: ECWEBSESS=YOUR_COOKIE_VALUE" \
  -H "accept: application/json" \
  -H "user-agent: Mozilla/5.0 AppleWebKit/537.36" | jq '.TotalProducts'
```

成功時會顯示追蹤商品數量，失敗則會返回空白或錯誤。

## Cookie 更新時機

以下情況需要重新獲取 cookie：

1. Cookie 過期（約 2 年後）
2. 手動登出 PChome 帳號
3. 在其他裝置登入同一帳號（可能導致舊 session 失效）
4. PChome 系統維護後

## 設定到 .env

將獲取的 cookie 值填入專案根目錄的 `.env` 檔案：

```env
PCHOME_ECWEBSESS=你複製的cookie值
```

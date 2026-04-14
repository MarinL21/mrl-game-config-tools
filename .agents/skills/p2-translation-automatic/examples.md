# 本地化配置示例

## 完整输出示例

### 示例1：商店界面

**输入场景：** 商店页面包含标题、购买按钮、价格显示

```markdown
| ID_int | ID | cn | en | fr | de | po | zh | id | th | sp | ru | tr | vi | it | pl | ar | jp | kr | cns |
|--------|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|-----|
| 10110300001 | shop_title | 商店 | Shop | Boutique | Laden | Loja | 商店 | Toko | ร้านค้า | Tienda | Магазин | Mağaza | Cửa hàng | Negozio | Sklep | متجر | ショップ | 상점 | 商店 |
| 10110300002 | shop_btn_buy | 购买 | Buy | Acheter | Kaufen | Comprar | 購買 | Beli | ซื้อ | Comprar | Купить | Satın Al | Mua | Acquista | Kup | شراء | 購入 | 구매 | 購買 |
| 10110300003 | shop_price_desc | 价格：{0} | Price: {0} | Prix : {0} | Preis: {0} | Preço: {0} | 價格：{0} | Harga: {0} | ราคา: {0} | Precio: {0} | Цена: {0} | Fiyat: {0} | Giá: {0} | Prezzo: {0} | Cena: {0} | السعر: {0} | 価格：{0} | 가격: {0} | 價格：{0} |
```

> 备注：shop_price_desc 的 {0} = 价格数值

---

### 示例2：带颜色的状态文本

**输入场景：** 资源状态显示（足够/不足）

```markdown
| ID_int | ID | cn | en | fr | de | po | zh | id | th | sp | ru | tr | vi | it | pl | ar | jp | kr | cns |
|--------|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|-----|
| 10110400001 | bag_have_enough | <color=#3ef742>资源充足</color> | <color=#3ef742>Sufficient</color> | <color=#3ef742>Suffisant</color> | <color=#3ef742>Ausreichend</color> | <color=#3ef742>Suficiente</color> | <color=#3ef742>資源充足</color> | <color=#3ef742>Cukup</color> | <color=#3ef742>เพียงพอ</color> | <color=#3ef742>Suficiente</color> | <color=#3ef742>Достаточно</color> | <color=#3ef742>Yeterli</color> | <color=#3ef742>Đủ</color> | <color=#3ef742>Sufficiente</color> | <color=#3ef742>Wystarczające</color> | <color=#3ef742>كافٍ</color> | <color=#3ef742>十分</color> | <color=#3ef742>충분</color> | <color=#3ef742>資源充足</color> |
| 10110400002 | bag_not_enough | <color=#CD2F2F>资源不足</color> | <color=#CD2F2F>Insufficient</color> | <color=#CD2F2F>Insuffisant</color> | <color=#CD2F2F>Unzureichend</color> | <color=#CD2F2F>Insuficiente</color> | <color=#CD2F2F>資源不足</color> | <color=#CD2F2F>Tidak Cukup</color> | <color=#CD2F2F>ไม่เพียงพอ</color> | <color=#CD2F2F>Insuficiente</color> | <color=#CD2F2F>Недостаточно</color> | <color=#CD2F2F>Yetersiz</color> | <color=#CD2F2F>Không đủ</color> | <color=#CD2F2F>Insufficiente</color> | <color=#CD2F2F>Niewystarczające</color> | <color=#CD2F2F>غير كافٍ</color> | <color=#CD2F2F>不足</color> | <color=#CD2F2F>부족</color> | <color=#CD2F2F>資源不足</color> |
```

---

### 示例3：多参数复杂文本

**输入场景：** 升级提示"需要{0}金币，当前拥有{1}"

```markdown
| ID_int | ID | cn | en | fr | de | po | zh | id | th | sp | ru | tr | vi | it | pl | ar | jp | kr | cns |
|--------|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|-----|
| 10110500001 | hero_upgrade_cost | 需要{0}金币，当前拥有{1} | Requires {0} Gold, you have {1} | Nécessite {0} Or, vous avez {1} | Benötigt {0} Gold, du hast {1} | Requer {0} Ouro, você tem {1} | 需要{0}金幣，當前擁有{1} | Butuh {0} Koin, kamu punya {1} | ต้องการ {0} ทอง มี {1} | Requiere {0} Oro, tienes {1} | Нужно {0} золота, у вас {1} | {0} Altın gerekli, {1} var | Cần {0} Vàng, bạn có {1} | Richiede {0} Oro, hai {1} | Wymaga {0} Złota, masz {1} | يتطلب {0} ذهب، لديك {1} | {0}ゴールド必要、所持{1} | {0} 골드 필요, 보유 {1} | 需要{0}金幣，當前擁有{1} |
```

> 备注：{0}=所需金币数, {1}=当前拥有数

---

### 示例4：换行文本

**输入场景：** 确认弹窗内容（多行）

```markdown
| ID_int | ID | cn | en |
|--------|----|----|-----|
| 10110100010 | confirm_delete_desc | 确定要删除该物品吗？\n删除后无法恢复 | Are you sure you want to delete this item?\nThis action cannot be undone |
```

---

### 示例5：图文混排

**输入场景：** 显示"获得 100 [金币图标]"

```markdown
| ID_int | ID | cn | en |
|--------|----|----|-----|
| 10110100011 | reward_gold_get | 获得{0}<quad displaykey=icon_gold size=28 offsety=-4 /> | Get {0}<quad displaykey=icon_gold size=28 offsety=-4 /> |
```

> 备注：{0}=金币数量

---

## 常见场景ID命名规范

### 按钮类
```
btn_confirm      - 确认按钮
btn_cancel       - 取消按钮
btn_close        - 关闭按钮
btn_back         - 返回按钮
btn_next         - 下一步
btn_prev         - 上一步
btn_submit       - 提交
btn_retry        - 重试
```

### 标题类
```
{module}_title   - 模块标题 (如 shop_title)
{module}_cap     - 弹窗标题 (如 confirm_cap)
{module}_header  - 页头标题
```

### 描述类
```
{module}_desc         - 通用描述
{module}_tips         - 提示文本
{module}_empty_hint   - 空状态提示
{module}_unlock_cond  - 解锁条件
```

### 状态类
```
status_idle           - 空闲中
status_busy           - 忙碌中
status_full           - 已满
status_locked         - 已锁定
status_unlocked       - 已解锁
status_completed      - 已完成
status_claimed        - 已领取
status_expired        - 已过期
```

### 数值类
```
{resource}_amount     - 数量显示
{resource}_cost       - 消耗显示
{resource}_reward     - 奖励显示
{resource}_have       - 拥有显示
{resource}_need       - 需要显示
```

---

## 错误示例与修正

### ❌ 错误：ID含大写
```
ID: Shop_Title  →  ✅ 修正: shop_title
```

### ❌ 错误：中文含空格
```
cn: "需要 100 金币"  →  ✅ 修正: "需要100金币"
```

### ❌ 错误：换行符错误
```
cn: "第一行
第二行"  →  ✅ 修正: "第一行\n第二行"
```

### ❌ 错误：参数不一致
```
cn: "需要{0}金币"
en: "Need Gold"  →  ✅ 修正: "Need {0} Gold"
```

### ❌ 错误：标签未闭合
```
cn: "<color=#FF0000>红色"  →  ✅ 修正: "<color=#FF0000>红色</color>"
```
